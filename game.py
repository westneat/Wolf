import threadcontrol as tc
import roles as role
import random
import pandas as pd
import copy
import datetime

bot_member_id = 498

keywords = ["arm", "visit", "check", "convert", "corrupt", "couple", "deaths",
            "disguise", "douse", "weapon", "shield", "infect", "jail", "judge",
            "kill", "mark", "mute", "nightmare", "poison", "potion", "protect",
            "redirect", "resign", "reveal", "revive", "rock", "sacrifice", "shaman",
            "shoot", "spell", "tag", "take", "trap", "trick", "watch", "water", "cancel",
            "vote", "berserk", "confusion", "shadow", "skip", "action", "escape"]


# test data
# [47, 157, 62, 101, 95, 65, 7, 40, 4, 8, 100, 82, 54, 67, 306, 18]
#  Game object is responsible to manipulation of the game states
# Test Wolf Chat = 1425
class Game:
    def __init__(self, player_list, game_title):
        self.role_ids = [
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
        self.role_dictionary = {}  # gamenum : Role obj
        self.game_title = game_title
        self.player_list = player_list  # as memberids
        self.alive_players = player_list.copy()
#        self.id_to_player = {}
#        self.player_to_id = {}
        self.player_game_numbers = {}  # game number : memberid
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
        to_pandas = {
            'Player ID': self.player_list,
            'Player Name': self.player_names,
            'Player Name Caps': self.player_names_caps
        }
        self.master_data = pd.DataFrame.from_dict(to_pandas)
        self.saved_conjuror_data = role.Player()
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
        self.day_open_tm = datetime.datetime.now()
        self.day_close_tm = datetime.datetime.now()
        self.first_death = role.Player()
        self.couple = []
        self.cupid = role.Player()
        self.instigator = role.Player()

    # These methods are necessary as different identifiers are used for different purposes,
    # and we need to be able to go between them easily
    def name_to_gamenum(self, playername):
        gamenums = self.player_game_numbers
        return gamenums['Game Number'][gamenums['Player ID'].index(self.player_names_dict[playername])]

    def name_to_memberid(self, playername):
        return self.player_names_dict[playername]

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

        # do every iteration in case names change
    def rebuild_dict(self):
        self.player_names = [tc.get_membername(x) for x in self.player_list]
        self.player_names_caps = [x.upper() for x in self.player_names]
        self.player_names_dict = {}
        for i in range(len(self.player_names_caps)):
            self.player_names_dict[self.player_names_caps[i]] = self.player_names[i]
            self.player_names_dict[i] = self.player_names[i]
            self.player_names_dict[self.player_names[i]] = self.player_list[i]
        to_pandas = {
            'Player ID': self.player_list,
            'Player Name': self.player_names,
            'Player Name Caps': self.player_names_caps
        }
        to_merge = pd.DataFrame.from_dict(to_pandas)
        self.master_data.drop(columns=['Player Name', 'Player Name Caps'])
        self.master_data = self.master_data.merge(to_merge, how='inner', on='Player ID')

        # assigns players their game numbers
    def assign_player_numbers(self):
        h = open("nouns.txt", 'r')
        temp = h.read()
        h.close()
        all_nouns = temp.split('\n')
        nouns = []
        scrambled = self.player_list.copy()
        while len(nouns) < len(scrambled):
            nouns.append(all_nouns.pop(random.randint(0, len(all_nouns)-1)))
        i = 1
        game_num = []
        memberids = []
        while len(scrambled) > 0:
            rand = random.randint(0, len(scrambled)-1)
            game_num.append(i)
            memberids.append(scrambled.pop(rand))
            self.noun_lookup[i] = nouns[i-1]
            self.noun_lookup[nouns[i-1]] = i
            i += 1
        self.player_game_numbers['Game Number'] = game_num
        self.player_game_numbers['Player ID'] = memberids
        self.player_game_numbers['Nouns'] = nouns
        to_merge = pd.DataFrame.from_dict(self.player_game_numbers)
        self.master_data = self.master_data.merge(to_merge, how='inner', on='Player ID')

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
    def assign_roles(self, rsv=3, rrv=7, rww=4, rv=1, rk=1):
        # set these for use in thread posts
        self.global_rsv = rsv
        self.global_rrv = rrv
        self.global_rww = rww
        self.global_rv = rv
        self.global_rk = rk

        # reset master data in case we re-roll
        self.master_data = self.master_data[['Player ID', 'Player Name', 'Player Name Caps', 'Game Number', 'Nouns']]
        # pick number of each category specified
        rsv_roles = [x for x in self.role_ids if x(0).category == "Strong Villager"]
        rrv_roles = [x for x in self.role_ids if x(0).category == "Regular Villager"]
        rww_roles = [x for x in self.role_ids if x(0).category == "Werewolf"]
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
                    if self.role_dictionary[rand].category == "Werewolf":
                        self.role_dictionary[rand] = role.Sorcerer(rand, self.role_dictionary[rand].screenname,
                                                                   self.role_dictionary[rand].noun)
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
        to_pandas = {
            'Role': temp,
            'Game Number': self.role_dictionary.keys()
        }
        to_merge = pd.DataFrame.from_dict(to_pandas)
        self.master_data = self.master_data.merge(to_merge, how='inner', on='Game Number')
        solos = [self.role_dictionary[x] for x in self.role_dictionary
                 if self.role_dictionary[x].category == "Solo Killer"]
        for solo_obj in solos:
            # Initialize Instigator recruits
            if solo_obj.role == "Instigator":
                # get solo number
                solo_num = 0
                for i in self.role_dictionary:
                    if self.role_dictionary[i].role == "Instigator":
                        solo_num = i
                        break
                # randomly pick until we get a villager
                while True:
                    pick = random.randint(1, len(self.role_dictionary))
                    if self.role_dictionary[pick].team == 'Village':
                        self.role_dictionary[pick].instigated = True
                        self.role_dictionary[solo_num].instigated_villager = pick
                        self.couple.append(self.role_dictionary[pick])
                        break
                # randomly pick until we get a villager
                while True:
                    pick = random.randint(1, len(self.role_dictionary))
                    # no WWfans here
                    if self.role_dictionary[pick].team == 'Wolf' and self.role_dictionary[pick].role != 'Werewolf Fan':
                        self.role_dictionary[pick].instigated = True
                        self.couple.append(self.role_dictionary[pick])
                        self.role_dictionary[solo_num].instigated_wolf = pick
                        break

    def day_post(self):
        post_list = sorted(self.player_names, key=lambda v: v.upper())
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
        text = (f'''Dictionary: https://gwforums.com/threads/zell-wolf-role-dictionary-and-hall-of-fame.427/

Here's the list of players:

{tag_list}
And here are the roles:

Village team:
{self.global_rsv}x Random Strong Villagers
{self.global_rrv}x Random Regular Villagers

''' +
                ('Note: There will be NO MORE than one person who has a "speak with the dead" role. '
                 'There will also be no more than one person with a "lock players up at night" role. '
                 'There may be none of either, but there will not be multiple.') + f'''

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

''' +
                ('Votes will be conducted via poll. The poll will close exactly at the deadline. '
                 'You have unlimited changes until that point.\n\n'
                 'There will be a minimum number of votes required to lynch. '
                 'In the event of a tie, nobody is lynched. '
                 'In the event that the minimum number of votes is not reached, nobody is lynched.\n\n'
                 'Skips require a skip vote from every player. '
                 'Once you vote to skip, you cannot unskip. You can skip night sessions in the nightly PM chat.') + f'''

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

''' +
                ('Please do not talk about the game outside of the designated threads. '
                 'This is honor system. When you die, you will gain access to a special forum that is already set up. '
                 'One player may have access to this forum at night. '
                 'If you are revived, you will lose access. '
                 'Please use this forum for all discussion by dead players about the game. '
                 'Alive players can talk during the main thread during the day.\n\n'
                 'It is possible, if very unlikely, for the game to end in a tie if every single player is killed. '
                 'The game also ends in a tie if there are no deaths for three straight days and nights.') + f'''

Winning Conditions:

''' +
                f"{'[s]' if not villagers_alive else ''}Village: Kill all wolves and the solo killer. "
                f"{'[/s]' if not villagers_alive else ''}\n\n{'[s]' if not wolves_alive else ''}"
                f"Wolves: {'[s]' if not solos_alive else ''}Kill the solo killer.{'[/s]' if not solos_alive else ''} "
                f"Afterwards, once the wolves make up half the total players, the wolves win. "
                f"{'[/s]' if not wolves_alive else ''}\n\n{'[s]' if not solos_alive else ''}"
                f"Solo Killer: Kill all other players.{'[/s]' if not solos_alive else ''}\n\n"
                f"{'[s]' if not wildcards_alive else ''}Wildcard Role: Satisfy your winning condition. "
                f"Your winning condition trumps any other that may occur at the same time. "
                f"(For example, if you lynch the fool and it creates a situation where there are 3 wolves left "
                f"and 3 villagers, the Fool wins only).{'[/s]' if not wildcards_alive else ''}")
        return text

    # can be chat or thread pieces passed in
    def get_keyword_phrases(self, pieces, dedupe=True):
        phrases = [[], [], [], []]
        for index, message in enumerate(pieces[2]):
            message_uniform = message.upper().replace('"', '').replace("'", '').replace("@", '')
            # replace all nouns with their corresponding name. No need to reverse.
            for gamenum in self.role_dictionary:
                message_uniform = message_uniform.replace(self.noun_lookup[gamenum].upper(),
                                                          self.role_dictionary[gamenum].screenname.upper())
            # replace names with tokens to fix space issues. Can reverse
            for name in reversed(self.player_names_caps):
                message_uniform = message_uniform.replace(" "+name, " ZELLWOLFBOTID" +
                                                          str(self.player_names_dict[self.player_names_dict[name]])+" ")
            message_words = message_uniform.split()
            for i, word in enumerate(message_words):
                if i < len(message_words)-1:
                    if word == "WOLFBOT" and message_words[i+1].lower() in keywords:
                        temp = message_words[i + 2:]
                        users = []
                        for j in range(0, len(temp), 2):
                            if "ZELLWOLFBOTID" in temp[j] or temp[j] in role.kill_methods()['keyword']:
                                users.append(self.player_names_dict[int(temp[j][13:])])
                            else:
                                break
                        phrases[0].append(pieces[0][index])  # returns post_id
                        phrases[1].append(pieces[1][index])  # returns poster_id
                        phrases[2].append(message_words[i+1])  # returns keyword
                        phrases[3].append(users)  # returns users to apply it to (if applicable)
        if dedupe:
            # Once we get all valid commands, now iterate backwards,
            # and we keep only the latest valid command per person for each keyword
            final_commands = [[], [], [], []]
            member_keyword_combos = []
            for i in range(len(phrases[0]) - 1, -1, -1):
                member_keyword = phrases[2][i] + str(phrases[1][i])
                if member_keyword not in member_keyword_combos and phrases[1][i] in self.player_list:
                    member_keyword_combos.append(member_keyword)
                    final_commands[0].append(phrases[0][i])  # returns post_id, reverse order
                    final_commands[1].append(phrases[1][i])  # returns poster_id, reverse order
                    final_commands[2].append(phrases[2][i])  # returns keyword, reverse order
                    final_commands[3].append(phrases[3][i])  # returns users to apply it to, reverse order
            final_commands_in_order = [[], [], [], []]
            for i in range(len(final_commands[0])):
                final_commands_in_order[0].append(final_commands[0][len(final_commands[0]) - i - 1])  # return post_id
                final_commands_in_order[1].append(final_commands[1][len(final_commands[0]) - i - 1])  # return poster_id
                final_commands_in_order[2].append(final_commands[2][len(final_commands[0]) - i - 1])  # return keyword
                final_commands_in_order[3].append(final_commands[3][len(final_commands[0]) - i - 1])  # return victims
        else:
            final_commands_in_order = phrases.copy()
        return final_commands_in_order

    def count_wolf_votes(self):
        pot_votes = self.get_keyword_phrases(self.wolf_chat.convo_pieces())
        post_ids = []
        poster_ids = []
        votes = []
        for i in range(len(pot_votes[0])):
            if pot_votes[2][i] == "VOTE" and len(pot_votes[3][i]) == 1:
                post_ids.append(pot_votes[0][i])  # returns post_id
                poster_ids.append(pot_votes[1][i])  # returns poster_id as memberid
                votes.append(pot_votes[3][i][0])  # returns who voted for as screenname
        for i in range(len(post_ids)-1, -1, -1):
            if (self.role_dictionary[self.name_to_gamenum(votes[i])].wolf_targetable is False or
                    self.role_dictionary[self.memberid_to_gamenum(poster_ids[i])].wolf_voting_power == 0):
                del post_ids[i]
                del poster_ids[i]
                del votes[i]
        to_pandas = {
            'Player Voting': [self.memberid_to_name(x) for x in poster_ids],
            'Voted Player': votes,
            'Wolf Power': [self.role_dictionary[self.memberid_to_gamenum(x)].wolf_voting_power *
                           self.role_dictionary[self.memberid_to_gamenum(x)].wolf_order
                           if not self.role_dictionary[self.memberid_to_gamenum(x)].jailed and not
                           self.role_dictionary[self.memberid_to_gamenum(x)].concussed else 0
                           for x in poster_ids],
            'Votes': [1 for _ in poster_ids]
        }
        vote_table = pd.DataFrame.from_dict(to_pandas)
        vote_tabulation = vote_table.groupby('Voted Player').sum().reset_index()
        vote_tabulation = vote_tabulation.sort_values(by=['Votes', 'Wolf Power'], ascending=False)
        # print(vote_table[['Player Voting', 'Voted Player']])
        # print(vote_tabulation)
        vote_list = vote_tabulation['Voted Player'].tolist()
        fin_votes = []
        # convert screennames to role objects
        for i in vote_list:
            for j in self.role_dictionary:
                if i == self.role_dictionary[j].screenname:
                    fin_votes.append(self.role_dictionary[j])
        return fin_votes

    # Use this to change conjuror between roles, also for WWFan and Sorcerer
    # Need to be a new role, but keep attributes that keep you "you"
    def role_swap(self, old_role, new_role):
        gamenum = old_role.gamenum
        solo_kill_attempt = old_role.solo_kill_attempt
        bell_ringer_watched_by = old_role.bell_ringer_watched_by
        sheriff_watched_by = old_role.sheriff_watched_by
        preacher_watched_by = old_role.preacher_watched_by
        doused_by = old_role.doused_by
        disguised_by = old_role.disguised_by
        coupled = old_role.coupled
        concussed = old_role.concussed
        has_been_concussed = old_role.has_been_concussed
        nightmared = old_role.nightmared
        tricked_by = old_role.tricked_by
        jellied_by = old_role.jellied_by
        muted_by = old_role.muted_by
        hhtarget = old_role.hhtarget
        corrupted_by = old_role.corrupted_by
        cult = old_role.cult
        infected_by = old_role.infected_by
        seen_by = old_role.seen_by
        instigated = old_role.instigated
        protected_by = old_role.protected_by
        conjuror = old_role.conjuror
        jailed = old_role.jailed
        given_warden_weapon = old_role.given_warden_weapon
        can_jail = old_role.can_jail
        warden_eligible = old_role.warden_eligible
        has_forger_gun = old_role.has_forger_gun
        has_forger_shield = old_role.has_forger_shield
        forger_guns = old_role.forger_guns
        forger_shields = old_role.forger_shields
        red_potion = old_role.red_potion
        black_potion = old_role.black_potion
        spelled = old_role.spelled
        trapped_by = old_role.trapped_by
        shadow = old_role.shadow
        shamaned_by = old_role.shamaned_by
        has_killed = old_role.has_killed
        poisoned = old_role.poisoned
        lynchable = old_role.lynchable
        mp = old_role.mp
        screenname = old_role.screenname
        last_thread_id = old_role.last_thread_id
        chat = old_role.chat
        current_thread = old_role.current_thread
        voting_power = old_role.voting_power
        noun = old_role.noun
        self.role_dictionary[old_role.gamenum] = new_role
        new_role.noun = noun
        new_role.gamenum = gamenum
        new_role.alive = True
        new_role.solo_kill_attempt = solo_kill_attempt
        new_role.bell_ringer_watched_by = bell_ringer_watched_by
        new_role.sheriff_watched_by = sheriff_watched_by
        new_role.preacher_watched_by = preacher_watched_by
        new_role.doused_by = doused_by
        new_role.disguised_by = disguised_by
        new_role.coupled = coupled
        new_role.concussed = concussed
        new_role.has_been_concussed = has_been_concussed
        new_role.nightmared = nightmared
        new_role.tricked_by = tricked_by
        new_role.jellied_by = jellied_by
        new_role.muted_by = muted_by
        new_role.hhtarget = hhtarget
        new_role.corrupted_by = corrupted_by
        new_role.cult = cult
        new_role.infected_by = infected_by
        new_role.seen_by = seen_by
        new_role.instigated = instigated
        new_role.protected_by = protected_by
        new_role.conjuror = conjuror
        new_role.jailed = jailed
        new_role.given_warden_weapon = given_warden_weapon
        new_role.can_jail = can_jail
        new_role.warden_eligible = warden_eligible
        new_role.has_forger_gun = has_forger_gun
        new_role.has_forger_shield = has_forger_shield
        new_role.forger_guns = forger_guns
        new_role.forger_shields = forger_shields
        new_role.red_potion = red_potion
        new_role.black_potion = black_potion
        new_role.spelled = spelled
        new_role.trapped_by = trapped_by
        new_role.shadow = shadow
        new_role.shamaned_by = shamaned_by
        new_role.has_killed = has_killed
        new_role.poisoned = poisoned
        new_role.lynchable = lynchable
        new_role.mp = mp
        new_role.screenname = screenname
        new_role.last_thread_id = last_thread_id
        new_role.chat = chat
        new_role.current_thread = current_thread
        new_role.voting_power = voting_power
        new_role.conjuror = conjuror

    def start_night(self, night_number):
        self.first_death = role.Player()
        self.day_thread.create_thread(f"{self.game_title} Day {night_number}", self.day_post())
        self.day_thread.lock_thread()
        self.day_thread.stick_thread()
        if night_number == 1:
            # get noun list
            # Set up dead forum with Mark
            self.mark_pm.create_conversation("New Wolf game", r'''Hi Mark,
            
            Could you please reset the dead forum for another game?''', [3])
            # Set up Wolf Chat
            wolves_id = []  # holds member ids
            wolf_message = "This is wolf chat." + '\n' + '\n'
            sorc_flag = False
            shadow_flag = False
            instigators = []  # holds member ids
            for player in self.role_dictionary:
                if self.role_dictionary[player].team == 'Wolf' and self.role_dictionary[player].category != 'Wildcard':
                    wolves_id.append(self.gamenum_to_memberid(self.role_dictionary[player].gamenum))
                    if self.role_dictionary[player].role == 'Shadow Wolf':
                        shadow_flag = True
                    if self.role_dictionary[player].role == 'Sorcerer':
                        sorc_flag = True
                    wolf_message = wolf_message + (f'The word for[b] {self.role_dictionary[player].screenname} [/b]'
                                                   f'is [b] {self.role_dictionary[player].noun}[/b]. They are the '
                                                   f'[b]{self.role_dictionary[player].role}.[/b]') + '\n' + '\n'
                if self.role_dictionary[player].role == 'Instigator':
                    instigators.append(self.gamenum_to_memberid(self.role_dictionary[player].gamenum))
                    self.instigator = self.role_dictionary[player]
            if sorc_flag:
                wolf_message = wolf_message + ("The Sorcerer may read this chat, but [b]may not[/b] participate "
                                               "by either commenting or reacting.") + '\n' + '\n'
            if shadow_flag:
                wolf_message = wolf_message + ("Wolf Chat will be [b]Closed[/b] at the start of the day due "
                                               "to the Shadow Wolf.") + '\n' + '\n'
            wolf_message = wolf_message + ("For night 1 only, you must choose to act against this list of potential "
                                           "targets: ") + '\n' + self.get_randomized_nouns()
            self.wolf_chat.create_conversation(f"{self.game_title} Wolf Chat", wolf_message, wolves_id)
            # Set up Instigator Chat
            if len(instigators) > 0:
                insti_text = ''
                for player in self.role_dictionary:
                    if self.role_dictionary[player].instigated:
                        instigators.append(self.gamenum_to_memberid(self.role_dictionary[player].gamenum))
                        insti_text = insti_text + (f'The word for [b]{self.role_dictionary[player].screenname}[/b] is '
                                                   f'[b]{self.role_dictionary[player].noun}[/b]. They are the [b]'
                                                   f'{self.role_dictionary[player].role}[/b]') + '\n' + '\n'
                insti_text = ((f'Welcome to Instigator Chat. [b]You can only win with the Instigator, and can no '
                               f'longer win with your original teams[/b].\n\n'
                               f'{self.role_dictionary[self.memberid_to_gamenum(instigators[0])].screenname} is the '
                               f'[b]Instigator[/b]. Their word is [b]'
                               f'{self.role_dictionary[self.memberid_to_gamenum(instigators[0])].noun}[/b].\n\n') +
                              insti_text)
                insti_chat = tc.Chat()
                insti_chat.create_conversation("Instigators Chat", insti_text, instigators)

        # Set up Jailer/Warden Chat
        self.jailed = []
        self.jailer = 0  # is gamenum
        for player in self.role_dictionary:
            if self.role_dictionary[player].can_jail:
                self.jailer = self.role_dictionary[player].gamenum
            if self.role_dictionary[player].jailed is True:
                self.jailed.append(self.role_dictionary[player])
                # if jailed before, but NOT this time, they're eligible again
            if self.role_dictionary[player].warden_eligible is False and self.role_dictionary[player].jailed is False:
                self.role_dictionary[player].warden_eligible = True
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
                                                 [self.gamenum_to_memberid(self.jailer)])
        elif len(self.jailed) == 2:
            body = ("You have been jailed together. ANY messages you send here will be sent verbatim to the warden. "
                    "You have no message limit.")
            if self.jailed[0].category == 'Werewolf' and self.jailed[1].category == 'Werewolf':
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
                                                 [self.gamenum_to_memberid(self.jailer)])

        # Iterate through all players to initialize game
        for player in self.role_dictionary:
            if night_number == 1:
                self.role_dictionary[player].chat.create_conversation(f"{self.game_title} Role",
                                                                      self.role_dictionary[player].initial_PM + '\n\n' +
                                                                      "For night 1 only, you must choose to act against"
                                                                      " this list of potential targets:" + '\n' +
                                                                      self.get_randomized_nouns(),
                                                                      [self.gamenum_to_memberid(
                                                                          self.role_dictionary[player].gamenum)])
            # Revert Conjuror if they didn't take a new role
            if self.role_dictionary[player].conjuror is True and self.role_dictionary[player].new_role == 0:
                self.role_swap(self.role_dictionary[player], self.saved_conjuror_data)
            # Add speak with dead player back to dead forum
            if self.role_dictionary[player].speak_with_dead and self.role_dictionary[player].alive:
                self.mark_pm.write_message(f"Can you add {self.role_dictionary[player].screenname} please?")
            # remove mutes
            self.role_dictionary[player].muted = []
            # WWFan shows role at start of night
            if self.role_dictionary[player].role == 'Werewolf Fan':
                [_, _, actions, membernames] = self.get_keyword_phrases(
                    self.role_dictionary[player].chat.convo_pieces())
                for j in range(len(actions)):
                    self.role_dictionary[player].phased_action(actions[j], membernames[j])
            # Revive players spelled by Ritualist if time period has been met, also dump Ritu MP
            if self.role_dictionary[player].spelled and not self.role_dictionary[player].alive:
                if self.spell_count > 1:
                    self.day_thread.write_post(f'By some miracle, {self.role_dictionary[player].screenname} '
                                               f'has returned to us from the dead.')
                    self.role_dictionary[player].alive = True
                    self.role_dictionary[player].spelled = False
                self.spell_count += 1
            if self.role_dictionary[player].role == 'Ritualist' and self.spell_count > 1:
                self.role_dictionary[player].mp = 0

    def phased_actions(self, rolelist):
        for player in self.role_dictionary:
            if self.role_dictionary[player].role in rolelist:
                if (not self.role_dictionary[player].jailed and not self.role_dictionary[player].concussed
                        and not self.role_dictionary[player].nightmared):
                    [_, _, actions, victims] = self.get_keyword_phrases(
                        self.role_dictionary[player].chat.convo_pieces())
                    if len(actions) == 0:  # do this so that the phased method gets run even if the player does nothing
                        actions = ['null']
                        victims = ['null']
                    if self.role_dictionary[player].role == 'Violinist':
                        victims.append(self.first_death)
                    for i in range(len(actions)):
                        outcome = self.role_dictionary[player].phased_action(actions[i], victims[i])
                        if len(outcome) == 3:
                            self.new_thread_text = self.new_thread_text + self.kill_player(outcome[0], outcome[1],
                                                                                           outcome[2])
                        if len(outcome) == 1:  # Place Beast Hunter Trap if timeframe reached
                            self.role_dictionary[outcome[0]].protected_by['Beast Hunter'].append(
                                self.role_dictionary[player])

    def solo_attack(self, rolelist):
        # Go through all players, but we only care about the solo killers
        for solo_killer in self.role_dictionary:  # player is solo killer
            # Apply to solo killers
            if self.role_dictionary[solo_killer].role in rolelist:  # Infector and Illusionist have different priority
                # If abilities aren't available then just skip everything
                if (not self.role_dictionary[solo_killer].jailed and not self.role_dictionary[solo_killer].concussed
                        and not self.role_dictionary[solo_killer].nightmared):
                    # Go through solo killer chat, pick out all keywords and who they apply to
                    [_, _, actions, victims] = self.get_keyword_phrases(
                        self.role_dictionary[solo_killer].chat.convo_pieces())
                    # Go through each keyword. Most roles should only be one
                    for i in range(len(actions)):
                        # We need to figure out if the attack is blocked. Lots of ways to block an attack
                        # If we don't have a list of victims, make it one so we can iterate in case of multiple deaths
                        if isinstance(victims[i], list):
                            victims_list = victims[i]
                        else:
                            victims_list = [victims[i]]
                        for subjects in victims_list:
                            blocked = False  # assume attack isn't blocked
                            attacked = subjects.gamenum
                            # These bypass protection
                            if (self.role_dictionary[solo_killer].role != 'Arsonist' and not
                               (self.role_dictionary[solo_killer].role == 'Alchemist' and actions[i] == 'potion')
                                    and not (self.role_dictionary[solo_killer].role == 'Cult Leader'
                                             and actions[i] == 'sacrifice')):
                                # protected_by is dictionary with keyword = role, values = list of role objects of that
                                # role attempting to protect this player.
                                for j in self.role_dictionary[attacked].protected_by:
                                    if j == 'Flagger' and len(self.role_dictionary[attacked].protected_by[j]) > 0:
                                        random_flag = random.randint(0,
                                                                     len(self.role_dictionary[attacked].
                                                                         protected_by[j]) - 1)
                                        # Charge protection to random if multiple flaggers on same player
                                        flagger = self.role_dictionary[attacked].protected_by[j][random_flag]
                                        del self.role_dictionary[attacked].protected_by[j][random_flag]
                                        attacked = flagger.attacking
                                        flagger.mp = flagger.mp - 50
                                        flagger.chat.write_message("You successfully redirected an attack tonight.")
                                        flagger.cooldown = True
                                for j in self.role_dictionary[attacked].protected_by:
                                    if j == 'Doctor' and len(self.role_dictionary[attacked].protected_by[j]) > 0:
                                        blocked = True
                                        for blocker in self.role_dictionary[attacked].protected_by[j]:
                                            blocker.chat.write_message("You successfully protected a "
                                                                       "player from being attacked tonight.")
                                for j in self.role_dictionary[attacked].protected_by:
                                    if (j == 'Jailer' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                                            and not blocked):
                                        blocked = True
                                for j in self.role_dictionary[attacked].protected_by:
                                    if (j == 'Bodyguard' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                                            and not blocked):
                                        blocked = True
                                        for blocker in self.role_dictionary[attacked].protected_by[j]:
                                            if blocker.shield is False:
                                                blocker.chat.write_message("You've been hurt tonight. Either you or "
                                                                           "the person you were protecting "
                                                                           "was attacked.")
                                                outcome = self.role_dictionary[solo_killer].phased_action(actions,
                                                                                                          blocker)
                                                if len(outcome) == 3:
                                                    self.new_thread_text = (self.new_thread_text +
                                                                            self.kill_player(outcome[0],
                                                                                             outcome[1], outcome[2]))
                                            else:
                                                blocker.shield = False
                                for j in self.role_dictionary[attacked].protected_by:
                                    if (j == 'Witch' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                                            and not blocked):
                                        blocked = True
                                        for blocker in self.role_dictionary[attacked].protected_by[j]:
                                            blocker.has_protect_potion = False
                                            blocker.chat.write_message("You successfully protected a player "
                                                                       "from being attacked tonight.")
                                for j in self.role_dictionary[attacked].protected_by:
                                    if (j == 'Tough Guy' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                                            and not blocked):
                                        blocked = True
                                        for blocker in self.role_dictionary[attacked].protected_by[j]:
                                            blocker.triggered = True
                                            msg = (f"You've been hurt tonight and will die at the end of the day. "
                                                   f"Either you or the person you were protecting was attacked. "
                                                   f"You have seen the identity of your attacker. You were attacked "
                                                   f"by [b]{self.role_dictionary[solo_killer].screenname}[/b], and "
                                                   f"they are the [b]{self.role_dictionary[solo_killer].role}[/b].")
                                            blocker.chat.write_message(msg)
                                            msg2 = (f"You've attacked one strong player. You attacked by [b]"
                                                    f"{blocker.screenname}[/b], and they are the "
                                                    f"[b]{blocker.role}[/b].")
                                            self.role_dictionary[solo_killer].chat.write_message(msg2)
                                for j in self.role_dictionary[attacked].protected_by:
                                    if (j == 'Defender' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                                            and not blocked):
                                        blocked = True
                                        for blocker in self.role_dictionary[attacked].protected_by[j]:
                                            blocker.chat.write_message(f"You successfully protected "
                                                                       f"{self.role_dictionary[attacked].screenname}"
                                                                       f" from being attacked tonight.")
                                for j in self.role_dictionary[attacked].protected_by:
                                    if (j == 'Forger' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                                            and not blocked):
                                        blocked = True
                                        self.role_dictionary[attacked].has_forger_shield = (
                                                self.role_dictionary[attacked].has_forger_shield - 1)
                                for j in self.role_dictionary[attacked].protected_by:
                                    if (j == 'Beast Hunter' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                                            and not blocked):
                                        blocked = True
                                        for blocker in self.role_dictionary[attacked].protected_by[j]:
                                            blocker.trap_on = 0
                                            blocker.chat.write_message(
                                                "Your trap was triggered by an attack tonight, but the attacker was "
                                                "too strong and survived. You need to reset your trap.")
                            if not blocked:
                                outcome = self.role_dictionary[solo_killer].phased_action(actions[i],
                                                                                          self.role_dictionary[
                                                                                              attacked])
                                # outcome returns kill method, killer, victim OR LIST of victims. Need to check.
                                if len(outcome) == 3:
                                    # if there's multiple victims, handle those first, edet and SK
                                    if isinstance(outcome[2], list):
                                        for deaths in outcome[2]:
                                            self.new_thread_text = (self.new_thread_text +
                                                                    self.kill_player(outcome[0], outcome[1], deaths))
                                    else:
                                        self.new_thread_text = (self.new_thread_text +
                                                                self.kill_player(outcome[0], outcome[1], outcome[2]))
                            else:
                                self.role_dictionary[solo_killer].chat.write_message("Your target could not be killed")

    def wolf_attack(self):
        votes = self.count_wolf_votes()
        berserk = False
        # Check for berserk
        for i in self.role_dictionary:
            if self.role_dictionary[i].berserking:
                berserk = True
                self.role_dictionary[i].berserking = False
                break
        blocked = False  # assume attack isn't blocked
        attacked = 0
        for player in votes:
            if player.alive:
                attacked = player.gamenum
                break
        # Calculate weakest wolf for TG / BH purposes
        weakest_wolf_power = 20
        weakest_wolf = role.Player()
        for i in self.role_dictionary:
            if 0 < self.role_dictionary[i].wolf_order < weakest_wolf_power:
                weakest_wolf_power = self.role_dictionary[i].wolf_order
                weakest_wolf = self.role_dictionary[i]
        # These bypass protection
        if not berserk:
            # protected_by is dictionary with keyword = role, values = list of role objects of that
            # role attempting to protect this player.
            for j in self.role_dictionary[attacked].protected_by:
                if j == 'Flagger' and len(self.role_dictionary[attacked].protected_by[j]) > 0:
                    random_flag = random.randint(0,
                                                 len(self.role_dictionary[attacked].protected_by[j])-1)
                    # Charge protection to random if multiple flaggers on same player
                    flagger = self.role_dictionary[attacked].protected_by[j][random_flag]
                    del self.role_dictionary[attacked].protected_by[j][random_flag]
                    attacked = flagger.attacking
                    flagger.mp = flagger.mp - 50
                    flagger.chat.write_message("You successfully redirected an attack tonight.")
                    flagger.cooldown = True
            for j in self.role_dictionary[attacked].protected_by:
                if j == 'Doctor' and len(self.role_dictionary[attacked].protected_by[j]) > 0:
                    blocked = True
                    for blocker in self.role_dictionary[attacked].protected_by[j]:
                        blocker.chat.write_message("You successfully protected a "
                                                   "player from being attacked tonight.")
            for j in self.role_dictionary[attacked].protected_by:
                if (j == 'Jailer' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                        and not blocked):
                    blocked = True
            for j in self.role_dictionary[attacked].protected_by:
                if (j == 'Bodyguard' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                        and not blocked):
                    blocked = True
                    for blocker in self.role_dictionary[attacked].protected_by[j]:
                        if blocker.shield is False:
                            blocker.chat.write_message("You've been hurt tonight. Either you or the "
                                                       "person you were protecting was attacked.")
                            self.new_thread_text = self.new_thread_text + self.kill_player(
                                "wolf", weakest_wolf, blocker)
                        else:
                            blocker.shield = False
            for j in self.role_dictionary[attacked].protected_by:
                if (j == 'Witch' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                        and not blocked):
                    blocked = True
                    for blocker in self.role_dictionary[attacked].protected_by[j]:
                        blocker.has_protect_potion = False
                        blocker.chat.write_message("You successfully protected a player "
                                                   "from being attacked tonight.")
            for j in self.role_dictionary[attacked].protected_by:
                if (j == 'Tough Guy' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                        and not blocked):
                    blocked = True
                    for blocker in self.role_dictionary[attacked].protected_by[j]:
                        blocker.triggered = True
                        msg = (f"You've been hurt tonight and will die at the end of the day. Either "
                               f"you or the person you were protecting was attacked. You have seen the "
                               f"identity of your attacker. You were attacked by [b]"
                               f"{weakest_wolf.screenname}[/b], and they are the "
                               f"[b]{weakest_wolf.role}[/b].")
                        blocker.chat.write_message(msg)
                        msg2 = (f"You've attacked one strong player. You attacked by [b]"
                                f"{blocker.screenname}[/b], and they are the [b]{blocker.role}[/b].")
                        weakest_wolf.chat.write_message(msg2)
            for j in self.role_dictionary[attacked].protected_by:
                if (j == 'Defender' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                        and not blocked):
                    blocked = True
                    for blocker in self.role_dictionary[attacked].protected_by[j]:
                        blocker.chat.write_message(f"You successfully protected "
                                                   f"{self.role_dictionary[attacked].screenname} from"
                                                   f" being attacked tonight.")
            for j in self.role_dictionary[attacked].protected_by:
                if (j == 'Forger' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                        and not blocked):
                    blocked = True
                    self.role_dictionary[attacked].has_forger_shield = (
                            self.role_dictionary[attacked].has_forger_shield - 1)
            for j in self.role_dictionary[attacked].protected_by:
                if (j == 'Beast Hunter' and len(self.role_dictionary[attacked].protected_by[j]) > 0
                        and not blocked):
                    blocked = True
                    for blocker in self.role_dictionary[attacked].protected_by[j]:
                        blocker.trap_on = 0
                        blocker.chat.write_message(
                            "Your trap was triggered by an attack tonight.")
                        self.new_thread_text = (self.new_thread_text + self.kill_player(
                            "trap", blocker, weakest_wolf))

            if not blocked:
                self.new_thread_text = (self.new_thread_text + self.kill_player(
                    "wolf", weakest_wolf, self.role_dictionary[attacked]))
            else:
                self.wolf_chat.write_message(f"Your target ({self.role_dictionary[attacked].screenname}) "
                                             f"could not be killed!")
        else:
            # kill everyone with berserk
            self.new_thread_text = (self.new_thread_text + self.kill_player(
                "wolf", weakest_wolf, self.role_dictionary[attacked]))
            for deads in self.role_dictionary[attacked].protected_by:
                self.new_thread_text = (self.new_thread_text + self.kill_player(
                    "berserk", weakest_wolf, deads))

    def end_night(self):
        self.new_thread_text = ''
        # beast_hunters = [] #takes BH objects to run later

        # Nightmare, Shaman, WWFan, Jailing all take place at start of night (Phase 0)
        # PHASE 1
        self.phased_actions(['Wolf Avenger', 'Avenger', 'Loudmouth', 'Wolf Trickster', 'Confusion Wolf'])

        # PHASE 2 (Wolves break out of warden prison or warden weapon used)
        if len(self.jailed) == 2:
            action_taken = False
            for i in range(2):
                if not action_taken:
                    [_, _, actions, _] = self.get_keyword_phrases(self.jailed[i].chat.convo_pieces())
                    for action in actions:
                        if action == 'kill' and self.jailed[i].given_warden_weapon:
                            if self.jailed[i].role == 'Werewolf Fan':
                                self.new_thread_text = (self.new_thread_text +
                                                        self.kill_player('prisoner', self.jailed[i], self.jailed[1-i]))
                            elif self.jailed[1-i].role == 'Werewolf Fan':
                                self.new_thread_text = (self.new_thread_text +
                                                        self.kill_player('prisoner', self.jailed[1-i], self.jailed[i]))
                            elif self.jailed[i].team == self.jailed[1-i].team:
                                self.new_thread_text = (self.new_thread_text +
                                                        self.kill_player('prisoner', self.jailed[1-i], self.jailed[i]))
                            elif self.jailed[i].team != self.jailed[1-i].team:
                                self.new_thread_text = (self.new_thread_text +
                                                        self.kill_player('prisoner', self.jailed[i], self.jailed[1-i]))
                            self.jailed[0].jailed = False
                            self.jailed[1].jailed = False
                            self.jailer_chat.write_message("Chat is Closed.")
                            self.jailee_chat.write_message("Chat is Closed.")
                            self.jailee_chat.close_chat()
                            self.jailer_chat.close_chat()
                            action_taken = True
                            break
                        if (action == 'escape' and self.jailed[0].category == 'Werewolf'
                                and self.jailed[1].category == 'Werewolf'):
                            self.role_dictionary[self.jailer].alive = False
                            self.new_thread_text = (self.new_thread_text +
                                                    self.kill_player('breakout',
                                                                     self.role_dictionary[self.jailer],
                                                                     self.role_dictionary[self.jailer]))
                            self.jailed[0].jailed = False
                            self.jailed[1].jailed = False
                            self.jailed[0].has_killed = True
                            self.jailed[1].has_killed = True
                            action_taken = True
                            self.jailer_chat.write_message("Chat is Closed.")
                            self.jailee_chat.write_message("Chat is Closed.")
                            self.jailee_chat.close_chat()
                            self.jailer_chat.close_chat()
                            break

        # PHASE 3 No wolf checks, those are under immediate action in the night loop
        self.phased_actions(['Voodoo Wolf', 'Librarian', 'Medium', 'Ritualist'])

        # PHASE 4 All protectors lumped together, can sort when attacks performed
        self.phased_actions(['Flagger', 'Doctor', 'Bodyguard', 'Witch', 'Tough Guy',
                             'Defender', 'Jelly Wolf', 'Beast Hunter'])

        # PHASE 5 Illu and Infector attack
        self.solo_attack(['Infector', 'Illusionist'])

        # Apply misdirection before seers go
        for player in self.role_dictionary:
            if len(self.role_dictionary[player].disguised_by) > 0:
                self.role_dictionary[player].apparent_role = 'Illusionist'
                self.role_dictionary[player].apparent_aura = 'Unknown'
                self.role_dictionary[player].apparent_team = 'Illusionist'
            if len(self.role_dictionary[player].shamaned_by) > 0:
                self.role_dictionary[player].apparent_aura = 'Evil'
                self.role_dictionary[player].apparent_team = 'Wolf'

        # PHASE 6 Seers - Except Spirit
        self.phased_actions(['Violinist', 'Detective', 'Aura Seer', 'Sheriff',
                             'Bell Ringer', 'Preacher'])

        # PHASE 7
        self.phased_actions(['Marksman'])
        # WIN CONDITION AFTER EACH BW

        # PHASE 8
        self.phased_actions(['Witch'])

        # PHASE 9
        self.phased_actions(['Jailer'])

        # Phase 10
        self.phased_actions(['Red Lady', 'Forger'])

        # Phase 11
        self.solo_attack(['Alchemist', 'Arsonist', 'Corruptor', 'Cult Leader', 'Evil Detective',
                          'Instigator', 'Serial Killer'])

        # Phase 12
        self.wolf_attack()

        # Phase 13
        self.phased_actions(['Spirit Seer'])

        # Phase 14
        self.phased_actions(['Forger'])
        self.phased_actions(['Forger'])

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

        # Write method to deal with warden weapon
        # Go through attack order
        # See who is credited with protect (take witch potion / flagger redirect if successful)
        # Take MP where actions are successful
        # Figure out flagger redirect
        # Do Preacher and sheriff watching + spirit seer results
        # IS TG triggered?
        # On protection, message protectors IN ORDER
        # solo attack method?
        # wolf attack method?
        # Add first to die to array, pass to Violinist
        # handle berserk
        # handle red lady visits including visiting attacked player
        # handle solo kill attempts
        # NEW WOLF CHAT DURING NIGHT IF SORC RESIGNS
        # New wolf chat at end of day if fan turned
        # Run werewolf fan shown only at start of night, not end of night
        pass

    def start_day(self, day_number):
        self.day_thread.unlock_thread()
        # check if Cupid
        for player in self.role_dictionary:
            if self.role_dictionary[player].role == 'Cupid':
                self.cupid = self.role_dictionary[player]
        # If Cupid is in game, set up Lovers on day 1
        if day_number == 1 and self.cupid.gamenum > 0:
            couple_num = []  # holds game nums
            self.couple = []  # holds role objects
            cupid_message = "You have fallen in love!" + '\n' + '\n'
            for player in self.role_dictionary:
                if self.role_dictionary[player].coupled is True:
                    self.couple.append(self.role_dictionary[player])
                    couple_num.append(self.role_dictionary[player].gamenum)
            # what if we don't have lover because they were killed
            while len(couple_num) < 2:
                # generate a new gamenum to create as lover
                rand = random.randint(1, len(self.role_dictionary))
                if rand not in couple_num and rand != self.cupid.gamenum:
                    couple_num.append(rand)
                    self.couple.append(self.role_dictionary[rand])
                    self.role_dictionary[rand].coupled = True
            cupid_message = cupid_message + (f'[b]{self.couple[0].screenname}[/b] is number {self.couple[0].gamenum}.'
                                             f' They are the [b]{self.couple[0].role}.[/b]\n\n'
                                             f'[b]{self.couple[1].screenname}[/b] is number {self.couple[1].gamenum}.'
                                             f' They are the [b]{self.couple[1].role}.[/b]')
            lovers = tc.Chat()
            lovers.create_conversation(f"{self.game_title} Lovers Chat",
                                       cupid_message,
                                       [self.gamenum_to_memberid(self.couple[0].gamenum),
                                        self.gamenum_to_memberid(self.couple[1].gamenum)])
            cupid_chat = self.cupid.chat
            cupid_chat.write_message(f"Your couple is {self.couple[0].screenname} and "
                                     f"{self.couple[1].screenname}. Good luck!")

        # iterate through players to perform actions
        for player in self.role_dictionary:
            # Reset things from the night/previous day that no longer apply
            self.role_dictionary[player].current_thread = self.day_thread
            self.role_dictionary[player].concussed = False
            self.role_dictionary[player].nightmared = False
            self.role_dictionary[player].jailed = False
            self.role_dictionary[player].lynchable = True
            self.role_dictionary[player].sheriff_watched_by = []
            self.role_dictionary[player].protected_by['Flagger'] = []
            self.role_dictionary[player].protected_by['Doctor'] = []
            self.role_dictionary[player].protected_by['Jailer'] = []
            self.role_dictionary[player].protected_by['Bodyguard'] = []
            self.role_dictionary[player].protected_by['Witch'] = []
            self.role_dictionary[player].protected_by['Tough'] = []
            self.role_dictionary[player].protected_by['Defender'] = []
            self.role_dictionary[player].protected_by['Beast Hunter'] = []  # Trap will be replaced during the night
            self.role_dictionary[player].shamaned = False
            self.role_dictionary[player].has_killed = False
            self.role_dictionary[player].checked = 0
            self.role_dictionary[player].given_warden_weapon = False
            # remove "old" mute so they are eligible to be muted again the next night.
            if self.role_dictionary[player].role in ['Voodoo Wolf', 'Librarian']:
                del self.role_dictionary[player].muting[0]
            # Have Mark remove speak_with_dead players from the dead forum
            if self.role_dictionary[player].speak_with_dead:
                self.mark_pm.write_message(f"Can you remove {player.screenname} please?")
            # Conjuror defaults to reversion unless they pick a new target
            if self.role_dictionary[player].role == 'Conjuror':
                player.new_role = 0
            # Revive players spelled by Ritualist if time period has been met, also dump Ritu MP
            if self.role_dictionary[player].spelled and not self.role_dictionary[player].alive:
                if self.spell_count > 1:
                    self.new_thread_text = self.new_thread_text + (f'By some miracle, '
                                                                   f'{self.role_dictionary[player].screenname} has '
                                                                   f'returned to us from the dead.')
                    self.role_dictionary[player].alive = True
                    self.role_dictionary[player].spelled = False
                self.spell_count += 1
            if self.role_dictionary[player].role == 'Ritualist' and self.spell_count > 1:
                self.role_dictionary[player].mp = 0
            # Marksman has finished their waiting period to shoot
            if self.role_dictionary[player].role == 'Marksman':
                self.role_dictionary[player].cooldown = False
    # Handle red and black potion, corruptor, other solos?

    def run_day_checks(self):
        # role.check_action
        # DURING day always check for Illu kills
        # go through and check role actions are only performed at night/day
        # Enforce shadow and illu kill limits and timeframe
        # Figure out shadow votes and alpha chatting
        # Check for gun shots by forger armed players
        for player in self.role_dictionary:
            if player.conjuror is True and player.new_role != 0:
                self.role_swap(player, player.new_role)

    def run_night_check(self):
        # Swap Sorc for Werewolf if resigned
        pass

    def end_day(self):
        # all weapons and shields done being forged
        # self.forging_gun = False
        # self.forger_guns.append(self.gamenum)
        # if not lynch, do a judgment check
        # reset infector seen by
        self.phased_actions(['Shaman Wolf'])
        self.phased_actions(['Nightmare Wolf'])
        self.phased_actions(['Jailer', 'Warden'])

    def kill_player(self, method, killer, victim):
        if self.first_death.screenname == '':
            self.first_death = victim
        # If victim is jellied, no kill
        secondary_text = ''
        if victim.alive is False:
            return ''
        if len(victim.jellied_by) > 0:
            for jellier in victim.jellied_by:
                jellier.mp = 0
                del victim.jellied_by[victim.jellied_by.index(jellier)]
                jellier.chat.write_message(f"Your protection on {victim.screenname} has been consumed.")
            return 'The Jelly Wolf protection has been consumed.'
        if len(victim.scribed) != 0:
            method = victim.scribed[-1]  # Take most recent scribed info
            wolf_scribe = self.role_dictionary[victim.scribed_by[-1]]  # Who is responsible for the scribing
            wolf_scribe.mp = wolf_scribe.mp - 50  # Deduct their MP
            del victim.scribed[-1]  # Clean up
            del victim.scribed_by[-1]  # Clean up
            # BW HOW TO UNSCRIBE UPON SCRIBE DEATH? WHAT ABOUT ALL DEATHS BY PEOPLE EXERTING POWER, WHAT IF MULTIPLE?
        # Victim gets most attributes reset
        victim.alive = False
        victim.doused_by = []
        victim.disguised_by = []
        victim.concussed = False
        victim.has_been_concussed = False
        victim.nightmared = False
        victim.muted_by = []
        victim.infected_by = []
        victim.seen_by = []
        victim.protected_by = []
        victim.jailed = False
        victim.given_warden_weapon = False
        victim.warden_eligible = True
        # victim.has_forger_gun = False
        # victim.has_forger_shield = False
        # victim.forger_guns = []
        # victim.forger_shields = []
        victim.red_potion = 0
        victim.black_potion = False
        victim.trapped_by = []
        victim.shamaned_by = []
        victim.has_killed = False
        victim.poisoned = False
        victim.lynchable = True
        # if victim was watched by the bell ringer
        if len(victim.bell_ringer_watched_by) > 0:
            # watcher is the bell ringer who is getting info
            for watcher in victim.bell_ringer_watched_by:
                watcher.mp = 0
                # Go through the pair of people the bell ringer watched
                for pair in victim.bell_ringer_watched_by.bell_ringer_pair:
                    # both players are no longer being watched by this bell ringer
                    del pair.bell_ringer_watched_by[pair.bell_ringer_watched_by.index(watcher)]
                    # Report the bell ringer info
                    if pair.gamenum != victim.gamenum:
                        watcher.chat.write_message(f"{victim.screenname} is dead. "
                                                   f"{pair.screenname} is the {pair.role}")
        # if victim was watched by the preacher
        if len(victim.preacher_watched_by) > 0:
            # watcher is the preacher who is getting votes
            for watcher in victim.preacher_watched_by:
                watcher.votes = watcher.votes + 1
                watcher.chat.write_message(f"{victim.screenname} is dead. You have gained an additional vote.")
        victim.preacher_watched_by = []
        # if victim was watched by the sheriff, they are killed by normal wolf/solo at night
        if len(victim.sheriff_watched_by) > 0 and method in ['wolf', 'toxic', 'arsonist', 'sacrificed', 'cult',
                                                             'detective', 'instigator', 'stabbed']:
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
        victim.sheriff_watched_by = []
        if victim.coupled:
            # Uncouple the pair so recursion works
            for pair in self.couple:
                pair.coupled = False
            # Remove the person we already killed from the pair
            del self.couple[self.couple.index(victim)]
            # Kill the other coupled player
            secondary_text = secondary_text + self.kill_player("couple", victim, self.couple[0])
            # Kill Cupid
            secondary_text = secondary_text + self.kill_player("couple", victim, self.cupid)
        if victim.instigated:
            # Uncouple the pair so recursion works
            for pair in self.couple:
                pair.coupled = False
            # Remove the person we already killed from the pair
            del self.couple[self.couple.index(victim)]
            # Kill the other coupled player
            secondary_text = secondary_text + self.kill_player("couple", victim, self.couple[0])
            # Unleash Instigator
            self.instigator.instigators_dead = True
        if len(victim.tricked_by) > 0:
            victim.apparent_role = 'Wolf Trickster'
            for wolf in victim.tricked_by:
                wolf.mp = 0
                wolf.tricking = 0
                wolf.apparent_role = victim.role
                wolf.apparent_aura = victim.aura
                wolf.apparent_team = victim.team
            victim.tricked_by = []
        if victim.cult:
            secondary_text = secondary_text + f"{victim.screenname} was a member of the cult."
        if victim.hhtarget and method == 'lynched':
            self.win_conditions('Headhunter')
        if victim.role == 'Fool' and method == 'lynched':
            self.win_conditions('Fool')
        # Now go through each role and clean up their role effects upon death
        if victim.role in ['Jailer', 'Warden']:
            for player in self.jailed:
                player.jailed = False
                player.protected_by['Jailer'] = []
        elif victim.role in ['Avenger', 'Wolf Avenger']:
            secondary_text = secondary_text + self.kill_player("avenger", victim, victim.avenging)
        # Remove protections by now-dead player
        elif victim.role in ('Flagger', 'Doctor', 'Bodyguard', 'Witch', 'Tough Guy',
                             'Defender', 'Beast Hunter'):
            if victim.role == 'Beast Hunter':
                victim.trap_on = 0
            if victim.role == 'Flagger':
                victim.attacking = 0
                victim.cooldown = False
            for player in self.role_dictionary:
                if victim in self.role_dictionary[player].protected_by[victim.role]:
                    delindex = self.role_dictionary[player].protected_by[victim.role].index(victim)
                    del self.role_dictionary[player].protected_by[victim.role][delindex]
        elif victim.role == 'Bell Ringer':
            delindex = victim.bell_ringer_pair[0].bell_ringer_watched_by.index(victim)
            del victim.bell_ringer_pair[0].bell_ringer_watched_by[delindex]
            delindex = victim.bell_ringer_pair[1].bell_ringer_watched_by.index(victim)
            del victim.bell_ringer_pair[1].bell_ringer_watched_by[delindex]
        elif victim.role in ('Flower Child', 'Guardian Wolf'):
            victim.saved_lynch.lynchable = True
        # WWFan
        # Go through and print messages for each death method
        if method == 'lynched':
            return (f"[b]{victim.screenname}[/b] was lynched by the village. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'rock':
            return (f'[b]{victim.screenname}[/b] was hit by a rock and killed after being concussed. '
                    f'{killer.screenname} is the [b]Bully[/b].\n[b]{victim.screenname}[/b] is dead.'
                    f' {victim.screenname} was the [b]{victim.apparent_role}[/b].\n' + secondary_text)
        elif method == 'jailer':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed in jail. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'prisoner':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed by a fellow prisoner in jail. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'gunner':
            return (f'[b]{killer.screenname}[/b] has shot and killed [b]{victim.screenname}[/b]. '
                    f'{killer.screenname} is the [b]Gunner[/b].\n{victim.screenname} is dead. '
                    f'{victim.screenname} was the [b]{victim.apparent_role}[/b].\n' + secondary_text)
        elif method == 'shot':
            return (f"[b]{victim.screenname}[/b] was shot and killed. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'avenger':
            return (f"The avenger has taken their revenge and killed [b]{victim.screenname}[/b]. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'trap':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed by the Beast Hunter's trap. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'marksman':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was shot and killed by the marksman. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'misfire':
            return (f'{killer.screenname} was shot by the marksman and lived. '
                    f'[b]{victim.screenname}[/b] was killed by their own arrow. '
                    f'{victim.screenname} was the [b]{victim.apparent_role}[/b].\n' + secondary_text)
        elif method == 'water':
            return (f"[b]{victim.screenname}[/b] was killed by holy water. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'drowned':
            return (f"[b]{victim.screenname}[/b] killed themselves attempting to water {killer.screenname}. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'witch':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed by the Witch. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'wolf':
            return (f"[b]{victim.screenname}[/b] was killed by the werewolves. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'berserk':
            return (f"[b]{victim.screenname}[/b] was caught up in the werewolf berserk frenzy. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'toxic':
            return (f"[b]{victim.screenname}[/b] was killed after being poisoned by the werewolves. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'alchemist':
            return (f"[b]{victim.screenname}[/b] was killed by the Alchemist. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'arsonist':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed in the fire. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'corruptor':
            return (f"[b]{victim.screenname}[/b] was killed by the Corruptor. "
                    f"{victim.screenname} was the [b]??????[/b].\n" + secondary_text)
        elif method == 'sacrificed':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was sacrificed by the Cult Leader. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'cult':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was attacked by the Cult Leader. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'illusionist':
            return (f"[b]{victim.screenname}[/b] was killed by the Illusionist. "
                    f"{victim.screenname} was the [b]Illusionist[/b].\n" + secondary_text)
        elif method == 'infector':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed by the Infector. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'detective':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed by the Evil Detective. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'instigator':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed by the Instigator. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'stabbed':
            killer.has_killed = True
            return (f"[b]{victim.screenname}[/b] was killed by the Serial Killer. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'coupled':
            return (f"[b]{victim.screenname}[/b] is devastated by the loss of a person very close to them, "
                    f"and took their own life. {victim.screenname} was the "
                    f"[b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'breakout':
            return (f"[b]{victim.screenname}[/b] was killed by the werewolves breaking out of jail. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'judge':
            return (f"[b]{victim.screenname}[/b] was rightfully killed by the Judge carrying out Justice. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'mistrial':
            return (f'[b]{victim.screenname}[/b] was killed by townspeople after attempting to condemn '
                    f'{killer.screenname} to an innocent death.\n'
                    f'{victim.screenname} was the [b]{victim.apparent_role}[/b].\n' + secondary_text)
        elif method == 'evilvisit':
            return (f"[b]{victim.screenname}[/b] killed visiting a killer. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'poorvisit':
            return (f"[b]{victim.screenname}[/b] was attacked while visiting a player. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        elif method == 'tough':
            return (f"[b]{victim.screenname}[/b] died from their previously sustained injuries. "
                    f"{victim.screenname} was the [b]{victim.apparent_role}[/b].\n" + secondary_text)
        return ''
        # handle avenger and loudmouth
        # seer apprentice inheritance
        # remove MP from trickster

    def win_conditions(self, trigger='None'):
        pass
