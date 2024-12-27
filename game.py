import threadcontrol as tc
import roles as role
import random
import pandas as pd
import copy

bot_member_id = 498

keywords = ["arm", "visit", "check", "convert", "corrupt", "couple", "deaths",
            "disguise", "douse", "weapon", "shield", "infect", "jail", "judge",
            "kill", "mark", "mute", "nightmare", "poison", "potion", "protect",
            "redirect", "resign", "reveal", "revive", "rock", "sacrifice", "shaman",
            "shoot", "spell", "tag", "take", "trap", "trick", "watch", "water", "cancel",
            "vote", "berserk", "confusion", "shadow", "skip", "action", "escape"]

def print_kill_methods():
    bbcode = "[table]"
    # Add header row
    bbcode += "[tr][th]Keyword[/th][th]Cause of Death[/th][/tr]"
    # Add rows for each dictionary item
    keys = list(role.kill_methods().keys())
    table_len = len(role.kill_methods()[keys[0]])
    for i in range(table_len):
        bbcode += "[tr]"
        for j in range(2):
            bbcode += f"[td]{role.kill_methods()[keys[j]][i]}[/td]"
        bbcode += "[/tr]"

    bbcode += "[/table]"
    return bbcode


# test data
# [47, 157, 62, 101, 95, 65, 7, 40, 4, 8, 100, 82, 54, 67, 306, 18]
#  Game object is responsible to manipulation of the game states
class Game:
    def __init__(self, player_list, game_title):
        self.role_ids=[
            role.Bully, role.Conjuror, role.Detective, role.Gunner, role.Jailer,
            role.Medium, role.Ritualist, role.Warden, role.AuraSeer, role.Avenger,
            role.BeastHunter, role.BellRinger, role.Bodyguard, role.Defender, role.Doctor,
            role.Farmer, role.Flagger, role.FlowerChild, role.Forger, role.Judge,
            role.Librarian, role.Loudmouth, role.Marksman, role.Preacher, role.Priest,
            role.RedLady, role.SeerApprentice, role.Sheriff, role.SpiritSeer, role.ToughGuy,
            role.Violinist, role.Witch, role.AlphaWolf, role.BerserkWolf, role.BlindWolf,
            role.ConfusionWolf, role.GuardianWolf, role.JellyWolf, role.NightmareWolf, role.ShadowWolf,
            role.ShamanWolf, role.ToxicWolf, role.VoodooWolf, role.WolfAvenger, role.WolfScribe,
            role.WolfSeer, role.WolfTrickster, role.Cupid, role.Fool, role.Headhunter,
            role.WerewolfFan, role.Alchemist, role.Arsonist, role.Corruptor, role.CultLeader,
            role.EvilDetective, role.Illusionist, role.Infector, role.Instigator, role.SerialKiller
        ]
        self.role_dictionary = {} #gamenum : Role obj
        self.game_title = game_title
        self.player_list = player_list #as memberids
