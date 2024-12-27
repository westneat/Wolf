import threadcontrol as tc

def are_all_alive(actions):
    for player in actions:
        if player.alive is False:
            return False
    return True

def kill_methods():
    return {"keyword": ["lynched", "rock", "jailer", "prisoner",
                                 "shot", "avenger", "trap", "marksman", "misfire", "water", "drowned", "witch",
                                 "wolf", "berserk", "toxic", "alchemist", "arsonist", "corruptor", "sacrificed",
                                 "cult", "illusionist", "infector", "instigator", "stabbed", "coupled", "breakout",
                        "judge","mistrial","evilvisit","poorvisit","tough"],
                     "Cause of Death": ["Lynched by the village", "Killed by the Bully",
                                        "Shot by the Jailer", "Shot by a fellow prisoner jailed by the Warden",
                                        "Shot by a player",
                                        "Tagged by a dead Avenger", "Killed by a Beast Hunter trap",
                                        "Shot by the Marksman",
                                        "Failed shot by the Marksman", "Killed by the Priest", "Failed Priest attempt",
                                        "Killed by Witch potion", "Killed by the standard Werewolf night kill",
                                        "Killed protecting a player who was targeted by the Berserk Wolf",
                                        "Killed at night by the wolves after being poisoned by the Toxic Wolf",
                                        "Killed by Alchemist potion", "Killed by Arsonist burning",
                                        "Killed by the Corruptor",
                                        "Cult member sacrificed by the Cult Leader", "Killed by the Cult Leader",
                                        "Killed by the Illusionist",
                                        "Killed by the Infector", "Killed by the Instigator",
                                        "Killed by the Serial Killer",
                                        "Took their own life", "Killed by jailed wolves","Killed by Judge",
                                        "Killed by incorrect decision as Judge","Killed as Red Lady visiting a killer",
                                        "Killed as Red Lady visiting a player attacked","Killed by their injuries as Tough Guy"]}

class Player:
    def __init__(self):
        #These are attributes of roles that can apply to many/most players. Defaults are what apply the most often
        self.initial_PM = ''
        self.recurring_PM = ''
        self.alive=True
        self.category = 'Regular Villager'
        self.role = ''
        self.aura = 'Good'
        self.team = 'Village'
        self.mp = 100
        self.screenname = ''
        self.apparent_role = self.role
        self.apparent_team = self.team
        self.apparent_aura = self.aura
        self.last_thread_id = 0
        self.chat = tc.Chat()
        self.current_thread = tc.Thread()
        self.voting_power = 1
        self.is_killer = False
        self.noun = ''
        #Most Solos
        self.solo_kill_attempt = []
        #Werewolves
        self.wolf_targetable = True
        self.waterable = False
        self.wolf_order = 0
        self.wolf_voting_power=0
        #Watched by Bell Ringer
        self.bell_ringer_watched_by = [] # append number of player watching
        #Sheriff watched
        self.sheriff_watched_by = [] # append number of player watching
        #Preacher watched
        self.preacher_watched_by = [] # append number of player watching
        #Arsonist doused
        self.doused_by = []
        #All Solos
        self.wolf_immune = False
        #Illusionist disguised
        self.disguised_by = []
        #Pair Roles
        self.coupled = False
        #Used for role generation
        self.can_couple = False
        #Bully
        self.concussed = False
        self.has_been_concussed = False
        #Nightmare Wolf
        self.nightmared = False
        #Wolf Trickster
        self.tricked_by = []
        #Jelly Wolf
        self.jellied_by = []
        #Voodoo Wolf and Librarian
        self.muted_by = []
        #Conjuror/Medium/Ritualist, also used for role selection
        self.speak_with_dead = False
        #Headhunter
        self.hhtarget = False
        self.hhtargetable = True
        #Corruptor
        self.corrupted_by = []
        #All non-town
        self.mm_killable = False
        #Cult Leader
        self.cult = False
        #Infector
        self.infected_by = []
        self.seen_by = []
        #Instigator
        self.instigated = False
        #All protection roles (for berserk purposes)
        self.protected_by = []
        self.protecting = []
        #Conjuror
        self.conjuror = False
        self.conjuror_can_take = True
        #Jailer/Warden
        self.jailed = False
        self.given_warden_weapon = False
        self.can_jail = False
        self.warden_eligible = True
        #Forger
        self.has_forger_gun = 0 # how many guns they have (multiple forgers)
        self.has_forger_shield = 0
        self.forger_guns = [] #who provided the guns
        self.forger_shields = [] #who provided the shields
        #Alchemist
        self.red_potion = 0
        self.black_potion = False
        #Ritualist
        self.spelled = False
        #Beast Hunter
        self.trapped_by = [] # BH trap
        #Shadow Wolf
        self.shadow = False
        #Wolf Shaman
        self.shamaned_by = []
        self.is_last_evil = False
        #Seer Apprentice
        self.seer = False
        #Spirit Seer
        self.has_killed = False
        #Toxic Wolf
        self.poisoned = False
        #Blind Wolf / Sorcerer / Wolf Seer
        self.resigned = False
        self.checked = 0
        #Flower Child and Guardian Wolf
        self.lynchable = True
        #Wolf Scribe
        self.scribed = ''
        self.scribing = 0

    # These methods all take the keyword and a LIST of role objects to apply them to
    def immediate_action(self, keyword, victims):
        return []

    # These methods all take the keyword and a LIST of role objects to apply them to
    def phased_action(self, keyword, victims):
        return []

