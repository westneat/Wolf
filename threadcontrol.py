from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from subprocess import CREATE_NO_WINDOW
import pandas as pd
import time
import requests
import json

f = open("API.txt")
API_KEY = f.read()
f.close()


# queries the API to get the current membername for an ID. Useful because names change, IDs don't
def get_membername(memberid):
    api_url = f"https://gwforums.com/api/users/{memberid}"
    headers = {
        "XF-Api-Key": API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
        }
    response = requests.get(api_url, headers=headers)
    return json.loads(response.text)['user']['username']


# cleans up messages to look for keywords
def parse_post(text):
    parsed_text = ''
    ignore_blockquote = False
    ignore_img = False
    ignore_attach = False
    within_tag = False
    for i in range(len(text)):
        if not ignore_blockquote and not ignore_img and not ignore_attach and not within_tag:
            if text[i:i+6] == '[QUOTE':
                ignore_blockquote = True
            elif text[i:i+4] == '[IMG':
                ignore_img = True
            elif text[i:i+7] == '[ATTACH':
                ignore_attach = True
            elif text[i:i+1] == '[':
                within_tag = True
            else:
                parsed_text = parsed_text + text[i]
        if ignore_blockquote:
            if text[i-8:i] == '[/QUOTE]':
                ignore_blockquote = False
        if ignore_img:
            if text[i-6:i] == '[/IMG]':
                ignore_img = False
        if ignore_attach:
            if text[i-9:i] == '[/ATTACH]':
                ignore_attach = False
        if within_tag:
            if text[i:i+1] == ']':
                within_tag = False
    return parsed_text.replace('\n', '').replace('\t', '').replace('&nbsp;', ' ').replace('@', ' ').strip()


# cleans up messages similar to XenForo for quoting purposes
def parse_quote(text):
    parsed_text = ''
    ignore_blockquote = False
    ignore_attach = False
    for i in range(len(text)):
        if not ignore_blockquote and not ignore_attach:
            if text[i:i+6] == '[QUOTE':
                ignore_blockquote = True
            elif text[i:i+7] == '[ATTACH':
                ignore_attach = True
            else:
                parsed_text = parsed_text + text[i]
        if ignore_blockquote:
            if text[i-8:i] == '[/QUOTE]':
                ignore_blockquote = False
        if ignore_attach:
            if text[i-9:i] == '[/ATTACH]':
                ignore_attach = False
    return parsed_text.replace('&nbsp;', ' ').strip()