#        self.id_to_player = {}
#        self.player_to_id = {}
        self.player_game_numbers={} #game number : memberid
        self.wolf_chat = tc.Chat()
        self.mark_pm = tc.Chat()
        self.new_thread_text = ''
        self.wolf_chat_open = True
        self.night = 1
        self.spell_count = 0
        self.player_names = [tc.get_membername(x) for x in self.player_list]
        self.player_names_caps = [x.upper() for x in self.player_names]
        self.player_names_dict = {}
        for i in range(len(self.player_names_caps)):
            self.player_names_dict[self.player_names_caps[i]] = self.player_names[i]
            self.player_names_dict[self.player_list[i]] = self.player_names[i]
            self.player_names_dict[self.player_names[i]] = self.player_list[i]
        to_pandas={
        'Player ID' : self.player_list,
        'Player Name' : self.player_names,
        'Player Name Caps' : self.player_names_caps
        }
        self.master_data = pd.DataFrame.from_dict(to_pandas)
        self.saved_conjuror_data = role.Player()
        self.saved_nonconjuror_data = role.Player()
        self.global_rsv = 3
        self.global_rrv = 7
        self.global_rww = 4
        self.global_rv = 1
        self.global_rk = 1
        self.day_thread = tc.Thread()
        self.noun_lookup = {}
        self.jailer_chat = tc.Chat()
        self.jailee_chat = tc.Chat()
        self.jailed = []
        self.jailer = 0


    #These methods are necessary as different identifiers are used for different purposes, and we need to be able to go between them easily
    def name_to_gamenum(self, playername):
        return self.player_game_numbers['Game Number'][self.player_game_numbers['Player ID'].index(self.player_names_dict[playername])]

    def name_to_memberid(self, playername):
        return self.player_names_dict[playername]

    def gamenum_to_name(self,gamenum):
        return self.player_names_dict[self.player_game_numbers['Player ID'][self.player_game_numbers['Game Number'].index(gamenum)]]

    def memberid_to_name(self,memberid):
        return self.player_names_dict[memberid]

    def gamenum_to_memberid(self,gamenum):
        return self.player_game_numbers['Player ID'][self.player_game_numbers['Game Number'].index(gamenum)]

    def memberid_to_gamenum(self,memberid):
        return self.player_game_numbers['Game Number'][self.player_game_numbers['Player ID'].index(memberid)]

    def gamenum_to_noun(self, gamenum):
        return self.noun_lookup[gamenum]

    def noun_to_gamenum(self, noun):
        return self.noun_lookup[noun]

    def noun_to_name(self, noun):
        return self.gamenum_to_name(self.noun_lookup[noun])

    def name_to_noun(self, playername):
        return self.noun_lookup[self.name_to_gamenum(playername)]

    def noun_to_memberid(self, noun):
        return self.gamenum_to_memberid(self.noun_lookup[noun])

    def memberid_to_noun(self, memberid):
        return self.noun_lookup[self.memberid_to_gamenum(memberid)]

        #do every iteration in case names change
    def rebuild_dict(self):
        self.player_names = [tc.get_membername(x) for x in self.player_list]
        self.player_names_caps = [x.upper() for x in self.player_names]
        self.player_names_dict = {}
        for i in range(len(self.player_names_caps)):
            self.player_names_dict[self.player_names_caps[i]] = self.player_names[i]
            self.player_names_dict[i] = self.player_names[i]
            self.player_names_dict[self.player_names[i]] = self.player_list[i]
        to_pandas={
        'Player ID' : self.player_list,
        'Player Name' : self.player_names,
        'Player Name Caps' : self.player_names_caps
        }
        to_merge = pd.DataFrame.from_dict(to_pandas)
        self.master_data.drop(columns=['Player Name','Player Name Caps'])
        self.master_data = self.master_data.merge(to_merge, how='inner', on = 'Player ID')

        #assigns players their game numbers
    def assign_player_numbers(self):
        h = open("nouns.txt",'r')
        temp = h.read()
        h.close()
        all_nouns = temp.split('\n')
        nouns = []
        scrambled = self.player_list.copy()
        while len(nouns) < len(scrambled):
            nouns.append(all_nouns.pop(random.randint(0,len(all_nouns)-1)))
        i=1
        game_num = []
        memberids = []
        while len(scrambled) > 0:
            rand = random.randint(0,len(scrambled)-1)
            game_num.append(i)
            memberids.append(scrambled.pop(rand))
            self.noun_lookup[i] = nouns[i-1]
            self.noun_lookup[nouns[i-1]] = i
            i+=1
        self.player_game_numbers['Game Number'] = game_num
        self.player_game_numbers['Player ID'] = memberids
        self.player_game_numbers['Nouns'] = nouns
        to_merge = pd.DataFrame.from_dict(self.player_game_numbers)
        self.master_data = self.master_data.merge(to_merge, how='inner', on = 'Player ID')

    def get_randomized_nouns(self):
        noun_list = []
        fin_list = []
        text = ''
        for i in self.noun_lookup:
            if isinstance(i,int):
                noun_list.append(self.noun_lookup[i])
        while len(noun_list) > 0:
            fin_list.append(noun_list.pop(random.randint(0,len(noun_list)-1)))
        for j in fin_list:
            text = text + j + '\n'
        return text

        #assign numbers first
        #method assigns role and initializes for night 1 use
    def assign_roles(self, rsv=3, rrv=7, rww=4, rv=1, rk=1):
        #set these for use in thread posts
        self.global_rsv = rsv
        self.global_rrv = rrv
        self.global_rww = rww
        self.global_rv = rv
        self.global_rk = rk

        #reset master data in case we re-roll
        self.master_data = self.master_data[['Player ID', 'Player Name', 'Player Name Caps', 'Game Number', 'Nouns']]
        #pick number of each category specified
        rsv_roles = [x for x in self.role_ids if x(0).category=="Strong Villager"]
        rrv_roles = [x for x in self.role_ids if x(0).category=="Regular Villager"]
        rww_roles = [x for x in self.role_ids if x(0).category=="Werewolf"]
        rv_roles = [x for x in self.role_ids if x(0).category=="Wildcard"]
        rk_roles = [x for x in self.role_ids if x(0).category=="Solo Killer"]
        roles = []
        #Pick RSV roles and add to list. Re-pick if criteria aren't met
        while True:
            for i in range(rsv):
                roles.append(rsv_roles[random.randint(0,len(rsv_roles)-1)])
            dead_count = 0
            jail_count = 0
            for i in roles:
                if i(0).speak_with_dead:
                    dead_count+=1
                if i(0).can_jail:
                    jail_count+=1
            if dead_count <= 1 and jail_count<=1:
                break
            else:
                roles = []
        #Pick RRV roles and add to list.
        for i in range(rrv):
            roles.append(rrv_roles[random.randint(0,len(rrv_roles)-1)])
        #Pick RWW roles and add to list.
        for i in range(rww):
            roles.append(rww_roles[random.randint(0,len(rww_roles)-1)])
        #Pick RK and RV roles and add to list. Re-pick if there are multiple "coupling" roles
        saved_roles = roles.copy()
        while True:
            couples = 0
            for i in range(rk):
                solo = rk_roles[random.randint(0,len(rk_roles)-1)]
                roles.append(solo)
            for i in range(rv):
                wildcard = rv_roles[random.randint(0,len(rv_roles)-1)]
                roles.append(wildcard)
            for i in roles:
                if i(0).can_couple:
                    couples+=1
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
        #roles initialized here
        for i, j in enumerate(roles_fin):
            self.role_dictionary[i + 1] = j(i + 1, self.gamenum_to_name(i + 1), self.gamenum_to_noun(i + 1))
            temp.append(j(i).role)
            if self.role_dictionary[i + 1].conjuror:
                self.saved_conjuror_data = copy.deepcopy(self.role_dictionary[i + 1])
        #If draw werewolf fan, one wolf becomes Sorcerer
        wildcards = [self.role_dictionary[x] for x in self.role_dictionary
                     if self.role_dictionary[x].category == "Wildcard"]
        for wildcard_obj in wildcards:
            if wildcard_obj.role == "Werewolf Fan":
                while True:
                    rand = random.randint(1,len(self.role_dictionary))
                    if self.role_dictionary[rand].category == "Werewolf":
                        self.role_dictionary[rand] = role.Sorcerer(rand, self.role_dictionary[rand].screenname, self.role_dictionary[rand].noun)
                        break
            # Initialize headhunter target
            if wildcard_obj.role == "Headhunter":
                for i in self.role_dictionary:
                    if self.role_dictionary[i].role == "Headhunter":
                        # keep picking players until we get one that hh can target
                        while True:
                            rand = random.randint(1, len(self.role_dictionary))
                            if self.role_dictionary[rand].hhtargetable and self.role_dictionary[rand].hhtarget is False:
                                self.role_dictionary[i].target_name = self.gamenum_to_name(rand)
                                self.role_dictionary[i].target_num = rand
                                self.role_dictionary[rand].hhtarget = True
                                break
        to_pandas={
        'Role' : temp,
        'Game Number' : self.role_dictionary.keys()
        }
        to_merge = pd.DataFrame.from_dict(to_pandas)
        self.master_data = self.master_data.merge(to_merge, how='inner', on = 'Game Number')
        solos = [self.role_dictionary[x] for x in self.role_dictionary
                 if self.role_dictionary[x].category == "Solo Killer"]
        for solo_obj in solos:
            #Initialize Instigator recruits
            if solo_obj.role == "Instigator":
                #get solo number
                solo_num = 0
                for i in self.role_dictionary:
                    if self.role_dictionary[i].role == "Instigator":
                        solo_num = i
                        break
                #randomly pick until we get a villager
                while True:
                    pick = random.randint(1,len(self.role_dictionary))
                    if self.role_dictionary[pick].team == 'Village':
                        self.role_dictionary[pick].instigated = True
                        self.role_dictionary[solo_num].instigated_villager = pick
                        break
                #randomly pick until we get a villager
                while True:
                    pick = random.randint(1,len(self.role_dictionary))
                    if self.role_dictionary[pick].team == 'Wolf' and self.role_dictionary[pick].role != 'Werewolf Fan': #no WWfans here
                        self.role_dictionary[pick].instigated = True
                        self.role_dictionary[solo_num].instigated_wolf = pick
                        break

    def day_post(self):
        post_list = sorted(self.player_names, key = lambda v: v.upper())
        tag_list = ''
        wolves_alive = False
        villagers_alive = False
        wildcards_alive = False
        solos_alive = False
        for i in post_list:
            if self.role_dictionary[self.name_to_gamenum(i)].alive is True:
                tag_list = tag_list + '@' + i + '\n'
            else:
                tag_list = tag_list + '[s]@' + i + '[/s]' + '\n'
        for j in self.role_dictionary:
            if self.role_dictionary[j].alive is True:
                if 'Village' in self.role_dictionary[j].category:
                    villagers_alive = True
                elif self.role_dictionary[j].category == 'Werewolf':
                    wolves_alive = True
                elif 'Wildcard' in self.role_dictionary[j].category:
                    wildcards_alive = True
                elif 'Solo Killer' in self.role_dictionary[j].category:
                    solos_alive = True
        text = f'''Dictionary: https://gwforums.com/threads/zell-wolf-role-dictionary-and-hall-of-fame.427/

Here's the list of players:

{tag_list}
And here are the roles:

Village team:
{self.global_rsv}x Random Strong Villagers
{self.global_rrv}x Random Regular Villagers

Note: There will be NO MORE than one person who has a "speak with the dead" role. There will also be no more than one person with a "lock players up at night" role. There may be none of either, but there won't be multiple.

Wolf team:
{self.global_rww}x Random Wolves

The werewolves can be any of the numbered wolves (except regular werewolf) listed in the dictionary.

Solo team:
{self.global_rk}x Random Killer

Wildcard Role:
{self.global_rv}x Random Fool/Headhunter/Werewolf Fan/Cupid

If the Werewolf Fan is selected, one wolf will become the Sorcerer.

Rules:
Nights will be 12 hours and days will be 24 hours. The end of the next period will be clearly posted.

You may edit your posts. If you somehow manage to edit out an action before the bot reads it, then it won't count.

Votes will be conducted via poll. The poll will close exactly at the deadline. You have unlimited changes until that point.

There will be a minimum number of votes required to lynch. In the event of a tie, nobody is lynched. In the event that the minimum number of votes is not reached, nobody is lynched.

Skips require a skip vote from every player. Once you vote to skip, you cannot unskip. You can skip night sessions in the nightly PM chat.

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

Please do not talk about the game outside of the designated threads. This is honor system. When you die, you will gain access to a special forum that is already set up. One player may have access to this forum at night. If you are revived, you will lose access. Please use this forum for all discussion by dead players about the game. Alive players can talk during the main thread during the day.

It is possible, if very unlikely, for the game to end in a tie if every single player is killed. The game also ends in a tie if there are no deaths for three straight days and nights.

Winning Conditions:

{'[s]' if not villagers_alive else ''}Village: Kill all wolves and the solo killer.{'[/s]' if not villagers_alive else ''}

{'[s]' if not wolves_alive else ''}Wolves: {'[s]' if not solos_alive else ''}Kill the solo killer.{'[/s]' if not solos_alive else ''} Afterwards, once the wolves make up half the total players, the wolves win. {'[/s]' if not wolves_alive else ''}

{'[s]' if not solos_alive else ''}Solo Killer: Kill all other players.{'[/s]' if not solos_alive else ''}

{'[s]' if not wildcards_alive else ''}Wildcard Role: Satisfy your winning condition. Your winning condition trumps any other that may occur at the same time. (For example, if you lynch the fool and it creates a situation where there are 3 wolves left and 3 villagers, the Fool wins only).{'[/s]' if not wildcards_alive else ''}
'''
        return text

    #can be chat or thread pieces passed in
    def get_keyword_phrases(self, pieces, dedupe = True):
        phrases = [[],[],[],[]]
        for index,message in enumerate(pieces[2]):
            message_uniform = message.upper().replace('"','').replace("'",'').replace("@",'')
            # replace all nouns with their corresponding name. No need to reverse.
            for gamenum in self.role_dictionary:
                message_uniform = message_uniform.replace(self.noun_lookup[gamenum].upper(), self.role_dictionary[gamenum].screenname.upper())
            # replace names with tokens to fix space issues. Can reverse
            for name in reversed(self.player_names_caps):
                message_uniform = message_uniform.replace(" "+name, " ZELLWOLFBOTID" + str(self.player_names_dict[self.player_names_dict[name]])+" ")
            message_words = message_uniform.split()
            for i,word in enumerate(message_words):
                if i < len(message_words)-1:
                    if word == "WOLFBOT" and message_words[i+1].lower() in keywords:
                        temp = message_words[i+2:]
                        users = []
                        for j in range(0,len(temp),2):
                            if "ZELLWOLFBOTID" in temp[j] or temp[j] in role.kill_methods()['keyword']:
                                users.append(self.player_names_dict[int(temp[j][13:])])
                            else:
                                break
                        phrases[0].append(pieces[0][index]) #returns post_id
                        phrases[1].append(pieces[1][index]) #returns poster_id
                        phrases[2].append(message_words[i+1]) #returns keyword
                        phrases[3].append(users) #returns users to apply it to (if applicable)
        if dedupe:
            #Once we get all valid commands, now iterate backwards, and we keep only the latest valid command per person for each keyword
            final_commands = [[], [], [], []]
            member_keyword_combos = []
            for i in range(len(phrases[0]) - 1, -1, -1):
                member_keyword = phrases[2][i] + str(phrases[1][i])
                if member_keyword not in member_keyword_combos and phrases[1][i] in self.player_list:
                    member_keyword_combos.append(member_keyword)
                    final_commands[0].append(phrases[0][i]) #returns post_id, reverse order
                    final_commands[1].append(phrases[1][i]) #returns poster_id, reverse order
                    final_commands[2].append(phrases[2][i]) #returns keyword, reverse order
                    final_commands[3].append(phrases[3][i]) #returns users to apply it to (if applicable), reverse order
            final_commands_in_order = [[], [], [], []]
            for i in range(len(final_commands[0])):
                final_commands_in_order[0].append(final_commands[0][len(final_commands[0]) - i - 1]) #returns post_id
                final_commands_in_order[1].append(final_commands[1][len(final_commands[0]) - i - 1]) #returns poster_id
                final_commands_in_order[2].append(final_commands[2][len(final_commands[0]) - i - 1]) #returns keyword
                final_commands_in_order[3].append(final_commands[3][len(final_commands[0]) - i - 1]) #returns users to apply it to (if applicable)
        else:
            final_commands_in_order = phrases.copy()
        return final_commands_in_order

    def count_wolf_votes(self):
        pot_votes = self.get_keyword_phrases(self.wolf_chat.convo_pieces())
        post_ids = []
        poster_ids = []
        votes = []
        for i in range(len(pot_votes[0])):
            if pot_votes[2][i]=="VOTE" and len(pot_votes[3][i])==1:
                post_ids.append(pot_votes[0][i]) #returns post_id
                poster_ids.append(pot_votes[1][i]) #returns poster_id as memberid
                votes.append(pot_votes[3][i][0]) #returns who voted for as screenname
        for i in range(len(post_ids)-1,-1,-1):
            if self.role_dictionary[self.name_to_gamenum(votes[i])].wolf_targetable is False or \
            self.role_dictionary[self.memberid_to_gamenum(poster_ids[i])].wolf_voting_power == 0:
                del post_ids[i]
                del poster_ids[i]
                del votes[i]
        to_pandas = {'Player Voting' : [self.memberid_to_name(x) for x in poster_ids],
        'Voted Player' : votes,
        'Wolf Power' : [self.role_dictionary[self.memberid_to_gamenum(x)].wolf_voting_power*self.role_dictionary[self.memberid_to_gamenum(x)].wolf_order for x in poster_ids],
        'Votes' : [1 for _ in poster_ids]
        }
        vote_table = pd.DataFrame.from_dict(to_pandas)
        vote_tabulation = vote_table.groupby('Voted Player').sum().reset_index()
        vote_tabulation = vote_tabulation.sort_values(by=['Votes', 'Wolf Power'], ascending=False)
        print(vote_table[['Player Voting','Voted Player']])
        print(vote_tabulation)
        return vote_tabulation['Voted Player'].tolist()

    #Defined as "role" objects
    #If gamenum = new_gamenum, fall back to conjuror
    #Otherwise, take new role but keep attributes that make you "you"
    def conjuror_role_swap(self, gamenum, new_gamenum):
        solo_kill_attempt = self.role_dictionary[gamenum].solo_kill_attempt
        bell_ringer_watched_by = self.role_dictionary[gamenum].bell_ringer_watched_by
        sheriff_watched_by = self.role_dictionary[gamenum].sheriff_watched_by
        preacher_watched_by = self.role_dictionary[gamenum].preacher_watched_by
        doused_by= self.role_dictionary[gamenum].doused_by
        disguised_by = self.role_dictionary[gamenum].disguised_by
        coupled = self.role_dictionary[gamenum].coupled
        concussed = self.role_dictionary[gamenum].concussed
        has_been_concussed = self.role_dictionary[gamenum].has_been_concussed
        nightmared = self.role_dictionary[gamenum].nightmared
        tricked_by = self.role_dictionary[gamenum].tricked_by
        jellied_by = self.role_dictionary[gamenum].jellied_by
        muted_by = self.role_dictionary[gamenum].muted_by
        hhtarget = self.role_dictionary[gamenum].hhtarget
        corrupted_by = self.role_dictionary[gamenum].corrupted_by
        cult = self.role_dictionary[gamenum].cult
        infected_by = self.role_dictionary[gamenum].infected_by
        seen_by = self.role_dictionary[gamenum].seen_by
        instigated = self.role_dictionary[gamenum].instigated
        protected_by = self.role_dictionary[gamenum].protected_by
        protecting = self.role_dictionary[gamenum].protecting
        conjuror = self.role_dictionary[gamenum].conjuror
        jailed = self.role_dictionary[gamenum].jailed
        given_warden_weapon = self.role_dictionary[gamenum].given_warden_weapon
        can_jail = self.role_dictionary[gamenum].can_jail
        warden_eligible = self.role_dictionary[gamenum].warden_eligible
        has_forger_gun = self.role_dictionary[gamenum].has_forger_gun
        has_forger_shield = self.role_dictionary[gamenum].has_forger_shield
        forger_guns = self.role_dictionary[gamenum].forger_guns
        forger_shields = self.role_dictionary[gamenum].forger_shields
        red_potion = self.role_dictionary[gamenum].red_potion
        black_potion = self.role_dictionary[gamenum].black_potion
        spelled = self.role_dictionary[gamenum].spelled
        trapped_by = self.role_dictionary[gamenum].trapped_by
        shadow = self.role_dictionary[gamenum].shadow
        shamaned_by = self.role_dictionary[gamenum].shamaned_by
        has_killed = self.role_dictionary[gamenum].has_killed
        poisoned = self.role_dictionary[gamenum].poisoned
        lynchable = self.role_dictionary[gamenum].lynchable
        mp = self.role_dictionary[gamenum].mp
        screenname = self.role_dictionary[gamenum].screenname
        last_thread_id = self.role_dictionary[gamenum].last_thread_id
        chat = self.role_dictionary[gamenum].chat
        current_thread = self.role_dictionary[gamenum].current_thread
        voting_power = self.role_dictionary[gamenum].voting_power
        noun = self.role_dictionary[gamenum].noun
        if gamenum != new_gamenum:
            self.role_dictionary[gamenum] = copy.deepcopy(self.role_dictionary[new_gamenum])
            self.role_dictionary[new_gamenum].conjuror_can_take = False
        else:
            self.role_dictionary[gamenum] = copy.deepcopy(self.saved_conjuror_data)
        self.role_dictionary[gamenum].noun = noun
        self.role_dictionary[gamenum].gamenum = gamenum
        self.role_dictionary[gamenum].alive = True
        self.role_dictionary[gamenum].solo_kill_attempt = solo_kill_attempt
        self.role_dictionary[gamenum].bell_ringer_watched_by = bell_ringer_watched_by
        self.role_dictionary[gamenum].sheriff_watched_by = sheriff_watched_by
        self.role_dictionary[gamenum].preacher_watched_by = preacher_watched_by
        self.role_dictionary[gamenum].doused_by = doused_by
        self.role_dictionary[gamenum].disguised_by = disguised_by
        self.role_dictionary[gamenum].coupled = coupled
        self.role_dictionary[gamenum].concussed = concussed
        self.role_dictionary[gamenum].has_been_concussed = has_been_concussed
        self.role_dictionary[gamenum].nightmared = nightmared
        self.role_dictionary[gamenum].tricked_by = tricked_by
        self.role_dictionary[gamenum].jellied_by = jellied_by
        self.role_dictionary[gamenum].muted_by = muted_by
        self.role_dictionary[gamenum].hhtarget = hhtarget
        self.role_dictionary[gamenum].corrupted_by = corrupted_by
        self.role_dictionary[gamenum].cult = cult
        self.role_dictionary[gamenum].infected_by = infected_by
        self.role_dictionary[gamenum].seen_by = seen_by
        self.role_dictionary[gamenum].instigated = instigated
        self.role_dictionary[gamenum].protected_by = protected_by
        self.role_dictionary[gamenum].protecting = protecting
        self.role_dictionary[gamenum].conjuror = conjuror
        self.role_dictionary[gamenum].jailed = jailed
        self.role_dictionary[gamenum].given_warden_weapon = given_warden_weapon
        self.role_dictionary[gamenum].can_jail = can_jail
        self.role_dictionary[gamenum].warden_eligible = warden_eligible
        self.role_dictionary[gamenum].has_forger_gun = has_forger_gun
        self.role_dictionary[gamenum].has_forger_shield = has_forger_shield
        self.role_dictionary[gamenum].forger_guns = forger_guns
        self.role_dictionary[gamenum].forger_shields = forger_shields
        self.role_dictionary[gamenum].red_potion = red_potion
        self.role_dictionary[gamenum].black_potion = black_potion
        self.role_dictionary[gamenum].spelled = spelled
        self.role_dictionary[gamenum].trapped_by = trapped_by
        self.role_dictionary[gamenum].shadow = shadow
        self.role_dictionary[gamenum].shamaned_by = shamaned_by
        self.role_dictionary[gamenum].has_killed = has_killed
        self.role_dictionary[gamenum].poisoned = poisoned
        self.role_dictionary[gamenum].lynchable = lynchable
        self.role_dictionary[gamenum].mp = mp
        self.role_dictionary[gamenum].screenname = screenname
        self.role_dictionary[gamenum].last_thread_id = last_thread_id
        self.role_dictionary[gamenum].chat = chat
        self.role_dictionary[gamenum].current_thread = current_thread
        self.role_dictionary[gamenum].voting_power = voting_power
        self.role_dictionary[gamenum].conjuror = True

    def start_night(self, night_number):
        self.day_thread.create_thread(f"{self.game_title} Day {night_number}", self.day_post())
        self.day_thread.lock_thread()
        self.day_thread.stick_thread()
        if night_number == 1:
            #get noun list
            #Set up dead forum with Mark
            self.mark_pm.create_conversation("New Wolf game", r'''Hi Mark,
            
            Could you please reset the dead forum for another game?''',[3])
            # Set up Wolf Chat
            wolves_id = [] #holds member ids
            wolf_message = "This is wolf chat." + '\n' + '\n'
            sorc_flag = False
            shadow_flag = False
            instigators = [] #holds member ids
            for player in self.role_dictionary:
                if self.role_dictionary[player].team == 'Wolf' and self.role_dictionary[player].category != 'Wildcard':
                    wolves_id.append(self.gamenum_to_memberid(self.role_dictionary[player].gamenum))
                    if self.role_dictionary[player].role == 'Shadow Wolf':
                        shadow_flag = True
                    if self.role_dictionary[player].role == 'Sorcerer':
                        sorc_flag = True
                    wolf_message = wolf_message + f'The word for[b] {self.role_dictionary[player].screenname} [/b]is [b] {self.role_dictionary[player].noun}[/b]. They are the [b]{self.role_dictionary[player].role}.[/b]' + '\n' + '\n'
                if self.role_dictionary[player].role == 'Instigator':
                    instigators.append(self.gamenum_to_memberid(self.role_dictionary[player].gamenum))
            if sorc_flag:
                wolf_message = wolf_message + "The Sorcerer may read this chat, but [b]may not[/b] participate by either commenting or reacting." + '\n' + '\n'
            if shadow_flag:
                wolf_message = wolf_message + "Wolf Chat will be [b]Closed[/b] at the start of the day due to the Shadow Wolf." + '\n' + '\n'
            wolf_message = wolf_message + "For night 1 only, you must choose to act against this list of potential targets: " + '\n' + self.get_randomized_nouns()
            self.wolf_chat.create_conversation(f"{self.game_title} Wolf Chat", wolf_message, wolves_id)
            #Set up Instigator Chat
            if len(instigators) > 0:
                insti_text = ''
                for player in self.role_dictionary:
                    if self.role_dictionary[player].instigated:
                        instigators.append(self.gamenum_to_memberid(self.role_dictionary[player].gamenum))
                        insti_text = insti_text + f'The word for [b]{self.role_dictionary[player].screenname}[/b] is [b]{self.role_dictionary[player].noun}[/b]. They are the [b]{self.role_dictionary[player].role}[/b]' + '\n' + '\n'
                insti_text = f'''Welcome to Instigator Chat. [b]You can only win with the Instigator, and can no longer win with your original teams[/b]. 

{self.role_dictionary[self.memberid_to_gamenum(instigators[0])].screenname} is the [b]Instigator[/b]. Their word is [b]{self.role_dictionary[self.memberid_to_gamenum(instigators[0])].noun}[/b].

''' + insti_text
                insti_chat = tc.Chat()
                insti_chat.create_conversation("Instigators Chat", insti_text, instigators)

        # Set up Jailer/Warden Chat
        self.jailed = []
        self.jailer = 0 #is gamenum
        for player in self.role_dictionary:
            if self.role_dictionary[player].can_jail:
                self.jailer = self.role_dictionary[player].gamenum
            if self.role_dictionary[player].jailed is True:
                self.jailed.append(self.role_dictionary[player])
                #if jailed before, but NOT this time, they're eligible again
            if self.role_dictionary[player].warden_eligible is False and self.role_dictionary[player].jailed is False:
                self.role_dictionary[player].warden_eligible = True

        #can tell warden/jailer by number of people jailed
        if len(self.jailed) == 1:
            body = "You have been jailed. ANY messages you send here will be sent verbatim to the jailer in the next several minutes, and vice versa. You have no message limit."
            self.jailee_chat.create_conversation("Jailed", body, [self.gamenum_to_memberid(self.jailed[0].gamenum)])
            body2 = f"You have jailed your prisoner, {self.jailed[0].screenname}. ANY messages you send here will be sent verbatim to your prisoner in the next several minutes, and vice versa. You have no message limit."
            self.jailer_chat.create_conversation("On Duty", body2, [self.gamenum_to_memberid(self.jailer)])
        elif len(self.jailed) == 2:
            body = "You have been jailed together. ANY messages you send here will be sent verbatim to the warden. You have no message limit."
            if self.jailed[0].category == 'Werewolf' and self.jailed[1].category == 'Werewolf':
                body = body + '\n' + '\n' '(Since you are both wolves, you make break out of prison by either of you writing "Wolfbot escape" [b]in your individual chat[/b] with Wolfbot (not here).'
            self.jailee_chat.create_conversation("Jailed", body, [self.gamenum_to_memberid(self.jailed[0].gamenum), self.gamenum_to_memberid(self.jailed[1].gamenum)])
            body2 = f"You have jailed your prisoners, {self.jailed[0].screenname} and {self.jailed[1].screenname}. Any messages they write will be sent here. To drop the weapon, do so in your original role PM" #BW - IS THIS NECESSARY?
            self.jailer_chat.create_conversation("On Duty", body2, [self.gamenum_to_memberid(self.jailer)])

        #Iterate through all players to initialize game
        for player in self.role_dictionary:
            if night_number == 1:
                self.role_dictionary[player].chat.create_conversation(f"{self.game_title} Role"
                                                                      , self.role_dictionary[player].initial_PM + '\n\n' + "For night 1 only, you must choose to act against this list of potential targets:" + '\n' + self.get_randomized_nouns()
                                                                      , [self.gamenum_to_memberid(self.role_dictionary[player].gamenum)])
            #Revert Conjuror if they didn't take a new role
            if self.role_dictionary[player].conjuror is True and self.role_dictionary[player].new_role == 0:
                self.conjuror_role_swap(self.role_dictionary[player].gamenum, self.role_dictionary[player].gamenum)
            #Add speak with dead player back to dead forum
            if self.role_dictionary[player].speak_with_dead and self.role_dictionary[player].alive:
                self.mark_pm.write_message(f"Can you add {self.role_dictionary[player].screenname} please?")
            #remove mutes
            self.role_dictionary[player].muted = []
            #WWFan shows role at start of night
            if self.role_dictionary[player].role == 'Werewolf Fan':
                [_, _, actions, membernames] = self.get_keyword_phrases(self.role_dictionary[player].chat.convo_pieces())
                for j in range(len(actions)):
                    self.role_dictionary[player].perform_action(actions[j],membernames[j])
            #Revive players spelled by Ritualist if time period has been met, also dump Ritu MP
            if self.role_dictionary[player].spelled and not self.role_dictionary[player].alive:
                if self.spell_count > 1:
                    self.day_thread.write_post(f'By some miracle, {self.role_dictionary[player].screenname} has returned to us from the dead.')
                    self.role_dictionary[player].alive = True
                    self.role_dictionary[player].spelled = False
                self.spell_count += 1
            if self.role_dictionary[player].role == 'Ritualist' and self.spell_count > 1:
                self.role_dictionary[player].mp = 0

    def phased_actions(self, rolelist):
        for player in self.role_dictionary:
            if self.role_dictionary[player].role in rolelist:
                if not self.role_dictionary[player].jailed and not self.role_dictionary[player].concussed and not self.role_dictionary[player].nightmared:
                    [_, _, actions, victims] = self.get_keyword_phrases(self.role_dictionary[player].chat.convo_pieces())
                    for i in range(len(actions)):
                        self.new_thread_text = self.new_thread_text + self.role_dictionary[player].phased_action(actions[i], victims[i])

    def end_night(self):
        self.new_thread_text = ''
        # beast_hunters = [] #takes BH objects to run later

        #Nightmare, Shaman, WWFan, Jailing all take place at start of night (Phase 0)
        #PHASE 1
        self.phased_actions(['Wolf Avenger', 'Avenger', 'Loudmouth', 'Wolf Trickster', 'Confusion Wolf'])

        #PHASE 2 (Wolves break out of warden prison or warden weapon used)
        if len(self.jailed) == 2:
            action_taken = False
            for i in range(2):
                if not action_taken:
                    [_, _, actions, _] = self.get_keyword_phrases(self.jailed[i].chat.convo_pieces())
                    for action in actions:
                        if action == 'kill':
                            if self.jailed[i].role == 'Werewolf Fan':
                                self.new_thread_text = self.new_thread_text + self.kill_player('prisoner', self.jailed[i], self.jailed[1-i])
                            elif self.jailed[i].team == self.jailed[1-i].team:
                                self.new_thread_text = self.new_thread_text + self.kill_player('prisoner', self.jailed[1-i], self.jailed[i])
                            elif self.jailed[i].team != self.jailed[1-i].team:
                                self.new_thread_text = self.new_thread_text + self.kill_player('prisoner', self.jailed[i], self.jailed[1-i])
                            self.jailed[0].jailed = False
                            self.jailed[1].jailed = False
                            self.jailer_chat.write_message("Chat is Closed.")
                            self.jailee_chat.write_message("Chat is Closed.")
                            self.jailee_chat.close_chat()
                            self.jailer_chat.close_chat()
                            action_taken = True
                            break
                        if action == 'escape' and self.jailed[0].category == 'Werewolf' and self.jailed[1].category == 'Werewolf':
                            self.role_dictionary[self.jailer].alive = False
                            self.new_thread_text = self.new_thread_text + self.kill_player('breakout', self.role_dictionary[self.jailer], self.role_dictionary[self.jailer])
                            self.jailed[0].jailed = False
                            self.jailed[1].jailed = False
                            action_taken = True
                            self.jailer_chat.write_message("Chat is Closed.")
                            self.jailee_chat.write_message("Chat is Closed.")
                            self.jailee_chat.close_chat()
                            self.jailer_chat.close_chat()
                            break


        #After Arsonist douses, reset the "Action_Used" flag to False.

        #Phase 11
        for player in self.role_dictionary:
            if self.role_dictionary[player].shamaned:
                self.role_dictionary[player].apparent_aura = 'Evil'
                self.role_dictionary[player].apparent_team = 'Wolf'