# Strong Villagers
class Bully(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.aura = 'Unknown'
        self.role = 'Bully'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot rock (username)'''
        
        #only necessary for some roles, but all need to have the method
        #immediate action happens immediately, phased actions happen at end of day/night
        #FOR ALL DEATHS return method as keyword, killer as role obj, victim as role obj
        #For non deaths, return empty list
    def immediate_action(self, keyword, victims):
        # Only works if they are targeting one person, have thrown 3 or fewer rocks, victim is alive, and they haven't already thrown a rock today
        if (keyword == 'rock' and len(victims) == 1 and self.mp >= 25 and victims[0].alive
                and self.current_thread.thread_id != self.last_thread_id and victims[0].gamenum != self.gamenum
                and self.current_thread.open):
            self.last_thread_id = self.current_thread.thread_id
            self.mp = self.mp - 25
            self.chat.write_message(f"You have successfully hit {victims[0].screenname} with a rock.")
            if victims[0].has_been_concussed:
                return ['rock', self, victims[0]]
#                victims[0].alive = False
#                self.current_thread.write_post(
#                    f'{victims[0].screenname} has been hit by a second rock thrown by the Bully. {self.screenname} is the [b]Bully[/b].' + '\n' + kill_player('rock', victims[0]))
            else:
                victims.concussed = True
                victims.has_been_concussed = True
        return []

class Conjuror(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.speak_with_dead = True
        self.conjuror = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.role = 'Conjuror'
        self.new_role = 0
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot take (username)'''
    def immediate_action(self, keyword, victims):
        # Only works if they are targeting one person, have thrown 3 or fewer rocks, victim is dead, they haven't already taken a role today, and role hasn't been taken yet
        if (keyword == 'take' and len(victims) == 1 and not victims[0].alive and
                self.current_thread.thread_id != self.last_thread_id and victims[0].conjuror_can_take
                and self.current_thread.open):
            self.last_thread_id = self.current_thread.thread_id
            self.new_role = victims[0].gamenum
            self.chat.write_message(f"You have successfully taken {victims[0].screenname}'s role.")
        return []

class Detective(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.role = 'Detective'
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username) and (username)'''
    def immediate_action(self, keyword, victims):
        if (keyword == 'check' and len(victims) == 2 and are_all_alive(victims) and
                victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and victims[0].gamenum != victims[1].gamenum and not self.current_thread.open):
            self.chat.write_message(f"You are checking {victims[0].screenname} and {victims[1].screenname} at the end of the night.")
        return []

    def phased_action(self, keyword, victims):
        #Only works if they are targeting two people, haven't checked yet, people are alive, and they aren't checking themselves
        if (keyword == 'check' and len(victims) == 2 and are_all_alive(victims) and
                victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and victims[0].gamenum != victims[1].gamenum and not self.current_thread.open):
            if victims[0].apparent_team == victims[1].apparent_team:
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are on the [b]same team[/b].")
            else:
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are on [b]different teams[/b].")
            victims[0].seen_by.append(self.gamenum)
            victims[1].seen_by.append(self.gamenum)
        return []

class Gunner(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.aura = 'Unknown'
        self.role = 'Gunner'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]in the day thread[/b]:

        Wolfbot shoot (username)'''

    def immediate_action(self, keyword, victims):
        # Only works if they are targeting one person, have shot 1 or fewer bullets, victim is alive, and they haven't already shot today
        if (keyword == 'shoot' and len(victims) == 1 and self.mp >= 50 and victims[0].alive
                and self.current_thread.thread_id != self.last_thread_id and victims[0].gamenum != self.gamenum
                and self.current_thread.open):
            self.last_thread_id = self.current_thread.thread_id
            self.mp = self.mp - 50
        #    victims[0].alive = False
        #    self.current_thread.write_post(f'{victims[0].screenname} has been shot by the Gunner. {self.screenname} is the [b]Gunner[/b].' + '\n' + kill_player('shot', victims[0]))
            return ['shot', self, victims[0]]
        return []
    
class Jailer(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.aura = 'Unknown'
        self.can_jail = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Jailer'
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot jail (username)

        Once a player is jailed, a separate conversation window will be opened for you to talk to your prisoner. You may shoot your prisoner by posting [b]here[/b]:

        Wolfbot shoot (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'jail' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and self.current_thread.open):
            self.chat.write_message(f"{victims[0].screenname} will be jailed tonight.")
        if (keyword == 'shoot' and len(victims) == 1 and self.mp == 100 and victims[0].alive and victims[0].jailed
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.chat.write_message("Your prisoner will be shot tonight.")
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'jail' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and self.current_thread.open):
            victims[0].jailed = True
            victims[0].protected_by.append(self.gamenum)
            self.protecting = [victims[0].gamenum]
            self.chat.write_message(f"{victims[0].screenname} has been jailed.")
        if (keyword == 'shoot' and len(victims) == 1 and self.mp == 100 and victims[0].alive and victims[0].jailed
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.mp = self.mp - 100
        #    victims[0].alive = False
            return ['jail', self, victims[0]] # kill_player('jail', victims[0])
        return []

class Medium(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.aura = 'Unknown'
        self.speak_with_dead = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Medium'
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot revive (username)'''
    def immediate_action(self, keyword, victims):
        if (keyword == 'revive' and len(victims) == 1 and not victims[0].alive and self.mp == 100
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.chat.write_message(f"{victims[0].screenname} will be revived at the beginning of the day.")
        return []

    def phased_action(self, keyword, victims):
        #Only works if they are targeting one person, have not revived, victim is dead
        if (keyword == 'revive' and len(victims) == 1 and not victims[0].alive
                and self.mp == 100 and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.mp = self.mp - 100
           # victims[0].alive = True #handled in game - BW
#            return f'By some miracle, {victims[0]} has returned to us from the dead.'
        return []

class Ritualist(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.aura = 'Unknown'
        self.speak_with_dead = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Ritualist'
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot spell (username)'''
    def immediate_action(self, keyword, victims):
        if keyword == 'spell' and len(victims) == 1 and victims[0].alive and self.mp == 100:
            self.chat.write_message(f"{victims[0].screenname} has the revival spell cast upon them.")
            victims[0].spelled = True
        return []

class Warden(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.aura = 'Unknown'
        self.can_jail = True
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.role = 'Warden'
        self.category = 'Strong Villager'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot jail (username) and (username)

        Once a player is jailed, a separate conversation window will be opened for you to listen to your prisoners. You may give a prisonera weapon by posting [b]here[/b]:

        Wolfbot arm (username)'''
    def immediate_action(self, keyword, victims):
        if (keyword == 'jail' and len(victims) == 2 and are_all_alive(victims)
                and victims[0].warden_eligible and victims[1].warden_eligible
                and victims[0].gamenum != victims[1].gamenum
                and victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and self.current_thread.open):
            self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} will be jailed tonight.")
            #We put the action in the "check" stage because the players at night need to be notified of getting the weapon immediately.
        if keyword == 'arm' and len(victims) == 1 and victims[0].alive and victims[0].jailed and not self.current_thread.open:
            self.chat.write_message(f"{victims[0].screenname} was given the weapon.")
            victims[0].given_warden_weapon = True
            victims[0].chat.write_message(r'''You have been given a weapon by the Warden. You can use it by typing: 
            
            Wolfbot kill''')
        return []

    def phased_action(self, keyword, victims):
        #Only works if they are targeting two people, victims are alive, and they didn't just jail them
        if (keyword == 'jail' and len(victims) == 2 and are_all_alive(victims)
                and victims[0].warden_eligible and victims[1].warden_eligible
                and victims[0].gamenum != victims[1].gamenum
                and victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and self.current_thread.open):
            victims[0].jailed = True
            victims[1].jailed = True
            victims[0].warden_eligible = False
            victims[1].warden_eligible = False
            victims[0].protected_by.append(self.gamenum)
            self.protecting = [victims[0].gamenum, victims[1].gamenum]
            victims[1].protected_by.append(self.gamenum)
            self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are in jail. Their conversation will be relayed in a separate window.")
        return []

#Regular Villagers
class AuraSeer(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Aura Seer'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)'''
    def immediate_action(self, keyword, victims):
        if (keyword == 'check' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.chat.write_message(f"You are checking {victims[0].screenname} and {victims[1].screenname} at the end of the night.")
        return []

    def phased_action(self, keyword, victims):
        #Only works if they are targeting one person, haven't checked yet, people are alive, and they aren't checking themselves
        if (keyword == 'check' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.chat.write_message(f"{victims[0].screenname} is [b]{victims[0].apparent_aura}[/b].")
            victims[0].seen_by.append(self.gamenum)
        return []

class Avenger(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Avenger'
        self.avenging = 0
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot tag (username)'''
    def immediate_action(self, keyword, victims):
        if keyword == 'tag' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum:
            self.chat.write_message(f"You are currently avenging upon {victims[0].screenname}.")
            self.avenging = victims[0].gamenum
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'tag' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum:
            self.avenging = victims[0].gamenum
        return []

class BeastHunter(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Beast Hunter'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.trap_on = 0
        self.aura = 'Unknown'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot trap (username)'''
        
    def immediate_action(self, keyword, victims):
        if (keyword == 'trap' and len(victims) == 1 and victims[0].alive
                and not self.current_thread.open and victims[0].gamenum not in self.protecting):
            self.chat.write_message(f"Tonight you will move your trap to {victims[0].screenname}.")
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'trap' and len(victims) == 1 and victims[0].alive and not self.current_thread.open
                and victims[0].gamenum not in self.protecting):
            self.trap_on = victims[0].gamenum
            self.protecting = [victims[0].gamenum]
            victims[0].trapped_by.append(self.gamenum)
        return []

class BellRinger(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Bell Ringer'
        self.bell_ringer_pair = []
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username) and (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'watch' and len(victims) == 2 and are_all_alive(victims)
                and victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and victims[0].gamenum != victims[1].gamenum):
            self.chat.write_message(f"You will watch {victims[0].screenname} and {victims[1].screenname} until at least the next night phase.")
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'watch' and len(victims) == 2 and are_all_alive(victims)
                and victims[0].gamenum != self.gamenum and victims[1].gamenum != self.gamenum
                and victims[0].gamenum != victims[1].gamenum):
            victims[0].bell_ringer_watched_by.append(self.gamenum)
            victims[1].bell_ringer_watched_by.append(self.gamenum)
            self.bell_ringer_pair = [victims[0].gamenum, victims[1].gamenum]
        return []

class Bodyguard(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Bodyguard'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.shield = True
        self.protected_by = [self.gamenum]
        self.protecting = [self.gamenum]
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'protect' and len(victims) == 1 and victims[0].alive and not self.current_thread.open:
            self.chat.write_message(f"You will protect {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'protect' and len(victims) == 1 and victims[0].alive and not self.current_thread.open:
            victims[0].protected_by.append(self.gamenum)
            self.protecting = [self.gamenum, victims[0].gamenum]
        return []

class Defender(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Defender'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username) and (username) and (username) and (username) and (username) and (username)

        You can protect fewer by shortening the number of names given.'''

    def immediate_action(self, keyword, victims):
        if keyword == 'protect' and len(victims) <= self.mp // 16 and are_all_alive(victims) and not self.current_thread.open:
            text = "You will protect the following players tonight: "
            for i in victims:
                text = text + f"\n{i.screenname}"
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'protect' and len(victims) <= self.mp // 16 and are_all_alive(victims) and not self.current_thread.open:
            text = "You attempted to protect the following players tonight: "
            self.protecting = []
            for player in victims:
                player.protected_by.append(self.gamenum)
                self.protecting.append(player.gamenum)
                text = text + f"\n{player.screenname}"
            self.mp = self.mp - 16*len(victims)
        return []

class Doctor(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Doctor'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'protect' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            text = f"You will protect {victims[0].screenname} tonight."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'protect' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            victims[0].protected_by.append(self.gamenum)
            self.protecting = [victims[0].gamenum]
            self.chat.write_message(f"You attempted to protect {victims[0].screenname} tonight.")
        return []

class Farmer(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Farmer'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''

class Flagger(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Flagger'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.attacking = 0
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot redirect (username) to (username)'''

    #think about how to handle if target dead same night
    def immediate_action(self, keyword, victims):
        if (keyword == 'redirect' and len(victims) == 2 and are_all_alive(victims)
                and victims[0].gamenum != victims[1].gamenum and not self.current_thread.open):
            text = f"You will redirect all evil attacks from {victims[0].screenname} towards {victims[1].screenname} tonight."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'redirect' and len(victims) == 2 and are_all_alive(victims)
                and victims[0].gamenum != victims[1].gamenum and not self.current_thread.open):
            victims[0].protected_by.append(self.gamenum)
            self.protecting = [victims[0].gamenum]
            self.attacking = victims[1].gamenum
            self.chat.write_message(f"You attempted to redirect all evil attacks from {victims[0].screenname} towards {victims[1].screenname}.")
        return []

class FlowerChild(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Flower Child'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.saved_lynch = 0
        self.hhtargetable = False
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'protect' and self.mp == 100 and len(victims) == 1 and victims[0].alive and self.current_thread.open:
            text = f"You are currently saving {victims[0]} from being lynched."
            self.chat.write_message(text)
            victims[0].lynchable = False
            self.saved_lynch = victims[0].gamenum
        return []

class Forger(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Forger'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.guns_forged = 0
        self.shields_forged = 0
        self.forging_gun = False
        self.forging_shield = False
        self.aura = 'Unknown'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot weapon

        OR

        Wolfbot shield

        OR

        Wolfbot arm (username)

        The arm command works for whatever item you have finished. You can forge after arming someone in the same night. Do so in a separate post.'''

    def immediate_action(self, keyword, victims):
        if keyword == 'weapon' and self.guns_forged == 0 and not self.current_thread.open:
            text = f"You will begin forging the gun."
            self.chat.write_message(text)
        if keyword == 'shield' and self.shields_forged <= 1 and not self.current_thread.open:
            text = f"You will begin forging the shield."
            self.chat.write_message(text)
        if keyword == 'arm' and self.gamenum in self.forger_guns and victims[0].alive and len(victims) == 1 and not self.current_thread.open:
            text = f"You will give the gun to {victims[0]}."
            self.chat.write_message(text)
        if keyword == 'arm' and self.gamenum in self.forger_shields and victims[0].alive and len(victims) == 1 and not self.current_thread.open:
            text = f"You will give the shield to {victims[0]}."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'weapon' and self.guns_forged == 0 and self.gamenum not in self.forger_guns and not self.current_thread.open:
            self.guns_forged = self.guns_forged + 1
            self.forging_gun = True
            self.chat.write_message("You have successfully finished forging a gun.")
        if keyword == 'shield' and self.shields_forged <= 1 and self.gamenum not in self.forger_shields and not self.current_thread.open:
            self.shields_forged = self.shields_forged + 1
            self.forging_shield = True
            self.chat.write_message("You have successfully finished forging a shield.")
            #We have a gun, giftee is alive, one giftee, we haven't given them a gun before
        if (keyword == 'arm' and self.gamenum in self.forger_guns and victims[0].alive and len(victims) == 1
                and self.gamenum not in victims[0].forger_guns) and not self.current_thread.open:
            #self.forging_gun = False move to daytime actions
            #more guns to shoot
            victims[0].has_forger_gun = victims[0].has_forger_gun + 1
            #given gun from us, can't have another
            victims[0].forger_guns.append(self.gamenum)
            #we lose our gun
            self.forger_guns.remove(self.gamenum)
            text = f"You gave the gun to {victims[0]}."
            self.chat.write_message(text)
            # We have a shield, giftee is alive, one giftee, we haven't given them a shield before
        if (keyword == 'arm' and self.gamenum in self.forger_shields and victims[0].alive and len(victims) == 1
                and self.gamenum not in victims[0].forger_shields) and not self.current_thread.open:
            # self.forging_shield = False move to daytime actions
            # more guns to shoot
            victims[0].has_forger_shield = victims[0].has_forger_shield + 1
            # given gun from us, can't have another
            victims[0].forger_shields.append(self.gamenum)
            # we lose our gun
            self.forger_shields.remove(self.gamenum)
            text = f"You gave the shield to {victims[0]}."
            self.chat.write_message(text)
        return []

class Judge(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Judge'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot judge (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'judge' and len(victims) == 1 and victims[0].alive and self.mp >=50
                and victims[0].gamenum != self.gamenum and self.current_thread.open):
            text = f"You will judge {victims[0]} today if the village cannot decide who to lynch."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'judge' and len(victims) == 1 and victims[0].alive and self.mp >=50
                and victims[0].gamenum != self.gamenum and self.current_thread.open): #AND NO LYNCH
            self.mp = self.mp-50
            if victims[0].team == 'Village':
               # self.alive = False
                return ['mistrial', self, self] #  kill_player('mistrial', self)
            else:
               # victims[0].alive = False
                return ['judge', self, victims[0]] # kill_player('judge', victims[0])
        return []

class Librarian(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Librarian'
        self.muting = [0]
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot mute (username)'''
    def immediate_action(self, keyword, victims):
        if keyword == 'mute' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum:
            text = f"You will mute {victims[0]} tomorrow."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'mute' and len(victims) == 1 and victims[0].alive and victims[0].gamenum not in self.muting and victims[0].gamenum != self.gamenum:
            self.muting.append(victims[0].gamenum)
            victims[0].muted_by.append(self.gamenum)
            text = f"{victims[0]} has been muted."
            self.chat.write_message(text)
        else:
            self.muting.append(0)
        return []

class Loudmouth(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Loudmouth'
        self.screenname = screenname
        self.revealing = 0
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot reveal (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'reveal' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum:
            text = f"You will reveal {victims[0]} upon death."
            self.chat.write_message(text)
            self.revealing = victims[0].gamenum
        return []

class Marksman(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Marksman'
        self.screenname = screenname
        self.targeting = 0 # by marksman
        self.cooldown = False
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot mark (username)

        OR

        Wolfbot shoot (username)

        You can mark someone after shooting someone else in the same night. Do so in a separate post.'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'mark' and len(victims) == 1 and victims[0].alive and self.mp >= 50
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            text = f"You will mark {victims[0]} tonight."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'shoot' and len(victims) == 1 and victims[0].alive and self.mp >= 50 and self.cooldown == False
                and victims[0].gamenum == self.targeting and victims[0].gamenum != self.gamenum
                and not self.current_thread.open):
            self.mp = self.mp - 50
            if victims[0].mm_killable:
            #    victims[0].alive = False
                return ['marksman', self, victims[0]]     # kill_player('marksman', victims[0])
            else:
            #    self.alive = False
                return ['misfire', victims[0], self]
            #    return f'{victims[0].screenname} was shot by the marksman and survived!' + '\n' + kill_player('misfire', self)
        if (keyword == 'mark' and len(victims) == 1 and victims[0].alive and self.mp >= 50
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.cooldown = True
            self.targeting = victims[0].gamenum
            text = f"{victims[0]} is now marked."
            self.chat.write_message(text)
        return []

class Preacher(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Preacher'
        self.screenname = screenname
        self.preacher_watching = 0
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'watch' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            text = f"You will watch {victims[0]} tonight."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'watch' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.preacher_watching = victims[0].gamenum
            victims[0].preacher_watched_by.append(self.gamenum)
            self.chat.write_message(f"You watched {victims[0]} tonight.")
        return []


class Priest(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Priest'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]in the day thread[/b]:

        Wolfbot water (username)'''

    def immediate_action(self, keyword, victims):
        # Only works if they are targeting one person, have used water, victim is alive
        if (keyword == 'water' and len(victims) == 1 and self.mp == 100 and victims[0].alive
                and victims[0].gamenum != self.gamenum and self.current_thread.open):
            self.mp = self.mp - 100
            if victims[0].waterable:
                return ['water', self, victims[0]]
            else:
                return ['drowned', victims[0], self]
        return []

class RedLady(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Red Lady'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.visiting = 0
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot visit (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'visit' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum:
            text = f"You will visit {victims[0]} tonight."
            self.chat.write_message(text)
        return []


    def phased_action(self, keyword, victims):
        if keyword == 'visit' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum:
            self.visiting = victims[0].gamenum
            self.chat.write_message(f"You visited {victims[0]} last night.")
            if victims[0].is_killer:
                return ['evilvisit', victims[0], self]
        return []

class Sheriff(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Sheriff'
        self.screenname = screenname
        self.sheriff_watching = 0
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'watch' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            text = f"You will watch {victims[0]} tonight."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'watch' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.sheriff_watching = victims[0].gamenum
            victims[0].sheriff_watched_by.append(self.gamenum)
            victims[0].seen_by.append(self.gamenum)
            self.chat.write_message(f"You watched {victims[0]} tonight.")
        return []

class SeerApprentice(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Seer Apprentice'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''

class SpiritSeer(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Spirit Seer'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot watch (username) and (username)

        You can select only one player.'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'watch' and len(victims) == 2 and victims[0].gamenum != self.gamenum
        and victims[1].gamenum != self.gamenum and are_all_alive(victims) and victims[0].gamenum != victims[1].gamenum
                and not self.current_thread.open):
            self.chat.write_message(f"You are checking {victims[0].screenname} and {victims[1].screenname} at the end of the night.")
        if keyword == 'watch' and len(victims) == 1 and victims[0].gamenum != self.gamenum and victims[0].alive:
            self.chat.write_message(f"You are checking {victims[0].screenname} at the end of the night.")
        return []

    def phased_action(self, keyword, victims):
        if len(victims) == 2:
            if victims[1].alive is False:
                del victims[1]
            if victims[0].alive is False:
                del victims[0]
        if (keyword == 'watch' and len(victims) == 2 and victims[0].gamenum != self.gamenum
                and victims[1].gamenum != self.gamenum and victims[0].gamenum != victims[1].gamenum
                and not self.current_thread.open):
            if victims[0].has_killed is False and victims[1].has_killed is False:
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are [b]Blue[/b]. "
                                        f"Neither player killed anyone last night.")
            else:
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are [b]Red[/b]. "
                                        f"One or both players killed someone last night.")
            victims[0].seen_by.append(self.gamenum)
            victims[1].seen_by.append(self.gamenum)
        if keyword == 'watch' and len(victims) == 1 and victims[0].gamenum != self.gamenum:
            if victims[0].has_killed is False:
                self.chat.write_message(f"{victims[0].screenname} is [b]Blue[/b]. "
                                        f"They did not kill anyone last night.")
            else:
                self.chat.write_message(f"{victims[0].screenname} are [b]Red[/b]. "
                                        f"They killed someone last night.")
            victims[0].seen_by.append(self.gamenum)
        return []

class ToughGuy(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Tough Guy'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.shield = True
        self.triggered = False
        self.protected_by = [self.gamenum]
        self.protecting = True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'protect' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.chat.write_message(f"You will protect {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'protect' and len(victims) == 1 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            victims[0].protected_by.append(self.gamenum)
            self.protecting = [self.gamenum, victims[0].gamenum]
            self.chat.write_message(f"You attempted to protect {victims[0].screenname} last night.")
        return []

class Violinist(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Violinist'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.seer = True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'check' and len(victims) == 2 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            self.chat.write_message(f"You will check {victims[0].screenname} against {victims[1].screenname} tonight")
        return []

    def phased_action(self, keyword, victims):
        # Only works if they are targeting two people, haven't checked yet, people are alive, and they aren't checking themselves
        if (keyword == 'check' and len(victims) == 2 and victims[0].alive
                and victims[0].gamenum != self.gamenum and not self.current_thread.open):
            if victims[0].apparent_team == victims[1].apparent_team:
                self.chat.write_message(
                    f"{victims[0].screenname} appears to be mourning the death of {victims[1].screenname}. They are on the [b]same team[/b].")
            else:
                self.chat.write_message(
                    f"{victims[0].screenname} is not mourning the death of {victims[1].screenname}. They are on [b]different teams[/b].")
            victims[0].seen_by.append(self.gamenum)
        return []


class Witch(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Witch'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.has_protect_potion = True
        self.has_kill_potion = True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)

        OR

        Wolfbot poison (username)

        You can do both in the same night using the same or separate posts.'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'protect' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                and self.has_protect_potion and not self.current_thread.open):
            self.chat.write_message(f"You will attempt to protect {victims[0].screenname} tonight")
        if (keyword == 'poison' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                and self.has_kill_potion and not self.current_thread.open):
            self.chat.write_message(f"You will kill {victims[0].screenname} tonight")
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'protect' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                and self.has_protect_potion and not self.current_thread.open):
            victims[0].protected_by.append(self.gamenum)
            self.protecting = [victims[0].gamenum]
        if (keyword == 'poison' and len(victims) == 1 and victims[0].alive and victims[0].gamenum != self.gamenum
                and self.has_kill_potion and not self.current_thread.open):
            self.has_kill_potion = False
            victims[0].alive = False
            return ['witch', victims[0] , self]
        return []

#Wolves
class WolfAvenger(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Wolf Avenger'
        self.aura = 'Evil'
        self.wolf_order = 1
        self.wolf_voting_power=1
        self.team = 'Wolf'
        self.is_killer = True
        self.hhtargetable = False
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.screenname = screenname
        self.avenging = 0
        self.gamenum = gamenum
        self.noun = noun
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot tag (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'tag' and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable:
            self.chat.write_message(f"You are currently avenging upon {victims[0].screenname}.")
            self.avenging = victims[0].gamenum
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'tag' and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable:
            self.avenging = victims[0].gamenum
        return []

class Werewolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Werewolf'
        self.aura = 'Evil'
        self.wolf_order = 2
        self.wolf_voting_power=1
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
        self.category = 'None'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''

class ShamanWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Shaman Wolf'
        self.aura = 'Evil'
        self.wolf_order = 3
        self.wolf_voting_power=1
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time [b]during the day[/b] by posting [b]here[/b]:

        Wolfbot shaman (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'shaman' and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable:
            self.chat.write_message(f"You will enchant {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'shaman' and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable:
            self.chat.write_message(f"{victims[0].screenname} has been enchanted.")
            victims[0].shamaned_by.append(self.gamenum)
        return []

class BerserkWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Berserk Wolf'
        self.aura = 'Evil'
        self.wolf_order = 4
        self.wolf_voting_power=1
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot berserk'''

    def immediate_action(self, keyword, victims):
        if keyword == 'berserk' and self.mp == 100:
            text = r"Berserk will be activated tonight."
            if len(victims) > 0:
                text = text + f" You will need to vote {victims[0].screenname} in the normal wolf vote."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'berserk' and self.mp == 100:
            self.mp = self.mp - 100
            self.chat.write_message(f"The Werewolf Berserk is active.")
            self.berserking = True
        if victims[0].screenname == 'shortkut':
            self.chat.write_message(f"Wolfbot approves of your desire to murder shortkut, but the normal wolf vote must be used.")
        return []

class NightmareWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Nightmare Wolf'
        self.aura = 'Evil'
        self.wolf_order = 5
        self.wolf_voting_power=1
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot nightmare (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'nightmare' and len(victims) == 1 and victims[0].alive
                and victims[0].wolf_targetable and self.current_thread.open):
            self.chat.write_message(f"You will nightmare {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'nightmare' and len(victims) == 1 and victims[0].alive
                and victims[0].wolf_targetable and self.current_thread.open):
            self.chat.write_message(f"{victims[0].screenname} has been nightmared.")
            victims[0].nightmared = True
        return []

class VoodooWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Voodoo Wolf'
        self.aura = 'Evil'
        self.wolf_order = 6
        self.wolf_voting_power=1
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.is_killer = True
        self.muting = [0]
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot mute (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'mute' and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable and not self.current_thread.open:
            text = f"You will mute {victims[0]} tomorrow."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'mute' and len(victims) == 1 and victims[0].alive and victims[0].gamenum not in self.muting
                and victims[0].wolf_targetable and not self.current_thread.open):
            self.muting.append(victims[0].gamenum)
            victims[0].muted_by.append(self.gamenum)
            text = f"{victims[0]} has been muted."
            self.chat.write_message(text)
        else:
            self.muting.append(0)
        return []

class GuardianWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Guardian Wolf'
        self.aura = 'Evil'
        self.wolf_order = 7
        self.wolf_voting_power=1
        self.screenname = screenname
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.saved_lynch = 0
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'protect' and self.mp == 100 and len(victims) == 1 and victims[0].alive and self.current_thread.open:
            text = f"You are currently saving {victims[0]} from being lynched."
            victims[0].lynchable = False
            self.saved_lynch = victims[0].gamenum
            self.chat.write_message(text)
        return []

class WolfTrickster(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Wolf Trickster'
        self.aura = 'Evil'
        self.wolf_order = 8
        self.wolf_voting_power=1
        self.tricking = 0
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot trick (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'trick' and self.mp == 100 and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable:
            text = f"You are currently tricking {victims[0]}."
            self.chat.write_message(text)
            self.tricking = victims[0].gamenum
            victims[0].tricked_by.append(self.gamenum)
        return []

class ConfusionWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Confusion Wolf'
        self.aura = 'Evil'
        self.wolf_order = 9
        self.wolf_voting_power=1
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot confusion'''

    def immediate_action(self, keyword, victims):
        if keyword == 'confusion' and self.mp >= 50 and not self.current_thread.open:
            text = r"Confusion will be activated tonight."
            if len(victims) == 1:
                text = text + f"You will need to vote {victims[0].screenname} in the normal wolf vote."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'confusion' and self.mp >= 50 and not self.current_thread.open:
            self.chat.write_message(f"Wolf Confusion is active.")
            self.confusion = True
            self.mp = self.mp - 50
        if victims[0].screenname == 'shortkut':
            self.chat.write_message(f"Wolfbot approves of your desire to murder shortkut, but the normal wolf vote must be used.")
        return []

class ShadowWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Shadow Wolf'
        self.aura = 'Evil'
        self.wolf_order = 10
        self.wolf_voting_power=1
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.is_killer = True
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot shadow'''

    def immediate_action(self, keyword, victims):
        if keyword == 'shadow' and self.mp == 100 and self.current_thread.open:
            text = r"Shadow has been activated."
            self.mp = self.mp - 100
            self.current_thread.delete_poll()
            self.current_thread.write_post("[b]Today's voting has been manipulated by the Shadow Wolf.[/b]")
            self.shadow = True
            self.current_thread.post_shadow()
            if len(victims) == 1:
                text = text + f" You will need to vote {victims[0].screenname} in the normal wolf vote. Reminder that Wolf Chat is closed."
            self.chat.write_message(text)
        return []

class JellyWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Jelly Wolf'
        self.aura = 'Evil'
        self.wolf_order = 11
        self.wolf_voting_power=1
        self.wolf_targetable = False
        self.conjuror_can_take = False
        self.screenname = screenname
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Wolf'
        self.hhtargetable = False
        self.jellying = 0
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot protect (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'protect' and self.mp == 100 and len(victims) == 1 and victims[0].alive and not self.current_thread.open:
            text = f"You will attempt to place jelly on {victims[0]} tonight."
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'protect' and self.mp == 100 and len(victims) == 1 and victims[0].alive and not self.current_thread.open:
            victims[0].jellied_by.append(self.gamenum)
            self.jellying = victims[0].gamenum
            self.chat.write_message(f"You placed protective jelly on {victims[0]} last night.")
        return []

class ToxicWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Toxic Wolf'
        self.aura = 'Evil'
        self.wolf_order = 12
        self.wolf_voting_power=1
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day by posting [b]here[/b]:

        Wolfbot poison (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'poison' and self.mp >= 50 and len(victims) == 1 and victims[0].alive
                and victims[0].poisoned is False and self.current_thread.open):
            self.mp = self.mp - 50
            victims[0].poisoned = True
            self.chat.write_message(f"{victims[0].screenname} has been poisoned.")
        return []

class WolfScribe(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Wolf Scribe'
        self.aura = 'Evil'
        self.wolf_order = 13
        self.wolf_voting_power=1
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot kill (username) by (method)

        You can see a list of death methods by posting:

        Wolfbot deaths
        '''

    def immediate_action(self, keyword, victims):
        methods = kill_methods()['keyword']
        if keyword == 'kill' and self.mp >= 50 and len(victims) == 2 and victims[0].alive and victims[1] in methods:
            text = f"If {victims[0]} dies, they will be shown as having been killed by the following method: \n"
            text = text + kill_methods()['Cause of Death'][kill_methods()['keyword'].index(victims[1])]
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        methods = kill_methods()['keyword']
        if keyword == 'kill' and self.mp >= 50 and len(victims) == 2 and victims[0].alive and victims[1] in methods:
            self.scribing = victims[0].gamenum
            victims[0].scribed = victims[1]
        return []

class AlphaWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
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
        self.wolf_voting_power=100
        self.wolf_targetable = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.waterable = True
        self.mm_killable = True
        self.category = 'Werewolf'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''

class BlindWolf(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username) and (username)

        You can check only one person if you like.

        You can resign your powers at any time by posting [b]here[/b]:

        Wolfbot resign'''
        
    def immediate_action(self, keyword, victims):
        if (keyword == 'check' and len(victims) == 2 and are_all_alive(victims) and victims[0].wolf_targetable
                and victims[1].wolf_targetable and self.checked < 2 and not self.resigned
                and not self.current_thread.open and not self.jailed):
            self.chat.write_message(f"{victims[0].screenname} is the {victims[0].category}. {victims[1].screenname} is the {victims[1].category}.")
            self.checked = 2
            victims[0].seen_by.append(self.gamenum)
            victims[1].seen_by.append(self.gamenum)
        if (keyword == 'check' and len(victims) == 1 and victims[0].alive and victims[0].wolf_targetable
                and self.checked < 2 and not self.resigned and not self.current_thread.open and not self.jailed):
            self.chat.write_message(f"{victims[0].screenname} is the {victims[0].category}.")
            self.checked = self.checked + 1
            victims[0].seen_by.append(self.gamenum)
        if keyword == 'resign':
            self.chat.write_message(f"You have resigned your powers.")
            self.resigned = True
            self.wolf_voting_power=1
        return []

class WolfSeer(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)

        You can resign your powers at any time by posting [b]here[/b]:

        Wolfbot resign'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'check' and len(victims) == 1 and victims[0].alive
                and victims[0].wolf_targetable and self.checked == 0 and not self.resigned
                and not self.current_thread.open and not self.jailed):
            self.chat.write_message(f"{victims[0].screenname} is the {victims[0].role}.")
            self.checked = self.checked + 1
            victims[0].seen_by.append(self.gamenum)
        if keyword == 'resign':
            self.chat.write_message(f"You have resigned your powers.")
            self.resigned = True
            self.wolf_voting_power=1
        return []

class Sorcerer(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Sorcerer'
        self.aura = 'Evil'
        self.team = 'Wolf'
        self.apparent_team = 'Village'
        self.apparent_aura = 'Good'
        self.seer = True
        self.conjuror_can_take = False
        self.screenname = screenname
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.wolf_targetable = False
        self.mm_killable = True
        self.category = 'None'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username)

        During the day, you can reveal a player by posting [b]here[/b]:

        Wolfbot reveal (username)

        You can resign your powers at any time by posting [b]here[/b]:

        Wolfbot resign'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'check' and len(victims) == 1 and victims[0].alive
                and victims[0].wolf_targetable and self.checked == 0 and not self.resigned
                and not self.current_thread.open and not self.jailed):
            self.chat.write_message(f"{victims[0].screenname} is the {victims[0].role}.")
            self.checked = self.checked + 1
            victims[0].seen_by.append(self.gamenum)
        if keyword == 'resign':
            self.chat.write_message(f"You have resigned your powers and may participate in wolf chat.")
            self.resigned = True
            self.wolf_voting_power = 1
        return []

class WerewolfFan(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Werewolf Fan'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.team = 'Wolf'
        self.hhtargetable = False
        self.category = 'Wildcard'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the day or night by posting [b]here[/b]:

        Wolfbot reveal (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'reveal' and len(victims) == 1 and victims[0].alive:
            self.chat.write_message(f"You will reveal your role to {victims[0].screenname} at the start of the next night.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'reveal' and len(victims) == 1 and victims[0].alive:
            victims[0].chat.write_message(f"{self.screenname} has shown you their role. They are the {self.role}.")
            self.chat.write_message(f"You have revealed your role to {victims[0].screenname}.")
        return []

#Solos
class Cupid(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.role = 'Cupid'
        self.night = 1
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.hhtargetable = False
        self.category = 'Wildcard'
        self.can_couple=True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the first night by posting [b]here[/b]:

        Wolfbot couple (username) and (username)'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'couple' and len(victims) == 2 and are_all_alive(victims)
                and victims[1].gamenum != victims[0].gamenum and self.night == 1
                and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum):
            self.chat.write_message(f"You are attempting to couple {victims[0].screenname} and {victims[0].screenname}.")
        return []

    def phased_action(self, keyword, victims):
        if len(victims) == 2:
            if victims[1].alive is False:
                del victims[1]
            if victims[0].alive is False:
                del victims[0]
        if (keyword == 'couple' and len(victims) == 2 and are_all_alive(victims)
                and victims[1].gamenum != victims[0].gamenum and self.night == 1
                and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum):
            self.night = self.night + 1
            victims[0].coupled = True
            victims[1].coupled = True
        if (keyword == 'couple' and len(victims) == 1 and are_all_alive(victims)
                and self.night == 1 and self.gamenum != victims[0].gamenum):
            self.night = self.night + 1
            victims[0].coupled = True
        return []

class Fool(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b].'''

class Headhunter(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
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
        self.target_num = 0
        self.target_name = ''
        self.category = 'Wildcard'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Your target is {self.target_name}.'''

#Solo Killers
class Alchemist(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot kill (username)

        OR

        Wolfbot potion (username)

        'kill' gives the black potion. 'potion' gives the red potion. You may give one, both, or neither potion in one post or separate posts.'''

    def immediate_action(self, keyword, victims):
        if (keyword == 'kill' and len(victims) == 1 and victims[0].alive
                and self.gamenum != victims[0].gamenum and not self.current_thread.open):
            self.chat.write_message(f"You will give the black potion to {victims[0].screenname} tonight.")
        if (keyword == 'potion' and len(victims) == 1 and victims[0].alive
                and self.gamenum != victims[0].gamenum and not self.current_thread.open):
            self.chat.write_message(f"You will give the red potion to {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if (keyword == 'kill' and len(victims) == 1 and victims[0].alive
                and self.gamenum != victims[0].gamenum and not self.current_thread.open):
            victims[0].solo_kill_attempt.append('Alchemist')
        if (keyword == 'potion' and len(victims) == 1 and victims[0].alive
                and self.gamenum != victims[0].gamenum and not self.current_thread.open):
            victims[0].red_potion = victims[0].red_potion + 1
        return []

class Arsonist(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
        self.role = 'Arsonist'
        self.screenname = screenname
        self.conjuror_can_take = False
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.team = 'Arsonist'
        self.aura = 'Unknown'
        self.dousing = []
        self.hhtargetable = False
        self.mm_killable = True
        self.action_used = False
        self.category = 'Solo Killer'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot douse (username) and (username)

        You can douse only one player if you choose. If you choose to burn instead of dousing, use the command:

        Wolfbot kill all'''

    def immediate_action(self, keyword, victims):
        if keyword == 'kill':
            self.chat.write_message(f"You are choosing to burn tonight.")
        if (keyword == 'douse' and len(victims) == 2 and self.gamenum != victims[0].gamenum
                and self.gamenum != victims[1].gamenum and victims[1].gamenum != victims[0].gamenum
                and not self.current_thread.open):
            self.chat.write_message(f"You are dousing {victims[0].screenname} and {victims[1].screenname} tonight.")
        if (keyword == 'douse' and len(victims) == 1 and self.gamenum != victims[0].gamenum
                and not self.current_thread.open):
            self.chat.write_message(f"You are dousing {victims[0].screenname} tonight.")

    def phased_action(self, keyword, victims):
        if len(victims) == 2:
            if victims[1].alive is False:
                del victims[1]
            if victims[0].alive is False:
                del victims[0]
        if keyword == 'kill' and not self.current_thread.open and not self.action_used:
            self.solo_kill_attempt.append('Arsonist')
            self.action_used = True
            return "The Arsonist burns!\n"
        if (keyword == 'douse' and len(victims) == 2 and self.gamenum != victims[0].gamenum
                and self.gamenum != victims[1].gamenum and victims[1].gamenum != victims[0].gamenum
                and not self.current_thread.open and not self.action_used):
            self.chat.write_message(f"You successfully doused {victims[0].screenname} and {victims[1].screenname}.")
            self.dousing.extend([victims[0].gamenum, victims[1].gamenum])
            victims[0].doused_by.append(self.gamenum)
            victims[1].doused_by.append(self.gamenum)
            self.action_used = True
        if (keyword == 'douse' and len(victims) == 1 and self.gamenum != victims[0].gamenum
                and not self.current_thread.open and not self.action_used):
            self.chat.write_message(f"You successfully doused {victims[0].screenname}.")
            self.dousing.append(victims[0].gamenum)
            victims[0].doused_by.append(self.gamenum)
            self.action_used = True
        return []

class Corruptor(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot corrupt (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'corrupt' and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            self.chat.write_message(f"You will corrupt {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'corrupt' and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            victims[0].solo_kill_attempt.append('Corruptor')
        return []

class CultLeader(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
        self.role = 'Cult Leader'
        self.team = 'Cult'
        self.screenname = screenname
        self.conjuror_can_take = False
        self.is_killer = True
        self.gamenum = gamenum
        self.noun = noun
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.can_couple=True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot convert (username)

        You can sacrifice a convert to attack another player at night by posting [b]here[/b]:

        Wolfbot sacrifice (username) for (username)

        The second named player will be attacked and the first will die.'''

    def immediate_action(self, keyword, victims):
        if keyword == 'convert' and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            self.chat.write_message(f"You will attempt to convert {victims[0].screenname} to the cult tonight.")
        if (keyword == 'sacrifice' and len(victims) == 2 and are_all_alive(victims)
                and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum and victims[0].cult):
            self.chat.write_message(f"You will sacrifice {victims[0].screenname} in an attempt to kill {victims[1].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'convert' and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            victims[0].solo_kill_attempt.append('Cult Leader1')
        if (keyword == 'sacrifice' and len(victims) == 2 and victims[0].alive
                and self.gamenum != victims[0].gamenum and self.gamenum != victims[1].gamenum and victims[0].cult):
            victims[0].solo_kill_attempt.append('Cult Leader2')
            victims[0].solo_kill_attempt.append('Cult Leader3')
        return []

class EvilDetective(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot check (username) and (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'check' and len(victims) == 2 and are_all_alive(victims) and victims[1].gamenum != victims[0].gamenum:
            self.chat.write_message(f"You will check {victims[0].screenname} and {victims[1].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'check' and len(victims) == 2 and victims[1].gamenum != victims[0].gamenum:
            if victims[0].gamenum == self.gamenum:
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are on [b]different teams[/b].")
                victims[1].solo_kill_attempt.append('Evil Detective')
            elif victims[1].gamenum == self.gamenum:
                victims[0].solo_kill_attempt.append('Evil Detective')
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are on [b]different teams[/b].")
            elif victims[1].team != victims[0].team:
                victims[1].solo_kill_attempt.append('Evil Detective')
                victims[0].solo_kill_attempt.append('Evil Detective')
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are on [b]different teams[/b].")
            else:
                self.chat.write_message(f"{victims[0].screenname} and {victims[1].screenname} are on the [b]same team[/b].")
        return []

class Illusionist(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
        self.role = 'Illusionist'
        self.screenname = screenname
        self.gamenum = gamenum
        self.noun = noun
        self.conjuror_can_take = False
        self.team = 'Illusionist'
        self.is_killer = True
        self.aura = 'Unknown'
        self.hhtargetable = False
        self.disguising = []
        self.mm_killable = True
        self.category = 'Solo Killer'
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot disguise (username)

        You can kill at specified times during the day by posting [b]here[/b]:

        Wolfbot kill all'''

    def immediate_action(self, keyword, victims):
        if keyword == 'kill':
            self.solo_kill_attempt.append('Illusionist')
        if keyword == 'disguise' and len(victims) == 1 and self.gamenum != victims[0].gamenum:
            self.chat.write_message(f"You are disguising {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'disguise' and len(victims) == 1 and self.gamenum != victims[0].gamenum:
            self.chat.write_message(f"You have disguised {victims[0].screenname}.")
            victims[0].disguised_by.append(self.gamenum)
        return []

class Infector(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot infect (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'infect' and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            self.chat.write_message(f"You will infect {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'infect' and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            victims[0].solo_kill_attempt.append('Infector')
        return []

class Instigator(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
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
        self.can_couple=True
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night if you are by yourself by posting [b]here[/b]:

        Wolfbot kill (username)'''

    def immediate_action(self, keyword, victims):
        if keyword == 'kill' and self.instigators_dead and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            self.chat.write_message(f"You will kill {victims[0].screenname} tonight.")
        return []

    def phased_action(self, keyword, victims):
        if keyword == 'kill' and self.instigators_dead and len(victims) == 1 and victims[0].alive and self.gamenum != victims[0].gamenum:
            victims[0].solo_kill_attempt.append('Instigator')
        return []

class SerialKiller(Player):
    def __init__(self, gamenum = 0, screenname = '', noun = ''):
        super().__init__()
        self.wolf_immune=True
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
        self.initial_PM = f'''Your word is [b]{noun}[/b]. You are the [b]{self.role}[/b]. Use your ability at any time during the night by posting [b]here[/b]:

        Wolfbot kill (username) and (username) and (username)

        You may kill as many or as few players as you are able.'''

    def immediate_action(self, keyword, victims):
        if keyword == 'kill' and len(victims) <= (self.mp + 100) // 100 and are_all_alive(victims):
            text = "You will attempt to kill the following players tonight: "
            for i in victims:
                text = text + f"\n{i.screenname}"
            self.chat.write_message(text)
        return []

    def phased_action(self, keyword, victims):
        self.mp = self.mp+100
        if keyword == 'kill' and len(victims) <= self.mp // 100 and are_all_alive(victims):
            for player in victims:
                if player.gamenum != self.gamenum:
                    player.solo_kill_attempt.append('Serial Killer')
                    self.mp = self.mp - 100
        return []