# manipulate private chats on XenForo. Chat object represents and manipulates one chat
class Chat:
    def __init__(self, conv_id=''):
        self.headers = {
            "XF-Api-Key": API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.conv_id = conv_id

    def create_conversation(self, title, body, memberlist):
        api_url = "https://gwforums.com/api/conversations/"
        payload = {
            "recipient_ids[]": memberlist,
            "title": title,
            "message": body,
        }
        response = requests.post(api_url, headers=self.headers, data=payload)
        self.conv_id = json.loads(response.text)['conversation']['conversation_id']

    def quote_message(self, messageid):
        api_url = f"https://gwforums.com/api/conversation-messages/{messageid}"
        response = requests.get(api_url, headers=self.headers)
        message = json.loads(response.text)['message']['message']
        username = json.loads(response.text)['message']['User']['username']
        user_id = json.loads(response.text)['message']['User']['user_id']
        return f'[QUOTE={username}, convMessage: {messageid}, member: {user_id}]' + parse_quote(message) + "[/QUOTE]"

    def write_message(self, body):
        api_url = "https://gwforums.com/api/conversation-messages/"
        payload = {
            "conversation_id": self.conv_id,
            "message": body,
        }
        requests.post(api_url, headers=self.headers, data=payload)

    def convo_pieces(self):
        api_url = f"https://gwforums.com/api/conversations/{self.conv_id}/messages"
        response = requests.get(api_url, headers=self.headers)
        pages = json.loads(response.text)['pagination']['last_page']
        items = [[], [], [], []]
        for page in range(1, pages+1):
            response = requests.get(api_url + f"?page={page}", headers=self.headers)
            posts = json.loads(response.text)['messages']
            for post in posts:
                items[0].append(post['message_id'])  # what id
                items[1].append(post['user_id'])  # who posted
                items[2].append(parse_post(post['message']))  # what's message
                items[3].append(post['is_reacted_to'])  # have we seen it before
        return items

    def seen_message(self, messageid):
        api_url = f"https://gwforums.com/api/conversation-messages/{messageid}/react"
        payload = {
            "reaction_id": 22
        }
        requests.post(api_url, headers=self.headers, data=payload)

    def close_chat(self):
        api_url = f"https://gwforums.com/api/conversations/{self.conv_id}"
        payload = {
            "conversation_open": ''
        }
        requests.post(api_url, headers=self.headers, data=payload)

    def open_chat(self):
        api_url = f"https://gwforums.com/api/conversations/{self.conv_id}"
        payload = {
            "conversation_open": True
        }
        requests.post(api_url, headers=self.headers, data=payload)


# manipulate threads on XenForo. Thread object represents and manipulates one message board thread
class Thread:
    def __init__(self, thread_id=''):
        self.headers = {
            "XF-Api-Key": API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        self.forumid = 14
        self.gameover = 35
        self.thread_prefix = 60
        self.thread_id = thread_id
        self.end_in_lynch = False
        if self.thread_id == '':
            self.open = True
        else:
            response = requests.get(f"https://gwforums.com/api/threads/{thread_id}", headers=self.headers)
            self.open = json.loads(response.text)['thread']['discussion_open']

    def create_thread(self, title, body):
        api_url = "https://gwforums.com/api/threads/"
        payload = {
            "node_id": self.forumid,
            "title": title,
            "message": body,
            "prefix_id": self.thread_prefix,
        }
        response = requests.post(api_url, headers=self.headers, data=payload)
        self.thread_id = json.loads(response.text)['thread']['thread_id']

#        payload = {
#     "node_id": forumid,
#     "title": "test poll creation",
#     "message": "last frontier again",
#     "prefix_id": thread_prefix,
#     "discussion_type":"poll",
#     "poll[question]":"Kill someone",
#     "poll[new_responses][]":["Kat","Zell","shortkut"],
#     "poll[max_votes_type]":"single",
#     "poll[public_votes]":"1",
#     "poll[close]":"1",
#     "poll[close_units]":"hours",
# }

    def lock_thread(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}"
        payload = {
            "discussion_open": ''
        }
        requests.post(api_url, headers=self.headers, data=payload)
        self.open = False

    def unlock_thread(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}"
        payload = {
            "discussion_open": True
        }
        requests.post(api_url, headers=self.headers, data=payload)
        self.open = True

    def stick_thread(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}"
        payload = {
            "sticky": True
        }
        requests.post(api_url, headers=self.headers, data=payload)

    def unstick_thread(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}"
        payload = {
            "sticky": ''
        }
        requests.post(api_url, headers=self.headers, data=payload)

    def move_thread(self, destinationid):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}/move"
        payload = {
            "target_node_id": destinationid,
        }
        requests.post(api_url, headers=self.headers, data=payload)

    def gameover(self):
        self.lock_thread()
        self.unstick_thread()
        self.move_thread(self.gameover)

    def write_post(self, body):
        # [QUOTE="dimmerwit, post: 197510, member: 306"]
        api_url = "https://gwforums.com/api/posts/"
        payload = {
            "thread_id": self.thread_id,
            "message": body
        }
        response = requests.post(api_url, headers=self.headers, data=payload)
        post_id = json.loads(response.text)['post']['post_id']
        return post_id

    def thread_pieces(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}/posts"
        response = requests.get(api_url, headers=self.headers)
        pages = json.loads(response.text)['pagination']['last_page']
        items = [[], [], [], []]
        for page in range(1, pages+1):
            response = requests.get(api_url + f"?page={page}", headers=self.headers)
            posts = json.loads(response.text)['posts']
            for post in posts:
                items[0].append(post['post_id'])  # what id
                items[1].append(post['user_id'])  # who posted
                items[2].append(parse_post(post['message'].replace('[', ' [').replace(']', '] ')))  # what's message
                items[3].append(post['is_reacted_to'])  # have we seen it before
        return items

    def seen_post(self, postid):
        api_url = f"https://gwforums.com/api/posts/{postid}/react"
        payload = {
            "reaction_id": 22
        }
        requests.post(api_url, headers=self.headers, data=payload)

    # uses list of names
    def create_poll(self, memberlist):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}/change-type"
        memberlist = sorted(memberlist, key=lambda v: v.upper())
        lynch_threshold = len(memberlist) // 2
        memberlist.append("No Vote")
        payload = {
            "new_thread_type_id": "poll",
            "poll[question]": f"Who should the villagers lynch? ({lynch_threshold} votes required)",
            "poll[new_responses][]": memberlist,
            "poll[max_votes_type]": "single",
            "poll[public_votes]": "1",
            "poll[close]": "1",
            "poll[close_length]": "24",
            "poll[close_units]": "hours",
            }
        requests.post(api_url, headers=self.headers, data=payload)

    def check_poll_closed(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}"
        response = requests.get(api_url, headers=self.headers)
        poll = json.loads(response.text)['thread']['Poll']
        return time.time() > poll['close_date']

    def get_poll_results(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}"
        response = requests.get(api_url, headers=self.headers)
        votes = json.loads(response.text)['thread']['Poll']['responses']
        names = []
        vote_count = []
        for i in votes:
            names.append(votes[i]['text'])
            vote_count.append(votes[i]['vote_count'])
        final_structure = {'Name': names, 'Vote Count': vote_count}
        pandas_structure = pd.DataFrame.from_dict(final_structure)
        pandas_structure = pandas_structure[pandas_structure['Name'] != 'No Vote']
        lynch_threshold = len(pandas_structure) // 2
        top_vote = pandas_structure['Vote Count'].max()
        vote_winners = pandas_structure[pandas_structure['Vote Count'] == top_vote]
        if len(vote_winners) > 1 or top_vote < lynch_threshold:
            return 'None'
        else:
            return vote_winners['Name'].iloc[0]

    def delete_poll(self):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}/change-type"
        payload = {
            "new_thread_type_id": "discussion",
            }
        requests.post(api_url, headers=self.headers, data=payload)

    def edit_post(self, postid, body):
        api_url = f"https://gwforums.com/api/posts/{postid}"
        payload = {
            "message": body,
            }
        requests.post(api_url, headers=self.headers, data=payload)

    def post_shadow(self):
        api_url = f'https://gwforums.com/api/threads/f{self.thread_id}/posts'
        response = requests.post(api_url, headers=self.headers)
        message = json.loads(response.text)['posts'][0]['message']
        postid = json.loads(response.text)['posts'][0]['post_id']
        newmessage = r"[b]The Shadow Wolf has manipulated today's voting.[/b]"+'\n\n'
        self.edit_post(postid, newmessage+message)

        # [QUOTE="Zell 17, post: 197915, member: 45"] [/QUOTE]
    def quote_post(self, postid):
        api_url = f"https://gwforums.com/api/posts/{postid}"
        response = requests.get(api_url, headers=self.headers)
        message = json.loads(response.text)['post']['message']
        username = json.loads(response.text)['post']['User']['username']
        user_id = json.loads(response.text)['post']['User']['user_id']
        return f'[QUOTE={username}, post: {postid}, member: {user_id}]' + parse_quote(message) + "[/QUOTE]"

    # uses player name, OLD name if changing. Need to keep track!
    def change_poll_item(self, member, newname):
        api_url = f"https://gwforums.com/api/threads/{self.thread_id}"
        response = requests.get(api_url, headers=self.headers)
        votes = json.loads(response.text)['thread']['Poll']['responses']
        xref = {}
        for i in votes:
            xref[votes[i]['text']] = i  # names to poll_id dictionary
        if newname == '':
            lynch_threshold = (len(xref)-2) // 2
        else:
            lynch_threshold = (len(xref)-1) // 2
        options = Options()
        options.add_argument("--log-level=3")
        service = Service(r'F:\Python\chromedriver-win64\chromedriver.exe')
        service.creationflags = CREATE_NO_WINDOW
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(100)
        driver.get(r"https://gwforums.com/forums/forum-only-games.14/")
        driver.find_element(By.XPATH, r'//*[@id="top"]/div[1]/nav/div/div[3]/div[1]/a[1]/span').click()
        driver.find_element(By.NAME, "login").send_keys("WolfBot")
        time.sleep(2)
        g = open("Password.txt")
        passwd = g.read()
        g.close()
        driver.find_element(By.NAME, "password").send_keys(passwd)
        driver.find_element(By.XPATH, r'/html/body/div[5]/div/div[2]/div/form/div[1]/dl/dd/div/div[2]/button').click()
        time.sleep(1)
        driver.find_element(By.XPATH, r'/html/body/div[2]/ul/li/div/a').click()
        time.sleep(1)
        driver.find_element(By.XPATH, r'/html/body/div[2]/ul/li/div/div/div/div[2]/ul/li[3]/a').click()
        driver.get(f"https://gwforums.com/threads/{self.thread_id}/poll/edit")
        memberid = xref[member]
        element = driver.find_element(By.NAME, f"poll[existing_responses][{memberid}]")
        element.clear()  # remove a choice
        element.send_keys(newname)  # if blank, choice removed
        element = driver.find_element(By.NAME, f'poll[question]')  # update title
        element.clear()
        element.send_keys(f"Who should the villagers lynch? ({lynch_threshold} votes required)")  # update title
        xpath = r'/html/body/div[1]/div[5]/div/div[2]/div[2]/div/form[1]/div/dl/dd/div/div[2]/button/span'
        driver.find_element(By.XPATH, xpath).click()  # submit updates
        # payload = {
        #    "discussion_type":"poll",
        #    "poll[question]":f"Who should the villagers lynch? ({lynch_threshold} votes required)",
        #    "poll[new_responses][]": names,
        #    "poll[max_votes_type]":"single",
        # }
        # response = requests.post(api_url, headers=self.headers, data=payload)