#            [_, _, actions, victims] = self.get_keyword_phrases(self.role_dictionary[player].chat.convo_pieces())
            # need to wait until after wolf kill to apply BH
#            if self.role_dictionary[player].role != 'Beast Hunter':
#                for i in range(len(actions)):
#                    self.new_thread_text = self.new_thread_text + self.role_dictionary[player].phased_action(actions[i],victims[i])
#            else:
#                beast_hunters.append(self.role_dictionary[player])

        # PHASE LAST
        for player in self.role_dictionary:
            if self.role_dictionary[player].shamaned:
                self.role_dictionary[player].shamaned = False
                self.role_dictionary[player].apparent_aura = self.role_dictionary[player].aura
                self.role_dictionary[player].apparent_team = self.role_dictionary[player].team






            if self.role_dictionary[player].disguised:
                self.role_dictionary[player].apparent_aura = "Unknown"
                self.role_dictionary[player].apparent_team = "Illusionist"
                self.role_dictionary[player].apparent_role = "Illusionist"

        #Write method to deal with warden weapon
        #Go through attack order
        #See who is credited with protect (take witch potion / flagger redirect if successful)
        #Take MP where actions are successful
        #Figure out flagger redirect
        #Do Preacher and sheriff watching + spirit seer results
        #IS TG triggered?
        #On protection, message protectors IN ORDER
        #solo attack method?
        #wolf attack method?
        #Add first to die to array, pass to Violinist
        #handle berserk
        #handle red lady visits including visiting attacked player
        #handle solo kill attempts
        #NEW WOLF CHAT DURING NIGHT IF SORC RESIGNS
        #New wolf chat at end of day if fan turned
        #Run werewolf fan shown only at start of night, not end of night
        pass

    def start_day(self, day_number):
        self.day_thread.unlock_thread()
        #check if Cupid
        cupid = 0
        for player in self.role_dictionary:
            if self.role_dictionary[player].role == 'Cupid':
                cupid = self.role_dictionary[player].gamenum
        #If Cupid is in game, set up Lovers on day 1
        if day_number == 1 and cupid > 0:
            couple_num = [] #holds game nums
            couple_roles = [] #holds role objects
            cupid_message = "You have fallen in love!" + '\n' + '\n'
            for player in self.role_dictionary:
                if self.role_dictionary[player].coupled is True:
                    couple_roles.append(self.role_dictionary[player])
                    couple_num.append(self.role_dictionary[player].gamenum)
            #what if we don't have lover because they were killed
            while len(couple_num) < 2:
                #generate a new gamenum to create as lover
                rand = random.randint(1,len(self.role_dictionary))
                if rand not in couple_num and rand != cupid:
                    couple_num.append(rand)
                    couple_roles.append(self.role_dictionary[rand])
                    self.role_dictionary[rand].coupled = True
            cupid_message = cupid_message + f'''[b] {couple_roles[0].screenname} [/b]is number {couple_roles[0].gamenum}. They are the [b]{couple_roles[0].role}.[/b]

            [b] {couple_roles[1].screenname} [/b]is number {couple_roles[1].gamenum}. They are the [b]{couple_roles[1].role}.[/b]
            '''
            lovers = tc.Chat()
            lovers.create_conversation(f"{self.game_title} Lovers Chat", cupid_message, [self.gamenum_to_memberid(couple_roles[0].gamenum),self.gamenum_to_memberid(couple_roles[1].gamenum)])
            cupid_chat = self.role_dictionary[cupid].chat
            cupid_chat.write_message(f"Your couple is {couple_roles[0].screenname} and {couple_roles[1].screenname}. Good luck!")

        #iterate through players to perform actions
        for player in self.role_dictionary:
            #Reset things from the night/previous day that no longer apply
            self.role_dictionary[player].current_thread = self.day_thread
            self.role_dictionary[player].concussed = False
            self.role_dictionary[player].nightmared = False
            self.role_dictionary[player].jailed = False
            self.role_dictionary[player].lynchable = True
            self.role_dictionary[player].protected = False
            self.role_dictionary[player].shamaned = False
            self.role_dictionary[player].has_killed = False
            self.role_dictionary[player].checked = 0
            # remove "old" mute so they are eligible to be muted again the next night.
            if self.role_dictionary[player].role in ['Voodoo Wolf', 'Librarian']:
                del self.role_dictionary[player].muting[0]
            #Have Mark remove speak_with_dead players from the dead forum
            if self.role_dictionary[player].speak_with_dead:
                self.mark_pm.write_message(f"Can you remove {player.screenname} please?")
            #Conjuror defaults to reversion unless they pick a new target
            if self.role_dictionary[player].role == 'Conjuror':
                player.new_role = 0
            #Revive players spelled by Ritualist if time period has been met, also dump Ritu MP
            if self.role_dictionary[player].spelled and not self.role_dictionary[player].alive:
                if self.spell_count > 1:
                    self.new_thread_text = self.new_thread_text + f'By some miracle, {self.role_dictionary[player].screenname} has returned to us from the dead.'
                    self.role_dictionary[player].alive = True
                    self.role_dictionary[player].spelled = False
                self.spell_count += 1
            if self.role_dictionary[player].role == 'Ritualist' and self.spell_count > 1:
                self.role_dictionary[player].mp = 0
            #Marksman has finished their waiting period to shoot
            if self.role_dictionary[player].role == 'Marksman':
                self.role_dictionary[player].cooldown = False

    def run_day_checks(self):
        #role.check_action
        # DURING day always check for Illu kills
        # go through and check role actions are only performed at night/day
        # Enforce shadow and illu kill limits and timeframe
        #Figure out shadow votes and alpha chatting
        for player in self.role_dictionary:
            if player.conjuror is True and player.new_role != 0:
                self.conjuror_role_swap(player.gamenum, player.new_role)


    def run_night_check(self):
        #Swap Sorc for Werewolf if resigned
        pass

    def end_day(self):
        #all weapons and shields done being forged
        #self.forging_gun = False
        #self.forger_guns.append(self.gamenum)
        #if not lynch, do a judgment check
        #reset infector seen by
        self.phased_actions(['Shaman Wolf'])
        self.phased_actions(['Nightmare Wolf'])
        self.phased_actions(['Jailer', 'Warden'])

    def kill_player(self, method, killer, victim):
        if victim.scribed != '':
            method = victim.scribed  # BW HOW TO UNSCRIBE UPON SCRIBE DEATH? WHAT ABOUT ALL DEATHS BY PEOPLE EXERTING POWER, WHAT IF MULTIPLE?
        if method == 'lynched':
            return f"[b]{victim.screenname}[/b] was lynched by the village. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'rock':
            return f"[b]{victim.screenname}[/b] was hit by a rock and killed after being concussed. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'jailer':
            return f"[b]{victim.screenname}[/b] was killed in jail. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'prisoner':
            return f"[b]{victim.screenname}[/b] was killed by a fellow prisoner in jail. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'shot':
            return f"[b]{victim.screenname}[/b] was shot and killed. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'avenger':
            return f"The avenger has taken his revenge and killed [b]{victim.screenname}[/b]. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'trap':
            return f"[b]{victim.screenname}[/b] was killed by the Beast Hunter's trap. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'marksman':
            return f"[b]{victim.screenname}[/b] was shot and killed by the marksman. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'misfire':
            return f"[b]{victim.screenname}[/b] was killed by their own arrow. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'water':
            return f"[b]{victim.screenname}[/b] was killed by holy water. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'drowned':
            return f"[b]{victim.screenname}[/b] killed themselves attempting to water a player. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'witch':
            return f"[b]{victim.screenname}[/b] was killed by the Witch. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'wolf':
            return f"[b]{victim.screenname}[/b] was killed by the werewolves. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'berserk':
            return f"[b]{victim.screenname}[/b] was caught up in the werewolf berserk frenzy. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'toxic':
            return f"[b]{victim.screenname}[/b] was killed after being poisoned by the werewolves. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'alchemist':
            return f"[b]{victim.screenname}[/b] was killed by the Alchemist. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'arsonist':
            return f"[b]{victim.screenname}[/b] was killed in the fire. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'corruptor':
            return f"[b]{victim.screenname}[/b] was killed by the Corruptor. {victim.screenname} was the [b]??????[/b].\n"

        elif method == 'sacrificed':
            return f"[b]{victim.screenname}[/b] was sacrificed by the Cult Leader. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'cult':
            return f"[b]{victim.screenname}[/b] was attacked by the Cult Leader. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'illusionist':
            return f"[b]{victim.screenname}[/b] was killed by the Illusionist. {victim.screenname} was the [b]Illusionist[/b].\n"

        elif method == 'infector':
            return f"[b]{victim.screenname}[/b] was killed by the Infector. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'instigator':
            return f"[b]{victim.screenname}[/b] was killed by the Instigator. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'stabbed':
            return f"[b]{victim.screenname}[/b] was killed by the Serial Killer. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'coupled':
            return f"[b]{victim.screenname}[/b] is devastated by the loss of a person very close to them, and took their own life. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'breakout':
            return f"[b]{victim.screenname}[/b] was killed by the werewolves breaking out of jail. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'judge':
            return f"[b]{victim.screenname}[/b] was rightfully killed by the Judge carrying out Justice. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'mistrial':
            return f"[b]{victim.screenname}[/b] was killed by townspeople after accidentally attempt to condemn an innocent person to death. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'evilvisit':
            return f"[b]{victim.screenname}[/b] killed visiting a killer. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'poorvisit':
            return f"[b]{victim.screenname}[/b] was attacked while visiting a player. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"

        elif method == 'tough':
            return f"[b]{victim.screenname}[/b] died from their previous injuries. {victim.screenname} was the [b]{victim.apparent_role}[/b].\n"
        pass
        #reset all conditions
        #handle avenger and loudmouth
        #bell ringer
        #sheriff
        #seer apprentice inheritance
        #remove MP from trickster
        #check jelly

