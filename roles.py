import threadcontrol as tc
import sys
import inspect


def are_all_alive(actions):
    for player in actions:
        if player.alive is False:
            return False
    return True


def kill_methods():
    return {"keyword": ["lynched", 
                        "rock", 
                        "jailer", 
                        "prisoner", 
                        "shot", 
                        "gunner", 
                        "avenger", 
                        "trap", 
                        "marksman", 
                        "misfire", 
                        "water", 
                        "drowned", 
                        "witch",
                        "wolf", 
                        "berserk", 
                        "toxic", 
                        "alchemist", 
                        "arsonist", 
                        "corruptor", 
                        "sacrificed",
                        "cult",
                        "illusionist",
                        "detective", 
                        "infector", 
                        "instigator", 
                        "stabbed", 
                        "coupled", 
                        "breakout",
                        "judge", 
                        "mistrial", 
                        "evilvisit", 
                        "poorvisit", 
                        "tough"], 
            "Cause of Death": ["Lynched by the village", 
                               "Killed by the Bully", 
                               "Shot by the Jailer", 
                               "Shot by a fellow prisoner jailed by the Warden", 
                               "Shot by a player", 
                               "Shot by the Gunner", 
                               "Tagged by a dead Avenger", 
                               "Killed by a Beast Hunter trap", 
                               "Shot by the Marksman", 
                               "Failed shot by the Marksman", 
                               "Killed by the Priest", 
                               "Failed Priest attempt", 
                               "Killed by Witch potion", 
                               "Killed by the standard Werewolf night kill", 
                               "Killed protecting a player who was targeted by the Berserk Wolf", 
                               "Killed at night by the wolves after being poisoned by the Toxic Wolf", 
                               "Killed by Alchemist potion", 
                               "Killed by Arsonist burning",
                               "Killed by the Corruptor", 
                               "Cult member sacrificed by the Cult Leader", 
                               "Killed by the Cult Leader",
                               "Killed by the Illusionist",
                               "Killed by the Evil Detective", 
                               "Killed by the Infector", 
                               "Killed by the Instigator", 
                               "Killed by the Serial Killer", 
                               "Took their own life", 
                               "Killed by jailed wolves", 
                               "Killed by Judge", 
                               "Killed by incorrect decision as Judge", 
                               "Killed as Red Lady visiting a killer", 
                               "Killed as Red Lady visiting a player attacked", 
                               "Killed by their injuries as Tough Guy"]}


def print_kill_methods():
    bbcode = "[table]"
    # Add header row
    bbcode += "[tr][th]Keyword[/th][th]Cause of Death[/th][/tr]"
    # Add rows for each dictionary item
    keys = list(kill_methods().keys())
    table_len = len(kill_methods()[keys[0]])
    for i in range(table_len):
        bbcode += "[tr]"
        for j in range(2):
            bbcode += f"[td]{kill_methods()[keys[j]][i]}[/td]"
        bbcode += "[/tr]"
    bbcode += "[/table]"
    return bbcode


def print_roles():
    bbcode = "[table]"
    # Add header row
    bbcode += "[tr][th]Keyword[/th][th]Role Name[/th][/tr]"
    # Add rows for each dictionary item
    keys = list(class_list().keys())
    table_len = len(class_list()[keys[0]])
    for i in range(table_len):
        bbcode += "[tr]"
        for j in range(2):
            bbcode += f"[td]{class_list()[keys[j]][i]}[/td]"
        bbcode += "[/tr]"
    bbcode += "[/table]"
    return bbcode


class Player:
    def __init__(self):
        # These are attributes of roles that can apply to many/most players. Defaults are what apply the most often
        self.initial_PM = ''
        self.alive = True
        self.category = 'Regular Villager'
        self.role = ''
        self.aura = 'Good'
        self.team = 'Village'
        self.mp = 100
        self.screenname = ''
        self.acting_upon = []
        self.apparent_role = self.role
        self.apparent_aura = self.aura
        self.apparent_team = self.team
        self.last_thread_id = 0
        self.chat = tc.Chat()
        self.current_thread = tc.Thread()
        self.is_killer = False
        self.reviving = False
        self.noun = ''
        self.gamenum = 0
        self.votes = 0
        self.extra_life = False
        self.shield = False
        self.cooldown = False
        self.action_used = False
        self.bell_ringer_watched_by = []  # append player watching
        self.sheriff_watched_by = []  # append player watching
        self.preacher_watched_by = []  # append player watching
        self.visited = []
        self.doused_by = []
        self.disguised_by = []
        self.coupled = False
        self.concussed = False
        self.has_been_concussed = False
        self.nightmared = False
        self.tricked_by = []
        self.jellied_by = []
        self.muted_by = {0: []}
        self.speak_with_dead = False
        self.hhtarget = False
        self.hhtargetable = True
        self.wolf_targetable = True
        self.waterable = False
        self.wolf_order = 0
        self.wolf_voting_power = 0
        self.wolf_immune = False
        self.can_couple = False
        self.corrupted_by = []
        self.mm_killable = False
        self.cult = False
        self.infected_by = []
        self.instigated = False
        self.protected_by = {'Flagger': [],
                             'Doctor': [],
                             'Jailer': [],
                             'Bodyguard': [],
                             'Witch': [],
                             'Tough Guy': [],
                             'Defender': [],
                             'Forger': [],
                             'Beast Hunter': []
                             }
        self.conjuror = False
        self.conjuror_can_take = True
        self.new_role = 0
        self.jailed = False
        self.given_warden_weapon = False
        self.can_jail = False
        self.warden_eligible = True
        self.has_forger_gun = 0  # how many guns they have (multiple forgers)
        self.has_forger_shield = 0
        self.forger_guns = []  # who provided the guns
        self.forger_shields = []  # who provided the shields
        self.spelled = False
        self.shamaned_by = []
        self.has_killed = False
        self.seer = False
        self.seer_apprentice = False
        self.first_seer = False
        self.poisoned = False
        self.unlynchable_by = []
        self.scribe_method = []
        self.scribed_by = []
        self.skipped = False
        # Forger
        self.guns_forged = 0
        self.shields_forged = 0
        # Alchemist
        self.red_potion = 0
        self.black_potion = False
        # Beast Hunter
        self.trap_on = 0
        # Shadow Wolf
        self.shadow = False
        # Confusion Wolf
        self.confusion = False
        # Berserk Wolf
        self.berserking = False
        # Wolf Shaman \ Sorcerer \ Blind Wolf \ Wolf Seer
        self.is_last_evil = False
        # Blind Wolf / Sorcerer / Wolf Seer
        self.resigned = False
        self.checked = 0
        self.seen = []
        # Flagger
        self.attacking = 0
        # Tough Guy
        self.triggered = False
        # Witch
        self.has_protect_potion = False
        self.has_kill_potion = False
        # Cupid
        self.night = 1
        # Headhunter
        self.target_name = ''
        # Instigator
        self.instigators_dead = False
        self.night_killed = 0

    # These methods all take the keyword and a LIST of role objects to apply them to
    def immediate_action(self, messageid, keyword, victims, chat_obj):
        return []

    # These methods all take the keyword and a LIST of role objects to apply them to
    def phased_action(self, messageid, keyword, victims, chat_obj):
        return []

    def get_shadow_vote(self, messageid, keyword, voted, chat_obj, end=False):
        if keyword == 'vote' and isinstance(chat_obj, tc.Chat):
            if not end:
                if (len(voted) == 1 and voted[0].alive and self.current_thread.open and len(self.corrupted_by) == 0
                        and voted[0].gamenum == self.gamenum and not self.concussed
                        and len(self.muted_by[self.night-1]) == 0):
                    self.chat.write_message(self.chat.quote_message(messageid) + f"You are voting for "
                                                                                 f"{voted[0].screenname}.")
                elif len(voted) != 1:
                    self.chat.write_message("You can only vote one person.")
                elif not voted[0].alive:
                    self.chat.write_message("Your vote is for a dead person.")
                elif voted[0].gamenum == self.gamenum:
                    self.chat.write_message("You can't vote yourself.")
                elif not self.current_thread.open:
                    self.chat.write_message("You can only vote during the day.")
                elif self.concussed:
                    self.chat.write_message("You are concussed and cannot vote.")
                elif len(self.corrupted_by) != 0:
                    self.chat.write_message("You are corrupted and cannot vote.")
                elif len(self.muted_by[self.night-1]) != 0:
                    self.chat.write_message("You are muted and cannot vote.")
            else:
                if (len(voted) == 1 and voted[0].alive and self.current_thread.open and len(self.corrupted_by) == 0
                        and voted[0].gamenum == self.gamenum and not self.concussed
                        and len(self.muted_by[self.night - 1]) == 0):
                    if self.category == 'Werewolf' and self.role != 'Sorcerer':
                        return [voted[0], voted[0]]
                    else:
                        return [voted[0]]
        return []

    def shoot_forger_gun(self, keyword, victims, chat_obj):
        if keyword == 'shoot' and isinstance(chat_obj, tc.Thread):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum == self.gamenum and self.alive and
                    self.current_thread.open and self.has_forger_gun > 0 and not self.concussed
                    and len(self.corrupted_by) == 0):
                self.has_forger_gun -= 1
                return ['shot', self, victims[0]]
            elif self.has_forger_gun == 0:
                return []
            elif len(victims) != 1:
                self.chat.write_message("You can only shoot one person.")
            elif not victims[0].alive:
                self.chat.write_message("Your target is already dead.")
            elif victims[0].gamenum == self.gamenum:
                self.chat.write_message("You can't shoot yourself.")
            elif not self.current_thread.open:
                self.chat.write_message("You can only act during the day.")
            elif not self.alive:
                self.chat.write_message("You are dead.")
            elif self.concussed:
                self.chat.write_message("You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                self.chat.write_message("You are corrupted and cannot act.")
        return []

    def skip_check(self, keyword, messageid, chat_obj):
        if keyword == 'skip' and not self.skipped:
            self.skipped = True
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are marked as having skipped.")
        return []


# Strong Villagers
class Bully(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.aura = 'Unknown'
        self.role = 'Bully'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot rock (username)'''
        
        # only necessary for some roles, but all need to have the method
        # immediate action happens immediately, phased actions happen at end of day/night
        # FOR ALL DEATHS return method as keyword, killer as role obj, victim as role obj
        # For non deaths, return empty list
    def immediate_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting one person, have thrown 3 or fewer rocks, victim is alive, 
        # and they haven't already thrown a rock today
        if keyword == 'rock' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and self.mp >= 25 and victims[0].alive and victims[0].gamenum != self.gamenum
                    and self.current_thread.open and self.alive and not self.action_used
                    and not self.concussed and len(self.corrupted_by) == 0):
                self.action_used = True
                self.mp = self.mp - 25
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You have successfully hit {victims[0].screenname} with a rock.")
                if victims[0].has_been_concussed:
                    return ['rock', self, victims[0]]
                else:
                    victims[0].chat.write_message("You've been hit by a rock and are now concussed. "
                                                  "You cannot use any actions until the next day phase, "
                                                  "and will die if struck again. ")
                    victims[0].concussed = True
                    victims[0].has_been_concussed = True
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only rock one person per day.")
            elif self.mp < 25:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of rocks.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.action_used:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already thrown a rock today.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
        return []


class Conjuror(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.speak_with_dead = True
        self.conjuror = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.role = 'Conjuror'
        self.new_role = self
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot take (username)

        You have the honor of starting the dead thread on the first night with whatever theme you like.'''
    
    def immediate_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting one person, have thrown 3 or fewer rocks, victim is dead,
        # they haven't already taken a role today, and role hasn't been taken yet
        if keyword == 'take' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and not victims[0].alive and victims[0].conjuror_can_take and self.alive
                    and self.current_thread.open and not self.action_used and not self.concussed and
                    len(self.corrupted_by) == 0):
                self.action_used = True
                self.new_role = victims[0]
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You have successfully taken {victims[0].screenname}'s role.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only take one role.")
            elif victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target must be dead.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.action_used:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already acted today.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
        return []


class Detective(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.role = 'Detective'
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username) and (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'check' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and are_all_alive(victims) and victims[0].gamenum != self.gamenum
                    and victims[1].gamenum != self.gamenum and victims[0].gamenum != victims[1].gamenum
                    and not self.current_thread.open and not self.jailed and self.alive and
                    len(self.corrupted_by) == 0 and not self.concussed and not self.nightmared):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are checking "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"and {victims[1].screenname if self.night > 1 else victims[1].noun} "
                                       f"at the end of the night.")
            elif len(victims) != 2 or victims[0].gamenum == victims[1].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You must select two, and only two, "
                                                                           "different people.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You must check alive targets.")
            elif victims[0].gamenum == self.gamenum or victims[1].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting two people, haven't checked yet,
        # people are alive, and they aren't checking themselves
        if (keyword == 'check' and len(victims) == 2 and are_all_alive(victims) and victims[0].gamenum != self.gamenum
                and victims[1].gamenum != self.gamenum and victims[0].gamenum != victims[1].gamenum
                and not self.current_thread.open and not self.jailed and self.alive and
                len(self.corrupted_by) == 0 and not self.concussed and isinstance(chat_obj, tc.Chat)
                and not self.nightmared):
            if victims[0].apparent_team == victims[1].apparent_team:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and {victims[1].screenname} "
                                       f"are on the [b]same team[/b].")
            else:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and {victims[1].screenname} "
                                       f"are on [b]different teams[/b].")
            if len(victims[0].infected_by) > 0:
                self.infected_by = victims[0].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
            if len(victims[1].infected_by) > 0:
                self.infected_by = victims[1].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
        return []


