init -9 python:
    # ========================= Arena and related ===========================>>>
    class Arena(_object):
        """
        First prototype of Arena, will take care of most related logic and might have to be split in the future.
        @Note to myself: This code needs to be updated post-Alpha release to account for Arena Fighters and restructured for further use in the game!
        -------------------------->
        """
        PERMIT_REP = 5000    # the required arena reputation to buy an arena permit
        PERMIT_PRICE = 10000 # the price of an arena permit
        EMPTY_TEAM = Team(max_size=0)
        def __init__(self):
            super(Arena, self).__init__()

            # Scheduled matches:
            #                       Off Team          Def Team      Day
            self.matches_1v1 = [[Arena.EMPTY_TEAM, Arena.EMPTY_TEAM, 1] for i in xrange(8)]
            self.matches_2v2 = [[Arena.EMPTY_TEAM, Arena.EMPTY_TEAM, 1] for i in xrange(5)]
            self.matches_3v3 = [[Arena.EMPTY_TEAM, Arena.EMPTY_TEAM, 1] for i in xrange(5)]
            # Ladders and their team members.
            #  The separate list is necessary because a team can be changed.
            #  At the moment only the hero-teams can change, so the initial team members are not copied. 
            self.ladder_1v1 = [Team(max_size=1) for i in xrange(20)]
            self.ladder_2v2 = [Team(max_size=2) for i in xrange(10)]
            self.ladder_3v3 = [Team(max_size=3) for i in xrange(10)]
            self.ladder_1v1_members = [t.members for t in self.ladder_1v1]
            self.ladder_2v2_members = [t.members for t in self.ladder_2v2]
            self.ladder_3v3_members = [t.members for t in self.ladder_3v3]
            self.ladder = [None] * 100

            # ----------------------------->
            self.king = None

            # A list of Arena Fighters loaded into the game and actively participating in the Arena.
            self.teams_2v2 = list()
            self.teams_3v3 = list()

            self.dogfights_1v1 = list()
            self.dogfights_2v2 = list()
            self.dogfights_3v3 = list()

            # ND-Report
            self.df_count = 0
            self.daily_match_results = []
            self.daily_report = []

        # -------------------------- Sorting ---------------------------------------------------------->
        def get_matches_fighters(self, matches="all"):
            '''
            Returns all fighters that are set to participate at official maches.
            '''
            if matches == "1v1":
                fighters = set([f for ladder in self.matches_1v1 for f in itertools.chain(ladder[0], ladder[1])])
            elif matches == "2v2":
                fighters = set([f for ladder in self.matches_2v2 for f in itertools.chain(ladder[0], ladder[1])])
            elif matches == "3v3":
                fighters = set([f for ladder in self.matches_3v3 for f in itertools.chain(ladder[0], ladder[1])])
            else:
                fighters = set([f for ladder in self.matches_1v1 for f in itertools.chain(ladder[0], ladder[1])])
                fighters.update([f for ladder in self.matches_2v2 for f in itertools.chain(ladder[0], ladder[1])])
                fighters.update([f for ladder in self.matches_3v3 for f in itertools.chain(ladder[0], ladder[1])])

            return fighters

        def get_teams_fighters(self, teams="all"):
            """
            Returns fighters that are in the Arena teams.
            """
            if teams == "2v2":
                fighters = set([f for team in self.teams_2v2 for f in team])
            elif teams == "3v3":
                fighters = set([f for team in self.teams_3v3 for f in team])
            else:
                fighters = set([f for team in self.teams_2v2 for f in team])
                fighters.update([f for team in self.teams_3v3 for f in team])
            return fighters

        def get_ladders_fighters(self, ladder="all"):
            """
            Returns fighters currently in Arena lineups (heavyweights basically)
            """
            if ladder == "1v1":
                fighters = set([f for team in self.ladder_1v1 for f in team])
            elif ladder == "2v2":
                fighters = set([f for team in self.ladder_2v2 for f in team])
            elif ladder == "3v3":
                fighters = set([f for team in self.ladder_3v3 for f in team])
            else:
                fighters = set([f for team in self.ladder_1v1 for f in team])
                fighters.update([f for team in self.ladder_2v2 for f in team])
                fighters.update([f for team in self.ladder_3v3 for f in team])

            return fighters

        def get_dogfights_fighters(self, dogfights="all"):
            """
            All fighters that are currently in dogfights!
            """
            if dogfights == "1v1":
                fighters = set([f for team in self.dogfights_1v1 for f in team])
            elif dogfights == "2v2":
                fighters = set([f for team in self.dogfights_2v2 for f in team])
            elif dogfights == "3v3":
                fighters = set([f for team in self.dogfights_3v3 for f in team])
            else:
                fighters = set([f for team in self.dogfights_1v1 for f in team])
                fighters.update([f for team in self.dogfights_2v2 for f in team])
                fighters.update([f for team in self.dogfights_3v3 for f in team])

            return fighters

        def get_arena_fighters(self):
            '''
            Returns all fighters active at the arena.
            hero = true will include all girls in heros employment as well.
            Updated to include all Arena Fighters as well!
            Note to self: This REALLY should simply be a list in the Arena namespace...
            '''
            return [f for f in itertools.chain(chars.itervalues(), fighters.itervalues()) if f.arena_active]

        def get_arena_candidates(self):
            '''
            Returns a list of all characters available/willing to fight in the Arena.
            Excludes all girls participating in girl_meets to avoid them being at multiple locations (this needs better handling)
            '''
            interactions_chars = set(iam.get_all_girls())
            interactions_chars.update(hero.chars)
            return [c for c in chars.itervalues() if c.arena_willing and c not in interactions_chars] + fighters.values()

        # -------------------------- Teams control/checks -------------------------------------->
        def remove_team_from_dogfights(self, fighter):
            for group in (self.dogfights_1v1, self.dogfights_2v2, self.dogfights_3v3):
                group[:] = [team for team in group if fighter not in team]

        @staticmethod
        def check_if_team_ready_for_dogfight(unit, dogfighters=[]):
            """
            Checks if a team/fighter is ready for dogfight by eliminating them on grounds of health, scheduled matches, presense in other dogfights or lack of AP.
            """
            if unit in dogfighters:
                return False

            if not isinstance(unit, Team):
                unit = [unit]

            for f in unit:
                for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                    if f.get_stat(stat) < f.get_max(stat)*9/10:
                        return False
                if day+1 in f.fighting_days:
                    return False
                if f.PP < 200: # PP_PER_AP
                    return False

            return True

        # -------------------------- Update Methods ---------------------------------------------->
        def update_teams(self):
            '''Makes sure that there are enough teams for Arena to function properly.
            If members are removed from teams directly, it is up to the respective method to find a replacement...
            '''
            candidates = None
            amount = 30 - len(self.teams_2v2)
            if amount > 0:
                if candidates is None:
                    candidates = self.get_arena_candidates()
                inteams_2v2 = self.get_teams_fighters(teams="2v2")
                templist = [fighter for fighter in candidates if fighter not in inteams_2v2]
                shuffle(templist)

                for __ in xrange(min(amount, len(templist)/2)):
                    team = Team(name=get_team_name(), max_size=2)
                    for __ in xrange(2):
                        f = templist.pop()
                        f.arena_active = True
                        team.add(f)
                    self.teams_2v2.append(team)

            amount = 30 - len(self.teams_3v3)
            if amount > 0:
                if candidates is None:
                    candidates = self.get_arena_candidates()
                inteams_3v3 = self.get_teams_fighters(teams="3v3")
                templist = [fighter for fighter in candidates if fighter not in inteams_3v3]
                shuffle(templist)

                for __ in xrange(min(amount, len(templist)/3)):
                    team = Team(name=get_team_name(), max_size=3)
                    for __ in xrange(3):
                        f = templist.pop()
                        f.arena_active = True
                        team.add(f)
                    self.teams_3v3.append(team)

        def update_dogfights(self):
            """
            Just populates dogfights, no more checking for anything...
            """
            level_range = range(hero.level-10, hero.level+10)

            # 1v1
            amount = 20 - len(self.dogfights_1v1)
            if amount > 0:
                candidates = self.get_arena_candidates()
                dogfighters = self.get_dogfights_fighters()
                candidates = [f for f in candidates if f not in dogfighters]
                shuffle(candidates)

                amount = min(min(randint(15, 20), amount), len(candidates))
                in_range_exists = len([f for f in dogfighters if f.level in level_range])

                # do first pass over those candidates who's level is near Hero's
                for f in candidates[:]:
                    if amount == 0 or in_range_exists >= 5:
                        break

                    if f.level in level_range:
                        amount -= 1
                        in_range_exists += 1
                        f.arena_active = True
                        candidates.remove(f)
                        team = Team(implicit=[f], max_size=1)
                        self.dogfights_1v1.append(team)


                while amount != 0:
                    amount -= 1
                    f = candidates.pop()
                    f.arena_active = True
                    team = Team(implicit=[f], max_size=1)
                    self.dogfights_1v1.append(team)

            # 2v2, 3v3
            for teams, teams_setup in ([self.teams_2v2, self.dogfights_2v2],
                                       [self.teams_3v3, self.dogfights_3v3]):
                amount = 15 - len(teams_setup)
                if amount:
                    candidates = [team for team in teams if team not in teams_setup]
                    amount = min(min(randint(8, 15), amount), len(candidates))
                    in_range_exists = len([t for t in teams_setup if t.get_level() in level_range])

                    for team in candidates[:]:
                        if amount == 0 or in_range_exists >= 4:
                            break

                        if team.get_level() in level_range:
                            amount -= 1
                            in_range_exists += 1
                            candidates.remove(team)
                            teams_setup.append(team)

                    if amount != 0:
                        shuffle(candidates)

                        while amount != 0:
                            amount -= 1
                            teams_setup.append(candidates.pop())

        def update_matches(self):
            for matches, ladder in [(self.matches_1v1, self.ladder_1v1), (self.matches_2v2, self.ladder_2v2), (self.matches_3v3, self.ladder_3v3)]:
                teams = candidates = None
                tmap = dict()
                for setup in matches:
                    if setup[1]:
                        continue
                    fday = day + randint(3, 14)
                    setup[2] = fday
                    dt = tmap.get(fday, None)
                    if dt is None:
                        if teams is None:
                            teams = [i for m in matches for i in (m[0], m[1])]
                            teams = [i for i in ladder if i not in teams and i.leader != hero and i.leader.employer != hero]
                        dt = [t for t in teams if all((fday not in f.fighting_days for f in t))]
                        if dt:
                            shuffle(dt)
                        else:
                            # could not find a ladder team -> select one from the best candidates
                            if candidates is None:
                                num = len(ladder[0])
                                if num == 1:
                                    fighters = self.get_matches_fighters(matches="1v1")
                                    candidates = [i for i in self.get_arena_candidates() if i not in fighters]
                                    sorted(candidates, key=attrgetter("arena_rep"))
                                elif num == 2:
                                    teams = [i for m in matches for i in (m[0], m[1])]
                                    candidates = [t for t in self.teams_2v2 if t not in teams]
                                    sorted(candidates, key=methodcaller("get_rep"))
                                elif num == 3:
                                    teams = [i for m in matches for i in (m[0], m[1])]
                                    candidates = [t for t in self.teams_3v3 if t not in teams]
                                    sorted(candidates, key=methodcaller("get_rep"))
                                else:
                                    raise Exception("Invalid team size for update_matches: %d" % num)
                            if candidates:
                                dt = candidates.pop()
                                if not isinstance(dt, Team):
                                    dt = Team(implicit=[dt], max_size=1)
                                dt = [dt]
                        tmap[fday] = dt
                    if dt:
                        dt = dt.pop()
                        for fighter in dt:
                            fighter.fighting_days.append(fday)
                        setup[1] = dt

        def update_setups(self, winner, loser):
            """
            Responsible for repositioning winners + losers in setups!
            """
            team_size = len(winner)
            if team_size == 1:
                ladder = self.ladder_1v1
                members = self.ladder_1v1_members
            elif team_size == 2:
                ladder = self.ladder_2v2
                members = self.ladder_2v2_members
            elif team_size == 3:
                ladder = self.ladder_3v3
                members = self.ladder_3v3_members
            else:
                raise Exception("Invalid team size for update_setups: %d" % team_size)

            if winner in ladder:
                index = ladder.index(winner)
                if index != 0:
                    ladder[index], ladder[index-1] = ladder[index-1], winner
                    members[index], members[index-1] = members[index-1], winner.members[:]
            else:
                # check if the hero has an another team in the ladder
                if winner == hero.team:
                    for idx, t in enumerate(ladder):
                        if t.leader == hero:
                            # another team in the ladder -> replace it with the current one
                            ladder[idx] = winner
                            members[idx] = winner.members[:]
                            winner_added = True
                            break
                if not "winner_added" in locals():
                    ladder[-1] = winner
                    members[-1] = winner.members[:]

            if loser in ladder:
                index = ladder.index(loser)
                if index != len(ladder)-1:
                    ladder[index], ladder[index+1] = ladder[index+1], loser
                    members[index], members[index+1] = members[index+1], loser.members[:]

        def find_opfor(self):
            """
            Find a team to fight challenger team in the official arena matches.
            """
            # 1vs1:
            fighters = None
            tmap = dict()
            for setup in self.matches_1v1:
                if setup[0]:
                    continue
                fday = setup[2]
                if dice(100/(fday - day + 1)):
                    df = tmap.get(fday, None)
                    if df is None:
                        if fighters is None:
                            fighters = self.get_matches_fighters(matches="1v1")
                            fighters = [i for i in self.get_arena_candidates() if i not in fighters]
                        df = [i for i in fighters if fday not in i.fighting_days]
                        shuffle(df)
                        tmap[fday] = df

                    if df:
                        df = df.pop()
                        df.fighting_days.append(fday)
                        df.arena_active = True
                        setup[0] = Team(implicit=[df], max_size=1)

            # 2vs2, 3vs3
            for matches, lineup in [(self.matches_2v2, self.teams_2v2), (self.matches_3v3, self.teams_3v3)]:
                teams = None
                tmap = dict()
                for setup in matches:
                    if setup[0]:
                        continue
                    fday = setup[2]
                    if dice(100/(fday - day + 1)):
                        dt = tmap.get(fday, None)
                        if dt is None:
                            if teams is None:
                                teams = [i for m in matches for i in (m[0], m[1])]
                                teams = [i for i in lineup if i not in teams]
                            dt = []
                            for team in teams:
                                for fighter in team:
                                    if fday in fighter.fighting_days:
                                        break
                                else:
                                    dt.append(team)
                            shuffle(dt)
                            tmap[fday] = dt

                        if dt:
                            dt = dt.pop()
                            for fighter in dt:
                                fighter.fighting_days.append(fday)
                            setup[0] = dt

        # -------------------------- GUI methods ---------------------------------->
        def char_in_match_results(self, char):
            for match_result in self.daily_match_results:
                for f in chain(match_result[0], match_result[1]):
                    if f == char:
                        return True 

        def get_arena_match(self, team=None):
            matches = [m for m in chain(self.matches_1v1, self.matches_2v2, self.matches_3v3) if m[2] == day]
            if team is None:
                # get the arena match for the hero
                for m in matches:
                    if m[0].leader is hero:
                        return m
            else:
                for m in matches:
                    if m[0] is team or m[1] is team:
                        return m

        @staticmethod
        def match_entry_fee(off_team, def_team):
            return max(50, (off_team.get_level()+def_team.get_level())/10*10)

        def check_arena_fight(self, type, team, opponent):
            for t in team:
                if t.status == "slave":
                    return PyTGFX.message("%s is a Slave forbidden from participation in Combat!" % t.name)

            if opponent is not None and len(team) != len(opponent):
                return PyTGFX.message("Make sure that your team has %d members!" % len(opponent))

            if type == "dogfight":
                hlvl = team.get_level()
                elvl = opponent.get_level()
                if elvl > max(hlvl+12, hlvl*1.3):
                    if len(opponent) == 1:
                        msg = "You're not worth my time, go train some."
                    else:
                        msg = "You guys need to grow up before challenging the likes of us."
                    opponent.leader.say(msg)
                    return 
                if hlvl > max(elvl+12, elvl*1.3):
                    if len(opponent) == 1:
                        msg = "I am not feeling up to it... really!"
                    else:
                        msg = "We are not looking for a fight outside of our league."
                    opponent.leader.say(msg)
                    return
            elif type == "matchfight":
                for t in team:
                    if t == hero:
                        continue
                    if t.arena_rep < Arena.PERMIT_REP:
                        return PyTGFX.message("%s does not have enough arena reputation to buy an arena permit which is required to participate in matches!" % t.name)
                    if day in t.fighting_days:
                        if self.char_in_match_results(t):
                            return PyTGFX.message("%s already had a fight today. Having two official matches on the same day is not allowed!" % t.name)
                        else:
                            return PyTGFX.message("%s already has a fight planned for day %d. Having two official matches on the same day is not allowed!" % (t.name, day))

                for t in team:
                    if t != hero and not t.arena_permit:
                        temp = "{color=gold}%s Gold{/color}" % ("{:,d}".format(Arena.PERMIT_PRICE).replace(",", " "))
                        if renpy.call_screen("yesno_prompt",
                                         message="%s does not have an arena permit yet. Would you like to buy one for %s?" % (t.name, temp),
                                         yes_action=Return(True), no_action=Return(False)):
                            if hero.take_money(Arena.PERMIT_PRICE, reason="Arena Permit"):
                                t.arena_permit = True
                                continue
                            msg = "You do not have %s to buy the arena permit! " % temp
                        else:
                            msg = ""
                        msg += "You need to replace %s in your team!" % t.name
                        return PyTGFX.message(msg)
            return True

        def match_challenge(self, setup):
            """
            Checks if player already has fight setup on a given day.
            Handles confirmation screen for the fight.

            Adds player team to a setup.
            Now also checks if player has an Arena permit.
            """
            if not hero.arena_permit:
                return PyTGFX.message("Arena Permit is required to fight in the official matches!")

            fday = setup[2]

            if fday in hero.fighting_days:
                if self.char_in_match_results(hero):
                    return PyTGFX.message("You already had a fight today. Having two official matches on the same day is not allowed!")
                else:
                    return PyTGFX.message("You already have a fight planned for day %d. Having two official matches on the same day is not allowed!" % fday)

            if renpy.call_screen("yesno_prompt", "Are you sure you want to schedule a fight? Backing out of it later will mean a hit on reputation!",
                Return(True), Return(False)):
                setup[0] = hero.team
                hero.fighting_days.append(fday)

        # -------------------------- Setup Methods -------------------------------->
        def update_ladder(self):
            # Update top 100 ladder:
            candidates = self.get_arena_fighters()
            if hero.arena_rep > 0:
                candidates.append(hero)
            candidates.sort(reverse=True, key=attrgetter("arena_rep"))

            self.ladder = candidates[:len(self.ladder)]

        def update_actives(self):
            actives = set(self.ladder) | self.get_teams_fighters() | self.get_ladders_fighters() | self.get_dogfights_fighters() | self.get_matches_fighters()

            for c in chars.values():
                if c.arena_active and c not in actives:
                    c.arena_active = False

        @classmethod
        def load_chainfights(cls):
            chain_fights = load_db_json("arena_chainfights.json")
            chain_fights.sort(key=itemgetter("level"))
            for i in chain_fights:
                i["boss_portrait"] = mobs[i["boss"]]["portrait"]
            cls.all_chain_fights = chain_fights

        def load_special_team_presets(self):
            teams = load_db_json("arena_teams.json")
            team_members = set() # collect the fighters which are already added to teams
            for team in teams:
                members = team["members"]
                name = team["name"]
                lineups = team.get("lineups", False)
                tiers = team.get("tiers", None)
                if tiers is None:
                    tiers = [uniform(.8, 1.2) for m in members]
                teamsize = len(members)

                if teamsize > 3:
                    raise Exception("Arena Team %s has more than the allowed 3 members!" % name)
                elif teamsize == 0:
                    raise Exception("Arena Team %s has no members at all!" % name)

                a_team = Team(name=name, max_size=teamsize)
                for member, tier in zip(members, tiers):
                    if member == "random_char":
                        member = build_rc(bt_group="Combatant",
                                          tier=tier,
                                          give_bt_items=True)
                    elif member in rchars:
                        member = build_rc(id=member,
                                          bt_group="Combatant",
                                          tier=tier,
                                          give_bt_items=True)
                    else:
                        if teamsize != 1:
                            if member in team_members:
                                if member in chars:
                                    msg = "Unique character %s is added to teams twice!" % member.name
                                else: # member in fighters:
                                    msg = "Arena Fighter %s is added to teams twice!" % member.name
                                raise Exception(msg)
                            team_members.add(member)
                        if member in chars:
                            member = chars[member]
                            if member.status != "free":
                                raise Exception("Only free citizens can participate in arena fighting. A slave called '%s' added to arena teams." % member.name)
                            #if member in hero.chars:
                            #    hero.remove_char(member)
                        elif member in fighters:
                            member = fighters[member]
                        else:
                            break

                        tier_up_to(member, tier)
                        give_tiered_magic_skills(member)
                        give_tiered_items(member, False, True)

                    member.arena_active = True
                    #member.arena_permit = True
                    member.arena_rep = int(tier*10000*random.uniform(.9, 1.1))

                    a_team.add(member)

                if teamsize != len(a_team):
                    char_debug("Team Fighter %s is of unknown origin! (Set as MC?)" % member)
                    continue

                if lineups:
                    lineups -= 1
                    if teamsize == 1:
                        if lineups == 0:
                            raise Exception("Number one spot for 1v1 ladder (lineup) is reserved by the game!")
                        ladder = self.ladder_1v1
                        if not ladder[lineups]:
                            ladder[lineups] = a_team
                            self.ladder_1v1_members[lineups] = a_team.members
                            continue
                    elif teamsize == 2:
                        ladder = self.ladder_2v2
                        if not ladder[lineups]:
                            ladder[lineups] = a_team
                            self.ladder_2v2_members[lineups] = a_team.members
                            self.teams_2v2.append(a_team)
                            continue
                    else: # if teamsize == 3:
                        ladder = self.ladder_3v3
                        if not ladder[lineups]:
                            ladder[lineups] = a_team
                            self.ladder_3v3_members[lineups] = a_team.members
                            self.teams_3v3.append(a_team)
                            continue
                    raise Exception("Team %s failed to take place %d " \
                        "in %dv%d lineups. It is already taken by another team (%s), " \
                        "check your arena_teams.json file."%(a_team.name, lineups+1,
                        teamsize, teamsize, ladder[lineups].name))
                else:
                    if teamsize == 1:
                        raise Exception("Single member teams are only available for lineups!")
                    elif teamsize == 2:
                        self.teams_2v2.append(a_team)
                    else: # if teamsize == 3:
                        self.teams_3v3.append(a_team)


        def setup_arena(self):
            """Initial Arena Setup, this will be improved and prolly split several
            times and I should prolly call it init() as in other classes...
            """
            # Team formations!!!: -------------------------------------------------------------->
            self.load_special_team_presets()

            # Loading rest of Arena Combatants:
            candidates = self.get_arena_candidates()
            shuffle(candidates)

            # print("CANDIDATES: {}".format(len(candidates)))

            # Add da King!
            if not self.king:
                tier_kwargs = {"level_bios": (1.0, 1.2), "stat_bios": (1.0, 1.2)}
                if candidates:
                    char = candidates.pop()
                    tier_up_to(char, 7, **tier_kwargs)
                    give_tiered_magic_skills(char)
                    give_tiered_items(char, False, True)
                else:
                    char = build_rc(bt_group="Combatant", tier=7,
                                    tier_kwargs=tier_kwargs, give_bt_items=True)

                char.arena_active = True
                #char.arena_permit = True

                char.arena_rep = randint(79000, 81000)
                self.king = char

            # Setting up some decent fighters:
            power_levels = [uniform(3.8, 5.2) for i in range(15)]
            power_levels.extend([uniform(3.0, 4.5) for i in range(15)])
            power_levels.extend([uniform(2.3, 3.5) for i in range(15)])
            power_levels.extend([uniform(1.8, 2.6) for i in range(15)])
            power_levels.extend([uniform(1.5, 2.3) for i in range(15)])
            power_levels.extend([uniform(.8, 1.8) for i in range(15)])
            power_levels.extend([uniform(.4, 1.2) for i in range(10)])
            power_levels.extend([uniform(.2, .8) for i in range(10)])
            # print("POWER LEVELS: {}".format(len(power_levels)))
            new_candidates = []
            for tier, fighter in izip_longest(power_levels, candidates):
                if tier is None:
                    break
                if fighter is None:
                    fighter = build_rc(bt_group="Combatant", tier=tier, give_bt_items=True)
                    # print("Created Arena RG: {}".format(fighter.name))
                    new_candidates.append(fighter)
                else:
                    tier_up_to(fighter, tier)
                    give_tiered_magic_skills(fighter)
                    give_tiered_items(fighter, False, True)

            candidates.extend(new_candidates)

            # Populate tournament ladders:
            # 1v1 Ladder lineup:
            temp = candidates[:30]
            shuffle(temp)
            temp.append(self.king)

            for team in self.ladder_1v1:
                if not team:
                    f = temp.pop()
                    f.arena_active = True
                    #f.arena_permit = True
                    if f.arena_rep == 0:
                        f.arena_rep = int(f.level * 500 * random.uniform(.9, 1.1))
                    team.add(f)
                    team.name = f.name

            # 2v2 Ladder lineup:
            temp = candidates[:50]
            shuffle(temp)
            temp.append(self.king)

            for team in self.ladder_2v2:
                if not team.name:
                    team.name = get_team_name()
                while len(team) < 2:
                    f = temp.pop()
                    f.arena_active = True
                    #f.arena_permit = True
                    if f.arena_rep == 0:
                        f.arena_rep = int(f.level * 500 * random.uniform(.9, 1.1))
                    team.add(f)

            # 3v3 Ladder lineup:
            temp = candidates[:60]
            shuffle(temp)
            temp.append(self.king)

            for team in self.ladder_3v3:
                if not team.name:
                    team.name = get_team_name()
                while len(team) < 3:
                    f = temp.pop()
                    f.arena_active = True
                    #f.arena_permit = True
                    if f.arena_rep == 0:
                        f.arena_rep = int(f.level * 500 * random.uniform(.9, 1.1))
                    team.add(f)

            self.update_ladder() # Populate the reputation ladder:
            self.update_matches()
            self.update_teams()
            self.find_opfor()
            self.update_dogfights()

        # -------------------------- ChainFights vs Mobs ------------------------>
        def run_chainfight(self, setup, off_team, logical):
            """Running a chainfight.
            """
            combat_log = []
            for encounter in xrange(1, 6):
                combat_log.append("--------------- Round %d ---------------" % encounter)

                # Picking an opponent(s):
                num_opps = len(off_team)
                enemy_team = Team(name=setup["id"], max_size=num_opps)

                mob_level = setup["level"]
                mob_level += mob_level*(.1*encounter)
                if encounter == 5: # Boss!
                    mob_level = round_int(mob_level*1.1) # 10% extra for the Boss!
                    enemy_team.add(build_mob(setup["boss"], level=mob_level))
                    num_opps -= 1
                else:
                    mob_level = round_int(mob_level)

                # Add the same amount of mobs as there characters on the off team:
                for i in range(num_opps):
                    mob = build_mob(choice(setup["mobs"]), level=mob_level)
                    enemy_team.add(mob)

                # Mini-Game only for the hero
                if off_team == hero.team:
                    # Get team luck:
                    luck = sum((member.get_stat("luck") for member in off_team)) 
                    luck = float(luck)/len(off_team)

                    # Bonus:
                    if dice(25 + encounter*3 + luck*.5):
                        self.run_minigame(luck)

                if logical:
                    result = True
                else:
                    result = renpy.call_screen("confirm_chainfight", setup, encounter, enemy_team)
                    if result == "break":
                        return (enemy_team, off_team), combat_log

                # the actual battle
                member_aps = {member: member.PP for member in off_team}

                global battle
                if result is True:
                    battle = run_auto_be(off_team, enemy_team, simple_ai=False)
                else:
                    renpy.music.stop(channel="world")
                    renpy.play(choice(["content/sfx/sound/world/arena/prepare.mp3", "content/sfx/sound/world/arena/new_opp.mp3"]))
                    track = get_random_battle_track()
                    renpy.music.play(track, fadein=1.5)
                    renpy.pause(.5)

                    enemy_team.setup_controller()

                    battle = BE_Core(bg=ImageReference("chainfights"), start_sfx=get_random_image_dissolve(1.5),
                                     end_bg="battle_arena_1", end_sfx=dissolve, give_up="surrender",
                                     max_turns=off_team.leader is not hero, teams=[off_team, enemy_team])
                    battle.start_battle()

                    # Reset the controllers:
                    #off_team.reset_controller()
                    enemy_team.reset_controller()

                    renpy.music.stop(fadeout=1.0)

                combat_log.extend(battle.combat_log)
                if battle.winner != off_team:
                    return (enemy_team, off_team), combat_log

                for member, aps in member_aps.iteritems():
                    member_aps[member] = (aps - member.PP)/100.0 # PP_PER_AP = 100

                # Awards:
                #  - No cash, low a-rep, low EXP and items at the end - 
                #  a bit of reputation
                rep = max(int(mob_level*.2), 1)

                combat_stats = dict()
                for member in off_team:
                    statdict = OrderedDict()
                    if member in battle.corpses:
                        statdict["K.O."] = "Yes"
                    else:
                        rew_xp = exp_reward(member, enemy_team, exp_mod=member_aps[member]*.15)
                        if rew_xp:
                            member.mod_exp(rew_xp)
                            statdict["Exp"] = rew_xp

                        member.arena_rep += rep
                        statdict["Arena Rep"] = rep
                    combat_stats[member] = statdict

                for member in enemy_team:
                    defeated_mobs.add(member.id)
                    combat_stats[member] = OrderedDict([("K.O.", "Yes")])
                # Ladder
                self.update_ladder()

                if encounter <= 4:
                    if not logical:
                        renpy.call_screen("arena_aftermatch", off_team, enemy_team, combat_stats, True)
                    continue

                # rewards
                leader = off_team.leader
                amount = 2
                amount += min(round_int(leader.arena_rep/max(15000.0, self.ladder[0].arena_rep / 3.0)), 3)
                tier = mob_level/40.0
                #types = ['scroll', 'restore', 'armor', 'weapon'] 
                types = "all" 
                rewards = get_item_drops(types=types, tier=tier, locations=["Arena"], amount=amount)
                for i in rewards:
                    leader.inventory.append(i)

                if not logical:
                    renpy.call_screen("arena_finished_chainfight", off_team, enemy_team, combat_stats, rewards)

            # end of the chainfight
            return (off_team, enemy_team), combat_log

        def run_minigame(self, luck):
            # New total is 300, each of the stats may get 25!
            length = 300
            hpbar = 20
            mpbar = 20
            vpbar = 20

            # Luck mod:
            if dice(luck):
                hpbar += 5
            if dice(luck):
                mpbar += 5
            if dice(luck):
                vpbar += 5
            black = (length-(hpbar+mpbar+vpbar))/2 # Bupkis
 
            # Color: range (int) pairs =======>>>
            data = (("black", black), ("red", hpbar), ("blue", mpbar), ("green", vpbar), ("black", black))

            # Pass the minigame screen:
            renpy.call_screen("arena_minigame", data, length)

        def settle_minigame(self, udd, data):
            # Award the bonuses:
            value = udd.value

            for idx, (color, val) in enumerate(data):
                value -= val
                if value <= 0:
                    break

            bonus = (None, "health", "mp", "vitality", None)
            reward = bonus[idx]

            if reward:
                for member in hero.team:
                    member.mod_stat(reward, member.get_max(reward))
            else:
                reward = "bupkis"

            return reward

        # -------------------------- Battle/Next Day ------------------------------->
        @staticmethod
        def arena_rep_reward(loser, winner):
            return max(0.0, (loser.get_rep() - (winner.get_rep() / 2)) / 10.0)

        def auto_resolve_combat(self, off_team, def_team, type="dogfight"):

            battle = run_auto_be(off_team, def_team, simple_ai=True)

            winner = battle.winner
            loser = off_team if winner == def_team else def_team

            rep = self.arena_rep_reward(loser, winner)
            if type != "match":
                rep = min(50.0, max(3.0, rep))

            for fighter in winner:
                if fighter not in battle.corpses:
                    for stat in ("attack", "defence", "agility", "magic"):
                        fighter.mod_stat(stat, randint(1, 2))
                    fighter.arena_rep += int(rep)
                    fighter.mod_exp(exp_reward(fighter, loser, exp_mod=2))

            rep = rep / 10.0
            for fighter in loser:
                fighter.arena_rep -= int(rep)

            if type == "match":
                self.update_setups(winner, loser)

            return winner, loser

        def run_dogfight(self, def_team, off_team, logical):
            '''
            Bridge to battle engine + rewards/penalties
            '''
            member_aps = {member: member.PP for member in chain(off_team, def_team)}
            member_hps = {member: member.get_stat("health") for member in chain(off_team, def_team)}

            global battle
            if logical is True:
                battle = run_auto_be(off_team, def_team, simple_ai=False)
            else:
                renpy.music.stop(channel="world")
                renpy.play(choice(["content/sfx/sound/world/arena/prepare.mp3", "content/sfx/sound/world/arena/new_opp.mp3"]))
                track = get_random_battle_track()
                renpy.music.play(track, fadein=1.5)
                renpy.pause(.5)

                def_team.setup_controller()

                battle = BE_Core(bg="battle_dogfights_1", start_sfx=get_random_image_dissolve(1.5),
                                 end_bg="battle_arena_1", end_sfx=dissolve, give_up="surrender",
                                 max_turns=off_team.leader is not hero, teams=[off_team, def_team])
                battle.start_battle()

                # Reset the controllers:
                #off_team.reset_controller()
                def_team.reset_controller()

                renpy.music.stop(fadeout=1.0)

            winner = battle.winner
            loser = def_team if winner is off_team else off_team

            for member, aps in member_aps.iteritems():
                member_aps[member] = (aps - member.PP)/100.0 # PP_PER_AP = 100

            finish_health = 0
            for member in off_team:
                finish_health += member.get_stat("health")

            # Awards: 
            #  - Decent cash, low a-rep and normal EXP. -
            #  Max gold as a constant with added blood money:
            max_gold = (def_team.get_level()+off_team.get_level())*5
            blood = sum((member_hps[member] - member.get_stat("health") for member in winner))
            rew_gold = round_int(max_gold*(float(loser.get_level())/max(1, winner.get_level())))
            if blood > 0:
                rew_gold += blood
            #  a bit of reputation
            rep = min(50, max(3, self.arena_rep_reward(loser, winner)))

            combat_stats = dict()
            for member in winner:
                statdict = OrderedDict()
                if member in battle.corpses:
                    statdict["K.O."] = "Yes"
                    rew_xp = exp_reward(member, loser, exp_mod=member_aps[member]*.15)
                    if rew_xp:
                        member.mod_exp(rew_xp)
                        statdict["Exp"] = rew_xp
                else:
                    rew_xp = exp_reward(member, loser, exp_mod=member_aps[member])
                    if rew_xp:
                        member.mod_exp(rew_xp)
                        statdict["Exp"] = rew_xp

                    member.add_money(rew_gold, reason="Arena")
                    statdict["Gold"] = rew_gold

                    rew_rep = int(rep)
                    member.arena_rep += rew_rep
                    statdict["Arena Rep"] = rew_rep

                    if dice(loser.get_level()):
                        if random.random() > .5:
                            member.mod_stat("fame", 1)
                            statdict["Fame"] = 1
                        if random.random() > .5:
                            member.mod_stat("reputation", 1)
                            statdict["Reputation"] = 1
                combat_stats[member] = statdict

            rep = -int(rep / 10.0)
            for member in loser:
                statdict = OrderedDict()
                if member in battle.corpses:
                    statdict["K.O."] = "Yes"
                    mod = .15
                else:
                    mod = .3
                rew_xp = exp_reward(member, winner, exp_mod=member_aps[member]*mod)
                if rew_xp:
                    member.mod_exp(rew_xp)
                    statdict["Exp"] = rew_xp
                if rep:
                    member.arena_rep += rep
                    statdict["Arena Rep"] = rep
                combat_stats[member] = statdict
                self.remove_team_from_dogfights(member)

            for member in def_team:
                restore_battle_stats(member)

            if not logical:
                renpy.call_screen("arena_aftermatch", winner, loser, combat_stats, off_team is winner)

            # Ladder
            self.update_ladder()

            # record the event
            self.df_count += 1

            return (winner, loser), list(battle.combat_log)

        @staticmethod
        def shallow_copy_team(team):
            """
            Create a shallow copy of the team to preserve the important team informations for today's report
            """ 
            return Team(name=team.name, implicit=team.members, max_size=team.max_size)

        def run_matchfight(self, def_team, off_team, logical):
            """
            Bridge to battle engine + rewards/penalties.
            """
            member_aps = {member: member.PP for member in chain(off_team, def_team)}

            global battle
            if logical:
                battle = run_auto_be(off_team, def_team, simple_ai=False)
            else:
                renpy.music.stop(channel="world")
                renpy.play(choice(["content/sfx/sound/world/arena/prepare.mp3", "content/sfx/sound/world/arena/new_opp.mp3"]))
                track = get_random_battle_track()
                renpy.music.play(track, fadein=1.5)
                renpy.pause(.5)

                def_team.setup_controller()

                battle = BE_Core(bg="battle_arena_1", start_sfx=get_random_image_dissolve(1.5),
                                 end_bg="battle_arena_1", end_sfx=dissolve, give_up="surrender",
                                 max_turns=off_team.leader is not hero, teams=[off_team, def_team])
                battle.start_battle()

                # Reset the controllers:
                #off_team.reset_controller()
                def_team.reset_controller()

                renpy.music.stop(fadeout=1.0)

            winner = battle.winner
            loser = def_team if winner is off_team else off_team

            for member, aps in member_aps.iteritems():
                member_aps[member] = (aps - member.PP)/100.0 # PP_PER_AP = 100

            # Awards:
            #  - Decent cash, decent a-rep, normal EXP -
            rew_rep = self.arena_rep_reward(loser, winner)
            rew_gold = int(max(200, 250*(float(loser.get_level()) /max(1, winner.get_level()))))

            combat_stats = dict()
            for member in winner:
                statdict = OrderedDict()
                if member in battle.corpses:
                    statdict["K.O."] = "Yes"
                    rew_xp = exp_reward(member, loser, exp_mod=member_aps[member]*.15)
                    if rew_xp:
                        member.mod_exp(rew_xp)
                        statdict["Exp"] = rew_xp
                else:
                    rew_xp = exp_reward(member, loser, exp_mod=member_aps[member])
                    if rew_xp:
                        member.mod_exp(rew_xp)
                        statdict["Exp"] = rew_xp

                    member.add_money(rew_gold, reason="Arena")
                    statdict["Gold"] = rew_gold

                    rew_r = int(rew_rep)
                    if rew_r:
                        member.arena_rep += rew_r
                        statdict["Arena Rep"] = rew_r

                    if dice(loser.get_level()):
                        rew_fame = randrange(3)
                        if rew_fame:
                            member.mod_stat("fame", rew_fame)
                            statdict["Fame"] = rew_fame
                        rew_r = randrange(3)
                        if rew_r:
                            member.mod_stat("reputation", rew_r)
                            statdict["Reputation"] = rew_r
                combat_stats[member] = statdict

            rew_rep = -int(rew_rep / 10.0)
            for member in loser:
                statdict = OrderedDict()
                if member in battle.corpses:
                    statdict["K.O."] = "Yes"
                    mod = .15
                else:
                    mod = .3
                rew_xp = exp_reward(member, winner, exp_mod=member_aps[member]*mod)
                if rew_xp:
                    member.mod_exp(rew_xp)
                    statdict["Exp"] = rew_xp
                if rew_rep:
                    member.arena_rep += rew_rep
                    statdict["Arena Rep"] = rew_rep
                combat_stats[member] = statdict
                # self.remove_team_from_dogfights(member)

            for member in def_team:
                restore_battle_stats(member)

            if not logical:
                renpy.call_screen("arena_aftermatch", winner, loser, combat_stats, off_team is winner)

            # Update match
            setup = self.get_arena_match(team=def_team)
            setup[0] = setup[1] = Arena.EMPTY_TEAM

            # Line-up positioning:
            self.update_setups(winner, loser)

            # Ladder
            self.update_ladder()

            # record the event
            self.daily_match_results.append((self.shallow_copy_team(winner), self.shallow_copy_team(loser)))

            return (winner, loser), list(battle.combat_log)

        @staticmethod
        def append_match_result(txt, f2f, match_result):
            winner, loser = match_result
            if f2f:
                temp = "%s has defeated %s in a one on one fight. " % (winner.leader.name, loser.leader.name)
            else:
                temp = "%s team has defeated %s in an official match. " % (winner.name, loser.name)
            temp += choice(["It was quite a show!",
                            "Amazing performance!",
                            "Crowd never stopped cheering!",
                  ("The crowd chanted %s name for minutes!" if f2f else
                  "Team's leader %s got most of the credit!") % winner.leader.name])
            txt.append(temp)

        @staticmethod
        def missed_match_result(txt, off_team, def_team):
            # player missed an Arena match -> Rep penalty!
            rep_penalty = max(500, (def_team.get_rep()/10))
            leader = off_team.leader
            leader.arena_rep -= rep_penalty

            if len(def_team) == 1:
                def_team = def_team.leader
                temp = "%s {color=red}missed{/color} a 1v1 fight against %s, who entrained the public by boasting of %s prowess " \
                        "and making funny jabs at %s's cowardliness!" % (leader.name, def_team.name, def_team.pd, leader.name)
            else:
                temp = "%s {color=red}didn't show up{/color} for a team combat against %s! The spectators were very displeased!" % (off_team.name, def_team.name)

            txt.append(temp)

        def next_day(self):
            # For the daily report:
            txt = []

            # Normalizing amount of teams available for the Arena.
            fday = store.day
            if not fday % 5:
                self.update_teams()

            self.find_opfor()

            # Add results run during the day
            for match_result in self.daily_match_results:
                self.append_match_result(txt, len(match_result[0]) == 1, match_result)

                # update fighting_days
                for f in chain(match_result[0], match_result[1]):
                    f.fighting_days.remove(fday)

            tl.start("Arena: Matches")
            # Running the matches:
            # Join string method is used here to improve performance over += or + (Note: Same should prolly be done for jobs.)
            for size, matches in enumerate([self.matches_1v1, self.matches_2v2, self.matches_3v3], 1):
                for setup in matches:
                    if setup[2] == fday:
                        off_team, def_team = setup[0], setup[1]
                        if off_team and def_team:
                            leader = off_team.leader
                            if leader is not hero and leader.employer is not hero:
                                match_result = self.auto_resolve_combat(off_team, def_team, "match")
                                self.append_match_result(txt, size == 1, match_result)
                            else:
                                self.missed_match_result(txt, off_team, def_team)

                        # update fighting_days
                        for f in chain(off_team, def_team):
                            f.fighting_days.remove(fday)

                        setup[0] = setup[1] = Arena.EMPTY_TEAM

            self.update_matches()
            tl.end("Arena: Matches")

            # Some random dogfights
            # 1v1:
            tl.start("Arena: Dogfights")
            dogfighters = self.get_dogfights_fighters()
            opfor_pool = [f for f in self.get_arena_candidates() if self.check_if_team_ready_for_dogfight(f, dogfighters)]
            dogfights = [t for t in self.dogfights_1v1 if self.check_if_team_ready_for_dogfight(f)]

            shuffle(opfor_pool)
            shuffle(dogfights)

            for __ in xrange(min(min(randint(4, 7), len(dogfights)), len(opfor_pool))):
                defender = dogfights.pop()
                opfor = Team(implicit=[opfor_pool.pop()], max_size=1)
                self.auto_resolve_combat(opfor, defender)
                self.df_count += 1

            # 2v2:
            dogfights = self.dogfights_2v2
            opfor_pool = [t for t in self.teams_2v2 if self.check_if_team_ready_for_dogfight(t, dogfights)]
            dogfights = [t for t in dogfights if self.check_if_team_ready_for_dogfight(f)]

            shuffle(opfor_pool)
            shuffle(dogfights)

            for __ in xrange(min(min(randint(2, 4), len(dogfights)), len(opfor_pool))):
                defender = dogfights.pop()
                opfor = opfor_pool.pop()
                self.auto_resolve_combat(opfor, defender)
                self.df_count += 1

            # 3v3:
            dogfights = self.dogfights_3v3
            opfor_pool = [t for t in self.teams_3v3 if self.check_if_team_ready_for_dogfight(t, dogfights)]
            dogfights = [t for t in dogfights if self.check_if_team_ready_for_dogfight(f)]

            shuffle(opfor_pool)
            shuffle(dogfights)

            for __ in xrange(min(min(randint(2, 4), len(dogfights)), len(opfor_pool))):
                defender = dogfights.pop()
                opfor = opfor_pool.pop()
                self.auto_resolve_combat(opfor, defender)
                self.df_count += 1

            self.update_dogfights()
            tl.end("Arena: Dogfights")

            txt.append("%d unofficial dogfights took place yesterday!" % self.df_count)

            # Update top 100 ladder:
            self.update_ladder()

            # Update arena actives
            self.update_actives()

            # Warning the player of a scheduled arena match:
            fday += 1
            for setup in chain(self.matches_1v1, self.matches_2v2, self.matches_3v3):
                if setup[2] != fday:
                    continue
                off_team, def_team = setup[0], setup[1]
                if off_team and def_team:
                    num = len(off_team)
                    if num == 1:
                        ladder = self.ladder_1v1
                    elif num == 2:
                        ladder = self.ladder_2v2
                    elif num == 3:
                        ladder = self.ladder_3v3
                    else:
                        raise Exception("Invalid team size for next_day/matches: %d" % num)

                    for idx, team in enumerate(ladder):
                        if team == off_team or team == def_team:
                            idx = 3 * idx / len(ladder)
                            temp = ["very", "really", "quite"][idx]
                            temp = choice(["The upcoming match between %s and %s looks {} interesting.",
                                           "%s challenged %s in the Arena. The match is going to be {} entertaining!",
                                           "Today's match of %s and %s is going to be {} spectacular (according to our sources).",
                                           "%s and %s are going to provide a {} good show for the spectators of the Arena.",
                                           "The scheduled match of %s against %s seems {} promising."]).format(temp)
                            break
                    else:
                        temp = choice(["There is going to be a match between %s and %s, but we do not know much about them...",
                                       "The match of %s and %s takes place today, but it is quite possible that no one will remember it tomorrow."])
                    if num == 1:
                        off_team = off_team[0]
                        def_team = def_team[0]
                    txt.append(temp % ("{b}" + off_team.name + "{/b}", "{b}" +def_team.name + "{/b}"))


            # Reset daily variables
            self.daily_report = gazette.arena = txt
            self.daily_match_results = []
            self.df_count = 0
