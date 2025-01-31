import threadcontrol as tc
import roles as role
import random
import pandas as pd
import copy
import datetime
import re
import inspect
import sys

bot_member_id = 498
admin_id = 3

keywords = ["arm", "visit", "check", "convert", "corrupt", "couple", "deaths", "roles",
            "disguise", "douse", "weapon", "shield", "infect", "jail", "judge", "scribe",
            "kill", "mark", "mute", "nightmare", "poison", "potion", "protect",
            "redirect", "resign", "reveal", "revive", "rock", "sacrifice", "shaman",
            "shoot", "spell", "tag", "take", "trap", "trick", "watch", "water", "cancel",
            "vote", "berserk", "confusion", "shadow", "skip", "action", "escape", "unskipped"]

output_dir = r"Games\\"


def export(value):
    if isinstance(value, str):
        # f.write(attribute + ": " + "'''" + self.__dict__[attribute].replace('\n', 'ZELL/n') + "'''" + '\n')
        return "'''" + value.replace('\n', 'ZELL/n') + "'''"
    elif isinstance(value, (int, bool)):
        return str(value)
    elif isinstance(value, tc.Chat):
        return "tc.Chat(" + str(value.conv_id) + ')'
    elif isinstance(value, tc.Thread):
        return "tc.Thread(" + str(value.thread_id) + ')'
    elif isinstance(value, datetime.datetime):
        return '"' + str(value) + '"'
    elif isinstance(value, role.Player):
        return "Player(" + str(value.gamenum) + ')'
    elif isinstance(value, list):
        text = "["
        for i, item in enumerate(value):
            if i == len(value) - 1:
                text = text + export(item)
            else:
                text = text + export(item) + ','
        return text + ']'
    elif isinstance(value, dict):
        text = "{"
        for key in value:
            text = text + export(key) + ":" + export(value[key]) + ","
        return text + "}"
    else:
        return ''