class Gunner(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.aura = 'Unknown'
        self.role = 'Gunner'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]in the day thread[/b]:

        Wolfbot shoot (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting one person, have shot 1 or fewer bullets,
        # victim is alive, and they haven't already shot today
        if keyword == 'shoot' and isinstance(chat_obj, tc.Thread):
            if (len(victims) == 1 and self.mp >= 50 and victims[0].alive and not self.action_used and self.alive
                    and victims[0].gamenum != self.gamenum and self.current_thread.open and self.has_forger_gun == 0
                    and not self.concussed and len(self.corrupted_by) == 0):
                self.action_used = True
                self.mp = self.mp - 50
                return ['gunner', self, victims[0]]
            elif len(victims) != 1:
                self.chat.write_message("You can only shoot one person.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of bullets.")
            elif not victims[0].alive:
                self.chat.write_message("Your target is already dead.")
            elif victims[0].gamenum == self.gamenum:
                self.chat.write_message("You can't shoot yourself.")
            elif not self.current_thread.open:
                self.chat.write_message("You can only act during the day.")
            elif not self.alive:
                self.chat.write_message("You are dead.")
            elif self.action_used:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already shot today.")
            elif self.concussed:
                self.chat.write_message("You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                self.chat.write_message("You are corrupted and cannot act.")
        return []


class Jailer(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.aura = 'Unknown'
        self.can_jail = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Jailer'
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot jail (username)

        Once a player is jailed, a separate conversation window will be opened for you to talk to your prisoner. 
        You may shoot your prisoner by posting [b]here[/b]:

        Wolfbot shoot (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'jail' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and isinstance(chat_obj, tc.Chat) and self.alive
                    and victims[0].gamenum != self.gamenum and self.current_thread.open and not self.concussed and
                    len(self.corrupted_by) == 0):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} will be jailed tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only jail one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only jail during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
        if keyword == 'shoot' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and self.mp == 100 and victims[0].alive and victims[0].jailed and self.alive
                    and victims[0].gamenum != self.gamenum and not self.current_thread.open and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your prisoner will be shot tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only shoot one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of bullets.")
            elif not victims[0].jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only shoot someone "
                                                                           "you have jailed.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'jail' and len(victims) == 1 and victims[0].alive and isinstance(chat_obj, tc.Chat)
                and self.alive and victims[0].gamenum != self.gamenum and self.current_thread.open
                and not self.concussed and len(self.corrupted_by) == 0) and isinstance(chat_obj, tc.Chat):
            victims[0].jailed = True
            victims[0].protected_by['Jailer'].append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"{victims[0].screenname} has been jailed.")
        if (keyword == 'shoot' and len(victims) == 1 and self.mp == 100 and victims[0].alive and victims[0].jailed
                and self.alive and victims[0].gamenum != self.gamenum and not self.current_thread.open
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and isinstance(chat_obj, tc.Chat)):
            self.mp = self.mp - 100
            return ['jailer', self, victims[0]]
        return []


# Consider allowing medium to revive from dead thread - BW
class Medium(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.aura = 'Unknown'
        self.speak_with_dead = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Medium'
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot revive (username).

        You have the honor of starting the dead thread on the first night.
        '''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'revive' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and not victims[0].alive and self.mp == 100 and self.alive and not self.concussed
                    and victims[0].gamenum != self.gamenum and not self.current_thread.open and not self.jailed
                    and len(victims[0].corrupted_by) == 0 and not self.nightmared):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} will be revived at the beginning of the day.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only revive one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already used your ability.")
            elif victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only revive dead people.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting one person, have not revived, victim is dead
        if (keyword == 'revive' and len(victims) == 1 and not victims[0].alive and self.mp == 100 and self.alive
                and not self.concussed and victims[0].gamenum != self.gamenum and not self.current_thread.open
                and not self.jailed and len(victims[0].corrupted_by) == 0 and not self.nightmared
                and isinstance(chat_obj, tc.Chat)):
            self.mp = self.mp - 100
            victims[0].reviving = True
        return []


class Ritualist(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.aura = 'Unknown'
        self.speak_with_dead = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Ritualist'
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot spell (username)

        You have the honor of starting the dead thread on the first night.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'spell' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.mp == 100
                    and victims[0].gamenum != self.gamenum and self.alive and not self.concussed and
                    len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" has the revival spell cast upon them.")
                victims[0].spelled = True
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only spell one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already used your revive.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead. "
                                                                           "They must be spelled before dying.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []


class Warden(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.aura = 'Unknown'
        self.can_jail = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Warden'
        self.category = 'Strong Villager'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot jail (username) and (username)

        Once a player is jailed, a separate conversation window will be opened for you to listen to your prisoners. 
        You may give a prisoner a weapon by posting [b]here[/b]:

        Wolfbot arm (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'jail' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and are_all_alive(victims) and self.alive and not self.concussed
                    and victims[0].warden_eligible and victims[1].warden_eligible
                    and victims[0].gamenum != victims[1].gamenum and len(self.corrupted_by) == 0
                    and victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                    and self.current_thread.open):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and {victims[1].screenname} will be jailed tonight.")
            elif len(victims) != 2 or victims[0].gamenum != victims[1].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You must jail exactly two "
                                                                           "different people.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "One of your targets is dead.")
            elif victims[0].gamenum == self.gamenum or victims[1].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.action_used:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already thrown a rock today.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif not victims[0].warden_eligible or not victims[1].warden_eligible:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You cannot jail someone that "
                                                                           "you jailed last night.")
            # We put the action in the "check" stage because the players at night
            # need to be notified of getting the weapon immediately.
        if keyword == 'arm' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.mp == 100 and self.alive and not self.concussed
                    and victims[0].jailed and not self.current_thread.open and len(self.corrupted_by) == 0
                    and not self.nightmared):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} was given the weapon.")
                victims[0].given_warden_weapon = True
                victims[0].chat.write_message(r'''You have been given a weapon by the Warden. You can use it by typing: 
                
                Wolfbot kill
                
                Do it in the jail chat with the person you are killing.''')
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only arm one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your weapon has already been used.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only arm one of your prisoners.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting two people, victims are alive, and they didn't just jail them
        if (keyword == 'jail' and len(victims) == 2 and are_all_alive(victims) and self.alive and not self.concussed
                and victims[0].warden_eligible and victims[1].warden_eligible
                and victims[0].gamenum != victims[1].gamenum and len(self.corrupted_by) == 0
                and victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and self.current_thread.open and isinstance(chat_obj, tc.Chat)):
            victims[0].jailed = True
            victims[1].jailed = True
            victims[0].warden_eligible = False
            victims[1].warden_eligible = False
            victims[0].protected_by['Jailer'].append(self)
            victims[1].protected_by['Jailer'].append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"{victims[0].screenname} and {victims[1].screenname} are in jail. "
                                   f"Their conversation will be relayed in a separate window.")
        return []


# Regular Villagers
class AuraSeer(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Aura Seer'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'check' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and isinstance(chat_obj, tc.Chat) and not self.jailed
                    and victims[0].gamenum != self.gamenum and not self.current_thread.open and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are checking "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"at the end of the night.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only check one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting one person, haven't checked yet,
        # people are alive, and they aren't checking themselves
        if (keyword == 'check' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and isinstance(chat_obj, tc.Chat) and not self.jailed
                and victims[0].gamenum != self.gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"{victims[0].screenname} is [b]{victims[0].apparent_aura}[/b].")
            if len(victims[0].infected_by) > 0:
                self.infected_by = victims[0].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
        return []


class Avenger(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Avenger'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot tag (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'tag' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum and self.alive
                    and not self.concussed and not self.jailed and not self.nightmared and len(self.corrupted_by) == 0):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are currently avenging upon "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}.")
                self.acting_upon = victims
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only avenge upon one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []


class BeastHunter(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Beast Hunter'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.trap_on = 0
        self.aura = 'Unknown'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot trap (username)'''
        
    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'trap' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.alive and not self.jailed and not self.concussed
                    and not self.current_thread.open and victims[0].gamenum != self.trap_on
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"Tonight you will move your trap to "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only trap one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.trap_on:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "The trap is already here.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'trap' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.alive and not self.jailed and not self.concussed
                and not self.current_thread.open and victims[0].gamenum != self.trap_on
                and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            self.trap_on = victims[0].gamenum
            self.cooldown = True
            victims[0].protected_by['Beast Hunter'].append(self)
        return []


class BellRinger(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Bell Ringer'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username) and (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'watch' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and are_all_alive(victims) and not self.jailed and self.alive
                    and victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                    and victims[0].gamenum != victims[1].gamenum and self.mp == 100 and not self.concussed
                    and not self.current_thread.open and len(self.corrupted_by) == 0 and not self.nightmared):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will watch {victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"and {victims[1].screenname if self.night > 1 else victims[1].noun} "
                                       f"until the next night phase.")
            elif len(victims) != 2 or victims[0].gamenum == victims[1].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You must watch two different people.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already used your ability.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "One of your targets is dead.")
            elif victims[0].gamenum == self.gamenum or victims[1].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'watch' and isinstance(chat_obj, tc.Chat) and len(victims) == 2 and are_all_alive(victims)
                and not self.jailed and self.alive and victims[0].gamenum != self.gamenum
                and victims[1].gamenum != self.gamenum and victims[0].gamenum != victims[1].gamenum
                and self.mp == 100 and not self.concussed and not self.current_thread.open
                and len(self.corrupted_by) == 0 and not self.nightmared):
            victims[0].bell_ringer_watched_by.append(self)
            victims[1].bell_ringer_watched_by.append(self)
            self.acting_upon = [victims[0], victims[1]]
        return []


class Bodyguard(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Bodyguard'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.shield = True
        self.protected_by['Bodyguard'] = [self]
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and not self.current_thread.open and not self.jailed
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will protect "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only protect one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are jailed and cannot perform night actions. "
                                       f"If you are somehow unjailed, this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'protect' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and not self.current_thread.open and not self.jailed and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
            victims[0].protected_by['Bodyguard'].append(self)
        return []


class Defender(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Defender'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username) and (username) and (username) and (username) and (username) and (username)

        You can protect fewer players by shortening the number of names given.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (len(victims) <= self.mp // 16 and are_all_alive(victims) and not self.jailed and self.alive
                    and not self.current_thread.open and isinstance(chat_obj, tc.Chat) and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared):
                text = chat_obj.quote_message(messageid) + "You will protect the following players tonight: "
                if self.night != 1:
                    for i in victims:
                        text = text + f"\n{i.screenname}"
                else:
                    for i in victims:
                        text = text + f"\n{i.noun}"
                chat_obj.write_message(text)
            elif len(victims) > self.mp // 16:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You've selected more people "
                                                                           "than you can protect'.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Some of your targets are dead.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform "
                                                                           f"night actions. If you are somehow "
                                                                           f"unjailed, this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'protect' and isinstance(chat_obj, tc.Chat) and len(victims) <= self.mp // 16
                and are_all_alive(victims) and not self.jailed and self.alive
                and not self.current_thread.open and isinstance(chat_obj, tc.Chat) and not self.concussed
                and len(self.corrupted_by) == 0 and not self.nightmared):
            text = "You attempted to protect the following players tonight: "
            for player in victims:
                if player.alive:
                    player.protected_by['Defender'].append(self)
                    text = text + f"\n{player.screenname}"
                    self.mp = self.mp - 16*len(victims)
        return []


class Doctor(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Doctor'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and not self.jailed and self.alive and not self.concussed
                    and victims[0].gamenum != self.gamenum and not self.current_thread.open and
                    len(self.corrupted_by) == 0 and not self.nightmared):
                text = (chat_obj.quote_message(messageid) +
                        f"You will protect {victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only protect one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'protect' and isinstance(chat_obj, tc.Chat) and len(victims) == 1
                and victims[0].alive and not self.jailed and self.alive and not self.concussed
                and victims[0].gamenum != self.gamenum and not self.current_thread.open and
                len(self.corrupted_by) == 0 and not self.nightmared):
            victims[0].protected_by['Doctor'].append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You attempted to protect {victims[0].screenname} tonight.")
        return []


class Farmer(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Farmer'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''


class Flagger(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Flagger'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.cooldown = False
        self.aura = 'Unknown'
        self.attacking = 0
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot redirect (username) to (username)'''

    # think about how to handle if target dead same night BW
    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'redirect' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and are_all_alive(victims) and victims[0].gamenum != victims[1].gamenum and self.alive
                    and not self.current_thread.open and not self.cooldown and self.mp >= 50 and not self.jailed
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
                text = (chat_obj.quote_message(messageid) +
                        f"You will redirect all evil attacks from "
                        f"{victims[0].screenname if self.night > 1 else victims[0].noun} towards "
                        f"{victims[1].screenname if self.night > 1 else victims[1].noun} tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 2:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You must chooose both one person to "
                                                                           "protect and one person to redirect the "
                                                                           "attack to.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of redirects.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "One of your targets is dead.")
            elif victims[0].gamenum == victims[1].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't protect and redirect to "
                                                                           "the same person.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.cooldown:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't use your ability because you "
                                                                           "were successful last night.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are jailed and cannot perform night "
                                                                           "actions. If you are somehow unjailed, "
                                                                           "this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'redirect' and isinstance(chat_obj, tc.Chat) and len(victims) == 2 and are_all_alive(victims)
                and victims[0].gamenum != victims[1].gamenum and self.alive
                and not self.current_thread.open and not self.cooldown and self.mp >= 50 and not self.jailed
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
            victims[0].protected_by['Flagger'].append(self)
            self.attacking = victims[1].gamenum
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You attempted to redirect all evil attacks from "
                                   f"{victims[0].screenname} towards {victims[1].screenname}.")
        return []


class FlowerChild(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Flower Child'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (self.mp == 100 and len(victims) == 1 and victims[0].alive and self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0):
                text = (chat_obj.quote_message(messageid) +
                        f"You are currently saving {victims[0].screenname} from being lynched.")
                chat_obj.write_message(text)
                if len(self.acting_upon) > 0:
                    for i in self.acting_upon:
                        i.unlynchable_by.remove(self)
                victims[0].unlynchable_by.append(self)
                self.acting_upon = victims
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only protect one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already used your ability.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
        return []


class Forger(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Forger'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.guns_forged = 0
        self.shields_forged = 0
        self.aura = 'Unknown'
        self.action_used = False
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot weapon

        OR

        Wolfbot shield

        OR

        Wolfbot arm (username)

        The arm command works for whatever item you have finished. 
        You can forge a new item after arming someone in the same night. Do so in a separate post.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'weapon' and isinstance(chat_obj, tc.Chat):
            if (self.guns_forged == 0 and not self.current_thread.open and self.alive and not self.concussed
                    and not self.jailed and len(self.corrupted_by) == 0 and not self.nightmared
                    and self not in self.forger_shields and self not in self.forger_guns):
                text = chat_obj.quote_message(messageid) + f"You will begin forging the gun."
                chat_obj.write_message(text)
            elif self.guns_forged != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You already forged a gun.")
            elif self in self.forger_shields or self in self.forger_guns:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Remember you can't forge a new item unless "
                                                                           "you are also getting rid of the old one.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'shield' and isinstance(chat_obj, tc.Chat):
            if (self.shields_forged <= 1 and not self.current_thread.open and not self.jailed and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                    and self not in self.forger_shields and self not in self.forger_guns):
                text = chat_obj.quote_message(messageid) + f"You will begin forging the shield."
                chat_obj.write_message(text)
            elif self.shields_forged > 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You already forged your shields.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif self in self.forger_shields or self in self.forger_guns:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Remember you can't forge a new item unless "
                                                                           "you are also getting rid of the old one.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'arm' and isinstance(chat_obj, tc.Chat):
            if (self in self.forger_guns and victims[0].alive and not self.jailed and victims[0].gamenum != self.gamenum
                    and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and not self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
                text = chat_obj.quote_message(messageid) + f"You will give the gun to {victims[0].screenname}."
                chat_obj.write_message(text)
            elif (self in self.forger_shields and victims[0].alive and len(victims) == 1
                    and not self.current_thread.open and not self.jailed and victims[0].gamenum != self.gamenum
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
                text = chat_obj.quote_message(messageid) + f"You will give the shield to {victims[0].screenname}."
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only arm one person.")
            elif self not in self.forger_guns and self not in self.forger_shields:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have nothing to give.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'weapon' and isinstance(chat_obj, tc.Chat) and not self.action_used
                and self.guns_forged == 0 and not self.current_thread.open and self.alive and not self.concussed
                and not self.jailed and len(self.corrupted_by) == 0 and not self.nightmared
                and self not in self.forger_shields and self not in self.forger_guns):
            self.action_used = True
            self.guns_forged = self.guns_forged + 1
            self.forger_guns.append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   "You have successfully finished forging a gun.")
        if (keyword == 'shield' and isinstance(chat_obj, tc.Chat) and not self.action_used and
                self.shields_forged <= 1 and not self.current_thread.open and not self.jailed and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and self not in self.forger_shields and self not in self.forger_guns):
            self.action_used = True
            self.shields_forged = self.shields_forged + 1
            self.forger_shields.append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   "You have successfully finished forging a shield.")
            # We have a gun, giftee is alive, one giftee, we haven't given them a gun before
        if (keyword == 'arm' and self in self.forger_guns and victims[0].alive and len(victims) == 1
                and not self.jailed and victims[0].gamenum != self.gamenum and self.alive
                and self not in victims[0].forger_guns and not self.current_thread.open and not self.action_used
                and isinstance(chat_obj, tc.Chat) and not self.concussed and len(self.corrupted_by) == 0
                and not self.nightmared):
            # self.forging_gun = False move to daytime actions
            # more guns to shoot
            victims[0].has_forger_gun = victims[0].has_forger_gun + 1
            # given gun from us, can't have another
            victims[0].forger_guns.append(self)
            # we lose our gun
            self.forger_guns.remove(self)
            text = chat_obj.quote_message(messageid) + f"You gave the gun to {victims[0].screenname}."
            chat_obj.write_message(text)
            victims[0].chat.write_message("You have been gifted a gun by the Forger. Use it by writing:\n\n"
                                          "Wolfbot shoot (username)\n\nanytime during the day. If you already have "
                                          "bullets, you will use this gun first.")
            # We have a shield, giftee is alive, one giftee, we haven't given them a shield before
        if (keyword == 'arm' and self in self.forger_shields and victims[0].alive and len(victims) == 1
                and not self.jailed and victims[0].gamenum != self.gamenum and self.alive
                and self not in victims[0].forger_shields and not self.current_thread.open and not self.action_used
                and isinstance(chat_obj, tc.Chat) and not self.concussed and len(self.corrupted_by) == 0
                and not self.nightmared):
            # self.forging_shield = False move to daytime actions
            # more guns to shoot
            victims[0].has_forger_shield = victims[0].has_forger_shield + 1
            victims[0].protected_by['Forger'].append(self)
            # given shield from us, can't have another
            victims[0].forger_shields.append(self)
            # we lose our shield
            self.forger_shields.remove(self)
            text = chat_obj.quote_message(messageid) + f"You gave the shield to {victims[0].screenname}."
            chat_obj.write_message(text)
            victims[0].chat.write_message("You have been gifted a shield by the Forger. "
                                          "Use is automatic and requires no action from you.")
        return []


class Judge(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Judge'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot judge (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'judge' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.mp >= 50 and victims[0].gamenum != self.gamenum
                    and self.current_thread.open and self.alive and not self.concussed and len(self.corrupted_by) == 0
                    and not self.nightmared and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You will judge {victims[0].screenname} today if the village cannot decide who to lynch.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only judge one person.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have used up your ability.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'judge' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.mp >= 50 and victims[0].gamenum != self.gamenum and self.current_thread.open
                and self.alive and not self.concussed and len(self.corrupted_by) == 0
                and not self.nightmared and not self.jailed):
            self.mp = self.mp-50
            if victims[0].team == 'Village':
                return ['mistrial', self, self]
            else:
                return ['judge', self, victims[0]]
        return []


class Librarian(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Librarian'
        self.acting_upon = [0]
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot mute (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'mute' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum and not self.jailed
                    and not self.current_thread.open and self not in victims[0].muted_by[self.night - 1]
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared):
                text = (chat_obj.quote_message(messageid) +
                        f"You will mute {victims[0].screenname if self.night > 1 else victims[0].noun} tomorrow.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only mute one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif self in victims[0].muted_by[self.night - 1]:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't mute the same person "
                                                                           "consecutively.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'mute' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.jailed and not self.current_thread.open
                and self not in victims[0].muted_by[self.night - 1] and not self.concussed
                and len(self.corrupted_by) == 0 and not self.nightmared):
            self.acting_upon = victims
            victims[0].muted_by[self.night].append(self)
            text = chat_obj.quote_message(messageid) + f"{victims[0].screenname} has been muted."
            chat_obj.write_message(text)
        return []


class Loudmouth(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Loudmouth'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot reveal (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'reveal' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You will reveal {victims[0].screenname if self.night > 1 else victims[0].noun} upon death.")
                chat_obj.write_message(text)
                self.acting_upon = victims
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only reveal one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []


class Marksman(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Marksman'
        self.screenname = screenname
        self.acting_upon = [Player()]
        self.cooldown = False
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot mark (username)

        OR

        Wolfbot shoot (username)

        You can mark someone after shooting someone else in the same night. Do so in a separate post.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'mark' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.mp >= 50 and victims[0].gamenum != self.gamenum
                    and not self.current_thread.open and not self.concussed and len(self.corrupted_by) == 0
                    and not self.nightmared and not self.jailed and self.alive):
                text = (chat_obj.quote_message(messageid) +
                        f"You will mark {victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only mark one person.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of arrows.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'shoot' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.mp >= 50 and self.cooldown is False
                    and victims[0].gamenum == self.acting_upon[0].gamenum and victims[0].gamenum != self.gamenum
                    and not self.current_thread.open and not self.concussed and len(self.corrupted_by) == 0
                    and not self.nightmared and not self.jailed and self.alive):
                text = (chat_obj.quote_message(messageid) +
                        f"You will shoot {victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only mark one person.")
            elif victims[0].gamenum != self.acting_upon[0].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only shoot the person "
                                                                           "you have marked.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of arrows.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'shoot' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.mp >= 50 and self.cooldown is False and victims[0].gamenum == self.acting_upon[0].gamenum
                and victims[0].gamenum != self.gamenum and not self.current_thread.open and not self.concussed
                and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed and self.alive):
            self.mp = self.mp - 50
            if victims[0].mm_killable:
                return ['marksman', self, victims[0]]
            else:
                return ['misfire', victims[0], self]
        if (keyword == 'mark' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.mp >= 50 and victims[0].gamenum != self.gamenum and not self.current_thread.open
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and not self.jailed and self.alive):
            self.cooldown = True
            self.acting_upon = victims[0]
            text = chat_obj.quote_message(messageid) + f"{victims[0].screenname} is now marked."
            chat_obj.write_message(text)
        return []


class Preacher(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Preacher'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'watch' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You will watch {victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only watch one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'vote' and isinstance(chat_obj, tc.Chat):
            if (are_all_alive(victims) and self.current_thread.open and len(victims) <= self.votes
                    and self.current_thread.open and len(self.corrupted_by) == 0 and self not in victims
                    and not self.concussed and len(self.muted_by[self.night - 1]) == 0):
                names = ''
                for name in victims:
                    names = names + f"{name.screenname}\n"
                text = (chat_obj.quote_message(messageid) +
                        "Your extra votes are for: \n" + names)
                chat_obj.write_message(text)
            elif len(victims) > self.votes:
                self.chat.write_message("You are voting more people than you have votes.")
            elif not are_all_alive(victims):
                self.chat.write_message("Your are voting for a dead person.")
            elif self in victims:
                self.chat.write_message("You can't vote yourself.")
            elif not self.current_thread.open:
                self.chat.write_message("You can only vote during the day.")
            elif self.concussed:
                self.chat.write_message("You are concussed and cannot vote.")
            elif len(self.corrupted_by) != 0:
                self.chat.write_message("You are corrupted and cannot vote.")
            elif len(self.muted_by[self.night - 1]) != 0:
                self.chat.write_message("You are muted and cannot vote.")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'watch' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            self.acting_upon = victims
            victims[0].preacher_watched_by.append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"You watched {victims[0].screenname} tonight.")
        if (keyword == 'vote' and isinstance(chat_obj, tc.Chat) and are_all_alive(victims) and self.current_thread.open
                and len(victims) <= self.votes and self.current_thread.open and len(self.corrupted_by) == 0
                and self not in victims and not self.concussed and len(self.muted_by[self.night - 1]) == 0):
            return ['vote', victims]
        return []

    def get_shadow_vote(self, messageid, keyword, voted, chat_obj, end=False):
        if keyword == 'vote' and isinstance(chat_obj, tc.Chat):
            if not end:
                if (are_all_alive(voted) and self.current_thread.open and len(voted) <= self.votes
                        and self.current_thread.open and len(self.corrupted_by) == 0 and self not in voted
                        and not self.concussed and len(self.muted_by[self.night - 1]) == 0):
                    names = ''
                    for name in voted:
                        names = names + f"{name.screenname}\n"
                    text = (chat_obj.quote_message(messageid) +
                            f"Your vote{'s are' if len(voted) > 1 else ' is'} for: \n" + names)
                    chat_obj.write_message(text)
                elif len(voted) > self.votes:
                    self.chat.write_message("You are voting more people than you have votes.")
                elif not are_all_alive(voted):
                    self.chat.write_message("Your are voting for a dead person.")
                elif self in voted:
                    self.chat.write_message("You can't vote yourself.")
                elif not self.current_thread.open:
                    self.chat.write_message("You can only vote during the day.")
                elif self.concussed:
                    self.chat.write_message("You are concussed and cannot vote.")
                elif len(self.corrupted_by) != 0:
                    self.chat.write_message("You are corrupted and cannot vote.")
                elif len(self.muted_by[self.night - 1]) != 0:
                    self.chat.write_message("You are muted and cannot vote.")
            else:
                if (are_all_alive(voted) and self.current_thread.open and len(voted) <= self.votes
                        and self.current_thread.open and len(self.corrupted_by) == 0 and self not in voted
                        and not self.concussed and len(self.muted_by[self.night - 1]) == 0):
                    return [voted]
        return []


class Priest(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Priest'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]in the day thread[/b]:

        Wolfbot water (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting one person, have used water, victim is alive
        if keyword == 'water' and isinstance(chat_obj, tc.Thread):
            if (len(victims) == 1 and self.mp == 100 and victims[0].alive
                    and victims[0].gamenum != self.gamenum and self.current_thread.open
                    and isinstance(chat_obj, tc.Thread) and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0):
                self.mp = self.mp - 100
                if victims[0].waterable:
                    return ['water', self, victims[0]]
                else:
                    return ['drowned', victims[0], self]
            elif len(victims) != 1:
                self.chat.write_message(self.chat.quote_message(messageid) + "You can only water one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of water.")
            elif not victims[0].alive:
                self.chat.write_message(self.chat.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                self.chat.write_message(self.chat.quote_message(messageid) + "You can't target yourself.")
            elif not self.current_thread.open:
                self.chat.write_message(self.chat.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                self.chat.write_message(self.chat.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                self.chat.write_message(self.chat.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                self.chat.write_message(self.chat.quote_message(messageid) + "You are corrupted and cannot act.")
        return []


class RedLady(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Red Lady'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot visit (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'visit' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You will visit {victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only visit one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'visit' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            victims[0].visited.append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You visited {victims[0].screenname} last night.")
            if victims[0].is_killer:
                return ['evilvisit', victims[0], self]
        return []


class Sheriff(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Sheriff'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'watch' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You will watch {victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only watch one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'watch' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            self.acting_upon = victims
            victims[0].sheriff_watched_by.append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"You watched {victims[0].screenname} tonight.")
            if len(victims[0].infected_by) > 0:
                self.infected_by = victims[0].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
        return []


class SeerApprentice(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Seer Apprentice'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer_apprentice = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''


class SpiritSeer(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Spirit Seer'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username) and (username)

        You may select only one player instead of two if you wish.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'watch' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and victims[0].gamenum != self.gamenum
                    and victims[1].gamenum != self.gamenum and are_all_alive(victims) and
                    victims[0].gamenum != victims[1].gamenum and not self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0
                    and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are checking "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" and {victims[1].screenname if self.night > 1 else victims[1].noun}"
                                       f" at the end of the night.")
            if keyword == 'watch' and isinstance(chat_obj, tc.Chat):
                if (len(victims) == 1 and victims[0].gamenum != self.gamenum and victims[0].alive
                        and not self.current_thread.open and self.alive and not self.concussed
                        and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                    chat_obj.write_message(chat_obj.quote_message(messageid) +
                                           f"You are checking {victims[0].screenname} at the end of the night.")
            elif len(victims) != 1 and len(victims) != 2:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only check one  or two people.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")

        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if len(victims) == 2:
            if victims[1].alive is False:
                del victims[1]
            if victims[0].alive is False:
                del victims[0]
        if (keyword == 'watch' and isinstance(chat_obj, tc.Chat) and len(victims) == 2 and
                victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and are_all_alive(victims) and victims[0].gamenum != victims[1].gamenum
                and not self.current_thread.open and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            if victims[0].has_killed is False and victims[1].has_killed is False:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and {victims[1].screenname} are [b]Blue[/b]. "
                                       f"Neither player killed anyone last night.")
            else:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and {victims[1].screenname} are [b]Red[/b]. "
                                       f"One or both players killed someone last night.")
            if len(victims[0].infected_by) > 0:
                self.infected_by = victims[0].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
            if len(victims[1].infected_by) > 0:
                self.infected_by = victims[1].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
        if (keyword == 'watch' and isinstance(chat_obj, tc.Chat) and len(victims) == 1
                and victims[0].gamenum != self.gamenum and victims[0].alive and not self.current_thread.open
                and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and not self.jailed):
            if victims[0].has_killed is False:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} is [b]Blue[/b]. "
                                       f"They did not kill anyone last night.")
            else:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} are [b]Red[/b]. "
                                       f"They killed someone last night.")
            if len(victims[0].infected_by) > 0:
                self.infected_by = victims[0].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
        return []


class ToughGuy(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Tough Guy'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.shield = True
        self.triggered = False
        self.protected_by['Tough Guy'] = [self]
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and isinstance(chat_obj, tc.Chat)
                    and victims[0].gamenum != self.gamenum and not self.current_thread.open and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will protect "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only protect one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'protect' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and isinstance(chat_obj, tc.Chat) and victims[0].gamenum != self.gamenum
                and not self.current_thread.open and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            victims[0].protected_by['Tough Guy'].append(self)
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You attempted to protect {victims[0].screenname} last night.")
        return []


class Violinist(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Violinist'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'check' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and victims[0].alive and victims[0].gamenum != self.gamenum
                    and not self.current_thread.open and victims[1].screenname != '' and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will check "
                                       f"{victims[0].screenname} against {victims[1].screenname} tonight")
            elif victims[1].screenname == '':
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"Nobody has died since last night to compare with.")
            elif len(victims) != 2:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only check one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")

        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        # Only works if they are targeting one person, haven't checked yet,
        # people are alive, and they aren't checking themselves
        if (keyword == 'check' and isinstance(chat_obj, tc.Chat) and len(victims) == 2 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open
                and victims[1].screenname != '' and self.alive and not self.concussed and len(self.corrupted_by) == 0
                and not self.nightmared and not self.jailed):
            if victims[0].apparent_team == victims[1].team:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} appears to be mourning the death of "
                                       f"{victims[1].screenname}. "
                                       f"They are on the [b]same team[/b].")
            else:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} is not mourning the death of {victims[1].screenname}. "
                                       f"They are on [b]different teams[/b].")
            if len(victims[0].infected_by) > 0:
                self.infected_by = victims[0].infected_by.copy()
                self.chat.write_message(
                    f"You have been infected and will die at the end of the day if the Infector is not killed.")
        elif keyword == 'check' and victims[1].screenname == '':
            chat_obj.write_message(f"Nobody has died, so no info tonight.")
        return []


class Witch(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Witch'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.has_protect_potion = True
        self.has_kill_potion = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)

        OR

        Wolfbot poison (username)

        You can do both in the same night using the same or separate posts.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                    and self.has_protect_potion and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You will attempt to protect "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} tonight")
        elif len(victims) != 1:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only protect one person.")
        elif not self.has_protect_potion:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of protect potions.")
        elif not victims[0].alive:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
        elif victims[0].gamenum == self.gamenum:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
        elif self.current_thread.open:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
        elif not self.alive:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
        elif self.concussed:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
        elif len(self.corrupted_by) != 0:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
        elif self.nightmared:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
        elif self.jailed:
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                       f"actions. If you are somehow unjailed, "
                                                                       f"this action will be performed")
        if keyword == 'poison' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                    and self.has_kill_potion and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will kill {victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" tonight")
        elif len(victims) != 1:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only poison one person.")
        elif not self.has_kill_potion:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of rocks.")
        elif not victims[0].alive:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
        elif victims[0].gamenum == self.gamenum:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
        elif self.current_thread.open:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
        elif not self.alive:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
        elif self.concussed:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
        elif len(self.corrupted_by) != 0:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
        elif self.nightmared:
            chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
        elif self.jailed:
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                       f"actions. If you are somehow unjailed, "
                                                                       f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'protect' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and self.has_protect_potion and not self.current_thread.open
                and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and not self.jailed):
            victims[0].protected_by['Witch'].append(self)
        if (keyword == 'poison' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and self.has_kill_potion and not self.current_thread.open
                and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and not self.jailed):
            self.has_kill_potion = False
            return ['witch', self, victims[0]]
        return []


# Wolves
class WolfAvenger(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Wolf Avenger'
        self.aura = 'Evil'
        self.wolf_order = 1
        self.wolf_voting_power = 1
        self.team = 'Wolf'
        self.is_killer = True
        self.hhtargetable = False
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot tag (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'tag' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are currently avenging upon "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}.")
                self.acting_upon = victims
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only tag one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []


class Werewolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Werewolf'
        self.aura = 'Evil'
        self.wolf_order = 2
        self.wolf_voting_power = 1
        self.wolf_targetable = False
        self.is_killer = True
        self.conjuror_can_take = False
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''


class ShamanWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Shaman Wolf'
        self.aura = 'Evil'
        self.wolf_order = 3
        self.wolf_voting_power = 1
        self.wolf_targetable = False
        self.is_killer = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time [b]during the day[/b] by posting [b]here[/b]:

        Wolfbot shaman (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'shaman' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and not self.is_last_evil
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will enchant "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only shaman one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.is_last_evil:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't shaman if you are "
                                                                           "the only remaining wolf.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'shaman' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].wolf_targetable and not self.is_last_evil and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.jailed):
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"{victims[0].screenname} has been enchanted.")
            victims[0].shamaned_by.append(self.gamenum)
        return []


class BerserkWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Berserk Wolf'
        self.aura = 'Evil'
        self.wolf_order = 4
        self.wolf_voting_power = 1
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.is_killer = True
        self.berserking = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot berserk'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'berserk' and isinstance(chat_obj, tc.Chat):
            if (self.mp == 100 and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.jailed):
                text = chat_obj.quote_message(messageid) + r"Berserk will be activated tonight. "
                if len(victims) > 0:
                    text = text + (f"You will need to vote "
                                   f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                   f" in the normal wolf vote.")
                chat_obj.write_message(text)
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already used berserk.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'berserk' and isinstance(chat_obj, tc.Chat) and self.mp == 100 and not self.current_thread.open
                and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed):
            self.mp = self.mp - 100
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"The Werewolf Berserk is active.")
            self.berserking = True
            if victims[0].screenname == 'shortkut' and isinstance(chat_obj, tc.Chat):
                chat_obj.write_message(f"Wolfbot approves of your desire to murder shortkut, "
                                       f"but the normal wolf vote must be used.")
        return []


class NightmareWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Nightmare Wolf'
        self.aura = 'Evil'
        self.wolf_order = 5
        self.wolf_voting_power = 1
        self.wolf_targetable = False
        self.is_killer = True
        self.conjuror_can_take = False
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot nightmare (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'nightmare' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed
                    and self.mp >= 50):
                self.mp -= 50
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will nightmare {victims[0].screenname} tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only nightmare one person.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of nightmares.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'nightmare' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].wolf_targetable and self.current_thread.open and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.jailed and self.mp >= 50):
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"{victims[0].screenname} has been nightmared.")
            victims[0].nightmared = True
        return []


class VoodooWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Voodoo Wolf'
        self.aura = 'Evil'
        self.wolf_order = 6
        self.wolf_voting_power = 1
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.is_killer = True
        self.acting_upon = [Player()]
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot mute (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'mute' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and not self.current_thread.open
                    and self not in victims[0].muted_by[self.night - 1] and self.alive and not self.concussed and
                    len(self.corrupted_by) == 0 and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You will mute {victims[0].screenname if self.night > 1 else victims[0].noun} tomorrow.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only mute one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self in victims[0].muted_by[self.night - 1]:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You cannot mute someone in "
                                                                           "consecutive nights.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'mute' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and victims[0].wolf_targetable and not self.current_thread.open
                and self not in victims[0].muted_by[self.night - 1] and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.jailed):
            self.acting_upon = victims
            victims[0].muted_by[self.night].append(self)
            text = chat_obj.quote_message(messageid) + f"{victims[0].screenname} has been muted."
            chat_obj.write_message(text)
        return []


class GuardianWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Guardian Wolf'
        self.aura = 'Evil'
        self.wolf_order = 7
        self.wolf_voting_power = 1
        self.screenname = screenname
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (self.mp == 100 and len(victims) == 1 and victims[0].alive and self.current_thread.open and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You are currently saving {victims[0].screenname} from being lynched.")
                if len(self.acting_upon) > 0:
                    for i in self.acting_upon:
                        i.unlynchable_by.remove(self)
                victims[0].unlynchable_by.append(self)
                self.acting_upon = victims
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only protect one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already used your ability.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []


class WolfTrickster(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Wolf Trickster'
        self.aura = 'Evil'
        self.wolf_order = 8
        self.wolf_voting_power = 1
        self.screenname = screenname
        self.conjuror_can_take = False
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.wolf_targetable = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot trick (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'trick' and isinstance(chat_obj, tc.Chat):
            if (self.mp == 100 and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You are currently tricking {victims[0].screenname if self.night > 1 else victims[0].noun}.")
                chat_obj.write_message(text)
                if len(self.acting_upon) > 0:
                    for i in self.acting_upon:
                        i.tricked_by.remove(self)
                victims[0].tricked_by.append(self)
                self.acting_upon = victims
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only trick one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already used your ability.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []


class ConfusionWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Confusion Wolf'
        self.aura = 'Evil'
        self.wolf_order = 9
        self.wolf_voting_power = 1
        self.wolf_targetable = False
        self.is_killer = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.conjuror_can_take = False
        self.hhtargetable = False
        self.waterable = True
        self.confusion = False
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot confusion'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'confusion' and isinstance(chat_obj, tc.Chat):
            if (self.mp >= 50 and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.jailed):
                text = chat_obj.quote_message(messageid) + r"Confusion will be activated tonight."
                if len(victims) == 1:
                    text = text + (f"You will need to vote "
                                   f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                   f" in the normal wolf vote.")
                chat_obj.write_message(text)
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of uses.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'confusion' and isinstance(chat_obj, tc.Chat) and self.mp >= 50
                and not self.current_thread.open and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.jailed):
            chat_obj.write_message(chat_obj.quote_message(messageid) + f"Wolf Confusion is active.")
            self.confusion = True
            self.mp = self.mp - 50
        if victims[0].screenname == 'shortkut' and isinstance(chat_obj, tc.Chat):
            chat_obj.write_message(f"Wolfbot approves of your desire to murder shortkut, "
                                   f"but the normal wolf vote must be used.")
        return []


class ShadowWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Shadow Wolf'
        self.aura = 'Evil'
        self.wolf_order = 10
        self.wolf_voting_power = 1
        self.screenname = screenname
        self.gamenum = gamenum
        self.shadow = True
        self.noun = noun
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.is_killer = True
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot shadow'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'shadow' and isinstance(chat_obj, tc.Chat):
            if (self.mp == 100 and self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.jailed):
                text = chat_obj.quote_message(messageid) + r"Shadow has been activated."
                self.mp = self.mp - 100
                self.current_thread.delete_poll()
                self.current_thread.write_message("[b]Today's voting has been manipulated by the Shadow Wolf.[/b]")
                self.shadow = False
                self.current_thread.post_shadow()
                if len(victims) == 1:
                    text = text + (f" You will need to vote {victims[0].screenname} "
                                   f"in the normal wolf vote. Reminder that Wolf Chat is closed.")
                chat_obj.write_message(text)
                return ['shadow']
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have used your ability.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []


class JellyWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Jelly Wolf'
        self.aura = 'Evil'
        self.wolf_order = 11
        self.wolf_voting_power = 1
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.screenname = screenname
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.acting_upon = []
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'protect' and isinstance(chat_obj, tc.Chat):
            if (self.mp == 100 and len(victims) == 1 and victims[0].alive and not self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed):
                text = (chat_obj.quote_message(messageid) +
                        f"You will attempt to place jelly on "
                        f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                        f" tonight.")
                chat_obj.write_message(text)
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only protect one person.")
            elif self.mp < 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of jelly.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'protect' and isinstance(chat_obj, tc.Chat) and self.mp == 100 and len(victims) == 1
                and victims[0].alive and not self.current_thread.open and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.jailed):
            victims[0].jellied_by.append(self)
            self.acting_upon = victims
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You placed protective jelly on {victims[0].screenname} last night.")
        return []


class ToxicWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Toxic Wolf'
        self.aura = 'Evil'
        self.wolf_order = 12
        self.wolf_voting_power = 1
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.screenname = screenname
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot poison (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'poison' and isinstance(chat_obj, tc.Chat):
            if (self.mp >= 50 and len(victims) == 1 and victims[0].alive and victims[0].poisoned is False
                    and self.current_thread.open and self.alive and not self.concussed and len(self.corrupted_by) == 0
                    and not self.jailed):
                self.mp = self.mp - 50
                victims[0].poisoned = True
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"{victims[0].screenname} has "
                                                                           f"been poisoned.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only poison one person.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are out of rocks.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].poisoned:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "They are already poisoned.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []


class WolfScribe(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Wolf Scribe'
        self.aura = 'Evil'
        self.wolf_order = 13
        self.wolf_voting_power = 1
        self.is_killer = True
        self.wolf_targetable = False
        self.screenname = screenname
        self.conjuror_can_take = False
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time by posting [b]here[/b]:

        Wolfbot scribe (username) by (method) as (role)
        OR
        Wolfbot scribe (username) as (role) by (method)

        The role attribute and method attribute are each optional, but one must be present. You can use either:
        
        Wolfbot scribe (username) as (role)
        OR
        Wolfbot scribe (username) by (method)
        
        The bot needs the roles to have no spacing. You can see the list of accepted roles by posting:
        
        Wolfbot roles
        
        You can see a list of death methods by posting:

        Wolfbot deaths
        '''

    def phased_action(self, messageid, keyword, victims, chat_obj):
        methods = [x.lower() for x in kill_methods()['keyword']]
        deaths = kill_methods()['Cause of Death']
        classes = [x.lower() for x in class_list()['keyword']]
        names = class_list()['Role Name']
        if keyword == 'scribe' and isinstance(chat_obj, tc.Chat):
            if (self.mp >= 50 and len(victims) == 3 and isinstance(victims[0], Player) and not self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.jailed
                    and victims[0].alive):
                if victims[1].lower() in methods and victims[2].lower() in classes:
                    ind = classes.index(victims[2].lower())
                    ind2 = methods.index(victims[1].lower())
                    text = (chat_obj.quote_message(messageid) +
                            (f"If {victims[0].screenname if self.night > 1 else victims[0].noun}"
                             f" dies, they will be shown as having been [b]{deaths[ind2]}[/b]. "
                             f"They will also be revealed as the [b]{names[ind]}[/b]."))
                    chat_obj.write_message(text)
                    if len(self.acting_upon) > 0:
                        for i in self.acting_upon:
                            delindex = i.scribed_by.index(self)
                            del i.scribed_by[delindex]
                            del i.scribe_method[delindex]
                    self.acting_upon = [victims[0]]
                    victims[0].scribe_method.append([victims[1], names[ind]])
                    victims[0].scribed_by.append(self)
                elif victims[2].lower() in methods and victims[1].lower() in classes:
                    ind = classes.index(victims[1].lower())
                    ind2 = methods.index(victims[2].lower())
                    text = (chat_obj.quote_message(messageid) +
                            (f"If {victims[0].screenname if self.night > 1 else victims[0].noun}"
                             f" dies, they will be shown as having been [b]{deaths[ind2]}[/b]. "
                             f"They will also be revealed as the [b]{names[ind]}[/b]."))
                    chat_obj.write_message(text)
                    if len(self.acting_upon) > 0:
                        for i in self.acting_upon:
                            delindex = i.scribed_by.index(self)
                            del i.scribed_by[delindex]
                            del i.scribe_method[delindex]
                    self.acting_upon = [victims[0]]
                    victims[0].scribe_method.append([names[ind], victims[1]])
                    victims[0].scribed_by.append(self)
            elif (self.mp >= 50 and len(victims) == 2 and isinstance(victims[0], Player)
                  and not self.current_thread.open and self.alive and not self.concussed
                  and len(self.corrupted_by) == 0 and not self.jailed and victims[0].alive):
                if victims[1].lower() in methods:
                    ind2 = methods.index(victims[1].lower())
                    text = (chat_obj.quote_message(messageid) +
                            (f"If {victims[0].screenname if self.night > 1 else victims[0].noun}"
                             f" dies, they will be shown as having been [b]{deaths[ind2]}[/b]. "
                             f"They will also be revealed as their normal role."))
                    chat_obj.write_message(text)
                    if len(self.acting_upon) > 0:
                        for i in self.acting_upon:
                            delindex = i.scribed_by.index(self)
                            del i.scribed_by[delindex]
                            del i.scribe_method[delindex]
                    self.acting_upon = [victims[0]]
                    victims[0].scribe_method.append([victims[1], ''])
                    victims[0].scribed_by.append(self)
                elif victims[1].lower() in classes:
                    ind = classes.index(victims[1].lower())
                    text = (chat_obj.quote_message(messageid) +
                            (f"If {victims[0].screenname if self.night > 1 else victims[0].noun}"
                             f" dies, they will be shown as being killed normally. "
                             f"They will also be revealed as the [b]{names[ind]}[/b]."))
                    chat_obj.write_message(text)
                    if len(self.acting_upon) > 0:
                        for i in self.acting_upon:
                            delindex = i.scribed_by.index(self)
                            del i.scribed_by[delindex]
                            del i.scribe_method[delindex]
                    self.acting_upon = [victims[0]]
                    victims[0].scribe_method.append(['', names[ind]])
                    victims[0].scribed_by.append(self)
            elif (len(victims) != 2 and len(victims) != 3) or not isinstance(victims[0], Player):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Reformat your request, you must change "
                                                                           "either a role or death method.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have used up your ability.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'deaths' and isinstance(chat_obj, tc.Chat):
            chat_obj.write_message(chat_obj.quote_message(messageid) + print_kill_methods())
        if keyword == 'roles' and isinstance(chat_obj, tc.Chat):
            chat_obj.write_message(chat_obj.quote_message(messageid) + print_roles())
        return []


class AlphaWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Alpha Wolf'
        self.extra_life = True
        self.aura = 'Unknown'
        self.wolf_order = 14
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.is_killer = True
        self.wolf_voting_power = 100
        self.wolf_targetable = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''


class BlindWolf(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Blind Wolf'
        self.aura = 'Evil'
        self.wolf_order = 15
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.is_killer = True
        self.wolf_targetable = False
        self.hhtargetable = False
        self.conjuror_can_take = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username) and (username)

        You can check only one person if you like.

        You can resign your powers at any time by posting [b]here[/b]:

        Wolfbot resign'''
        
    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'check' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and are_all_alive(victims) and victims[0].wolf_targetable
                    and victims[1].wolf_targetable and self.checked < 2 and not self.resigned
                    and not self.current_thread.open and not self.concussed
                    and self.alive and len(self.corrupted_by) == 0 and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"is the {victims[0].category}. "
                                       f"{victims[1].screenname if self.night > 1 else victims[1].noun} "
                                       f"is the {victims[1].category}.")
                self.checked = 2
                if len(victims[0].infected_by) > 0:
                    self.infected_by = victims[0].infected_by.copy()
                    self.chat.write_message(
                        f"You have been infected and will die at the end of the day if the Infector is not killed.")
                if len(victims[1].infected_by) > 0:
                    self.infected_by = victims[1].infected_by.copy()
                    self.chat.write_message(
                        f"You have been infected and will die at the end of the day if the Infector is not killed.")
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and self.checked < 2
                    and not self.resigned and not self.current_thread.open and not self.jailed and not self.concussed
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" is the {victims[0].category}.")
                self.checked = self.checked + 1
                if len(victims[0].infected_by) > 0:
                    self.infected_by = victims[0].infected_by.copy()
                    self.chat.write_message(
                        f"You have been infected and will die at the end of the day if the Infector is not killed.")
            elif len(victims) != 1 and len(victims) != 2:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only check one or two people.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "One of your targets is dead.")
            elif not victims[0].wolf_targetable or not victims[1].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.checked >= 2:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already checked tonight.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.resigned:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already resigned your powers.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'resign' and isinstance(chat_obj, tc.Chat) and not self.resigned:
            self.chat.write_message(f"You have resigned your powers.")
            self.resigned = True
            self.wolf_voting_power = 1
        return []


class WolfSeer(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Wolf Seer'
        self.aura = 'Evil'
        self.wolf_order = 16
        self.screenname = screenname
        self.conjuror_can_take = False
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.wolf_targetable = False
        self.is_killer = True
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)

        You can resign your powers at any time by posting [b]here[/b]:

        Wolfbot resign'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'check' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and self.checked == 0
                    and not self.resigned and not self.current_thread.open and not self.concussed
                    and self.alive and len(self.corrupted_by) == 0 and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" is the {victims[0].role}.")
                self.checked = self.checked + 1
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only check one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.checked != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already checked today.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.resigned:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already resigned your ability.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'resign' and isinstance(chat_obj, tc.Chat) and not self.resigned:
            self.chat.write_message(f"You have resigned your powers.")
            self.resigned = True
            self.wolf_voting_power = 1
        return []


class Sorcerer(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Sorcerer'
        self.aura = 'Evil'
        self.team = 'Wolf'
        self.apparent_team = 'Village'
        self.apparent_aura = 'Good'
        self.conjuror_can_take = False
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.wolf_targetable = False
        self.mm_killable = True
        self.category = 'Werewolf'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)

        During the day, you can reveal a player by posting [b]here[/b]:

        Wolfbot reveal (username)

        You can resign your powers at any time by posting [b]here[/b]:

        Wolfbot resign'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'check' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and self.checked == 0
                    and not self.resigned and not self.current_thread.open and not self.concussed and self.alive
                    and len(self.corrupted_by) == 0 and not self.jailed):
                self.chat.write_message(f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                        f" is the {victims[0].role}.")
                self.checked = self.checked + 1
                self.seen.append(victims[0])
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only check one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.checked != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already checked today.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.resigned:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already resigned your powers.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'reveal' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and self.mp >= 50
                    and not self.resigned and self.current_thread.open and not self.concussed
                    and victims[0] in self.seen and self.alive and len(self.corrupted_by) == 0 and not self.jailed):
                self.mp -= 50
                return ['reveal', victims[0]]
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only reveal one person.")
            elif self.mp < 50:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have used up your ability to reveal.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif not victims[0].wolf_targetable:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target a wolf.")
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.resigned:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have already resigned your powers.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif victims[0] not in self.seen:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only reveal people "
                                                                           "you have checked.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'resign' and isinstance(chat_obj, tc.Chat) and not self.resigned:
            self.chat.write_message(f"You have resigned your powers and may participate in wolf chat.")
            self.resigned = True
            self.wolf_voting_power = 1
        return []


class WerewolfFan(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Werewolf Fan'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.category = 'Wildcard'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot reveal (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'reveal' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.alive and not self.concussed
                    and victims[0].gamenum == self.gamenum and len(self.corrupted_by) == 0 and not self.nightmared
                    and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will reveal your role to "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"at the start of the next night.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only reveal to one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'reveal' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.alive and not self.concussed and victims[0].gamenum == self.gamenum
                and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            victims[0].chat.write_message(f"{self.screenname} has shown you their role. They are the {self.role}.")
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You have revealed your role to {victims[0].screenname}.")
        return []


# Solos
class Cupid(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Cupid'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.category = 'Wildcard'
        self.can_couple = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the first night by posting [b]here[/b]:

        Wolfbot couple (username) and (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'couple' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and victims[1].gamenum != victims[0].gamenum and self.night == 1
                    and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum and self.alive):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will attempt to couple {victims[0].screenname} "
                                       f"and {victims[0].screenname}.")
            elif len(victims) != 2 or victims[1].gamenum != victims[0].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You must only couple two different people.")
            elif victims[0].gamenum == self.gamenum or victims[1].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if len(victims) == 2:
            if victims[1].alive is False:
                del victims[1]
            if victims[0].alive is False:
                del victims[0]
        if (keyword == 'couple' and len(victims) == 2 and are_all_alive(victims) and isinstance(chat_obj, tc.Chat)
                and victims[1].gamenum != victims[0].gamenum and self.night == 1
                and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum):
            victims[0].coupled = True
            victims[1].coupled = True
        if (keyword == 'couple' and len(victims) == 1 and are_all_alive(victims) and isinstance(chat_obj, tc.Chat)
                and self.night == 1 and self.gamenum != victims[0].gamenum):
            victims[0].coupled = True
        return []


class Fool(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Fool'
        self.team = 'Fool'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Wildcard'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''


class Headhunter(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Headhunter'
        self.team = 'Headhunter'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.aura = 'Unknown'
        self.conjuror_can_take = False
        self.mm_killable = True
        self.target_name = ''
        self.category = 'Wildcard'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Your target is {self.target_name}. Good luck!'''


# Solo Killers
class Alchemist(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Alchemist'
        self.team = 'Alchemist'
        self.screenname = screenname
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot kill (username)

        OR

        Wolfbot potion (username)

        'kill' gives the black potion. 'potion' gives the red potion. 
        You may give one, both, or neither potion in one post or separate posts.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'kill' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will give the black potion to "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only use one "
                                                                           "potion per one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'potion' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will give the red potion to "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only use one "
                                                                           "potion per one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'kill' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.gamenum != victims[0].gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            victims[0].black_potion = True
            victims[0].chat.write_message("You've received a potion! "
                                          "You can't tell what color it is...you might die today.")
        if (keyword == 'potion' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.gamenum != victims[0].gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            victims[0].red_potion = victims[0].red_potion + 1
            victims[0].chat.write_message("You've received a potion! "
                                          "You can't tell what color it is...you might die today.")
        return []


class Arsonist(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Arsonist'
        self.screenname = screenname
        self.conjuror_can_take = False
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Arsonist'
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.mm_killable = True
        self.action_used = False
        self.category = 'Solo Killer'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot douse (username) and (username)

        You can douse only one player if you choose. If you choose to burn instead of dousing, use the command:

        Wolfbot kill all'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'kill' and isinstance(chat_obj, tc.Chat):
            if (not self.current_thread.open and len(self.acting_upon) > 0 and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are choosing to burn tonight.")
            elif len(self.acting_upon) == 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You have nobody doused.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'douse' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum
                    and victims[1].gamenum != victims[0].gamenum and not self.current_thread.open and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed
                    and are_all_alive(victims)):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are dousing "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"and {victims[1].screenname if self.night > 1 else victims[1].noun} tonight.")
            elif (len(victims) == 1 and self.gamenum != victims[0].gamenum and not self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                    and not self.jailed and victims[0].alive):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are dousing ONLY "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"tonight.")
            elif len(victims) != 1 and len(victims) != 2:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only douse one or two people.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "One of your targets is dead.")
            elif victims[0].gamenum == self.gamenum or self.gamenum != victims[1].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if len(victims) == 2:
            if victims[1].alive is False:
                del victims[1]
            if victims[0].alive is False:
                del victims[0]
        if (keyword == 'kill' and isinstance(chat_obj, tc.Chat) and not self.current_thread.open
                and len(self.acting_upon) > 0 and self.alive and not self.concussed
                and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            self.action_used = True
            return ['arsonist', self, self.acting_upon]
        if (keyword == 'douse' and isinstance(chat_obj, tc.Chat) and len(victims) == 2
                and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum
                and victims[1].gamenum != victims[0].gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed
                and are_all_alive(victims)):
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You successfully doused {victims[0].screenname} and {victims[1].screenname}.")
            self.acting_upon.extend([victims[0], victims[1]])
            victims[0].doused_by.append(self)
            victims[1].doused_by.append(self)
            self.action_used = True
        if (keyword == 'douse' and isinstance(chat_obj, tc.Chat) and len(victims) == 1
                and self.gamenum != victims[0].gamenum and not self.current_thread.open
                and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and not self.jailed and victims[0].alive):
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You successfully doused {victims[0].screenname}.")
            self.acting_upon.append(victims[0])
            victims[0].doused_by.append(self)
            self.action_used = True
        return []


class Corruptor(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Corruptor'
        self.team = 'Corruptor'
        self.screenname = screenname
        self.is_killer = True
        self.conjuror_can_take = False
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot corrupt (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'corrupt' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed
                    and not self.current_thread.open and self.gamenum != victims[0].gamenum):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will corrupt "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only attack one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'corrupt' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and not self.jailed and not self.current_thread.open and self.gamenum != victims[0].gamenum):
            victims[0].corrupted_by.append(self)
            self.acting_upon.append(victims[0])
        return []


class CultLeader(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Cult Leader'
        self.team = 'Cult'
        self.screenname = screenname
        self.conjuror_can_take = False
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = self.noun
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.sacrifice_selected = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.can_couple = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot convert (username)

        You can sacrifice a convert to attack another player at night by posting [b]here[/b]:

        Wolfbot sacrifice (username)
        
        Pick your person to kill with
        
        Wolfbot kill (username)

        You can sacrifice someone without attacking anybody. You cannot attack a player without a sacrifice. '''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        self.sacrifice_selected = False
        if keyword == 'convert' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You will attempt to convert "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun} "
                                       f"to the cult tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only convert one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'sacrifice' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed
                    and self.gamenum != victims[0].gamenum and victims[0].cult and not self.current_thread.open):
                self.sacrifice_selected = True
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will sacrifice {victims[0].screenname} tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only convert one person.")
            elif not victims[0].cult:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can sacrifice a cult member.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        if keyword == 'kill' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum
                    and self.sacrifice_selected and not self.current_thread.open and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are using your sacrifice to kill {victims[0].screenname} tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only convert one person.")
            elif victims[0].cult:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't attack a cult member, "
                                                                           "sacrifice them instead.")
            elif not self.sacrifice_selected:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You need to sacrifice a cult member"
                                                                           " to attack another player")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'convert' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and self.gamenum != victims[0].gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            victims[0].cult = True
            victims[0].apparent_team = "Cult"
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You successfully converted {victims[0].screenname} to the cult.")
            victims[0].chat.write_message(f"You have been converted to the cult.")
        elif (keyword == 'sacrifice' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
              and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
              and not self.jailed and self.gamenum != victims[0].gamenum and victims[0].cult
              and not self.current_thread.open):
            return ['sacrificed', self, victims[0]]
        elif (keyword == 'kill' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
              and self.gamenum != victims[0].gamenum and self.sacrifice_selected and not self.current_thread.open
              and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
              and not self.jailed):
            return ['cult', self, victims[0]]
        return []


class EvilDetective(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Evil Detective'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Evil Detective'
        self.is_killer = True
        self.conjuror_can_take = False
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username) and (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'check' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 2 and are_all_alive(victims) and victims[1].gamenum != victims[0].gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will check {victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" and {victims[1].screenname if self.night > 1 else victims[1].noun} tonight.")
            elif len(victims) != 2 or victims[1].gamenum == victims[0].gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You must compare two different players.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "One of your targets is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'check' and isinstance(chat_obj, tc.Chat) and len(victims) == 2 and are_all_alive(victims)
                and victims[1].gamenum != victims[0].gamenum and not self.current_thread.open and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            if victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and "
                                       f"{victims[1].screenname} are on [b]different teams[/b].")
                return ['detective', self, victims[0]]
            elif victims[1].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and "
                                       f"{victims[1].screenname} are on [b]different teams[/b].")
                return ['detective', self, victims[1]]
            elif victims[1].team != victims[0].team:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and "
                                       f"{victims[1].screenname} are on [b]different teams[/b].")
                return ['detective', self, victims]
            else:
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"{victims[0].screenname} and "
                                       f"{victims[1].screenname} are on the [b]same team[/b].")
        return []


class Illusionist(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Illusionist'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.team = 'Illusionist'
        self.is_killer = True
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot disguise (username)

        You can kill at specified times during the day by posting [b]here[/b]:

        Wolfbot kill all'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'kill' and isinstance(chat_obj, tc.Chat):
            if self.current_thread.open and self.alive and not self.concussed and len(self.corrupted_by) == 0:
                return ['illusionist']
            elif not self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only kill during the day.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
        if keyword == 'disguise' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and self.gamenum != victims[0].gamenum and victims[0].alive
                    and self not in victims[0].disguised_by and not self.current_thread.open and self.alive
                    and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You are disguising "
                                       f"{victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only disguise one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self in victims[0].disguised_by:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "This person is already disguised.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'disguise' and isinstance(chat_obj, tc.Chat) and len(victims) == 1
                and self.gamenum != victims[0].gamenum and victims[0].alive and self not in victims[0].disguised_by
                and not self.current_thread.open and self.alive and not self.concussed and len(self.corrupted_by) == 0
                and not self.nightmared and not self.jailed):
            chat_obj.write_message(chat_obj.quote_message(messageid) +
                                   f"You have disguised {victims[0].screenname}.")
            victims[0].disguised_by.append(self)
            self.acting_upon.append(victims[0])
        return []


class Infector(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Infector'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Infector'
        self.aura = 'Unknown'
        self.conjuror_can_take = False
        self.is_killer = True
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot infect (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'infect' and isinstance(chat_obj, tc.Chat):
            if (len(victims) == 1 and victims[0].alive and not self.current_thread.open
                    and self.gamenum != victims[0].gamenum and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will infect {victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" tonight.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only attack one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'infect' and isinstance(chat_obj, tc.Chat) and len(victims) == 1 and victims[0].alive
                and not self.current_thread.open and self.gamenum != victims[0].gamenum and self.alive
                and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
            victims[0].infected_by.append(self)
            victims[0].chat.write_message(
                f"You have been infected and will die at the end of the day if the Infector is not killed.")
            self.acting_upon.append(victims[0])
            return ['infector', self, victims[0]]
        return []


class Instigator(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.role = 'Instigator'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Instigator'
        self.hhtargetable = False
        self.conjuror_can_take = False
        self.instigators_dead = False
        self.mm_killable = True
        self.is_killer = True
        self.category = 'Solo Killer'
        self.can_couple = True
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night if you are by yourself by posting [b]here[/b]:

        Wolfbot kill (username)'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'kill' and isinstance(chat_obj, tc.Chat):
            if (self.instigators_dead and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum
                    and not self.current_thread.open and self.alive and not self.concussed
                    and len(self.corrupted_by) == 0 and not self.nightmared and not self.jailed):
                chat_obj.write_message(chat_obj.quote_message(messageid) +
                                       f"You will kill {victims[0].screenname if self.night > 1 else victims[0].noun}"
                                       f" tonight.")
            elif not self.instigators_dead:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only kill people if the "
                                                                           "Instigator team has died.")
            elif len(victims) != 1:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only attack one person.")
            elif not victims[0].alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "Your target is dead.")
            elif victims[0].gamenum == self.gamenum:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        if (keyword == 'kill' and isinstance(chat_obj, tc.Chat) and self.instigators_dead and len(victims) == 1
                and victims[0].alive and self.gamenum != victims[0].gamenum and not self.current_thread.open
                and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                and not self.jailed):
            return ['instigator', self, victims[0]]
        return []


class SerialKiller(Player):
    def __init__(self, gamenum=0, screenname='', noun=''):
        super().__init__()
        self.wolf_immune = True
        self.role = 'Serial Killer'
        self.mp = 0
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Serial Killer'
        self.conjuror_can_take = False
        self.aura = 'Unknown'
        self.is_killer = True
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. 
        Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot kill (username) and (username) and (username)

        You may kill as many or as few players as you are able.'''

    def immediate_action(self, messageid, keyword, victims, chat_obj):
        if keyword == 'kill' and isinstance(chat_obj, tc.Chat):
            if (len(victims) <= self.mp // 100 and are_all_alive(victims) and not self.current_thread.open
                    and self.alive and not self.concussed and len(self.corrupted_by) == 0 and not self.nightmared
                    and not self.jailed and self not in victims):
                text = chat_obj.quote_message(messageid) + "You will attempt to kill the following players tonight: "
                if self.night == 1:
                    for i in victims:
                        text = text + f"\n{i.noun}"
                else:
                    for i in victims:
                        text = text + f"\n{i.screenname}"
                chat_obj.write_message(text)
            elif len(victims) > self.mp // 100:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You attacking too many people, you have "
                                                                           f"{self.mp // 100} kills remaining.")
            elif len(victims) == 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You aren't attacking anyone.")
            elif not are_all_alive(victims):
                chat_obj.write_message(chat_obj.quote_message(messageid) + "One of your targets is dead.")
            elif self in victims:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can't target yourself.")
            elif self.current_thread.open:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You can only act during the night.")
            elif not self.alive:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are dead.")
            elif self.concussed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are concussed and cannot act.")
            elif len(self.corrupted_by) != 0:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are corrupted and cannot act.")
            elif self.nightmared:
                chat_obj.write_message(chat_obj.quote_message(messageid) + "You are nightmared and cannot act.")
            elif self.jailed:
                chat_obj.write_message(chat_obj.quote_message(messageid) + f"You are jailed and cannot perform night "
                                                                           f"actions. If you are somehow unjailed, "
                                                                           f"this action will be performed")
        return []

    def phased_action(self, messageid, keyword, victims, chat_obj):
        deaths = []
        if (keyword == 'kill' and isinstance(chat_obj, tc.Chat) and len(victims) <= self.mp // 100
                and not self.current_thread.open and self.alive and not self.concussed and len(self.corrupted_by) == 0
                and not self.nightmared and not self.jailed and self not in victims):
            for player in victims:
                if player.alive and player.gamenum != self.gamenum:
                    self.mp = self.mp - 100
                    deaths.append(player)
                    self.has_killed = True
            return ['stabbed', self, deaths]
        return []


def class_list():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    classes = []
    names = []
    for member in clsmembers:
        if member[0] != 'Player':
            classes.append(member[0])
            names.append(member[1]().role)
    return {'keyword': classes, 'Role Name': names}