# test data
# [47, 157, 62, 101, 95, 65, 7, 40, 4, 8, 100, 82, 54, 67, 306, 18]
# Game object is responsible to manipulation of the game states
# Test Wolf Chat = 1425
class Game:
    def __init__(self, player_list=None, game_title=''):
        if player_list is None:
            player_list = []
        self.role_ids = [cls_obj for cls_name, cls_obj in inspect.getmembers(sys.modules['roles'])
                         if (inspect.isclass(cls_obj) and cls_obj != role.Player)]
        self.strong_village = [cls_obj().role for cls_name, cls_obj in inspect.getmembers(sys.modules['roles'])
                               if (inspect.isclass(cls_obj) and cls_obj().category == 'Strong Villager')]
        self.regular_village = [cls_obj().role for cls_name, cls_obj in inspect.getmembers(sys.modules['roles'])
                                if (inspect.isclass(cls_obj) and cls_obj().category == 'Regular Villager')]
        self.wildcard = [cls_obj().role for cls_name, cls_obj in inspect.getmembers(sys.modules['roles'])
                         if (inspect.isclass(cls_obj) and cls_obj().category == 'Wildcard')]
        self.wolves = [cls_obj().role for cls_name, cls_obj in inspect.getmembers(sys.modules['roles'])
                       if (inspect.isclass(cls_obj) and cls_obj().category == 'Werewolf')]
        self.solo = [cls_obj().role for cls_name, cls_obj in inspect.getmembers(sys.modules['roles'])
                     if (inspect.isclass(cls_obj) and cls_obj().category == 'Solo Killer')]
        self.role_dictionary = {}  # gamenum : Role obj
        self.game_title = game_title
        self.player_list = player_list  # as memberids
        self.player_game_numbers = {}  # game number : memberid
        self.wolf_chat = tc.Chat()
        self.admin_pm = tc.Chat()  # Necessary for manipulation of dead forum
        self.new_thread_text = ''
        self.wolf_chat_open = True
        self.night = 1
        self.spell_count = 0  # Used solely for Ritualist revivals
        self.player_names = [tc.get_membername(x) for x in self.player_list]
        self.player_names_caps = [x.upper().replace("'", "").replace('"', '') for x in self.player_names]
        self.player_names_dict = {}
        self.caps_to_id = {}
        for i in range(len(self.player_names_caps)):
            self.caps_to_id[self.player_names_caps[i]] = self.player_list[i]
            self.player_names_dict[self.player_list[i]] = self.player_names[i]
            self.player_names_dict[self.player_names[i]] = self.player_list[i]
        self.master_data = pd.DataFrame.from_dict({
            'Player ID': self.player_list,
            'Player Name': self.player_names,
            'Player Name Caps': self.player_names_caps
        })
        self.saved_conjuror_data = role.Player()
        self.day_thread = tc.Thread()
        self.noun_lookup = {}
        self.jailer_chat = tc.Chat()  # Warden and Jailer use
        self.jailee_chat = tc.Chat()  # Warden and Jailer use
        self.cult_chat = tc.Chat()
        self.jailed = []  # List who is currently jailed
        self.jailer = role.Player()
        self.day_open_tm = datetime.datetime.now()
        self.day_close_tm = datetime.datetime.now()
        self.alch_deaths_tm = datetime.datetime.now()
        self.night_close_tm = datetime.datetime.now()
        self.night_open_tm = datetime.datetime.now()
        self.first_death = role.Player()  # Violinist
        self.couple = []  # Used for Instigator and Cupid
        self.cupid = role.Player()
        self.instigator = role.Player()
        self.confusion_in_effect = False
        self.manual_votes = []  # Added Preacher votes
        self.shadow_in_effect = False
        self.shadow_available = False  # Need to close wolf chat
        self.game_over = False
        self.death = False  # For calculating ties
        self.tie_count = 0  # For calculating ties
        self.cult_chat = tc.Chat()
        self.cultleader = role.Player()
        self.to_skip = []
        self.insti_chat = tc.Chat()
        self.lover_chat = tc.Chat()
        self.rrv = 0
        self.rww = 0
        self.rk = 0
        self.rv = 0
        self.rsv = 0
        self.secondary_text = ''  # Used for when there are multiple kills at once
        self.dead_speaker = role.Player()
        self.first_post = 0
        self.actions = '[table][tr][th]Phase[/th][th]Player[/th][th]Cause of Death[/th][th]Role[/th][/tr][/table]'
        self.log = {'Phase': [], 'Player': [], 'Action': [], 'Result': []}

    def add_action(self, player, method, revealed_role):
        self.actions = self.actions[:self.actions.find("[/table]")]
        phase = "Day " if self.day_thread.open else "Night "
        num = self.night if phase == "Night " else self.night - 1
        self.actions = self.actions + (f"[tr][td]{phase}{num}[/td][td]{player.screenname}[/td]"
                                       f"[td]{method}[/td][td]{revealed_role}[/td][/tr][/table]")

    # Used once, at the end of night 1 to make a pretty table with all nouns -> names
    def print_nouns(self):
        bbcode = "[table]"
        # Add header row
        bbcode += "[tr][th]Player Name[/th][th]Word[/th][/tr]"
        temp = self.master_data.copy()
        temp = temp.sort_values('Player Name')
        # Add rows for each item
        names = temp['Player Name'].to_list()
        nouns = temp['Nouns'].to_list()
        table_len = len(names)
        for i in range(table_len):
            bbcode += "[tr]"
            bbcode += f"[td]{names[i]}[/td][td]{nouns[i]}[/td]"
            bbcode += "[/tr]"
        bbcode += "[/table]"
        return bbcode

    # These methods are necessary as different identifiers are used for different purposes,
    # and we need to be able to go between them easily
    def name_to_gamenum(self, playername):
        gamenums = self.player_game_numbers
        return gamenums['Game Number'][gamenums['Player ID'].index(self.player_names_dict[playername])]

    def gamenum_to_name(self, gamenum):
        gamenums = self.player_game_numbers
        return self.player_names_dict[gamenums['Player ID'][gamenums['Game Number'].index(gamenum)]]

    def memberid_to_name(self, memberid):
        return self.player_names_dict[memberid]

    def gamenum_to_memberid(self, gamenum):
        return self.player_game_numbers['Player ID'][self.player_game_numbers['Game Number'].index(gamenum)]

    def memberid_to_gamenum(self, memberid):
        return self.player_game_numbers['Game Number'][self.player_game_numbers['Player ID'].index(memberid)]

    def gamenum_to_noun(self, gamenum):
        return self.noun_lookup[gamenum]

    # do every iteration in case names change
    def rebuild_dict(self):
        self.player_names = [tc.get_membername(x) for x in self.player_list]
        self.player_names_caps = [x.upper().replace("'", "").replace('"', '') for x in self.player_names]
        old_dict = self.player_names_dict.copy()
        self.player_names_dict = {}
        self.caps_to_id = {}
        # If a name is changed, we'll keep both the old and new
        for i, number in enumerate(self.player_list):
            if old_dict[number] not in self.player_names:
                self.player_names_dict[old_dict[number]] = number
                self.caps_to_id[old_dict[number].upper().replace("'", "").replace('"', '')] = number
        for i in range(len(self.player_names_caps)):
            self.caps_to_id[self.player_names_caps[i]] = self.player_list[i]
            self.player_names_dict[self.player_list[i]] = self.player_names[i]
            self.player_names_dict[self.player_names[i]] = self.player_list[i]
        to_merge = pd.DataFrame.from_dict({
            'Player ID': self.player_list,
            'Player Name': self.player_names,
            'Player Name Caps': self.player_names_caps
        })
        self.master_data = self.master_data.drop(columns=['Player Name', 'Player Name Caps'])
        self.master_data = self.master_data.merge(to_merge, how='inner', on='Player ID')

    # assigns players their game numbers
    def assign_player_numbers(self):
        h = open("nouns.txt", 'r')  # Pull from approved list of nouns that are dissimilar from keywords
        temp = h.read()
        h.close()
        all_nouns = temp.split('\n')
        nouns = []
        scrambled = self.player_list.copy()
        while len(nouns) < len(scrambled):  # randomly choose as many nouns as we have players
            nouns.append(all_nouns.pop(random.randint(0, len(all_nouns)-1)))
        i = 1
        game_num = []
        memberids = []
        while len(scrambled) > 0:
            rand = random.randint(0, len(scrambled)-1)
            game_num.append(i)  # Pick players randomly to assign gamenums
            memberids.append(scrambled.pop(rand))
            self.noun_lookup[i] = nouns[i-1]
            self.noun_lookup[nouns[i-1]] = i  # Creates a noun: gamenum cross reference
            i += 1  # Get next gamenum
        self.player_game_numbers['Game Number'] = game_num
        self.player_game_numbers['Player ID'] = memberids
        self.player_game_numbers['Nouns'] = nouns
        to_merge = pd.DataFrame.from_dict(self.player_game_numbers)
        self.master_data = self.master_data.merge(to_merge, how='inner', on='Player ID')

    # Use this so each player gets the same list of nouns in a different order
    def get_randomized_nouns(self):
        noun_list = []
        fin_list = []
        text = ''
        for i in self.noun_lookup:
            if isinstance(i, int):
                noun_list.append(self.noun_lookup[i])
        while len(noun_list) > 0:
            fin_list.append(noun_list.pop(random.randint(0, len(noun_list)-1)))
        for j in fin_list:
            text = text + j + '\n'
        return text

    # assign numbers first
    # method assigns role and initializes for night 1 use
    def assign_roles(self, rsv=3, rww=4, rv=1, rk=1):
        rrv = len(self.player_list) - rsv - rww - rv - rk
        self.rrv = rrv
        self.rww = rww
        self.rk = rk
        self.rv = rv
        self.rsv = rsv
        # reset master data in case we re-roll
        self.master_data = self.master_data[['Player ID', 'Player Name', 'Player Name Caps', 'Game Number', 'Nouns']]
        # pick number of each category specified
        rsv_roles = [x for x in self.role_ids if x(0).category == "Strong Villager"]
        rrv_roles = [x for x in self.role_ids if x(0).category == "Regular Villager"]
        rww_roles = [x for x in self.role_ids if x(0).category == "Werewolf"
                     and x(0).role not in ['Sorcerer', 'Werewolf']]
        rv_roles = [x for x in self.role_ids if x(0).category == "Wildcard"]
        rk_roles = [x for x in self.role_ids if x(0).category == "Solo Killer"]
        roles = []
        # Pick RSV roles and add to list. Re-pick if criteria aren't met
        while True:
            for i in range(rsv):
                roles.append(rsv_roles[random.randint(0, len(rsv_roles)-1)])
            dead_count = 0
            jail_count = 0
            for i in roles:
                if i(0).speak_with_dead:
                    dead_count += 1
                if i(0).can_jail:
                    jail_count += 1
            if dead_count <= 1 and jail_count <= 1:
                break
            else:
                roles = []
        # Pick RRV roles and add to list.
        for i in range(rrv):
            roles.append(rrv_roles[random.randint(0, len(rrv_roles)-1)])
        # Pick RWW roles and add to list.
        for i in range(rww):
            roles.append(rww_roles[random.randint(0, len(rww_roles)-1)])
        # Pick RK and RV roles and add to list. Re-pick if there are multiple "coupling" roles
        saved_roles = roles.copy()
        while True:
            couples = 0
            for i in range(rk):
                solo = rk_roles[random.randint(0, len(rk_roles)-1)]
                roles.append(solo)
            for i in range(rv):
                wildcard = rv_roles[random.randint(0, len(rv_roles)-1)]
                roles.append(wildcard)
            for i in roles:
                if i(0).can_couple:
                    couples += 1
            if couples <= 1:
                break
            else:
                roles = saved_roles.copy()
        # Mix up roles for number assignment
        roles_fin = []
        for i in range(len(roles)):
            rand = random.randint(0, len(roles) - 1)
            roles_fin.append(roles.pop(rand))
        # Number assignment + update master_data
        temp = []
        # roles initialized here
        for i, j in enumerate(roles_fin):
            self.role_dictionary[i + 1] = j(i + 1, self.gamenum_to_name(i + 1), self.gamenum_to_noun(i + 1))
            temp.append(j(i).role)
            if self.role_dictionary[i + 1].conjuror:
                self.saved_conjuror_data = copy.deepcopy(self.role_dictionary[i + 1])
        # If draw werewolf fan, one wolf becomes Sorcerer
        wildcards = [self.role_dictionary[x] for x in self.role_dictionary
                     if self.role_dictionary[x].category == "Wildcard"]
        for wildcard_obj in wildcards:
            if wildcard_obj.role == "Werewolf Fan":
                while True:
                    rand = random.randint(1, len(self.role_dictionary))
                    if (self.role_dictionary[rand].category == "Werewolf"
                            and self.role_dictionary[rand].role != 'Sorcerer'):
                        temp[rand-1] = 'Sorcerer'
                        self.role_dictionary[rand] = role.Sorcerer(rand, self.role_dictionary[rand].screenname,
                                                                   self.role_dictionary[rand].noun)
                        break
            # Initialize headhunter target
            if wildcard_obj.role == "Headhunter":
                # keep picking players until we get one that hh can target
                while True:
                    rand = random.randint(1, len(self.role_dictionary))
                    if self.role_dictionary[rand].hhtargetable and self.role_dictionary[rand].hhtarget is False:
                        wildcard_obj.target_name = self.gamenum_to_name(rand)
                        self.role_dictionary[rand].hhtarget = True
                        break
        to_merge = pd.DataFrame.from_dict({
            'Role': temp,
            'Game Number': self.role_dictionary.keys()
        })
        self.master_data = self.master_data.merge(to_merge, how='inner', on='Game Number')
        # Initialize Instigator recruits and notable villagers
        for player in self.role_dictionary:
            if self.role_dictionary[player].role == 'Cupid':
                self.cupid = self.role_dictionary[player]
            elif self.role_dictionary[player].speak_with_dead:
                self.dead_speaker = self.role_dictionary[player]
            elif self.role_dictionary[player].role == 'Cult Leader':
                self.cultleader = self.role_dictionary[player]
            elif self.role_dictionary[player].can_jail:
                self.jailer = self.role_dictionary[player]
            elif self.role_dictionary[player].role == 'Instigator':
                self.instigator = self.role_dictionary[player]
                # randomly pick until we get a villager
                while True:
                    pick = random.randint(1, len(self.role_dictionary))
                    if self.role_dictionary[pick].team == 'Village':
                        self.role_dictionary[pick].instigated = True
                        self.couple.append(self.role_dictionary[pick])
                        break
                # randomly pick until we get a wolf
                while True:
                    pick = random.randint(1, len(self.role_dictionary))
                    # no WWfans here
                    if self.role_dictionary[pick].team == 'Wolf' and self.role_dictionary[pick].role != 'Werewolf Fan':
                        self.role_dictionary[pick].instigated = True
                        self.couple.append(self.role_dictionary[pick])
                        break

    def day_post(self):
        post_list = sorted(self.player_names, key=lambda v: v.upper())
        tag_list = ''
        all_alive = True
        for i in post_list:
            if self.role_dictionary[self.name_to_gamenum(i)].alive:
                tag_list = tag_list + '@' + i + '\n'
            else:
                all_alive = False
                tag_list = tag_list + '[s]@' + i + '[/s]' + '\n'
        text0 = "[b]Today's voting has been manipulated by the Shadow Wolf.[/b]\n\n" if self.shadow_in_effect else ''
        text1 = f'''The day will start at [TIME=datetime]{self.night_close_tm.strftime('%Y-%m-%dT%H:%M:%S-0500')}[/TIME]
        
        Dictionary: https://gwforums.com/threads/zell-wolf-role-dictionary-and-hall-of-fame.427/
        
        Here's the list of players:
        
        {tag_list}
        And here are the remaining roles:
        
        Village team:
        {self.rsv}x Random Strong Villagers
        {self.rrv}x Random Regular Villagers
        
        '''
        text2 = ('Note: There will be NO MORE than one person who has a "speak with the dead" role. '
                 'There will also be no more than one person with a "lock players up at night" role. '
                 'There may be none of either, but there will not be multiple.\n\n')

        text3 = f'''Wolf team:
        {self.rww}x Random Wolves
        
        The werewolves can be any of the numbered wolves (except regular werewolf) listed in the dictionary.
        
        Solo team:
        {self.rk}x Random Killer
        
        Wildcard Role:
        {self.rv}x Random Fool/Headhunter/Werewolf Fan/Cupid
        
        If the Werewolf Fan is selected, one wolf will become the Sorcerer.
        
        Rules:
        [spoiler]
        Nights will be 12 hours and days will be 24 hours. The end of the next period will be clearly posted.
        
        You may edit your posts. If you manage to edit out an action before the bot reads it, then it won't count.
        '''
        text4 = ('Votes will be conducted via poll. The poll will close exactly at the deadline. '
                 'You have unlimited changes until that point.\n\n'
                 'There will be a minimum number of votes required to lynch. '
                 'In the event of a tie, nobody is lynched. '
                 'In the event that the minimum number of votes is not reached, nobody is lynched.\n\n'
                 'Skips require a skip vote from every player. '
                 'Once you vote to skip, you cannot unskip. You can skip night sessions in the nightly PM chat.\n\n'
                 'Please do not talk about the game outside of the designated threads. '
                 'This is honor system. When you die, you will gain access to a special forum that is already set up. '
                 'One player may have access to this forum at night. '
                 'If you are revived, you will lose access. '
                 'Please use this forum for all discussion by dead players about the game. '
                 'Alive players can talk during the main thread during the day.\n\n'
                 'It is possible, if very unlikely, for the game to end in a tie if every single player is killed. '
                 'The game also ends in a tie if there are no deaths for three straight days and nights.')

        text5 = f'''[/spoiler]
        Night events will go in the following priority order regardless of when the PMs are sent:
        [spoiler]
        Wolf Nightmare activates
        Wolf Shaman activates
        Werewolf fan reveals
        Confusion activates
        Trickster set
        Wolf Avenger / Avenger tag
        Loudmouth tag
        Player gets Jailed
        Wolves break out of warden prison
        Warden weapon used
        Voodoo wolf / Librarian mute
        Medium/Ritualist revive spell
        Blind wolf/Wolf seer/Sorcerer check
        Blind wolf/Wolf seer/Sorcerer choice to resign
        Blind Wolf check
        Flagger redirect
        Doctor protect
        Jailer/Warden protect
        Bodyguard protect
        Witch protect
        Tough Guy protect
        Defender protect
        Forger Item Completed
        Jelly Wolf Protect
        Illusionist disguise
        Infector attack
        Violinist check + gets results
        Detective check + gets results
        Aura Seer checks + gets results
        Spirit Seer check
        Sheriff check
        Bell Ringer places bells
        Preacher watch
        Marksman shot
        Witch kill (if not killed by marksman, otherwise potion unused)
        Jailer kill (if not killed by marksman/witch)
        Red Lady visit
        Revived players return from the dead (cannot be targeted by wolves/solo in same night)
        Beast Hunter picks up trap (if moved)
        Forger Item Selection
        Solo killer attack
        Wolf berserk mode activates
        Wolves kill
        Spirit Seer gets results
        Sheriff gets results
        Beast Hunter places trap
        Forger Item Gifted
        Cupid selection
        [/spoiler]
        
        In the event that two of the same role perform the exact same action, they will both be credited.
        
        Winning Conditions:\n'''

        text6 = (f"{'[s]' if self.rsv + self.rrv == 0 else ''}Village: Kill {'[s]' if self.rww == 0 else ''}"
                 f"all wolves {'[s]' if self.rk == 0 else ''}and {'[/s]' if self.rww == 0 else ''}"
                 f"the solo killer.{'[/s]' if self.rk == 0 else ''} "
                 f"{'[/s]' if self.rsv + self.rrv == 0 else ''}\n\n{'[s]' if self.rww == 0 else ''}"
                 f"Wolves: {'[s]' if self.rk == 0 else ''}Kill the solo killer."
                 f"{'[/s]' if self.rk == 0 else ''} "
                 f"Afterwards, once the wolves make up half the total players, the wolves win. "
                 f"{'[/s]' if self.rww == 0 else ''}\n\n{'[s]' if self.rk == 0 else ''}"
                 f"Solo Killer: Kill all other players.{'[/s]' if self.rk == 0 else ''}\n\n"
                 f"{'[s]' if self.rv == 0 else ''}Wildcard Role: Satisfy your winning condition. "
                 f"Your winning condition trumps any other that may occur at the same time. "
                 f"(For example, if you lynch the fool and it creates a situation where there are 3 wolves left "
                 f"and 3 villagers, the Fool wins only).{'[/s]' if self.rv == 0 else ''}\n")

        text7 = self.actions if not all_alive else ''
        return text0 + text1 + text2 + text3 + text4 + text5 + text6 + text7

    # can be chat or thread pieces passed in
    def get_keyword_phrases(self, pieces, dedupe=True, new=False):
        # pieces = message_id, user_id, parsed_message, is_reacted_to, message_time, chat/thread obj
        phrases = [[], [], [], [], [], []]
        for index, message in enumerate(pieces[2]):
            message_uniform = message.upper().replace('"', '').replace("'", '')
            # if night 1, delete player names to avoid targeting (except for Cupid)
            if pieces[1][index] != bot_member_id:
                if self.night == 1 and self.role_dictionary[self.memberid_to_gamenum(pieces[1][index])].role != 'Cupid':
                    for name in self.player_names_caps:
                        message_uniform = message_uniform.replace(name, '')
            # replace all nouns with their corresponding name. No need to reverse.
            for gamenum in self.role_dictionary:
                message_uniform = message_uniform.replace(self.noun_lookup[gamenum].upper(),
                                                          self.role_dictionary[gamenum].screenname.upper())
            message_uniform = message_uniform.upper().replace('"', '').replace("'", '')
            # replace names with tokens to fix space issues. Can reverse
            for name in reversed(self.player_names_caps):
                message_uniform = message_uniform.replace(" "+name, " ZELLWOLFBOTID" +
                                                          str(self.caps_to_id[name])+" ")
            message_uniform = re.sub('[^0-9a-zA-Z]+', ' ', message_uniform)
            message_words = message_uniform.split()
            for i, word in enumerate(message_words):
                if i < len(message_words)-1:
                    if word == "WOLFBOT" and message_words[i+1].lower() in keywords:
                        temp = message_words[i + 2:]
                        users = []
                        for j in range(0, len(temp), 2):
                            if "ZELLWOLFBOTID" in temp[j]:
                                users.append(self.role_dictionary[self.name_to_gamenum(
                                    self.player_names_dict[int(temp[j][13:])])])
                            elif (temp[j].lower() in [x.lower() for x in role.kill_methods()['keyword']]
                                  or temp[j].lower() in [x.lower() for x in role.class_list()['keyword']]):
                                users.append(temp[j])
                            else:
                                break
                        if pieces[1][index] in self.player_list:
                            if not new:
                                phrases[0].append(pieces[0][index])  # returns post_id
                                phrases[1].append(self.role_dictionary[self.memberid_to_gamenum(pieces[1][index])])
                                phrases[2].append(message_words[i + 1])  # returns keyword
                                phrases[3].append(users)  # returns users to apply it to (if applicable)
                                phrases[4].append(pieces[4][index])  # returns time
                                phrases[5].append(pieces[5][index])  # returns chat/thread obj
                            else:
                                if pieces[3][index] is False:
                                    phrases[0].append(pieces[0][index])  # returns post_id
                                    phrases[1].append(self.role_dictionary[self.memberid_to_gamenum(pieces[1][index])])
                                    phrases[2].append(message_words[i + 1])  # returns keyword
                                    phrases[3].append(users)  # returns users to apply it to (if applicable)
                                    phrases[4].append(pieces[4][index])  # returns time
                                    phrases[5].append(pieces[5][index])  # returns chat/thread obj
        if dedupe:
            # Once we get all valid commands, now iterate backwards,
            # and we keep only the latest valid command per person for each keyword
            to_sort = pd.DataFrame.from_dict({'post_id': phrases[0], 'player': phrases[1], 'keyword': phrases[2],
                                              'victims': phrases[3], 'times': phrases[4], 'chats': phrases[5]})
            to_sort = to_sort.sort_values('times')
            post_id = to_sort['post_id'].to_list()
            player = to_sort['player'].to_list()
            keyword = to_sort['keyword'].to_list()
            victims = to_sort['victims'].to_list()
            times = to_sort['times'].to_list()
            chats = to_sort['chats'].to_list()
            final_commands = [[], [], [], [], [], []]
            member_keyword_combos = []
            cancel = False
            for i in range(len(phrases[0]) - 1, -1, -1):
                member_keyword = phrases[2][i] + phrases[1][i].screenname
                if (member_keyword not in member_keyword_combos and
                        phrases[1][i].screenname in self.player_names and not cancel):
                    member_keyword_combos.append(member_keyword)
                    final_commands[0].append(post_id[i])  # returns post_id, reverse order
                    final_commands[1].append(player[i])  # returns player, reverse order
                    final_commands[2].append(keyword[i])  # returns keyword, reverse order
                    final_commands[3].append(victims[i])  # returns users to apply it to, reverse order
                    final_commands[4].append(times[i])  # returns time, reverse order
                    final_commands[5].append(chats[i])  # returns chat/thread, reverse order
                    if phrases[2][i] == "cancel":
                        cancel = True
            final_commands_in_order = [[], [], [], [], [], []]
            for i in range(len(final_commands[0])):
                final_commands_in_order[0].append(final_commands[0][len(final_commands[0]) - i - 1])  # return post_id
                final_commands_in_order[1].append(final_commands[1][len(final_commands[0]) - i - 1])  # return player
                final_commands_in_order[2].append(final_commands[2][len(final_commands[0]) - i - 1])  # return keyword
                final_commands_in_order[3].append(final_commands[3][len(final_commands[0]) - i - 1])  # return victims
                final_commands_in_order[4].append(final_commands[4][len(final_commands[0]) - i - 1])  # return time
                final_commands_in_order[5].append(final_commands[5][len(final_commands[0]) - i - 1])  # return chat
        else:
            final_commands_in_order = phrases.copy()
        return final_commands_in_order

    def wolf_vote_update(self):
        pieces = self.wolf_chat.convo_pieces()
        chat = [self.wolf_chat for _ in range(len(pieces[0]))]
        pieces.append(chat)
        pot_votes = self.get_keyword_phrases(pieces, new=True)
        post_ids = []
        posters = []
        votes = []
        for i in range(len(pot_votes[0])):
            if pot_votes[2][i] == "VOTE" and len(pot_votes[3][i]) > 0:
                post_ids.append(pot_votes[0][i])  # returns post_id
                posters.append(pot_votes[1][i])  # returns poster_id as role obj
                votes.append(pot_votes[3][i][0])  # returns who voted for as role obj
            elif pot_votes[2][i] == "VOTE" and len(pot_votes[3][i]) == 0:
                self.wolf_chat.write_message(self.wolf_chat.quote_message(pot_votes[0][i]) +
                                             f"This is not a valid vote for a current player.")
        for i in range(len(votes)):
            if not posters[i].jailed:
                if not posters[i].concussed:
                    if votes[i].wolf_targetable and votes[i].alive:
                        if posters[i].wolf_voting_power > 0:
                            if self.night != 1:
                                self.wolf_chat.write_message(self.wolf_chat.quote_message(post_ids[i]) +
                                                             f"{posters[i].screenname} is "
                                                             f"voting for [b]{votes[i].screenname}[/b]")
                            else:
                                self.wolf_chat.write_message(self.wolf_chat.quote_message(post_ids[i]) +
                                                             f"{posters[i].screenname} is "
                                                             f"voting for [b]{votes[i].noun}[/b]")
                        else:
                            self.wolf_chat.write_message(self.wolf_chat.quote_message(post_ids[i]) +
                                                         f"You must resign in order to vote.")
                    else:
                        self.wolf_chat.write_message(self.wolf_chat.quote_message(post_ids[i]) +
                                                     f"This is not a valid vote for an alive, non-wolf player.")
                else:
                    self.wolf_chat.write_message(self.wolf_chat.quote_message(post_ids[i]) +
                                                 f"You are concussed and cannot vote.")
            else:
                self.wolf_chat.write_message(self.wolf_chat.quote_message(post_ids[i]) +
                                             f"You are jailed, your vote does not count, "
                                             f"and you shouldn't be posting here at all!")

    def count_wolf_votes(self):
        pieces = self.wolf_chat.convo_pieces()
        chat = [self.wolf_chat for _ in range(len(pieces[0]))]
        pieces.append(chat)
        pot_votes = self.get_keyword_phrases(pieces)
        post_ids = []
        posters = []
        votes = []
        times = []
        for i in range(len(pot_votes[0])):
            if pot_votes[2][i] == "VOTE" and len(pot_votes[3][i]) > 0:
                post_ids.append(pot_votes[0][i])  # returns post_id
                posters.append(pot_votes[1][i])
                votes.append(pot_votes[3][i][0])
                times.append(pot_votes[4][i])
        for i in range(len(post_ids)-1, -1, -1):
            # disregard votes for these reasons, the wolf update routine should have weeded out these bad requests
            if (votes[i].wolf_targetable is False or posters[i].wolf_voting_power == 0 or
                    datetime.datetime.fromtimestamp(times[i]) < self.day_open_tm or posters[i].jailed
                    or posters[i].concussed):
                del post_ids[i]
                del posters[i]
                del votes[i]
        vote_table = pd.DataFrame.from_dict(
            {
                'Player Voting': posters,
                'Voted Player': votes,
                'Wolf Power': [x.wolf_voting_power * x.wolf_order for x in posters],
                'Votes': [1 for _ in posters],
                'Random': [random.random() for _ in posters]
            })
        vote_tabulation = vote_table.groupby('Voted Player').sum().reset_index()
        vote_tabulation = vote_tabulation.sort_values(by=['Votes', 'Wolf Power', 'Random'], ascending=False)
        vote_list = vote_tabulation['Voted Player'].tolist()
        return vote_list

    # Use this to change conjuror between roles, also for WWFan and Sorcerer and seer appr
    # Need to be a new role, but keep attributes that keep you "you"
    def role_swap(self, old_role, new_role):
        # save old attributes we want to carry over
        if old_role.role != new_role.role:
            old_role.chat.write_message(f"Your role has changed! Here are some things you may like to know:\n\n"
                                        f"{new_role.initial_PM}")
        if old_role.role == 'Conjuror':
            self.saved_conjuror_data = copy.deepcopy(old_role)
        acting_upon = old_role.acting_upon
        action_used = old_role.action_used
        conjuror_acted = old_role.conjuror_acted
        alive = old_role.alive
        attacking = old_role.attacking
        bell_ringer_watched_by = old_role.bell_ringer_watched_by
        black_potion = old_role.black_potion
        can_jail = old_role.can_jail
        category = old_role.category
        chat = old_role.chat
        concussed = old_role.concussed
        conjuror = old_role.conjuror
        corrupted_by = old_role.corrupted_by
        coupled = old_role.coupled
        cult = old_role.cult
        disguised_by = old_role.disguised_by
        doused_by = old_role.doused_by
        first_seer = old_role.first_seer
        forger_guns = old_role.forger_guns
        forger_shields = old_role.forger_shields
        gamenum = old_role.gamenum
        given_warden_weapon = old_role.given_warden_weapon
        guns_forged = old_role.guns_forged
        has_been_concussed = old_role.has_been_concussed
        has_forger_gun = old_role.has_forger_gun
        has_forger_shield = old_role.has_forger_shield
        has_kill_potion = old_role.has_kill_potion
        has_killed = old_role.has_killed
        has_protect_potion = old_role.has_protect_potion
        hhtarget = old_role.hhtarget
        infected_by = old_role.infected_by
        instigated = old_role.instigated
        jailed = old_role.jailed
        jellied_by = old_role.jellied_by
        last_thread_id = old_role.last_thread_id
        mp = old_role.mp
        muted_by = old_role.muted_by
        night = old_role.night
        night_killed = old_role.night_killed
        nightmared = old_role.nightmared
        noun = old_role.noun
        poisoned = old_role.poisoned
        preacher_watched_by = old_role.preacher_watched_by
        protected_by = old_role.protected_by
        red_potion = old_role.red_potion
        screenname = old_role.screenname
        scribe_method = old_role.scribe_method
        scribed_by = old_role.scribed_by
        seer_apprentice = old_role.seer_apprentice
        shadow = old_role.shadow
        shamaned_by = old_role.shamaned_by
        sheriff_watched_by = old_role.sheriff_watched_by
        shields_forged = old_role.shields_forged
        spelled = old_role.spelled
        tricked_by = old_role.tricked_by
        unlynchable_by = old_role.unlynchable_by
        votes = old_role.votes
        warden_eligible = old_role.warden_eligible
        current_thread = old_role.current_thread
        temp_role = copy.deepcopy(new_role)
        # swap current role to brand new role
        self.role_dictionary[gamenum] = copy.deepcopy(new_role)
        # everyone that was acting on the old role needs to be pointed to new one
        for player in self.role_dictionary:
            for i, actings in enumerate(self.role_dictionary[player].acting_upon):
                if actings == old_role:
                    self.role_dictionary[player].acting_upon[i] = new_role
        # populate our new role with all of our saved attributes
        self.role_dictionary[gamenum].acting_upon = acting_upon
        self.role_dictionary[gamenum].action_used = action_used
        self.role_dictionary[gamenum].new_role = temp_role
        self.role_dictionary[gamenum].conjuror_acted = conjuror_acted
        self.role_dictionary[gamenum].alive = alive
        self.role_dictionary[gamenum].attacking = attacking
        self.role_dictionary[gamenum].bell_ringer_watched_by = bell_ringer_watched_by
        self.role_dictionary[gamenum].black_potion = black_potion
        self.role_dictionary[gamenum].can_jail = can_jail
        self.role_dictionary[gamenum].category = category
        self.role_dictionary[gamenum].chat = chat
        self.role_dictionary[gamenum].concussed = concussed
        self.role_dictionary[gamenum].conjuror = conjuror
        self.role_dictionary[gamenum].corrupted_by = corrupted_by
        self.role_dictionary[gamenum].coupled = coupled
        self.role_dictionary[gamenum].cult = cult
        self.role_dictionary[gamenum].disguised_by = disguised_by
        self.role_dictionary[gamenum].doused_by = doused_by
        self.role_dictionary[gamenum].first_seer = first_seer
        self.role_dictionary[gamenum].forger_guns = forger_guns
        self.role_dictionary[gamenum].forger_shields = forger_shields
        self.role_dictionary[gamenum].gamenum = gamenum
        self.role_dictionary[gamenum].given_warden_weapon = given_warden_weapon
        self.role_dictionary[gamenum].guns_forged = guns_forged
        self.role_dictionary[gamenum].has_been_concussed = has_been_concussed
        self.role_dictionary[gamenum].has_forger_gun = has_forger_gun
        self.role_dictionary[gamenum].has_forger_shield = has_forger_shield
        self.role_dictionary[gamenum].has_kill_potion = has_kill_potion
        self.role_dictionary[gamenum].has_killed = has_killed
        self.role_dictionary[gamenum].has_protect_potion = has_protect_potion
        self.role_dictionary[gamenum].hhtarget = hhtarget
        self.role_dictionary[gamenum].infected_by = infected_by
        self.role_dictionary[gamenum].instigated = instigated
        self.role_dictionary[gamenum].jailed = jailed
        self.role_dictionary[gamenum].jellied_by = jellied_by
        self.role_dictionary[gamenum].last_thread_id = last_thread_id
        self.role_dictionary[gamenum].mp = mp
        self.role_dictionary[gamenum].muted_by = muted_by
        self.role_dictionary[gamenum].night = night
        self.role_dictionary[gamenum].night_killed = night_killed
        self.role_dictionary[gamenum].nightmared = nightmared
        self.role_dictionary[gamenum].noun = noun
        self.role_dictionary[gamenum].poisoned = poisoned
        self.role_dictionary[gamenum].preacher_watched_by = preacher_watched_by
        self.role_dictionary[gamenum].protected_by = protected_by
        self.role_dictionary[gamenum].red_potion = red_potion
        self.role_dictionary[gamenum].screenname = screenname
        self.role_dictionary[gamenum].scribe_method = scribe_method
        self.role_dictionary[gamenum].scribed_by = scribed_by
        self.role_dictionary[gamenum].seer_apprentice = seer_apprentice
        self.role_dictionary[gamenum].shadow = shadow
        self.role_dictionary[gamenum].shamaned_by = shamaned_by
        self.role_dictionary[gamenum].sheriff_watched_by = sheriff_watched_by
        self.role_dictionary[gamenum].shields_forged = shields_forged
        self.role_dictionary[gamenum].spelled = spelled
        self.role_dictionary[gamenum].tricked_by = tricked_by
        self.role_dictionary[gamenum].unlynchable_by = unlynchable_by
        self.role_dictionary[gamenum].votes = votes
        self.role_dictionary[gamenum].warden_eligible = warden_eligible
        self.role_dictionary[gamenum].current_thread = current_thread

    def create_wolf_chat(self):
        wolves_id = []  # holds member ids
        wolf_message = "This is wolf chat." + '\n' + '\n'
        sorc_flag = False
        for player in self.role_dictionary:
            if (self.role_dictionary[player].team == 'Wolf' and self.role_dictionary[player].role != 'Werewolf Fan'
                    and self.role_dictionary[player].alive):
                wolves_id.append(self.gamenum_to_memberid(self.role_dictionary[player].gamenum))
                if self.role_dictionary[player].role == 'Sorcerer':
                    sorc_flag = True
                wolf_message = wolf_message + (f'The word for[b] {self.role_dictionary[player].screenname} [/b]'
                                               f'is [b] {self.role_dictionary[player].noun}[/b]. They are the '
                                               f'[b]{self.role_dictionary[player].role}.[/b]\n\n')
        wolf_message = wolf_message + (f'You may vote for a player by posting in this chat:\n\n'
                                       f'Wolfbot vote (player name)\n\n')
        if sorc_flag:
            wolf_message = wolf_message + ("The Sorcerer may read this chat, but [b]may not[/b] participate "
                                           "by either commenting or reacting unless they resign.") + '\n' + '\n'
        if self.shadow_available:
            wolf_message = wolf_message + ("Wolf Chat will be [b]Closed[/b] at the start of the day due "
                                           "to the Shadow Wolf.") + '\n' + '\n'
        if self.night == 1:
            wolf_message = wolf_message + ("For night 1 only, you must choose to act against this list of potential "
                                           "targets: ") + '\n' + self.get_randomized_nouns()
        self.wolf_chat.create_conversation(f"{self.game_title} Wolf Chat", wolf_message, wolves_id)

    # simply getting the necessary attributes from many different chat/thread objects
    def multiple_conv_pieces(self):
        night_dict = {'messageids': [], 'userids': [], 'messages': [], 'reacted': [], 'time': [], 'chat': []}
        if self.cupid.gamenum != 0 and self.night != 1:
            [messageids, userids, messages, reacted, time] = self.lover_chat.convo_pieces()
            night_dict['messageids'].extend(messageids)
            night_dict['userids'].extend(userids)
            night_dict['messages'].extend(messages)
            night_dict['reacted'].extend(reacted)
            night_dict['time'].extend(time)
            night_dict['chat'].extend([self.lover_chat for _ in range(len(messageids))])
        if self.instigator.gamenum != 0:
            [messageids, userids, messages, reacted, time] = self.insti_chat.convo_pieces()
            night_dict['messageids'].extend(messageids)
            night_dict['userids'].extend(userids)
            night_dict['messages'].extend(messages)
            night_dict['reacted'].extend(reacted)
            night_dict['time'].extend(time)
            night_dict['chat'].extend([self.insti_chat for _ in range(len(messageids))])
        [messageids, userids, messages, reacted, time] = self.wolf_chat.convo_pieces()
        night_dict['messageids'].extend(messageids)
        night_dict['userids'].extend(userids)
        night_dict['messages'].extend(messages)
        night_dict['reacted'].extend(reacted)
        night_dict['time'].extend(time)
        night_dict['chat'].extend([self.wolf_chat for _ in range(len(messageids))])
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            [messageids, userids, messages, reacted, time] = player.chat.convo_pieces()
            night_dict['messageids'].extend(messageids)
            night_dict['userids'].extend(userids)
            night_dict['messages'].extend(messages)
            night_dict['reacted'].extend(reacted)
            night_dict['time'].extend(time)
            night_dict['chat'].extend([player.chat for _ in range(len(messageids))])
        to_sort = pd.DataFrame.from_dict(night_dict)
        to_sort = to_sort.sort_values('time')
        messageids = to_sort['messageids'].to_list()
        userids = to_sort['userids'].to_list()
        messages = to_sort['messages'].to_list()
        reacted = to_sort['reacted'].to_list()
        time = to_sort['time'].to_list()
        chat = to_sort['chat'].to_list()
        pieces = [messageids, userids, messages, reacted, time, chat]
        return pieces

    def protection_checks(self, killer, attempts):
        final_victims = []
        for attacked in attempts:
            blocked = False  # assume attack isn't blocked
            # protected_by is dictionary with keyword = role, values = list of role objects of
            # that role attempting to protect this player.
            for j in attacked.protected_by:
                if j == 'Flagger' and len(attacked.protected_by[j]) > 0:
                    random_flag = random.randint(0, len(attacked.protected_by[j]) - 1)
                    # Charge protection to random if multiple flaggers on same player
                    flagger = attacked.protected_by[j][random_flag]
                    del attacked.protected_by[j][random_flag]
                    attacked = self.role_dictionary[flagger.attacking]
                    flagger.mp = flagger.mp - 50
                    flagger.chat.write_message("You successfully redirected an attack tonight.")
                    if killer.category == 'Werewolf':
                        self.wolf_chat.write_message(f"Your attack was redirected towards {attacked.screenname}.")
                    else:
                        killer.chat.write_message(f"Your attack was redirected towards {attacked.screenname}.")
                    flagger.cooldown = True
            for j in attacked.protected_by:
                if j == 'Doctor' and len(attacked.protected_by[j]) > 0:
                    blocked = True
                    for blocker in attacked.protected_by[j]:
                        blocker.chat.write_message("You successfully protected a player from being attacked tonight.")
            for j in attacked.protected_by:
                if j == 'Jailer' and len(attacked.protected_by[j]) > 0 and not blocked:
                    blocked = True
            for j in attacked.protected_by:
                if j == 'Bodyguard' and len(attacked.protected_by[j]) > 0 and not blocked:
                    blocked = True
                    for blocker in attacked.protected_by[j]:
                        if blocker.shield is False:
                            # Bodyguard hit instead
                            final_victims.append(blocker)
                        else:
                            blocker.shield = False
                            blocker.chat.write_message("You've been hurt tonight. Either you "
                                                       "or the person you were protecting "
                                                       "was attacked.")
            for j in attacked.protected_by:
                if j == 'Witch' and len(attacked.protected_by[j]) > 0 and not blocked:
                    blocked = True
                    for blocker in attacked.protected_by[j]:
                        blocker.has_protect_potion = False
                        blocker.chat.write_message("You successfully protected a player from being attacked tonight.")
                    attacked.protected_by['Witch'] = []
            for j in attacked.protected_by:
                if j == 'Tough Guy' and len(attacked.protected_by[j]) > 0 and not blocked:
                    blocked = True
                    for blocker in attacked.protected_by[j]:
                        blocker.triggered = True
                        msg = (f"You've been hurt tonight and will die at the end of the day. "
                               f"Either you or the person you were protecting was attacked. "
                               f"You have seen the identity of your attacker. You were "
                               f"attacked by [b]{killer.screenname} [/b], and they are the [b]"
                               f"{killer.role}[/b].")
                        blocker.chat.write_message(msg)
                        msg2 = (f"You've attacked one strong player. You attacked [b]"
                                f"{blocker.screenname}[/b], and they are the "
                                f"[b]{blocker.role}[/b].")
                        killer.chat.write_message(msg2)
            for j in attacked.protected_by:
                if j == 'Defender' and len(attacked.protected_by[j]) > 0 and not blocked:
                    blocked = True
                    for blocker in attacked.protected_by[j]:
                        blocker.chat.write_message(f"You successfully protected [b]{attacked.screenname}[/b]"
                                                   f" from being attacked tonight.")
            for j in attacked.protected_by:
                if j == 'Forger' and len(attacked.protected_by[j]) > 0 and not blocked:
                    blocked = True
                    attacked.has_forger_shield = 0
                    attacked.protected_by['Forger'] = []
                    attacked.chat.write_message("You have been attacked. You no longer have any Forger protection.")
            for j in attacked.protected_by:
                if j == 'Beast Hunter' and len(attacked.protected_by[j]) > 0 and not blocked:
                    for bh in attacked.protected_by[j]:
                        if not bh.cooldown:
                            blocked = True
                            bh.trap_on = 0
                            while bh in attacked.protected_by[j]:
                                attacked.protected_by[j].remove(bh)
                            if killer.category == 'Werewolf':
                                bh.chat.write_message("Your trap was triggered by an attack tonight.")
                                self.new_thread_text = (
                                            self.new_thread_text + self.kill_player("trap", bh, killer))
                            else:
                                bh.chat.write_message("Your trap was triggered by an attack tonight, but the "
                                                      "attacker was too strong and survived. "
                                                      "You need to reset your trap.")
            if len(attacked.jellied_by) > 0 and not blocked:
                self.new_thread_text = (self.new_thread_text +
                                        'The Jelly Wolf protection has been consumed. ')
                for blocker in attacked.jellied_by:
                    blocked = True
                    blocker.mp = 0
                    blocker.acting_upon = []
                    blocker.chat.write_message("You successfully protected a player "
                                               "from being attacked tonight.")
                    while blocker in attacked.jellied_by:
                        attacked.jellied_by.remove(blocker)
            if not blocked:
                final_victims.append(attacked)
        return final_victims

    def phased_actions(self, rolelist, chat_items):
        [postids, posters, actions, victims, times, chats] = \
            [chat_items[0], chat_items[1], chat_items[2], chat_items[3], chat_items[4], chat_items[5]]
        for i in range(len(postids)):
            if posters[i].role in rolelist and datetime.datetime.fromtimestamp(times[i]) > self.day_open_tm:
                if not posters[i].jailed and not posters[i].concussed and not posters[i].nightmared:
                    if posters[i].role == 'Violinist':
                        victims[i].append(self.first_death)
                    outcome = posters[i].phased_action(postids[i], actions[i].lower(), victims[i], chats[i])
                    if len(outcome) == 3:
                        self.secondary_text = ''
                        self.new_thread_text = self.new_thread_text + self.kill_player(outcome[0],
                                                                                       outcome[1],
                                                                                       outcome[2])
                        phase = f"Day {self.night - 1}" if self.day_thread.open else f'Night {self.night}'
                        self.log['Phase'].append(phase)
                        self.log['Player'].append(posters[i].screenname)
                        text = ''
                        for k, victim in enumerate(victims[i]):
                            if k == len(victims[i]) - 1:
                                text = text + victim.screenname
                            else:
                                text = text + victim.screenname + ', '
                        self.log['Action'].append(actions[i].lower() + " " + text)
                        self.log['Result'].append("success")
                    if len(outcome) == 2 and outcome[0] == 'vote':
                        self.manual_votes = outcome[1]
                        self.secondary_text = ''
                        self.new_thread_text = self.new_thread_text + self.kill_player(outcome[0],
                                                                                       outcome[1],
                                                                                       outcome[2])
                        phase = f"Day {self.night - 1}" if self.day_thread.open else f'Night {self.night}'
                        self.log['Phase'].append(phase)
                        self.log['Player'].append(posters[i].screenname)
                        text = ''
                        for k, victim in enumerate(victims[i]):
                            if k == len(victims[i]) - 1:
                                text = text + victim.screenname
                            else:
                                text = text + victim.screenname + ', '
                        self.log['Action'].append(actions[i].lower() + " " + text)
                        self.log['Result'].append("success")
                elif posters[i].jailed:
                    posters[i].chat.write_message(posters[i].chat.quote_message(postids[i]) + "You are still jailed "
                                                                                              "and cannot act.")
                elif posters[i].concussed:
                    posters[i].chat.write_message(posters[i].chat.quote_message(postids[i]) + "You are concussed "
                                                                                              "and cannot act.")
                elif posters[i].nightmared:
                    posters[i].chat.write_message(posters[i].chat.quote_message(postids[i]) + "You are in a deep sleep "
                                                                                              "(nightmared) and cannot "
                                                                                              "act.")

    def solo_attack(self, rolelist):
        # Go through all players, but we only care about the solo killers
        solo_killers = [self.role_dictionary[x] for x in self.role_dictionary
                        if self.role_dictionary[x].role in rolelist and self.role_dictionary[x].alive
                        and not self.role_dictionary[x].jailed and not self.role_dictionary[x].concussed
                        and not self.role_dictionary[x].nightmared]
        for solo_killer in solo_killers:  # player is solo killer
            pieces = solo_killer.chat.convo_pieces()
            chat = [solo_killer.chat for _ in range(len(pieces[0]))]
            pieces.append(chat)
            # [postids, posters, actions, victims, times, chats]
            [postids, _, actions, victims, times, _] = self.get_keyword_phrases(pieces)
            # Go through each keyword. Most roles should only be one
            for i in range(len(actions)):
                if datetime.datetime.fromtimestamp(times[i]) > self.day_open_tm:
                    final_victims = victims[i]
                    if (solo_killer.role in ['Corruptor', 'Cult Leader', 'Illusionist', 'Infector'] or
                            solo_killer.role == 'Alchemist' and actions[i].lower() == 'kill'):
                        final_victims = self.protection_checks(solo_killer, victims[i])
                        outcome = solo_killer.phased_action(postids[i],
                                                            actions[i].lower(),
                                                            final_victims,
                                                            solo_killer.chat)
                        if len(outcome) == 3:
                            self.secondary_text = ''
                            self.new_thread_text = (self.new_thread_text + self.kill_player(outcome[0],
                                                                                            outcome[1],
                                                                                            outcome[2]))
                    elif solo_killer.role in ['Evil Detective', 'Instigator', 'Serial Killer']:
                        outcome = solo_killer.phased_action(postids[i],
                                                            actions[i].lower(),
                                                            victims[i],
                                                            solo_killer.chat)
                        if len(outcome) == 3:
                            final_victims = self.protection_checks(solo_killer, outcome[2])
                            for victim in final_victims:
                                self.secondary_text = ''
                                self.new_thread_text = (self.new_thread_text +
                                                        self.kill_player(outcome[0], outcome[1], victim))
                    else:
                        outcome = solo_killer.phased_action(postids[i],
                                                            actions[i].lower(),
                                                            final_victims,
                                                            solo_killer.chat)
                        if len(outcome) == 3:
                            self.secondary_text = ''
                            self.new_thread_text = (self.new_thread_text +
                                                    self.kill_player(outcome[0], outcome[1], outcome[2]))
                    for player in victims[i]:
                        if player not in final_victims:
                            solo_killer.chat.write_message(f"Your target ({player.screenname}) could not be attacked.")

    def wolf_attack(self, wolf_votes):
        votes = self.count_wolf_votes()
        if len(votes) == 0:
            votes = wolf_votes
        if len(votes) == 0:
            return
        berserk = False
        # Check for berserk
        for i in self.role_dictionary:
            if self.role_dictionary[i].berserking:
                berserk = True
                self.role_dictionary[i].berserking = False
                break
        attacked = 0
        for player in votes:
            if player.alive:
                attacked = player
                break
        if attacked == 0:
            return
        # Calculate the weakest wolf for TG / BH purposes
        weakest_wolf_power = 20
        weakest_wolf = role.Player()
        for i in self.role_dictionary:
            if 0 < self.role_dictionary[i].wolf_order < weakest_wolf_power and self.role_dictionary[i].alive:
                weakest_wolf_power = self.role_dictionary[i].wolf_order
                weakest_wolf = self.role_dictionary[i]
        # These bypass protection
        if not berserk and not attacked.poisoned:
            # protected_by is dictionary with keyword = role, values = list of role objects of that
            # role attempting to protect this player.
            final_victim = self.protection_checks(weakest_wolf, [attacked])
            if len(final_victim) == 1 and not final_victim[0].wolf_immune:
                self.secondary_text = ''
                self.new_thread_text = (self.new_thread_text + self.kill_player(
                    "wolf", weakest_wolf, final_victim[0]))
            else:
                self.wolf_chat.write_message(f"Your target could not be killed!")
        elif berserk:
            # kill everyone with berserk
            if not attacked.wolf_immune:
                self.secondary_text = ''
                self.new_thread_text = (self.new_thread_text +
                                        self.kill_player("wolf", weakest_wolf, attacked))
            if len(attacked.protected_by['Beast Hunter']) > 0:
                wolf_dead = False
                for bh in attacked.protected_by['Beast Hunter']:  # These need special handling depending on trap status
                    if not bh.cooldown:
                        if not wolf_dead:
                            wolf_dead = True
                            self.secondary_text = ''
                            self.new_thread_text = (self.new_thread_text +
                                                    self.kill_player("trap",
                                                                     bh,
                                                                     weakest_wolf))
                        self.secondary_text = ''
                        self.new_thread_text = (self.new_thread_text +
                                                self.kill_player("berserk",
                                                                 weakest_wolf,
                                                                 bh))
            for dead_type in attacked.protected_by:
                if dead_type != 'Beast Hunter':  # These are handled above
                    for deads in attacked.protected_by[dead_type]:
                        self.secondary_text = ''
                        self.new_thread_text = (self.new_thread_text + self.kill_player(
                            "berserk", weakest_wolf, deads))

        elif attacked.poisoned and not attacked.wolf_immune:
            self.secondary_text = ''
            self.new_thread_text = (self.new_thread_text + self.kill_player(
                "toxic", weakest_wolf, attacked))

        else:
            self.wolf_chat.write_message(f"Your target ({attacked.screenname}) "
                                         f"could not be killed!")

    def start_night(self):
        self.night_close_tm = datetime.datetime.now() + datetime.timedelta(hours=12)
        self.night_open_tm = datetime.datetime.now()
        self.death = False  # For Violinist
        self.wolf_chat.open_chat()
        self.first_death = role.Player()  # For Violinist
        self.to_skip = []
        if self.night == 1:
            # get noun list
            # Set up dead forum with Mark
            self.admin_pm.create_conversation("New Wolf game", r'''Hi Mark,
            
            Could you please reset the dead forum for another game?''', [admin_id])
            # Set up Wolf Chat
            self.create_wolf_chat()
            self.first_post = self.day_thread.create_thread(f"{self.game_title} Day {self.night}", self.day_post())
            self.day_thread.lock_thread()
            self.day_thread.stick_thread()

            if self.instigator.gamenum != 0:
                insti_text = ''
                for player in self.couple:
                    insti_text = insti_text + (f'The word for [b]{player.screenname}[/b] is '
                                               f'[b]{player.noun}[/b]. They are the [b]'
                                               f'{player.role}[/b]') + '\n' + '\n'
                insti_text = ((f'Welcome to Instigator Chat. [b]You can only win with the Instigator, and can no '
                               f'longer win with your original teams[/b].\n\n'
                               f'{self.instigator.screenname} is the '
                               f'[b]Instigator[/b]. Their word is [b]'
                               f'{self.instigator.noun}[/b].\n\n') +
                              insti_text)
                self.insti_chat.create_conversation("Instigators Chat",
                                                    insti_text,
                                                    [self.gamenum_to_memberid(self.couple[0].gamenum),
                                                     self.gamenum_to_memberid(self.couple[1].gamenum),
                                                     self.gamenum_to_memberid(self.instigator.gamenum)])
        else:
            self.day_thread.write_message(f"Night actions please. The next day will start at "
                                          f"[TIME=datetime]{self.night_close_tm.strftime('%Y-%m-%dT%H:%M:%S-0500')}"
                                          f"[/TIME] unless skipped.")
        # Set up Jailer/Warden Chat
        self.jailed = []
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if player.jailed is True:
                self.jailed.append(player)
                # if jailed before, but NOT this time, they're eligible again
            if player.warden_eligible is False and player.jailed is False:
                player.warden_eligible = True
        # can tell warden/jailer by number of people jailed
        if len(self.jailed) == 1:
            body = ("You have been jailed. ANY messages you send here will be sent verbatim to the jailer in the "
                    "next several minutes, and vice versa. You have no message limit.")
            self.jailee_chat.create_conversation("Jailed", body,
                                                 [self.gamenum_to_memberid(self.jailed[0].gamenum)])
            body2 = (f"You have jailed your prisoner, {self.jailed[0].screenname}. ANY messages you send here will be "
                     f"sent verbatim to your prisoner in the next several minutes, and vice versa. "
                     f"You have no message limit.")
            self.jailer_chat.create_conversation("On Duty", body2,
                                                 [self.gamenum_to_memberid(self.jailer.gamenum)])
            if self.jailed[0].team == 'Wolf' and self.jailed[0].role != 'Werewolf Fan':
                self.wolf_chat.write_message(f"{self.jailed[0].screenname} has been jailed tonight and "
                                             f"cannot participate in wolf chat.")
        elif len(self.jailed) == 2:
            body = ("You have been jailed together. ANY messages you send here will be sent verbatim to the warden. "
                    "You have no message limit.")
            if (self.jailed[0].category == 'Werewolf' and self.jailed[1].category == 'Werewolf'
                    and self.jailed[0].role != 'Sorcerer' and self.jailed[0].category != 'Sorcerer'):
                body = body + '\n' + '\n' + ('(Since you are both wolves, you make break out of prison by either '
                                             'of you writing "Wolfbot escape" [b]in your individual chat[/b] '
                                             'with Wolfbot (not here).')
            self.jailee_chat.create_conversation("Jailed", body,
                                                 [self.gamenum_to_memberid(self.jailed[0].gamenum),
                                                  self.gamenum_to_memberid(self.jailed[1].gamenum)])
            body2 = (f"You have jailed your prisoners, {self.jailed[0].screenname} and {self.jailed[1].screenname}. "
                     f"Any messages they write will be sent here. "
                     f"To drop the weapon, do so in your original role PM")  # BW - IS THIS NECESSARY?
            self.jailer_chat.create_conversation("On Duty", body2,
                                                 [self.gamenum_to_memberid(self.jailer.gamenum)])
            if self.jailed[0].team == 'Wolf' and self.jailed[0].role != 'Werewolf Fan':
                self.wolf_chat.write_message(f"{self.jailed[0].screenname} has been jailed tonight and "
                                             f"cannot participate in wolf chat unless freed.")
            if self.jailed[1].team == 'Wolf' and self.jailed[1].role != 'Werewolf Fan':
                self.wolf_chat.write_message(f"{self.jailed[1].screenname} has been jailed tonight and "
                                             f"cannot participate in wolf chat unless freed.")

        # Iterate through all players to initialize game
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if player.nightmared:
                player.chat.write_message("You have fallen into a deep sleep! You cannot use any abilities this night.")
            if player.role in ['Jelly Wolf', 'Bell Ringer']:
                player.acting_upon = []
            if player.role == 'Serial Killer':
                player.mp += 100
            if player.role in ['Bodyguard', 'Tough Guy']:
                player.protected_by[player.role] = [player]
            player.jellied_by = []
            player.bell_ringer_watched_by = []
            player.skipped = False
            player.current_thread = self.day_thread
            if player.alive:
                self.to_skip.append(player)
                if self.night != 1:
                    player.chat.write_message(f"It is now Night {self.night}.")
            if self.night == 1:
                player.chat.create_conversation(f"{self.game_title} Role",
                                                player.initial_PM + '\n\n' +
                                                "For night 1 only, you must choose to act against "
                                                "this list of potential targets:" + '\n' +
                                                self.get_randomized_nouns(), [self.gamenum_to_memberid(i)])
            # Revert Conjuror if they didn't take a new role
            if player.conjuror is True and player.new_role.gamenum == 0:
                self.role_swap(player, self.saved_conjuror_data)
            # Add speak with dead player back to dead forum
            if player.speak_with_dead and player.alive:
                self.admin_pm.write_message(f"Can you add {player.screenname} please?")
            # remove mutes
            player.muted_by[self.night] = []
            # Revive players spelled by Ritualist if time period has been met, also dump Ritu MP
            if (player.spelled and not player.alive
                    and len(player.corrupted_by) == 0):
                if self.spell_count > 1:
                    self.day_thread.write_message(f'By some miracle, {player.screenname} '
                                                  f'has returned to us from the dead.')
                    player.alive = True
                    player.spelled = False
                    # If we are reviving someone who caused seer apprentices to convert, then convert seer app back
                    if player.first_seer:
                        for j in self.role_dictionary:
                            seer_app = self.role_dictionary[j]
                            if seer_app.seer_apprentice:
                                self.role_swap(seer_app, role.SeerApprentice())
                                seer_app.chat.write_message(f"Due to the revival of {player.screenname}, "
                                                            f"you have reverted back to Seer Apprentice.")
                self.spell_count += 1
            if player.role == 'Ritualist' and self.spell_count > 1:
                player.mp = 0
        pieces = self.multiple_conv_pieces()
        chat_items = self.get_keyword_phrases(pieces, dedupe=True)
        if self.night != 1:
            self.phased_actions(['Werewolf Fan'], chat_items)
        self.output_data()

    def end_night(self):
        saved_votes = self.count_wolf_votes()  # Do this just in case a new wolf chat is created prior to wolf attack
        pieces = self.multiple_conv_pieces()
        chat_items = self.get_keyword_phrases(pieces, dedupe=True)

        # Nightmare, Shaman, WWFan, Jailing all take place at start of night (Phase 0)
        # PHASE 1
        self.phased_actions(['Wolf Avenger', 'Avenger', 'Loudmouth', 'Wolf Trickster', 'Confusion Wolf'], chat_items)
        for i in self.role_dictionary:
            if self.role_dictionary[i].confusion:
                self.confusion_in_effect = True
        if self.win_conditions():
            return
        # PHASE 2 (Wolves break out of warden prison or warden weapon used, moved to nightly check

        # PHASE 3 No wolf checks, those are under immediate action in the night loop
        self.phased_actions(['Voodoo Wolf', 'Librarian', 'Medium', 'Ritualist'], chat_items)
        if self.win_conditions():
            return
        # PHASE 4 All protectors lumped together, can sort when attacks performed
        self.phased_actions(['Flagger', 'Doctor', 'Bodyguard', 'Witch', 'Tough Guy',
                             'Defender', 'Jelly Wolf', 'Beast Hunter'], chat_items)
        if self.win_conditions():
            return
        # PHASE 5 Illu and Infector attack
        self.solo_attack(['Infector', 'Illusionist'])
        if self.win_conditions():
            return
        # Apply misdirection before seers go
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if len(player.disguised_by) > 0:
                player.apparent_role = 'Illusionist'
                player.apparent_aura = 'Unknown'
                player.apparent_team = 'Illusionist'
            if len(player.shamaned_by) > 0:
                player.apparent_aura = 'Evil'
                player.apparent_team = 'Wolf'

        # PHASE 6 Seers - Except Spirit
        self.phased_actions(['Violinist', 'Detective', 'Aura Seer', 'Sheriff',
                             'Bell Ringer', 'Preacher'], chat_items)
        if self.win_conditions():
            return
        # PHASE 7
        self.phased_actions(['Marksman'], chat_items)
        if self.win_conditions():
            return

        # PHASE 8
        self.phased_actions(['Witch'], chat_items)
        if self.win_conditions():
            return

        # PHASE 9
        self.phased_actions(['Jailer'], chat_items)
        if self.win_conditions():
            return

        # Phase 10
        self.phased_actions(['Red Lady', 'Forger'], chat_items)
        if self.win_conditions():
            return

        # Phase 11
        self.solo_attack(['Alchemist', 'Arsonist', 'Corruptor', 'Cult Leader', 'Evil Detective',
                          'Instigator', 'Serial Killer'])

        self.phased_actions(['Berserk Wolf'], chat_items)

        # Phase 12
        self.wolf_attack(saved_votes)

        # Phase 13
        self.phased_actions(['Spirit Seer'], chat_items)

        # Phase 14
        self.phased_actions(['Forger'], chat_items)

        self.phased_actions(['Cupid'], chat_items)

        # PHASE LAST
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if len(player.shamaned_by) > 0:
                player.shamaned = []
                player.apparent_aura = player.aura
                if not player.cult:
                    player.apparent_team = player.team
            if len(player.disguised_by) > 0:
                player.apparent_aura = "Unknown"
                player.apparent_team = "Illusionist"
                player.apparent_role = "Illusionist"
            if player.reviving:
                self.new_thread_text = (self.new_thread_text +
                                        (f'By some miracle, {player.screenname} '
                                         f'has returned to us from the dead.'))
                player.alive = True
                player.reviving = False
                # If we are reviving someone who caused seer apprentices to convert, then convert seer app back
                if player.first_seer:
                    for j in self.role_dictionary:
                        seer_app = self.role_dictionary[j]
                        if seer_app.seer_apprentice:
                            self.role_swap(seer_app, role.SeerApprentice())
                            seer_app.chat.write_message(f"Due to the revival of {player.screenname}, "
                                                        f"you have reverted back to Seer Apprentice.")
        if not self.death:
            self.tie_count += 1
        else:
            self.tie_count = 0
        if self.win_conditions():
            return
        self.output_data()

    def start_day(self):
        self.death = False
        self.day_open_tm = datetime.datetime.now()
        self.manual_votes = []
        self.confusion_in_effect = False
        self.shadow_available = False
        # check if Cupid / Wolf Chat open
        is_alpha = False
        cult = []
        self.day_thread.unlock_thread()
        self.to_skip = []
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            player.night += 1
            player.action_used = False
            player.conjuror_acted = False
            player.skipped = False
            if player.alive:
                player.chat.write_message(f"It is now Day {self.night}.")
                self.to_skip.append(player)
            if player.shadow:
                self.shadow_available = True
            if player.role == 'Alpha Wolf' and player.alive:
                is_alpha = True
            if player.cult:
                cult.append(player)
            # Method to let flagger working after 2 days. 1st day, attacking gets set to 0. Second day, cooldown expires
            if player.role == 'Flagger':
                if player.attacking == 0:
                    player.cooldown = False
                if player.cooldown:
                    player.attacking = 0
        if self.night == 1 and self.cultleader.gamenum > 0:
            self.cult_chat.create_conversation("Cult Orders",
                                               "Give your orders to the cult here. "
                                               "Anything you post here will be sent to the entire cult.",
                                               [self.gamenum_to_memberid(self.cultleader.gamenum)])
        if self.shadow_available and not is_alpha:
            self.wolf_chat.write_message("Wolf Chat is closed for the day.")
            self.wolf_chat.close_chat()
        if self.shadow_available and is_alpha:
            self.wolf_chat.write_message("Wolf Chat is closed for the day, except the Alpha Wolf may post messages.")
        # If Cupid is in game, set up Lovers on day 1
        if self.night == 1 and self.cupid.gamenum > 0:
            couple_num = []  # holds game nums
            self.couple = []  # holds role objects
            cupid_message = "You have fallen in love!" + '\n' + '\n'
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.coupled is True:
                    self.couple.append(player)
                    couple_num.append(player.gamenum)
            # what if we don't have lover because they were killed
            while len(couple_num) < 2:
                # generate a new gamenum to create as lover
                rand = random.randint(1, len(self.role_dictionary))
                if rand not in couple_num and rand != self.cupid.gamenum:
                    couple_num.append(rand)
                    self.couple.append(self.role_dictionary[rand])
                    self.role_dictionary[rand].coupled = True
            cupid_message = (cupid_message +
                             (f'[b]{self.couple[0].screenname}[/b] is the [b]{self.couple[0].role}.[/b]\n\n'
                              f'[b]{self.couple[1].screenname}[/b] is the [b]{self.couple[1].role}.[/b]'))
            self.lover_chat.create_conversation(f"{self.game_title} Lovers Chat", cupid_message,
                                                [self.gamenum_to_memberid(self.couple[0].gamenum),
                                                 self.gamenum_to_memberid(self.couple[1].gamenum)])
            self.cupid.chat.write_message(f"Your couple is {self.couple[0].screenname} and "
                                          f"{self.couple[1].screenname}. Good luck!")
        rand_time = random.random()*20+2
        self.alch_deaths_tm = (self.day_open_tm + datetime.timedelta(hours=rand_time//1) +
                               datetime.timedelta(minutes=60 * (rand_time % 1)))  # Time of alch deaths
        alive = []  # List of players for poll
        # iterate through players to perform actions
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            # Reset things from the night/previous day that no longer apply
            player.current_thread = self.day_thread
            player.concussed = False
            player.nightmared = False
            player.jailed = False
            player.unlynchable_by = []
            player.sheriff_watched_by = []
            player.preacher_watched_by = []
            player.protected_by['Flagger'] = []
            player.protected_by['Doctor'] = []
            player.protected_by['Jailer'] = []
            player.protected_by['Bodyguard'] = []
            player.protected_by['Witch'] = []
            player.protected_by['Tough Guy'] = []
            player.protected_by['Defender'] = []
            player.shamaned_by = []
            player.has_killed = False
            player.checked = 0
            player.poisoned = False
            player.given_warden_weapon = False
            player.visited = []
            # Have Mark remove speak_with_dead players from the dead forum
            if player.speak_with_dead and player.alive:
                self.admin_pm.write_message(f"Can you remove {player.screenname} please?")
            # Conjuror defaults to reversion unless they pick a new target
            if player.role == 'Conjuror':
                player.new_role = role.Player()
            # Revive players spelled by Ritualist if time period has been met, also dump Ritu MP
            if (player.spelled and not player.alive and
                    len(player.corrupted_by) == 0):
                if self.spell_count > 1:
                    self.new_thread_text = self.new_thread_text + (f'By some miracle, '
                                                                   f'{player.screenname} has '
                                                                   f'returned to us from the dead.')
                    player.alive = True
                    player.spelled = False
                self.spell_count += 1
            if player.role == 'Ritualist' and self.spell_count > 1:
                player.mp = 0
            if player.role == 'Alchemist':
                player.chat.write_message(f"Your potions are set to hit at [TIME=datetime]"
                                          f"{self.alch_deaths_tm.strftime('%Y-%m-%dT%H:%M:%S-0500')}[/TIME]")
            # BH/Marksman has finished their ability cooldown
            if player.role in ['Marksman', 'Beast Hunter']:
                player.cooldown = False
            if player.role == 'Confusion Wolf':
                player.confusion = False
            if player.role == 'Berserk Wolf':
                player.berserking = False
            if player.role in ['Flower Child', 'Guardian Wolf', 'Preacher', 'Sheriff']:
                player.acting_upon = []
            if player.alive:
                alive.append(player.screenname)
            if len(player.muted_by[self.night]) > 0:
                player.chat.write_message("You have been muted! Please refrain from posting or reacting in today's "
                                          "thread. You also may not vote in the poll. You may still use daytime "
                                          "abilities if you have them.")
            if len(player.corrupted_by) > 0:
                player.chat.write_message("You have been corrupted! You will die at the end of the day unless the "
                                          "Corruptor is killed. Please refrain from posting or reacting in today's "
                                          "thread as well as any other game chats you may be a part of (such as wolf "
                                          "chat). All your abilities are currently disabled. You also may not vote "
                                          "in the poll. ")
            if len(player.infected_by) > 0:
                player.chat.write_message("You have been infected! You will die at the "
                                          "end of the day unless the Infector is killed.")
        self.day_thread.create_poll(alive)
        if self.new_thread_text == '':
            self.new_thread_text = 'Nothing happened last night.\n\n'
        self.day_close_tm = self.day_open_tm + datetime.timedelta(hours=24)
        self.new_thread_text = self.new_thread_text + (f"The day will end at [TIME=datetime]"
                                                       f"{self.day_close_tm.strftime('%Y-%m-%dT%H:%M:%S-0500')}[/TIME]")
        self.day_thread.write_message(self.new_thread_text)
        self.new_thread_text = ''
        if self.night == 1:
            self.day_thread.write_message(self.print_nouns())
        self.night += 1
        post_list = sorted(self.player_names, key=lambda v: v.upper())
        tag_list = ''
        for i in post_list:
            if self.role_dictionary[self.name_to_gamenum(i)].alive:
                tag_list = tag_list + '@' + i + '\n'
        self.output_data()
        self.day_thread.write_message(tag_list)

    def end_day(self):
        pieces = self.multiple_conv_pieces()
        chat_items = self.get_keyword_phrases(pieces, dedupe=True)
        if not self.shadow_in_effect:
            # Run Preacher check to see if there are any more votes out there
            self.phased_actions(['Preacher'], chat_items)
            # Get results from poll
            poll_results = self.day_thread.get_raw_poll()
            # If we have additional votes, add them in before the final tally
            if len(self.manual_votes) > 0:
                for additional_vote in self.manual_votes:
                    if additional_vote.screenname in poll_results['Name']:
                        voted_ind = poll_results['Name'].index(additional_vote.screenname)
                        poll_results['Vote Count'][voted_ind] += 1
                    else:
                        poll_results['Name'].append(additional_vote.screenname)
                        poll_results['Vote Count'].append(1)

        # Shadow in effect
        else:
            votes = []
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.alive:
                    if player.can_jail:  # Necessary for Conjuror
                        self.jailer = player
                    pieces = player.chat.convo_pieces()
                    chat = [player.chat for _ in range(len(pieces[0]))]
                    pieces.append(chat)
                    [postids, posters, actions, victims, _, chats] = self.get_keyword_phrases(pieces)
                    for j in range(len(actions)):
                        if actions[j].lower() == "vote":
                            outcome = player.get_shadow_vote(postids[j], 'vote', victims[j], chats[j], True)
                            phase = f"Day {self.night - 1}" if self.day_thread.open else f'Night {self.night}'
                            self.log['Phase'].append(phase)
                            self.log['Player'].append(posters[i].screenname)
                            text = ''
                            for k, victim in enumerate(victims[i]):
                                if k == len(victims[i]) - 1:
                                    text = text + victim.screenname
                                else:
                                    text = text + victim.screenname + ', '
                            self.log['Action'].append(actions[i].lower() + " " + text)
                            self.log['Result'].append("success")
                        else:
                            outcome = []
                        votes.extend(outcome)
            votecount = []
            names = []
            for vote in votes:
                if vote in names:
                    ind = names.index(vote)
                    votecount[ind] += 1
                else:
                    names.append(vote.screenname)
                    votecount.append(1)
            poll_results = {'Name': names, 'Vote Count': votecount}
        pandas_structure = pd.DataFrame.from_dict(poll_results)
        pandas_structure = pandas_structure[pandas_structure['Name'] != 'No Vote']
        alives = 0
        for i in self.role_dictionary:
            if self.role_dictionary[i].alive:
                alives += 1
        lynch_threshold = alives // 2
        top_vote = pandas_structure['Vote Count'].max()
        vote_winners = pandas_structure[pandas_structure['Vote Count'] == top_vote]
        text = ''
        if len(vote_winners) != 1:
            text = text + "The village could not decide who to lynch."
            self.phased_actions(['Judge'], chat_items)
        else:
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.screenname == vote_winners.iloc[0, 0]:
                    vote_winner = player
                    if top_vote < lynch_threshold:
                        text = text + "The village could not decide who to lynch."
                        self.phased_actions(['Judge'], chat_items)
                    elif len(vote_winner.unlynchable_by) > 0:
                        text = text + (f"The village attempted to lynch {vote_winner.screenname}, "
                                       f"but their lynch was prevented by a mysterious power.")
                        for flower in self.role_dictionary:
                            if (self.role_dictionary[flower].role in ('Guardian Wolf', 'Flower Child')
                                    and vote_winner in self.role_dictionary[flower].acting_upon):
                                self.role_dictionary[flower].acting_upon = []
                                self.role_dictionary[flower].mp = 0
                                vote_winner.unlynchable_by = []
                    else:
                        self.secondary_text = ''
                        text = text + self.kill_player("lynched", role.Player(), vote_winner)
        if self.win_conditions():
            return
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if len(player.infected_by) > 0:
                self.secondary_text = ''
                text = text + self.kill_player("infector", player.infected_by[0], player)
            if len(player.corrupted_by) > 0:
                self.secondary_text = ''
                text = text + self.kill_player("corruptor", player.corrupted_by[0], player)
            if player.role == 'Tough Guy':
                self.secondary_text = ''
                if player.triggered and not player.conjuror:
                    text = text + self.kill_player("tough", role.Player(), player)
        self.day_thread.write_message(text)
        self.phased_actions(['Shaman Wolf'], chat_items)
        self.phased_actions(['Nightmare Wolf'], chat_items)
        self.phased_actions(['Jailer', 'Warden'], chat_items)
        self.day_thread.lock_thread()
        self.shadow_in_effect = False
        if not self.death:
            self.tie_count += 1
        else:
            self.tie_count = 0
        if self.win_conditions():
            return
        self.output_data()

    def run_day_checks(self):
        self.rebuild_dict()
        if datetime.datetime.now() > self.alch_deaths_tm:
            text = ''
            self.alch_deaths_tm = self.alch_deaths_tm + datetime.timedelta(days=100)  # trigger once
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.black_potion:
                    text = text + self.kill_player('alchemist', role.Player(), player)
                if player.red_potion > 1:
                    text = text + self.kill_player('alchemist', role.Player(), player)
            self.day_thread.write_message(text)
        if self.shadow_in_effect:
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.alive:
                    pieces = player.chat.convo_pieces()
                    chat = [player.chat for _ in range(len(pieces[0]))]
                    pieces.append(chat)
                    [postids, _, actions, victims, _, chats] = self.get_keyword_phrases(pieces, new=True)
                    for j in range(len(actions)):
                        if actions[j].lower() == "vote":
                            player.get_shadow_vote(postids[j], 'vote', victims[j], chats[j])
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if player.is_last_evil and not player.resigned:
                player.immediate_action('', 'resign', [], player.chat)
                self.log['Phase'].append(f"Day {self.night-1}")
                self.log['Player'].append(player.screenname)
                self.log['Action'].append(f"resign")
                self.log['Result'].append(f"resigned")
        pieces = self.day_thread.thread_pieces()
        chat = [self.day_thread for _ in range(len(pieces[0]))]
        pieces.append(chat)
        # Get posts from the thread
        [public_posts, public_posters, public_actions, public_victims, public_times, public_obj] = (
            self.get_keyword_phrases(pieces, dedupe=False, new=True))
        if self.cultleader.gamenum > 0:
            cult = []
            [post_ids, posters, posts, reacts, _] = self.cult_chat.convo_pieces()
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.cult and player.alive:
                    cult.append(player)
            for i, message in enumerate(post_ids):
                if reacts[i] is False:
                    self.cult_chat.seen_message(message)
            for i in range(len(posters)-1, -1, -1):
                if posters[i] == bot_member_id:
                    del posters[i]
                    del posts[i]
                    del reacts[i]
            for cultee in cult:
                for i, message in enumerate(posts):
                    if reacts[i] is False:
                        cultee.chat.write_message("From the Cult Leader: " + message)
        # Go through each player chat and get any actions
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            chat_pieces = player.chat.convo_pieces()
            chat = [player.chat for _ in range(len(chat_pieces[0]))]
            chat_pieces.append(chat)
            [private_posts, private_posters, private_actions, private_victims, private_times, private_obj] = (
                self.get_keyword_phrases(chat_pieces, dedupe=False, new=True))
            for j, message in enumerate(chat_pieces[0]):
                if chat_pieces[3][j] is False:
                    player.chat.seen_message(message)
            # Combine thread posts and chat posts into one group
            public_posts.extend(private_posts)
            public_posters.extend(private_posters)
            public_actions.extend(private_actions)
            public_victims.extend(private_victims)
            public_times.extend(private_times)
            public_obj.extend(private_obj)
        # Sort by time so actions occur in order
        to_pandas = {'posts': public_posts, 'posters': public_posters,
                     'actions': public_actions, 'victims': public_victims, 'times': public_times, 'object': public_obj}
        frame = pd.DataFrame.from_dict(to_pandas)
        frame = frame.sort_values('times')
        posts = frame['posts'].tolist()
        posters = frame['posters'].tolist()
        actions = frame['actions'].tolist()
        victims = frame['victims'].tolist()
        objs = frame['object'].tolist()
        post_skips = False
        post_skips_private = False
        skip_post = 0
        skip_private = []
        skip_chats = []
        for i, player in enumerate(posters):
            if player.conjuror and actions[i].lower() == 'take' and not player.conjuror_acted:
                self.role_swap(player, self.saved_conjuror_data)
                posters[i] = self.role_dictionary[player.gamenumalche]
        # Apply actions
        for i, player in enumerate(posters):
            if player.alive:
                player.skip_check(actions[i].lower(), posts[i], objs[i])
            if actions[i].lower() == 'unskipped':
                if isinstance(objs[i], tc.Thread):
                    post_skips = True
                    skip_post = posts[i]
                else:
                    post_skips_private = True
                    skip_private.append(posts[i])
                    skip_chats.append(objs[i])
            outcome = player.immediate_action(posts[i], actions[i].lower(), victims[i], objs[i])
            if len(outcome) == 1:
                if (outcome[0] == 'illusionist'
                        and datetime.datetime.now() < self.day_close_tm - datetime.timedelta(hours=2)):
                    player.acting_upon = []
                    text = ''
                    for pot_dead in self.role_dictionary:
                        if len(self.role_dictionary[pot_dead].disguised_by) > 0:
                            self.secondary_text = ''
                            text = text + self.kill_player("illusionist", player,
                                                           self.role_dictionary[pot_dead])
                    self.day_thread.write_message(text)
                    self.log['Phase'].append(f"Day {self.night - 1}")
                    self.log['Player'].append(player.screenname)
                    self.log['Action'].append("kill all disguised")
                    self.log['Result'].append("all disguised dead")
                elif (outcome[0] == 'shadow' and datetime.datetime.now() < self.day_close_tm -
                        datetime.timedelta(hours=12)):
                    self.shadow_in_effect = True
                    self.day_thread.delete_poll()
                    self.day_thread.write_message("[b]Today's voting has been manipulated by the Shadow Wolf.[/b]")
                    self.day_thread.edit_post(self.first_post, self.day_post())
                    self.log['Phase'].append(f"Day {self.night - 1}")
                    self.log['Player'].append(player.screenname)
                    self.log['Action'].append("shadow")
                    self.log['Result'].append("shadowed")
                else:
                    self.log['Phase'].append(f"Day {self.night - 1}")
                    self.log['Player'].append(player.screenname)
                    text = ''
                    for k, victim in enumerate(victims[i]):
                        if k == len(victims[i]) - 1:
                            text = text + victim.screenname
                        else:
                            text = text + victim.screenname + ', '
                    self.log['Action'].append(actions[i].lower() + " " + text)
                    self.log['Result'].append(outcome[0])
            elif len(outcome) == 2:
                if outcome[0] == 'reveal':
                    self.wolf_chat.write_message(f"The Sorcerer has revealed that [b]{outcome[1].screenname}"
                                                 f"[/b] is the [b]{outcome[1].role}[/b].")
                    self.log['Phase'].append(f"Day {self.night - 1}")
                    self.log['Player'].append(player.screenname)
                    text = ''
                    for k, victim in enumerate(victims[i]):
                        if k == len(victims[i]) - 1:
                            text = text + victim.screenname
                        else:
                            text = text + victim.screenname + ', '
                    self.log['Action'].append(actions[i].lower() + " " + text)
                    self.log['Result'].append("revealed")
            elif len(outcome) == 3:
                if isinstance(objs[i], tc.Thread):
                    self.secondary_text = ''
                    self.day_thread.write_message(self.day_thread.quote_message(posts[i]) +
                                                  self.kill_player(outcome[0], outcome[1], outcome[2]))
                else:
                    self.secondary_text = ''
                    self.day_thread.write_message(self.kill_player(outcome[0], outcome[1], outcome[2]))
                self.log['Phase'].append(f"Day {self.night - 1}")
                self.log['Player'].append(player.screenname)
                text = ''
                for k, victim in enumerate(victims[i]):
                    if k == len(victims[i]) - 1:
                        text = text + victim.screenname
                    else:
                        text = text + victim.screenname + ', '
                self.log['Action'].append(actions[i].lower() + " " + text)
                self.log['Result'].append("success")
            outcome2 = player.shoot_forger_gun(actions[i].lower(), victims[i], self.day_thread)
            if len(outcome2) == 3:
                self.secondary_text = ''
                self.day_thread.write_message(self.day_thread.quote_message(posts[i]) +
                                              self.kill_player(outcome2[0], outcome2[1], outcome2[2]))
                self.log['Phase'].append(f"Day {self.night - 1}")
                self.log['Player'].append(player.screenname)
                text = ''
                for k, victim in enumerate(victims[i]):
                    if k == len(victims[i]) - 1:
                        text = text + victim.screenname
                    else:
                        text = text + victim.screenname + ', '
                self.log['Action'].append(actions[i].lower() + " " + text)
                self.log['Result'].append("success")
            if player.role == 'Sorcerer' and player.resigned:
                self.role_swap(player, role.Werewolf())
            if self.win_conditions():
                return
        for i, post in enumerate(pieces[0]):
            if pieces[3][i] is False:
                self.day_thread.seen_post(post)
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if player.conjuror is True and player.new_role.role != player.role and player.new_role.gamenum != 0:
                self.role_swap(player, player.new_role)
            if player.skipped and player in self.to_skip:
                del self.to_skip[self.to_skip.index(player)]
        if len(self.to_skip) == 0:
            if self.day_close_tm < datetime.datetime.now() + datetime.timedelta(minutes=10):
                self.day_thread.write_message("The remainder of the day has been skipped by unanimous vote.")
            self.day_close_tm = datetime.datetime.now()
        if post_skips:
            text = self.day_thread.quote_message(skip_post) + "The following players have yet to skip:\n"
            for unskipped in self.to_skip:
                text = text + unskipped.screenname + '\n'
            self.day_thread.write_message(text)
        if post_skips_private:
            for i, postid in enumerate(skip_private):
                skip_chats[i].write_message(skip_chats[i].quote_message(postid) + f"There are still {len(self.to_skip)}"
                                                                                  f" people who have yet to skip.")
        self.output_data()

    def run_night_checks(self):
        self.rebuild_dict()
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if player.is_last_evil and not player.resigned:
                player.immediate_action('', 'resign', [], player.chat)
                self.log['Phase'].append(f"Night {self.night}")
                self.log['Player'].append(player.screenname)
                self.log['Action'].append(f"resign")
                self.log['Result'].append(f"resigned")
        if self.cultleader.gamenum > 0:
            cult = []
            [post_ids, posters, posts, reacts, _] = self.cult_chat.convo_pieces()
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.cult and player.alive:
                    cult.append(player)
            for i, message in enumerate(post_ids):
                if reacts[i] is False:
                    self.cult_chat.seen_message(message)
            for i in range(len(posters)-1, -1, -1):
                if posters[i] == bot_member_id:
                    del posters[i]
                    del posts[i]
                    del reacts[i]
            for cultee in cult:
                for i, message in enumerate(posts):
                    if reacts[i] is False:
                        cultee.chat.write_message("From the Cult Leader: " + message)
        if len(self.jailed) == 1:
            [postids, posters, posts, reacts, _] = self.jailee_chat.convo_pieces()
            for i in range(len(posters)-1, -1, -1):
                if posters[i] == bot_member_id:
                    del postids[i]
                    del posters[i]
                    del posts[i]
                    del reacts[i]
            for i, message in enumerate(posts):
                if reacts[i] is False:
                    self.jailer_chat.write_message("From your prisoner: " + message)
                    self.jailee_chat.seen_message(postids[i])
            [postids, posters, posts, reacts, _] = self.jailer_chat.convo_pieces()
            for i in range(len(posters)-1, -1, -1):
                if posters[i] == bot_member_id:
                    del postids[i]
                    del posters[i]
                    del posts[i]
                    del reacts[i]
            for i, message in enumerate(posts):
                if reacts[i] is False:
                    self.jailee_chat.write_message("From the Jailer: " + message)
                    self.jailer_chat.seen_message(postids[i])
        if len(self.jailed) == 2:
            if not self.jailed[0].alive or not self.jailed[1].alive:
                self.jailed = []
            else:
                [postids, posters, posts, reacts, _] = self.jailee_chat.convo_pieces()
                for i in range(len(posters) - 1, -1, -1):
                    if posters[i] == bot_member_id:
                        del postids[i]
                        del posters[i]
                        del posts[i]
                        del reacts[i]
                for i, message in enumerate(posts):
                    if reacts[i] is False:
                        self.jailer_chat.write_message(f"From prison, {self.memberid_to_name(posters[i])} says: "
                                                       + message)
                        self.jailee_chat.seen_message(postids[i])
                action_taken = False
                for i in range(2):
                    if not action_taken:
                        pieces = self.jailed[i].chat.convo_pieces()
                        chats = [self.jailed[i].chat for _ in pieces[0]]
                        pieces.append(chats)
                        [_, _, actions, _, _, _] = self.get_keyword_phrases(pieces)
                        for action in actions:
                            if action.lower() == 'kill' and self.jailed[i].given_warden_weapon:
                                survivor = role.Player()
                                self.jailer.mp = 0
                                if self.jailed[i].role == 'Werewolf Fan':
                                    self.secondary_text = ''
                                    self.new_thread_text = (self.new_thread_text +
                                                            self.kill_player('prisoner',
                                                                             self.jailed[i],
                                                                             self.jailed[1-i]))
                                    survivor = self.jailed[i]
                                elif self.jailed[1-i].role == 'Werewolf Fan':
                                    self.secondary_text = ''
                                    self.new_thread_text = (self.new_thread_text +
                                                            self.kill_player('prisoner',
                                                                             self.jailed[1-i],
                                                                             self.jailed[i]))
                                    survivor = self.jailed[1-i]
                                elif self.jailed[i].team == self.jailed[1-i].team:
                                    self.secondary_text = ''
                                    self.new_thread_text = (self.new_thread_text +
                                                            self.kill_player('prisoner',
                                                                             self.jailed[1-i],
                                                                             self.jailed[i]))
                                    survivor = self.jailed[1-i]
                                elif self.jailed[i].team != self.jailed[1-i].team:
                                    self.secondary_text = ''
                                    self.new_thread_text = (self.new_thread_text +
                                                            self.kill_player('prisoner',
                                                                             self.jailed[i],
                                                                             self.jailed[1-i]))
                                    survivor = self.jailed[i]
                                self.jailed[0].jailed = False
                                self.jailed[1].jailed = False
                                self.jailer_chat.write_message("Chat is Closed. "
                                                               "One of the prisoners has used the weapon.")
                                self.jailee_chat.write_message(f"Chat is Closed. {survivor.screenname} has survived "
                                                               f"and is free from jailing restrictions to perform "
                                                               f"night actions as usual.")
                                self.jailee_chat.close_chat()
                                self.jailer_chat.close_chat()
                                self.jailed = []
                                action_taken = True
                                break
                            if (action.lower() == 'escape' and self.jailed[0].category == 'Werewolf'
                                    and self.jailed[0].role != 'Sorcerer'
                                    and self.jailed[1].category == 'Werewolf'
                                    and self.jailed[1].role != 'Sorcerer'):
                                self.jailer.alive = False
                                self.secondary_text = ''
                                self.new_thread_text = (self.new_thread_text +
                                                        self.kill_player('breakout', self.jailer, self.jailer))
                                self.jailed[0].jailed = False
                                self.jailed[1].jailed = False
                                self.jailed[0].has_killed = True
                                self.jailed[1].has_killed = True
                                action_taken = True
                                self.jailer_chat.write_message("Chat is Closed. Sorry, you jailed two wolves.")
                                self.jailee_chat.write_message("Chat is Closed. You are free of jailing restrictions.")
                                self.jailee_chat.close_chat()
                                self.jailer_chat.close_chat()
                                self.jailed = []
                                break
        self.wolf_vote_update()
        [messageids, userids, messages, reacted, time, chat] = self.multiple_conv_pieces()
        pieces = [messageids, userids, messages, reacted, time, chat]
        for i, message in enumerate(pieces[0]):
            if pieces[3][i] is False and userids[i] != bot_member_id:
                chat[i].seen_message(message)
        [postids, posters, actions, victims, _, chats] = self.get_keyword_phrases(pieces, new=True)
        for i in range(len(postids)):
            if posters[i].alive:
                posters[i].skip_check(actions[i].lower(), postids[i], chats[i])
            if posters[i].role == 'Violinist':
                victims[i].append(self.first_death)
            outcome = posters[i].immediate_action(postids[i], actions[i].lower(), victims[i], chats[i])
            if len(outcome) == 3:
                self.secondary_text = ''
                self.new_thread_text = (self.new_thread_text +
                                        self.day_thread.write_message(self.kill_player(outcome[0],
                                                                                       outcome[1],
                                                                                       outcome[2])))
            if posters[i].role == 'Sorcerer' and posters[i].resigned:
                self.role_swap(posters[i], role.Werewolf())
            if posters[i].skipped and posters[i] in self.to_skip:
                del self.to_skip[self.to_skip.index(posters[i])]
            if actions[i].lower() == 'unskipped':
                chats[i].write_message(chats[i].quote_message(postids[i]) + f"There are {len(self.to_skip)} "
                                                                            f"people who have yet to skip.")
        if len(self.to_skip) == 0:
            self.night_close_tm = datetime.datetime.now()
        self.output_data()

    def kill_player(self, method, killer, victim):
        actual_method = method
        if self.first_death.screenname == '':
            self.first_death = victim
            if self.dead_speaker.gamenum == 0:
                self.dead_speaker = self.first_death
                self.first_death.chat.write_message("You are the first to die, and there is no role that can speak "
                                                    "with the dead. Therefore, you have the honor of creating the "
                                                    "dead thread with whatever theme you like.")
        # If victim is jellied, no kill
        if victim.alive is False:
            return ''
        # If victim is jellied, no kill
        if len(victim.jellied_by) > 0:
            for jellier in victim.jellied_by:
                jellier.mp = 0
                while jellier in victim.jellied_by:
                    delindex = victim.jellied_by.index(jellier)
                    del victim.jellied_by[delindex]
                jellier.chat.write_message(f"Your protection on {victim.screenname} has been consumed. ")
            victim.black_potion = False
            if victim.red_potion > 1:
                victim.red_potion = 0
            return 'The Jelly Wolf protection has been consumed. '
        if victim.role == 'Werewolf Fan' and actual_method in ['wolf', 'toxic']:
            self.role_swap(victim, role.Werewolf())
            victim.chat.write_message("You have been bitten! You have been converted to a Werewolf.")
            self.wolf_chat.close_chat()
            self.create_wolf_chat()
            return ''
        if victim.role == 'Alpha Wolf' and victim.extra_life:
            victim.extra_life = False
            victim.black_potion = False
            if victim.red_potion > 1:
                victim.red_potion = 0
            return 'The Alpha Wolf has been attacked.'
        if len(victim.scribed_by) > 0:
            scribe_data = victim.scribe_method[-1]  # Take most recent scribed info
            if scribe_data[0] != '':
                method = scribe_data[0]
            scribe_role = scribe_data[1]
            if scribe_role != '':
                victim.apparent_role = scribe_role
            wolf_scribe = victim.scribed_by[-1]  # Who is responsible for the scribing
            wolf_scribe.mp = wolf_scribe.mp - 50  # Deduct their MP
            del victim.scribe_method[-1]  # Clean up
            del victim.scribed_by[-1]  # Clean up
        # Victim gets most attributes reset
        victim.alive = False
        if victim in self.to_skip:
            del self.to_skip[self.to_skip.index(victim)]
        self.death = True
        victim.night_killed = self.night
        victim.doused_by = []
        victim.disguised_by = []
        victim.concussed = False
        victim.has_been_concussed = False
        victim.nightmared = False
        victim.infected_by = []
        victim.conjuror_acted = False
        victim.action_used = False
        victim.protected_by = {'Flagger': [],
                               'Doctor': [],
                               'Jailer': [],
                               'Bodyguard': [],
                               'Witch': [],
                               'Tough Guy': [],
                               'Defender': [],
                               'Forger': [],
                               'Beast Hunter': []
                               }
        victim.jailed = False
        victim.given_warden_weapon = False
        victim.warden_eligible = True
        victim.red_potion = 0
        victim.black_potion = False
        victim.shamaned_by = []
        victim.has_killed = False
        victim.poisoned = False
        victim.unlynchable_by = []
        if len(victim.tricked_by) > 0:
            victim.apparent_role = 'Wolf Trickster'
            for wolf in victim.tricked_by:
                wolf.mp = 0
                wolf.acting_upon = []
                wolf.apparent_aura = victim.aura
                wolf.apparent_team = victim.team
            victim.tricked_by = []
        if self.confusion_in_effect:
            victim.apparent_role = '??????'
        # if victim was watched by the bell ringer
        if len(victim.bell_ringer_watched_by) > 0:
            # watcher is the bell ringer who is getting info
            for watcher in victim.bell_ringer_watched_by:
                watcher.mp = 0
                # Go through the pair of people the bell ringer watched
                delindex = watcher.acting_upon.index(victim)
                del watcher.acting_upon[delindex]
                pair = watcher.acting_upon[0]
                watcher.chat.write_message(f"{victim.screenname} is dead. {pair.screenname} is the {pair.role}")
        victim.bell_ringer_watched_by = []
        # if victim was watched by the preacher
        if len(victim.preacher_watched_by) > 0:
            # watcher is the preacher who is getting votes
            for watcher in victim.preacher_watched_by:
                watcher.votes = watcher.votes + 1
                while watcher in victim.preacher_watched_by:
                    delindex = victim.preacher_watched_by.index(watcher)
                    del victim.preacher_watched_by[delindex]
                watcher.chat.write_message(f'{victim.screenname} is dead. You have gained an additional vote. '
                                           f'Your normal vote will be used in the poll as usual.'
                                           f'Your additional vote can be used anytime during the day by posting '
                                           f'[b]here[/b]:\n\n'
                                           f'Wolfbot vote (username)\n\n If you gain even more additional votes, '
                                           f'separate the votes with "and". Such as:\n\n'
                                           f'Wolfbot vote (username) and (username) and (username)\n\n'
                                           f'for three votes. The username can be different or the same.')
        victim.preacher_watched_by = []
        # if victim was watched by the sheriff, they are killed by normal wolf/solo at night
        if actual_method in ['wolf', 'toxic', 'arsonist', 'sacrificed',
                             'cult', 'detective', 'instigator', 'stabbed']:
            if len(victim.sheriff_watched_by) > 0:
                alive = []
                # get all alives
                for i in self.role_dictionary:
                    if self.role_dictionary[i].alive:
                        alive.append(self.role_dictionary[i])
                del alive[alive.index(killer)]
                # watcher is the sheriff who is getting info
                for watcher in victim.sheriff_watched_by:
                    order = random.randint(1, 2)
                    rand_player = random.randint(0, len(alive) - 1)
                    if order == 1:
                        watcher.chat.write_message(f"{victim.screenname} is dead. They were killed by either "
                                                   f"{killer.screenname} or {alive[rand_player]}.")
                    else:
                        watcher.chat.write_message(f"{victim.screenname} is dead. They were killed by either "
                                                   f"{alive[rand_player]} or {killer.screenname}.")
            if len(victim.visited) > 0:
                for redlady in victim.visited:
                    self.secondary_text = self.secondary_text + self.kill_player("poorvisit", victim, redlady)
        victim.sheriff_watched_by = []
        victim.visited = []
        if victim.coupled:
            # Uncouple the pair so recursion works
            for pair in self.couple:
                pair.coupled = False
            # Remove the person we already killed from the pair
            del self.couple[self.couple.index(victim)]
            # Kill the other coupled player
            self.secondary_text = self.secondary_text + self.kill_player("couple", victim, self.couple[0])
            # Kill Cupid
            self.secondary_text = self.secondary_text + self.kill_player("couple", victim, self.cupid)
        if victim.instigated:
            # Uncouple the pair so recursion works
            for pair in self.couple:
                pair.coupled = False
            # Remove the person we already killed from the pair
            del self.couple[self.couple.index(victim)]
            # Kill the other coupled player
            self.secondary_text = self.secondary_text + self.kill_player("couple", victim, self.couple[0])
            # Unleash Instigator
            self.instigator.instigators_dead = True
        if victim.cult:
            self.secondary_text = self.secondary_text + f"{victim.screenname} was a member of the cult.\n\n"
            victim.cult = False
        if victim.hhtarget:
            if actual_method == 'lynched':
                self.win_conditions('Headhunter')
                return
            else:
                victim.hhtarget = False
        if victim.role == 'Fool' and actual_method == 'lynched':
            self.win_conditions('Fool')
            return
        # Now go through each role and clean up their role effects upon death
        if victim.role in ['Jailer', 'Warden']:
            for player in self.jailed:
                player.jailed = False
                player.protected_by['Jailer'] = []
        if victim.seer:
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.role == 'Seer Apprentice':
                    victim.first_seer = True
                    player.chat.write_message(f"Due to [b]{victim.screenname}'s[/b] death, "
                                              f"you have converted to the role of [b]{victim.role}[/b].")
                    self.role_swap(player, victim)

        elif victim.role in ['Avenger', 'Wolf Avenger']:
            if len(victim.acting_upon) > 0:
                self.secondary_text = self.secondary_text + self.kill_player("avenger",
                                                                             victim,
                                                                             victim.acting_upon[-1])
                victim.acting_upon = []
        # Remove protections by now-dead player
        elif victim.role in ('Flagger', 'Doctor', 'Bodyguard', 'Witch', 'Tough Guy',
                             'Defender', 'Beast Hunter'):
            if victim.role == 'Beast Hunter':
                victim.trap_on = 0
                victim.cooldown = False
            if victim.role == 'Flagger':
                victim.attacking = 0
                victim.cooldown = False
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                while victim in player.protected_by[victim.role]:
                    delindex = player.protected_by[victim.role].index(victim)
                    del player.protected_by[victim.role][delindex]
        elif victim.role == 'Bell Ringer':
            if len(victim.acting_upon) > 0:
                delindex = victim.acting_upon[0].bell_ringer_watched_by.index(victim)
                del victim.acting_upon[0].bell_ringer_watched_by[delindex]
                delindex = victim.acting_upon[1].bell_ringer_watched_by.index(victim)
                del victim.acting_upon[1].bell_ringer_watched_by[delindex]
            victim.acting_upon = []
        elif victim.role in ('Flower Child', 'Guardian Wolf'):
            victim.acting_upon = []
        elif victim.role == 'Loudmouth':
            if len(victim.acting_upon) > 0:
                self.secondary_text = self.secondary_text + (f"The Loudmouth has revealed the role of [b]"
                                                             f"{victim.acting_upon[-1].screenname}.[/b] "
                                                             f"They are the [b]{victim.acting_upon[-1].role}."
                                                             f"[/b]\n\n")
                victim.acting_upon = []
        elif victim.role == 'Marksman':
            victim.cooldown = False
            victim.acting_upon = [role.Player()]
        elif victim.role == 'Preacher':
            if len(victim.acting_upon) > 0:
                while victim in victim.acting_upon[0].preacher_watched_by:
                    delindex = victim.acting_upon[0].preacher_watched_by.index(victim)
                    del victim.acting_upon[0].preacher_watched_by[delindex]
            victim.acting_upon = []
        elif victim.role == 'Sheriff':
            if len(victim.acting_upon) > 0:
                while victim in victim.acting_upon[0].sheriff_watched_by:
                    delindex = victim.acting_upon[0].sheriff_watched_by.index(victim)
                    del victim.acting_upon[0].sheriff_watched_by[delindex]
            victim.acting_upon = []
        elif victim.role == 'Jelly Wolf':
            if len(victim.acting_upon) > 0:
                while victim in victim.acting_upon[0].jellied_by:
                    delindex = victim.acting_upon[0].jellied_by.index(victim)
                    del victim.acting_upon[0].jellied_by[delindex]
            victim.acting_upon = []
        elif victim.role == 'Wolf Scribe':
            if len(victim.acting_upon) > 0:
                while victim in victim.acting_upon[0].scribed_by:
                    delindex = victim.acting_upon[0].scribed_by.index(victim)
                    del victim.acting_upon[0].scribed_by[delindex]
                    del victim.acting_upon[0].scribe_method[delindex]
            victim.acting_upon = []
        elif victim.role == 'Wolf Trickster':
            if len(victim.acting_upon) > 0:
                delindex = victim.acting_upon[0].tricked_by.index(victim)
                del victim.acting_upon[0].tricked_by[delindex]
            victim.acting_upon = []
        elif victim.role == 'Arsonist':
            for doused in victim.acting_upon:
                delindex = doused.doused_by.index(victim)
                del doused.doused_by[delindex]
            victim.acting_upon = []
        elif victim.role == 'Illusionist':
            for disguised in victim.acting_upon:
                delindex = disguised.disguised_by.index(victim)
                del disguised.disguised_by[delindex]
            victim.acting_upon = []
        elif victim.role == 'Corruptor':
            if len(victim.acting_upon) > 0:
                delindex = victim.acting_upon[0].corrupted_by.index(victim)
                del victim.acting_upon[0].corrupted_by[delindex]
                victim.acting_upon = []
        # Check everyone because infection spreads
        elif victim.role == 'Infector':
            victim.acting_upon = []
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if victim in player.infected_by:
                    delindex = player.infected_by.index(victim)
                    del player.infected_by[delindex]
        elif victim.role == 'Cult Leader':
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.cult:
                    player.cult = False
                    self.secondary_text = (self.secondary_text +
                                           self.kill_player("couple", victim, player))
        if victim.team == 'Wolf' and victim.role != 'Werewolf Fan':
            self.wolf_chat.close_chat()
            wolves_left = []
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if (player.team == 'Wolf'
                        and player.role != 'Werewolf Fan'
                        and player.alive):
                    wolves_left.append(player)
            if len(wolves_left) > 0:
                self.create_wolf_chat()
            if len(wolves_left) == 1:
                wolves_left[0].is_last_evil = True
        if self.day_thread.open and method not in ["lynched", "judge", "mistrial"]:
            # remove player from poll
            self.day_thread.change_poll_item(victim.screenname, '')
        self.admin_pm.write_message(f"Can you add {victim.screenname} please?")
        if victim.apparent_role in self.strong_village:
            self.rsv -= 1
        elif victim.apparent_role in self.regular_village:
            self.rrv -= 1
        elif victim.apparent_role in self.wildcard:
            self.rv -= 1
        elif victim.apparent_role in self.solo:
            self.rk -= 1
        elif victim.apparent_role in self.wolves:
            self.rww -= 1
        ind = role.kill_methods()['keyword'].index(method)
        self.add_action(victim, role.kill_methods()["Cause of Death"][ind], victim.apparent_role)
        self.day_thread.edit_post(self.first_post, self.day_post())  # Update first post
        # Go through and print messages for each death method
        if method == 'lynched':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was lynched by the village. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'rock':
            self.output_data()
            return (f'[b]{victim.screenname}[/b] was hit by a rock and killed after being concussed. '
                    f'{killer.screenname} is the [b]Bully[/b].\n\n[b]{victim.screenname}[/b] is dead.'
                    f' {victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n' + self.secondary_text)
        elif method == 'jailer':
            killer.has_killed = True
            self.jailed = []
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed in jail. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'prisoner':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by a fellow prisoner in jail. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'gunner':
            self.output_data()
            return (f'[b]{killer.screenname}[/b] has shot and killed [b]{victim.screenname}[/b]. '
                    f'{killer.screenname} is the [b]Gunner[/b].\n\n{victim.screenname} is dead. '
                    f'{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n' + self.secondary_text)
        elif method == 'shot':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was shot and killed. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'avenger':
            self.output_data()
            return (f"The avenger has taken their revenge and killed [b]{victim.screenname}[/b]. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'trap':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Beast Hunter's trap. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'marksman':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was shot and killed by the marksman. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'misfire':
            self.output_data()
            return (f'{killer.screenname} was shot by the marksman and lived. '
                    f'[b]{victim.screenname}[/b] was killed by their own arrow. '
                    f'{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n' + self.secondary_text)
        elif method == 'water':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by holy water. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'drowned':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] killed themselves attempting to water {killer.screenname}. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'witch':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Witch. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'wolf':
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.wolf_voting_power > 0:
                    player.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the werewolves. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'berserk':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was caught up in the werewolf berserk frenzy. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'toxic':
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.wolf_voting_power > 0:
                    player.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed after being poisoned by the werewolves. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'alchemist':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Alchemist. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'arsonist':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed in the fire. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'corruptor':
            victim.corrupted_by = [0]
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Corruptor. "
                    f"{victim.screenname} was the [b]??????[/b].\n\n" + self.secondary_text)
        elif method == 'sacrificed':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was sacrificed by the Cult Leader. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'cult':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was attacked by the Cult Leader. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'illusionist':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Illusionist. "
                    f"{victim.screenname} was the [b]Illusionist[/b].\n\n" + self.secondary_text)
        elif method == 'infector':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Infector. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'detective':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Evil Detective. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'instigator':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Instigator. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'stabbed':
            killer.has_killed = True
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the Serial Killer. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'coupled':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] is devastated by the loss of a person very close to them, "
                    f"and took their own life. {victim.screenname} was the "
                    f"[b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'breakout':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was killed by the werewolves breaking out of jail. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'judge':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was rightfully killed by the Judge carrying out Justice. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'mistrial':
            self.output_data()
            return (f'[b]{victim.screenname}[/b] was killed by townspeople after attempting to condemn '
                    f'{killer.screenname} to an innocent death.\n\n'
                    f'{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n' + self.secondary_text)
        elif method == 'evilvisit':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] died visiting a killer. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'poorvisit':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] was attacked while visiting a player. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        elif method == 'tough':
            self.output_data()
            return (f"[b]{victim.screenname}[/b] died from their previously sustained injuries. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n\n" + self.secondary_text)
        return ''

    def win_conditions(self, trigger='None'):
        player_count = 0
        wolf_count = 0
        solo_count = 0
        couple_count = 0
        cult_count = 0
        insti_count = 0
        self.output_data()

        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            if player.alive:
                player_count += 1
                if player.cult:
                    cult_count += 1
                if player.coupled:
                    couple_count += 1
                if player.instigated:
                    insti_count += 1
                if player.category == 'Solo Killer':
                    solo_count += 1
                if (player.category == 'Werewolf' and
                        player.role != 'Sorcerer'):
                    wolf_count += 1

        if trigger == 'Fool':
            self.new_thread_text = self.new_thread_text + "\n\n[b]The game is over[/b]. The Fool has won!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        elif trigger == 'Headhunter':
            self.new_thread_text = self.new_thread_text + "\n\n[b]The game is over[/b]. The Headhunter has won!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        elif self.tie_count >= 6:
            self.new_thread_text = self.new_thread_text + "\n\n[b]The game is over[/b]. It's a tie!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        elif couple_count == 2 and (player_count == 2 or (player_count == 3 and self.cupid.alive)):
            self.new_thread_text = self.new_thread_text + "\n\n[b]The game is over[/b]. The Lovers have won!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        elif insti_count == 2 and (player_count == 2 or (player_count == 3 and self.instigator.alive)):
            self.new_thread_text = self.new_thread_text + "\n\n[b]The game is over[/b]. The Instigator team has won!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        elif solo_count == 1 and player_count == 1:
            for i in self.role_dictionary:
                player = self.role_dictionary[i]
                if player.alive:
                    self.new_thread_text = self.new_thread_text + (f"\n\n[b]The game is over[/b]. "
                                                                   f"The {player.role} has won!")
                    self.game_over = True
                    self.day_thread.write_message(self.new_thread_text)
                    self.new_thread_text = ''
                    if not self.day_thread.open:
                        self.day_thread.unlock_thread()
                    return True

        elif wolf_count >= player_count / 2 and solo_count == 0:
            self.new_thread_text = self.new_thread_text + f"\n\n[b]The game is over[/b]. The Wolves have won!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        elif wolf_count == 0 and solo_count == 0:
            self.new_thread_text = self.new_thread_text + f"\n\n[b]The game is over[/b]. The Village has won!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        elif player_count == 0:
            self.new_thread_text = self.new_thread_text + f"\n\n[b]The game is over[/b]. Everyone is dead. It's a tie!"
            self.game_over = True
            self.day_thread.write_message(self.new_thread_text)
            self.new_thread_text = ''
            if not self.day_thread.open:
                self.day_thread.unlock_thread()
            return True

        else:
            return False

    def output_data(self):
        # These are the game attributes we want to save
        # attributes = ['game_title', 'player_list', 'wolf_chat', 'admin_pm', 'new_thread_text', 'wolf_chat_open',
        #              'night', 'spell_count', 'saved_conjuror_data', 'day_thread', 'jailer_chat', 'jailee_chat',
        #              'jailed', 'jailer', 'day_open_tm', 'day_close_tm', 'alch_deaths_tm', 'first_death', 'couple',
        #              'cupid', 'instigator', 'confusion_in_effect', 'manual_votes', 'shadow_in_effect',
        #              'shadow_available', 'tie_count', 'death', 'game_over', 'night_close_tm', 'night_open_tm',
        #              'cult_chat', 'cultleader', 'to_skip', 'insti_chat', 'lover_chat', 'villagers', 'wolves',
        #              'solos', 'wildcards']
        # output master data to csv
        self.master_data.to_csv(f"{output_dir + self.game_title}.csv", index=False)
        # output game attributes to a text file
        f = open(f"{output_dir + self.game_title}.txt", 'w')
        for attribute in self.__dict__:
            if attribute not in ['master_data', 'saved_conjuror_data']:
                f.write(attribute + ": " + export(self.__dict__[attribute]) + '\n')
        f.close()
        # output each player's attributes to individual text files
        attributes = []
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            g = open(f"{output_dir + self.game_title} Player {i}.txt", 'w')
            temp = str(type(player))
            obj = temp[temp.find(".") + 1:temp.find("'>")]
            g.write(f"object: {obj}\n")
            for j in player.__dict__:
                attributes.append(j)
            del attributes[attributes.index('initial_PM')]
            del attributes[attributes.index('current_thread')]
            for attribute in attributes:
                g.write(attribute + ": " + export(player.__dict__[attribute]) + '\n')
            attributes = []
            g.close()
        # output the saved conjuror data just in case
        g = open(f"{output_dir + self.game_title} Conjuror Data.txt", 'w')
        g.write("object: Conjuror\n")
        for i in self.saved_conjuror_data.__dict__:
            attributes.append(i)
        del attributes[attributes.index('initial_PM')]
        del attributes[attributes.index('current_thread')]
        for attribute in attributes:
            g.write(attribute + ": " + export(self.saved_conjuror_data.__dict__[attribute]) + '\n')
        g.close()

    def resume(self, data, delay=0):
        # read the saved master data file back in, use it to generate some dictionaries
        self.master_data = pd.read_csv(f"{output_dir + data}.csv")
        temp = self.master_data.sort_values('Game Number')
        nums = temp['Game Number'].to_list()
        nouns = temp['Nouns'].to_list()
        sorted_ids = temp['Player ID'].to_list()
        self.noun_lookup = {}
        for i in range(len(nums)):
            self.noun_lookup[nums[i]] = nouns[i]
            self.noun_lookup[nouns[i]] = nums[i]
        self.player_game_numbers = {'Game Number': nums,
                                    'Player ID': sorted_ids,
                                    'Nouns': nouns}
        self.rebuild_dict()
        # read in each individuals data back into the correct role objects
        players = [f"{data} Player {x + 1}.txt" for x in range(len(self.master_data))]
        for i, player_file in enumerate(players):
            f = open(output_dir + player_file)
            obj = f.readline().strip('\n')
            obj = obj[obj.find(": ")+2:]
            exec(f"self.role_dictionary[i + 1] = role.{obj}()")
            f.close()
        for i, player_file in enumerate(players):
            f = open(output_dir + player_file)
            f.readline().replace('ZELL/n', '\n')
            line = f.readline().replace('ZELL/n', '\n')
            while line:
                if "protected_by" not in line and "muted_by" not in line:
                    code = line.replace(": ", " = ")
                elif "protected_by" in line:
                    code = "protected_by = " + line[14:]
                else:
                    code = "muted_by = " + line[10:]
                code = "self.role_dictionary[i + 1]." + code
                if "Player(0)" in code:
                    code = code.replace("Player(0)", "role.Player()")
                elif "Player(" in code:
                    code = code.replace("Player(", "self.role_dictionary[")
                    code = code.replace(")", "]")
                exec(code)
                line = f.readline().replace('ZELL/n', '\n')
            f.close()
        # read the conjuror data
        f = open(output_dir + data + " Conjuror Data.txt")
        self.saved_conjuror_data = role.Conjuror()
        f.readline().replace('ZELL/n', '\n')
        line = f.readline().replace('ZELL/n', '\n')
        while line:
            if "protected_by" not in line and "muted_by" not in line:
                code = line.replace(": ", " = ")
            elif "protected_by" in line:
                code = "protected_by = " + line[14:]
            else:
                code = "muted_by = " + line[10:]
            code = "self.saved_conjuror_data." + code
            if "Player(0)" in code:
                code = code.replace("Player(0)", "role.Player()")
            elif "Player(" in code:
                code = code.replace("Player(", "self.role_dictionary[")
                code = code.replace(")", "]")
            exec(code)
            line = f.readline().replace('ZELL/n', '\n')
        f.close()
        # read in the remaining game attributes, filling in the role data where needed
        self.day_open_tm = ''
        self.day_close_tm = ''
        self.alch_deaths_tm = ''
        self.night_close_tm = ''
        self.night_open_tm = ''
        f = open(output_dir + data + ".txt")
        f.readline().replace('ZELL/n', '\n')
        line = f.readline().replace('ZELL/n', '\n')
        while line:
            code = line.replace(": ", " = ")
            code = "self." + code
            if "Player(0)" in code:
                code = code.replace("Player(0)", "role.Player()")
            elif "Player(" in code:
                code = code.replace("Player(", "self.role_dictionary[")
                code = code.replace(")", "]")
            exec(code)
            line = f.readline().replace('ZELL/n', '\n')
        self.day_open_tm = datetime.datetime.strptime(self.day_open_tm, '%Y-%m-%d %H:%M:%S.%f')
        self.day_close_tm = (datetime.datetime.strptime(self.day_close_tm, '%Y-%m-%d %H:%M:%S.%f')
                             + datetime.timedelta(hours=delay))
        self.alch_deaths_tm = (datetime.datetime.strptime(self.alch_deaths_tm, '%Y-%m-%d %H:%M:%S.%f')
                               + datetime.timedelta(hours=delay))
        self.night_close_tm = (datetime.datetime.strptime(self.night_close_tm, '%Y-%m-%d %H:%M:%S.%f')
                               + datetime.timedelta(hours=delay))
        self.night_open_tm = datetime.datetime.strptime(self.night_open_tm, '%Y-%m-%d %H:%M:%S.%f')
        for i in self.role_dictionary:
            player = self.role_dictionary[i]
            player.current_thread = self.day_thread
