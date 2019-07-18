init -9 python:
    # ========================= Arena and related ===========================>>>
    class Arena(_object):
        """
        First prototype of Arena, will take care of most related logic and might have to be split in the future.
        @Note to myself: This code needs to be updated post-Alpha release to account for Arena Fighters and restructured for further use in the game!
        -------------------------->
        """
        def __init__(self):
            super(Arena, self).__init__()
            # self.1v1 = list() # Tracking the 1v1 fights.
            # self.teams = list() # Tracking the team fights.

            # Team Lineups and Scheduled matches:
            #                      Off Team           Def Team      Day
            self.matches_1v1 = [[Team(max_size=1), Team(max_size=1), 1] for i in xrange(8)]
            #                      Off Team           Def Team      Day
            self.matches_2v2 = [[Team(max_size=2), Team(max_size=2), 1] for i in xrange(5)]
            #                      Off Team           Def Team      Day
            self.matches_3v3 = [[Team(max_size=3), Team(max_size=3), 1] for i in xrange(5)]
            self.lineup_1v1 = [Team(max_size=1) for i in xrange(20)]
            self.lineup_2v2 = [Team(max_size=2) for i in xrange(10)]
            self.lineup_3v3 = [Team(max_size=3) for i in xrange(10)]
            self.ladder = [None] * 100

            # ----------------------------->
            self.king = None

            # A list of Arena Fighters loaded into the game and actively participating in the Arena.
            self.teams_2v2 = list()
            self.teams_3v3 = list()

            self.dogfights_1v1 = list()
            self.dogfights_2v2 = list()
            self.dogfights_3v3 = list()
            self.dogfight_day = 1

            self.df_count = 0
            self.hero_match_result = None
            self.daily_report = []

            # Chanfighting:
            self.cf_mob = None
            self.cf_setup = None
            self.cf_count = 0

        # -------------------------- Sorting ---------------------------------------------------------->
        def get_matches_fighters(self, matches="all"):
            '''
            Returns all fighters that are set to participate at official maches.
            '''
            if matches == "1v1":
                fighters = set([f for lineup in self.matches_1v1 for f in itertools.chain(lineup[0].members, lineup[1].members)])
            elif matches == "2v2":
                fighters = set([f for lineup in self.matches_2v2 for f in itertools.chain(lineup[0].members, lineup[1].members)])
            elif matches == "3v3":
                fighters = set([f for lineup in self.matches_3v3 for f in itertools.chain(lineup[0].members, lineup[1].members)])
            else:
                fighters = set([f for lineup in self.matches_1v1 for f in itertools.chain(lineup[0].members, lineup[1].members)])
                fighters.update([f for lineup in self.matches_2v2 for f in itertools.chain(lineup[0].members, lineup[1].members)])
                fighters.update([f for lineup in self.matches_3v3 for f in itertools.chain(lineup[0].members, lineup[1].members)])

            return fighters

        def get_teams_fighters(self, teams="all"):
            """
            Returns fighters that are in the Arena teams.
            """
            if teams == "2v2":
                fighters = set([f for team in self.teams_2v2 for f in team.members])
            elif teams == "3v3":
                fighters = set([f for team in self.teams_3v3 for f in team.members])
            else:
                fighters = set([f for team in self.teams_2v2 for f in team.members])
                fighters.update([f for team in self.teams_3v3 for f in team.members])
            return fighters

        def get_lineups_fighters(self, lineup="all"):
            """
            Returns fighters currently in Arena lineups (heavyweights basically)
            """
            if lineup == "1v1":
                fighters = set([f for team in self.lineup_1v1 for f in team.members])
            elif lineup == "2v2":
                fighters = set([f for team in self.lineup_2v2 for f in team.members])
            elif lineup == "3v3":
                fighters = set([f for team in self.lineup_3v3 for f in team.members])
            else:
                fighters = set([f for team in self.lineup_1v1 for f in team.members])
                fighters.update([f for team in self.lineup_2v2 for f in team.members])
                fighters.update([f for team in self.lineup_3v3 for f in team.members])

            return fighters

        def get_dogfights_fighters(self, dogfights="all"):
            """
            All fighters that are currently in dogfights!
            """
            if dogfights == "1v1":
                fighters = set([f for team in self.dogfights_1v1 for f in team.members])
            elif dogfights == "2v2":
                fighters = set([f for team in self.dogfights_2v2 for f in team.members])
            elif dogfights == "3v3":
                fighters = set([f for team in self.dogfights_3v3 for f in team.members])
            else:
                fighters = set([f for team in self.dogfights_1v1 for f in team.members])
                fighters.update([f for team in self.dogfights_2v2 for f in team.members])
                fighters.update([f for team in self.dogfights_3v3 for f in team.members])

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
        def check_if_team_ready_for_dogfight(unit, dogfighters):
            """
            Checks if a team/fighter is ready for dogfight by eliminating them on grounds of health, scheduled matches, presense in other dogfights or lack of AP.
            """
            if unit in dogfighters:
                return False
            
            if isinstance(unit, Team):
                fighters = unit.members
            else:
                fighters = [unit]
                
            for member in fighters:
                if member.get_stat("health") < member.get_max("health")*9/10:
                    return False
                if day+1 in member.fighting_days:
                    return False
                if member.PP < 200: # PP_PER_AP
                    return False

            return True

        # -------------------------- Update Methods ---------------------------------------------->
        def update_teams(self):
            '''Makes sure that there are enough teams for Arena to function properly.
            If members are removed from teams directly, it is up to the respective method to find a replacement...
            '''
            candidates = None
            if len(self.teams_2v2) < 30:
                if candidates is None:
                    candidates = self.get_arena_candidates()
                inteams_2v2 = self.get_teams_fighters(teams="2v2")
                templist = [fighter for fighter in candidates if fighter not in inteams_2v2]
                shuffle(templist)

                for __ in xrange(min(30, len(templist)/2)):
                    team = Team(max_size=2)
                    team.name = get_team_name()
                    f = templist.pop()
                    f.arena_active = True
                    team.add(f)
                    f = templist.pop()
                    f.arena_active = True
                    team.add(f)
                    self.teams_2v2.append(team)

            if len(self.teams_3v3) < 30:
                if candidates is None:
                    candidates = self.get_arena_candidates()
                inteams_3v3 = self.get_teams_fighters(teams="3v3")
                templist = [fighter for fighter in candidates if fighter not in inteams_3v3]
                shuffle(templist)

                for __ in xrange(min(30, len(templist)/3)):
                    team = Team(max_size=3)
                    team.name = get_team_name()
                    f = templist.pop()
                    f.arena_active = True
                    team.add(f)
                    f = templist.pop()
                    f.arena_active = True
                    team.add(f)
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
            if len(self.dogfights_1v1) < 20:
                candidates = self.get_arena_candidates()
                dogfighters = self.get_dogfights_fighters()
                candidates = [f for f in candidates if f not in dogfighters]
                shuffle(candidates)

                amount = min(min(randint(15, 20), 20 - len(self.dogfights_1v1)), len(candidates))
                in_range_exists = len([f for f in dogfighters if f.level in level_range])

                # do first pass over those candidates who's level is near Hero's
                for f in candidates[:]:
                    if amount == 0 or in_range_exists >= 5:
                        break

                    if f.level in level_range:
                        amount -= 1
                        in_range_exists += 1
                        team = Team(max_size=1)
                        f.arena_active = True
                        team.add(f)
                        candidates.remove(f)
                        self.dogfights_1v1.append(team)


                while amount != 0:
                    amount -= 1
                    team = Team(max_size=1)
                    f = candidates.pop()
                    f.arena_active = True
                    team.add(f)
                    self.dogfights_1v1.append(team)

            # 2v2
            for teams, teams_setup in ([self.teams_2v2, self.dogfights_2v2],
                                       [self.teams_3v3, self.dogfights_3v3]):
                if len(teams_setup) < 15:
                    candidates = [team for team in teams if team not in teams_setup]
                    amount = min(min(randint(8, 15), 15 - len(teams_setup)), len(candidates))
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
            # 1vs1:
            teams = None
            for setup in self.matches_1v1:
                if not len(setup[1]):
                    setup[2] = day + randint(3, 14)
                    if teams is None:
                        match_fighters = self.get_matches_fighters(matches="1v1")
                        match_fighters.add(hero)
                        teams = list(i for i in self.lineup_1v1 if setup[2] not in i.leader.fighting_days and i.leader not in match_fighters)
                        shuffle(teams)
                    if teams:
                        c_team = teams.pop()
                        c_team.leader.fighting_days.append(setup[2])
                        setup[1] = c_team

            teams = None
            for setup in self.matches_2v2:
                if not len(setup[1]):
                    setup[2] = day + randint(3, 14)
                    if teams is None:
                        match_fighters = self.get_matches_fighters(matches="2v2")
                        match_fighters.add(hero)
                        teams = list()
                        for team in self.lineup_2v2:
                            for fighter in team:
                                if setup[2] in fighter.fighting_days or fighter in match_fighters:
                                    break
                            else:
                                teams.append(team)
                        shuffle(teams)
                    if teams:
                        c_team = teams.pop()
                        for fighter in c_team.members:
                            fighter.fighting_days.append(setup[2])
                        setup[1] = c_team

            teams = None
            for setup in self.matches_3v3:
                if not len(setup[1]):
                    setup[2] = day + randint(3, 14)
                    if teams is None:
                        match_fighters = self.get_matches_fighters(matches="3v3")
                        match_fighters.add(hero)
                        teams = list()
                        for team in self.lineup_3v3:
                            for fighter in team.members:
                                if setup[2] in fighter.fighting_days or fighter in match_fighters:
                                    break
                            else:
                                teams.append(team)
                        shuffle(teams)
                    if teams:
                        c_team = teams.pop()
                        for fighter in c_team.members:
                            fighter.fighting_days.append(setup[2])
                        setup[1] = c_team

        def update_setups(self, winner, loser):
            """
            Resonsible for repositioning winners + losers in setups!
            """
            team_size = len(winner)
            if team_size == 1:
                lineup = self.lineup_1v1
            elif team_size == 2:
                lineup = self.lineup_2v2
            elif team_size == 3:
                lineup = self.lineup_3v3
            else:
                raise Exception("Invalid team size for Automatic Arena Combat Resolver: %d" % team_size)

            if winner in lineup:
                index = lineup.index(winner)
                if index != 0:
                    lineup[index], lineup[index-1] = lineup[index-1], winner
            else:
                # check if the hero has an another team in the lineup
                if winner == hero.team:
                    for idx, t in enumerate(lineup):
                        if t.leader == hero:
                            # another team in the lineup -> replace it with the current one
                            lineup[idx] = winner
                            winner_added = True
                            break
                if not "winner_added" in locals():
                    lineup[-1] = winner

            if loser in lineup:
                index = lineup.index(loser)
                if index != len(lineup)-1:
                    lineup[index], lineup[index+1] = lineup[index+1], loser

        def find_opfor(self):
            """
            Find a team to fight challenger team in the official arena matches.
            """
            # 1vs1:
            fighters = None
            for setup in self.matches_1v1:
                if setup[0]:
                    continue
                if setup[2] == day:
                    deadline = 100
                elif setup[2] > day + 2:
                    deadline = 50
                else:
                    deadline = 15
                if dice(deadline):
                    if fighters is None:
                        match_fighters = self.get_matches_fighters(matches="1v1")
                        fighters = [i for i in self.get_arena_candidates() if setup[2] not in i.fighting_days and i not in match_fighters]
                        shuffle(fighters)

                    if fighters:
                        f = fighters.pop()
                        f.fighting_days.append(setup[2])
                        f.arena_active = True
                        setup[0].add(f)

            # 2vs2
            teams = None
            for setup in self.matches_2v2:
                if setup[0]:
                    continue
                if setup[2] == day:
                    deadline = 100
                elif setup[2] > day + 3:
                    deadline = 50
                else:
                    deadline = 20
                if dice(deadline):
                    if teams is None:
                        match_fighters = self.get_matches_fighters(matches="2v2")
                        teams = []
                        for team in self.teams_2v2:
                            for fighter in team.members:
                                if setup[2] in fighter.fighting_days or fighter in match_fighters:
                                    break
                            else:
                                teams.append(team)
                        shuffle(teams)
                    if teams:
                        c_team = teams.pop()
                        for fighter in c_team:
                            fighter.fighting_days.append(setup[2])
                        setup[0] = c_team

            # 3vs3
            teams = None
            for setup in self.matches_3v3:
                if setup[0]:
                    continue
                if setup[2] == day:
                    deadline = 100
                elif setup[2] > day + 3:
                    deadline = 50
                else:
                    deadline = 25
                if dice(deadline):
                    if teams is None:
                        match_fighters = self.get_matches_fighters(matches="3v3")
                        teams = []
                        for team in self.teams_3v3:
                            for fighter in team:
                                if setup[2] in fighter.fighting_days or fighter in match_fighters:
                                    break
                            else:
                                teams.append(team)
                        shuffle(teams)
                    if teams:
                        c_team = teams.pop()
                        for fighter in c_team:
                            fighter.fighting_days.append(setup[2])
                        setup[0] = c_team

        # -------------------------- GUI methods ---------------------------------->
        def dogfight_challenge(self, team):
            """
            Checks if player team is ready for a dogfight.
            """
            if len(hero.team) != len(team):
                return "Make sure that your team has %d members!"%len(team)
            for member in hero.team:
                if member.status == "slave":
                    return "%s is a slave and slaves are not allowed to fight in the Arena under the penalty of death to both a slave and the owner!"%member.name

            hlvl = hero.team.get_level()
            elvl = team.get_level()
            if elvl > max(hlvl+12, hlvl*1.3):
                if len(team) == 1:
                    team.leader.say("You're not worth my time, go train some.")
                    return
                else:
                    team.leader.say("You guys need to grow up before challenging the likes of us.")
                    return
            if max(elvl+12, elvl*1.3) < hlvl:
                if len(team) == 1:
                    team.leader.say("I am not feeling up to it... really!")
                    return
                else:
                    team.leader.say("We are not looking for a fight outside of our league.")
                    return

            renpy.scene(layer="screens")

            self.run_dogfight(team)

        def match_challenge(self, setup):
            """
            Checks if player already has fight setup on a given day.
            Handles confirmation screen for the fight.

            Adds player team to a setup.
            Now also checks if player has an Arena permit.
            """
            if not hero.arena_permit:
                return "Arena Permit is required to fight in the official matches!"

            fight_day = setup[2]

            if fight_day in hero.fighting_days:
                return "You already have a fight planned for day %d. Having two official matches on the same day is not allowed!"%fight_day

            if fight_day == day and self.hero_match_result:
                return "You already had a fight today. Having two official matches on the same day is not allowed!"

            result = renpy.call_screen("yesno_prompt",
                "Are you sure you want to schedule a fight? Backing out of it later will mean a hit on reputation!",
                Return(["Yes"]), Return(["No"]))
            if result == ["Yes"]:
                setup[0] = hero.team
                hero.fighting_days.append(fight_day)

        def check_before_matchfight(self):
            """
            Checks if player team is correctly setup before an official match.
            """
            # Figure out who we're fighting:
            for setup in list(itertools.chain(self.matches_1v1, self.matches_2v2, self.matches_3v3)):
                if setup[2] == day and setup[0].leader == hero:
                    battle_setup = setup
                    team = setup[1]

            if len(hero.team) != len(team):
                return "Make sure that your team has %d members!" % len(team)

            for member in hero.team:
                if member.status == "slave":
                    return "%s is a slave and slaves are not allowed to fight in the Arena under the penalty of death to both slave and the owner!"%member.name

            renpy.hide_screen("arena_inside")
            renpy.hide_screen("arena_1v1_fights")
            renpy.hide_screen("arena_2v2_fights")
            renpy.hide_screen("arena_3v3_fights")

            self.execute_matchfight(battle_setup)

        # -------------------------- Setup Methods -------------------------------->
        def update_ladder(self):
            # Update top 100 ladder:
            candidates = self.get_arena_fighters()
            if hero.arena_rep > 0:
                candidates.append(hero)
            candidates.sort(reverse=True, key=attrgetter("arena_rep"))

            self.ladder = candidates[:len(self.ladder)]

        def update_actives(self):
            actives = set(self.ladder) | self.get_teams_fighters() | self.get_lineups_fighters() | self.get_dogfights_fighters() | self.get_matches_fighters()

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
                    if teamsize == 1:
                        if lineups == 1:
                            raise Exception("Number one spot for 1v1 ladder (lineup) is reserved by the game!")
                        if not self.lineup_1v1[lineups-1]:
                            self.lineup_1v1[lineups-1] = a_team
                        else:
                            raise Exception("Team %s failed to take place %d in 1v1" \
                                            "lineups is already taken by another team (%s), check your arena_teams.json" \
                                            "file." % (a_team.name, team["lineups"], self.lineup_1v1[team["lineups"]-1].name))
                    elif teamsize == 2:
                        if not self.lineup_2v2[lineups-1]:
                            self.lineup_2v2[lineups-1] = a_team
                            self.teams_2v2.append(a_team)
                        else:
                            raise Exception("Team %s failed to take place %d " \
                                "in 2v2 lineups is already taken by another team (%s), " \
                                "check your arena_teams.json file."%(a_team.name,
                                team["lineups"], self.lineup_2v2[lineups-1].name))
                    else: # if teamsize == 3:
                        if not self.lineup_3v3[lineups-1]:
                            self.lineup_3v3[lineups-1] = a_team
                            self.teams_3v3.append(a_team)
                        else:
                            raise Exception("Team %s failed to take place %d in" \
                            " 3v3 lineups is already taken by another team (%s), " \
                            "check your arena_teams.json file."%(a_team.name, lineups,
                            self.lineup_3v3[lineups-1].name))
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

            for team in self.lineup_1v1:
                if not team:
                    f = temp.pop()
                    f.arena_active = True
                    #f.arena_permit = True
                    if f.arena_rep == 0:
                        f.arena_rep = int(f.level * 500 * random.uniform(.9, 1.1))
                    team.add(f)

            # 2v2 Ladder lineup:
            temp = candidates[:50]
            shuffle(temp)
            temp.append(self.king)

            for team in self.lineup_2v2:
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

            for team in self.lineup_3v3:
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
        def check_before_chainfight(self):
            """
            Checks before chainfight.
            """
            for member in hero.team:
                if member.status == "slave":
                    return "%s is a Slave forbidden from participation in Combat!"%member.name

            self.cf_count = 1

            # Select Opponent:
            result = renpy.call_screen("chain_fight")
            if result == "break":
                renpy.show_screen("arena_inside")
                return

            self.cf_setup = result

            self.setup_chainfight()

        def setup_chainfight(self):
            """Setting up a chainfight.
            """
            # Picking an opponent(s):
            num_opps = len(hero.team)
            team = Team(name=self.cf_setup.get("id", "Captured Creatures"), max_size=num_opps)

            new_level = self.cf_setup["level"]
            new_level += new_level*(.1*self.cf_count)
            if self.cf_count == 5: # Boss!
                new_level = round_int(new_level*1.1) # 10% extra for the Boss!
                team.add(build_mob(self.cf_setup["boss"], level=new_level))
                num_opps -= 1
            else:
                new_level = round_int(new_level)

            # Add the same amount of mobs as there characters on the MCs team:
            for i in range(num_opps):
                mob = build_mob(choice(self.cf_setup["mobs"]), level=new_level)
                team.add(mob)

            self.cf_mob = team
            self.mob_power = new_level

            luck = 0
            # Get team luck:
            for member in hero.team:
                luck += member.get_stat("luck")
            luck = float(luck)/len(hero.team)

            # Bonus:
            bonus = dice(25+self.cf_count*3 + luck*.5)

            # if DEBUG:
            #     bonus = True
            if bonus:
                self.setup_minigame(luck)

            renpy.show_screen("confirm_chainfight")

        def execute_chainfight(self, auto):
            """
            Bridge to battle engine + rewards/penalties.
            """
            enemy_team = self.cf_mob

            member_aps = []
            for member in hero.team:
                member_aps.append(member.PP)

            renpy.music.stop(channel="world")
            global battle
            if auto is True:
                battle = run_auto_be(hero.team, enemy_team, simple_ai=False)
            else:
                renpy.play(choice(["content/sfx/sound/world/arena/prepare.mp3", "content/sfx/sound/world/arena/new_opp.mp3"]))
                track = get_random_battle_track()
                renpy.pause(1.3)
                renpy.music.play(track, fadein=1.5)

                for mob in enemy_team:
                    mob.controller = Complex_BE_AI(mob)

                battle = BE_Core(bg=ImageReference("chainfights"), start_sfx=get_random_image_dissolve(1.5), give_up="surrender", end_bg="battle_arena_1")
                battle.teams = [hero.team, enemy_team]
                battle.start_battle()

                # Reset the controllers:
                #hero.team.reset_controller()
                enemy_team.reset_controller()

                renpy.music.stop(fadeout=1.0)

            if battle.winner == hero.team:
                for member, aps in zip(hero.team, member_aps):
                    # Awards:
                    if member not in battle.corpses:
                        aps = (aps - member.PP)/100.0 # PP_PER_AP = 100
                        rew_xp = exp_reward(member, enemy_team, exp_mod=aps*.15)
                        rew_rep = max(int(self.mob_power*.2), 1) # only little bit of reputation
                        #rew_gold = 0 # no gold for mobs, because they give items, unlike all other modes
                        member.mod_exp(rew_xp)
                        member.arena_rep += rew_rep
                        #member.add_money(rew_gold, reason="Arena")
                        member.combat_stats = {"exp":rew_xp, "Arena Rep": rew_rep}
                    else:
                        member.combat_stats = "K.O."

                for member in enemy_team:
                    defeated_mobs.add(member.id)
                    member.combat_stats = "K.O."

                # Ladder
                self.update_ladder()

                self.cf_count += 1

                if self.cf_count > 5:
                    amount = 2
                    amount += min(round_int(hero.arena_rep/max(15000.0, self.ladder[0].arena_rep / 3.0)), 3)
                    tier = self.mob_power/40.0
                    #types = ['scroll', 'restore', 'armor', 'weapon'] 
                    types = "all" 
                    rewards = get_item_drops(types=types, tier=tier, locations=["Arena"], amount=amount)
                    for i in rewards:
                        hero.inventory.append(i)

                    self.cf_mob = None
                    self.cf_setup = None
                    self.cf_count = 0
                    renpy.play("win_screen.mp3", channel="world")
                    renpy.show_screen("arena_finished_chainfight", hero.team, enemy_team, rewards)
                else:
                    renpy.show_screen("arena_aftermatch", hero.team, enemy_team, False)
            else: # Player lost -->
                self.cf_mob = None
                self.cf_setup = None
                self.cf_count = 0
                jump("arena_inside")

        def setup_minigame(self, luck):
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
            renpy.play("win_screen.mp3", channel="world")
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

        def auto_resolve_combat(self, off_team, def_team, type="dog_fight"):

            battle = run_auto_be(off_team, def_team, simple_ai=True)

            winner = battle.winner
            loser = off_team if winner == def_team else def_team

            rep = self.arena_rep_reward(loser, winner)
            if type == "dog_fight":
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

        def run_dogfight(self, enemy_team):
            '''
            Bridge to battle engine + rewards/penalties
            '''
            renpy.music.stop(channel="world")
            renpy.play(choice(["content/sfx/sound/world/arena/prepare.mp3",
                               "content/sfx/sound/world/arena/new_opp.mp3"]))
            track = get_random_battle_track()
            renpy.music.play(track, fadein=1.5)
            renpy.pause(.5)

            member_aps = {}
            start_health = 0
            for member in hero.team:
                start_health += member.get_stat("health")
                member_aps[member] = member.PP

            for member in enemy_team:
                member.controller = Complex_BE_AI(member)
                member_aps[member] = member.PP

            global battle
            battle = BE_Core(bg="battle_dogfights_1", start_sfx=get_random_image_dissolve(1.5),
                             end_bg="battle_arena_1", end_sfx=dissolve, give_up="surrender")
            battle.teams = [hero.team, enemy_team]
            battle.start_battle()

            # Reset the controllers:
            #hero.team.reset_controller()
            enemy_team.reset_controller()

            renpy.music.stop(fadeout=1.0)

            winner = battle.winner
            if winner == hero.team:
                loser = enemy_team
            else:
                loser = hero.team

            for member in chain(winner, loser):
                aps = member_aps[member]
                member_aps[member] = (aps - member.PP)/100.0 # PP_PER_AP = 100

            finish_health = 0
            for member in hero.team:
                finish_health += member.get_stat("health")

            # Idea for awards in DF: Decent cash, low a-rep and normal EXP.
            # Max gold as a constant:
            max_gold = (enemy_team.get_level()+hero.team.get_level())*5
            blood = start_health - finish_health
            # Awards:
            rew_gold = round_int(max_gold*(float(loser.get_level())/max(1, winner.get_level())))
            if blood > 0:
                rew_gold += blood

            rep = min(50, max(3, self.arena_rep_reward(loser, winner)))

            for member in winner:
                if member not in battle.corpses:
                    rew_xp = exp_reward(member, loser, exp_mod=member_aps[member])
                    rew_rep = int(rep)

                    member.mod_exp(rew_xp)
                    member.arena_rep += rew_rep
                    member.add_money(rew_gold, reason="Arena")

                    statdict = {"gold":rew_gold, "Arena Rep":rew_rep, "exp":rew_xp}
                    if dice(loser.get_level()):
                        if random.random() > .5:
                            member.mod_stat("fame", 1)
                            statdict["fame"] = 1
                        if random.random() > .5:
                            member.mod_stat("reputation", 1)
                            statdict["reputation"] = 1

                    member.combat_stats = statdict
                else:
                    member.combat_stats = "K.O."

            rep = rep / 10.0
            for member in loser:
                member.arena_rep -= int(rep)
                member.mod_exp(exp_reward(member, winner, exp_mod=member_aps[member]*.15))
                self.remove_team_from_dogfights(member)
                member.combat_stats = "K.O."

            for member in enemy_team:
                restore_battle_stats(member)

            renpy.show_screen("arena_aftermatch", winner, loser)

            # Ladder
            self.update_ladder()

            # record the event
            self.df_count += 1

        @staticmethod
        def shallow_copy_team(team):
            """
            Create a shallow copy of the team to preserve the important team informations for today's report
            """ 
            tmp = Team(name=team.name, implicit=team.implicit, free = team.free, max_size = team.max_size)
            tmp.set_leader(team.leader)
            return tmp

        def execute_matchfight(self, setup):
            """
            Bridge to battle engine + rewards/penalties.
            """
            enemy_team = setup[1]
            renpy.music.stop(channel="world")
            renpy.play(choice(["content/sfx/sound/world/arena/prepare.mp3", "content/sfx/sound/world/arena/new_opp.mp3"]))
            track = get_random_battle_track()
            renpy.pause(1.3)
            renpy.music.play(track, fadein=1.5)

            member_aps = {}
            for member in hero.team:
                member_aps[member] = member.PP

            for member in enemy_team:
                member.controller = Complex_BE_AI(member)
                member_aps[member] = member.PP

            global battle
            battle = BE_Core(bg="battle_arena_1", start_sfx=get_random_image_dissolve(1.5),
                             end_bg="battle_arena_1", end_sfx=dissolve, give_up="surrender")
            battle.teams = [hero.team, enemy_team]
            battle.start_battle()

            # Reset the controllers:
            #hero.team.reset_controller()
            enemy_team.reset_controller()

            renpy.music.stop(fadeout=1.0)

            winner = battle.winner
            if winner == hero.team:
                loser = enemy_team
            else:
                loser = hero.team

            for member in chain(winner, loser):
                aps = member_aps[member]
                member_aps[member] = (aps - member.PP)/100.0 # PP_PER_AP = 100

            rew_rep = self.arena_rep_reward(loser, winner)
            rew_gold = int(max(200, 250*(float(loser.get_level()) /max(1, winner.get_level()))))

            for member in winner:
                if member not in battle.corpses:
                    rew_xp = exp_reward(member, loser, exp_mod=member_aps[member])

                    member.mod_exp(rew_xp)
                    member.arena_rep += int(rew_rep)
                    member.add_money(rew_gold, reason="Arena")

                    statdict = {"gold":rew_gold, "Arena Rep":int(rew_rep), "exp":rew_xp}
                    if dice(loser.get_level()):
                        rew_fame = randrange(3)
                        if rew_fame:
                            member.mod_stat("fame", rew_fame)
                            statdict["fame"] = rew_fame
                        rew_r = randrange(3)
                        if rew_r:
                            member.mod_stat("reputation", rew_r)
                            statdict["reputation"] = rew_r
                    member.combat_stats = statdict
                else:
                    member.combat_stats = "K.O."

            rew_rep = rew_rep / 10.0
            for member in loser:
                member.arena_rep -= int(rew_rep)
                member.mod_exp(exp_reward(member, winner, exp_mod=member_aps[member]*.15))
                # self.remove_team_from_dogfights(member)
                member.combat_stats = "K.O."

            for member in enemy_team:
                restore_battle_stats(member)

            renpy.show_screen("arena_aftermatch", winner, loser)

            setup[0] = Team(max_size=len(setup[0]))
            setup[1] = Team(max_size=len(setup[1]))

            # Line-up positioning:
            self.update_setups(winner, loser)

            # Ladder
            self.update_ladder()

            # record the event
            self.hero_match_result = [self.shallow_copy_team(winner), self.shallow_copy_team(loser)]

            fday = setup[2]
            for d in hero.fighting_days[:]:
                if d == fday:
                    hero.fighting_days.remove(d)

        @staticmethod
        def append_match_result(txt, f2f, match_result):
            if f2f:
                temp = "{} has defeated {} in a one on one fight. ".format(
                          match_result[0][0].name, match_result[1][0].name)
            else:
                temp = "%s team has defeated %s in an official match. " % (match_result[0].name, match_result[1].name)
            temp += choice(["It was quite a show!",
                            "Amazing performance!",
                            "Crowd never stopped cheering!",
                  ("The crowd chanted %s name for minutes!" % match_result[0][0].name) if f2f else
                  ("Team's leader %s got most of the credit!" % match_result[0].leader.name)])
            txt.append(temp)

        @staticmethod
        def missed_match_result(txt, opfor):
            # player missed an Arena match -> Rep penalty!
            rep_penalty = max(500, (opfor.get_rep()/10))
            hero.arena_rep -= rep_penalty

            if len(opfor) == 1:
                opfor = opfor.leader
                temp = "%s missed a 1v1 fight against %s, who entrained the public by boasting of %s prowess " \
                        "and making funny jabs at %s's cowardliness!" % (hero.name, opfor.name, opfor.pd, hero.name)
            else:
                temp = "%s didn't show up for a team combat against %s! The spectators were very displeased!" % (hero.team.name, opfor.name)
            temp = set_font_color(temp, "red")

            txt.append(temp)

        def next_day(self):
            # For the daily report:
            txt = []

            # Normalizing amount of teams available for the Arena.
            if not day % 5:
                self.update_teams()

            self.find_opfor()

            # Add the hero's matchresult from today
            if self.hero_match_result:
                self.append_match_result(txt, len(self.hero_match_result[0]) == 1, self.hero_match_result)

            tl.start("Arena: Matches")
            # Running the matches:
            # Join string method is used here to improve performance over += or + (Note: Same should prolly be done for jobs.)
            for setup in self.matches_1v1:
                if setup[2] == day:
                    off_team, def_team = setup[0], setup[1]
                    if off_team.leader != hero:
                        if off_team and def_team:
                            match_result = self.auto_resolve_combat(off_team, def_team, "match")
                            self.append_match_result(txt, True, match_result)
                    else:
                        self.missed_match_result(txt, def_team)
                    setup[0] = Team(max_size=1)
                    setup[1] = Team(max_size=1)

            for setup in self.matches_2v2:
                if setup[2] == day:
                    off_team, def_team = setup[0], setup[1]
                    if off_team.leader != hero:
                        if off_team and def_team:
                            match_result = self.auto_resolve_combat(off_team, def_team, "match")
                            self.append_match_result(txt, False, match_result)
                    else:
                        self.missed_match_result(txt, def_team)
                    setup[0] = Team(max_size=2)
                    setup[1] = Team(max_size=2)

            for setup in self.matches_3v3:
                if setup[2] == day:
                    off_team, def_team = setup[0], setup[1]
                    if off_team.leader != hero:
                        if off_team and def_team:
                            match_result = self.auto_resolve_combat(off_team, def_team, "match")
                            self.append_match_result(txt, False, match_result)
                    else:
                        self.missed_match_result(txt, def_team)
                    setup[0] = Team(max_size=3)
                    setup[1] = Team(max_size=3)

            self.update_matches()
            tl.end("Arena: Matches")

            # Some random dogfights
            # 1v1:
            tl.start("Arena: Dogfights")
            opfor_pool = list()
            dogfighters = self.get_dogfights_fighters()
            for fighter in self.get_arena_candidates():
                if self.check_if_team_ready_for_dogfight(fighter, dogfighters):
                    opfor_pool.append(fighter)

            shuffle(opfor_pool)
            shuffle(self.dogfights_1v1)

            for __ in xrange(randint(4, 7)):
                if self.dogfights_1v1 and opfor_pool:
                    defender = self.dogfights_1v1.pop()
                    opfor_fighter = opfor_pool.pop()
                    opfor = Team(max_size=1)
                    opfor.add(opfor_fighter)
                    self.auto_resolve_combat(opfor, defender)
                    self.df_count += 1
            # 2v2:
            opfor_pool = list()

            for team in self.teams_2v2:
                if self.check_if_team_ready_for_dogfight(team, self.dogfights_2v2):
                    opfor_pool.append(team)

            shuffle(opfor_pool)
            shuffle(self.dogfights_2v2)

            for __ in xrange(randint(2, 4)):
                if self.dogfights_2v2 and opfor_pool:
                    defender = self.dogfights_2v2.pop()
                    opfor = opfor_pool.pop()
                    self.auto_resolve_combat(opfor, defender)
                    self.df_count += 1
            # 3v3:
            opfor_pool = list()

            for team in self.teams_3v3:
                if self.check_if_team_ready_for_dogfight(team, self.dogfights_3v3):
                    opfor_pool.append(team)

            shuffle(opfor_pool)
            shuffle(self.dogfights_3v3)

            for __ in xrange(randint(2, 4)):
                if self.dogfights_3v3 and opfor_pool:
                    defender = self.dogfights_3v3.pop()
                    opfor = opfor_pool.pop()
                    self.auto_resolve_combat(opfor, defender)
                    self.df_count += 1
            self.update_dogfights()
            tl.end("Arena: Dogfights")

            txt.append("%d unofficial dogfights took place yesterday!" % self.df_count)

            # Warning the player of a scheduled arena match:
            for setup in chain(self.matches_1v1, self.matches_2v2, self.matches_3v3):
                if setup[2] != day+1:
                    continue
                off_team, def_team = setup[0], setup[1]
                if off_team and def_team:
                    num = len(off_team)
                    if num == 1:
                        lineup = self.lineup_1v1
                    elif num == 2:
                        lineup = self.lineup_2v2
                    elif num == 3:
                        lineup = self.lineup_2v2
                    else:
                        raise Exception()

                    for idx, team in enumerate(lineup):
                        if team == off_team or team == def_team:
                            idx = 3 * idx / len(lineup)
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

            self.daily_report = gazette.arena = txt

            # Update top 100 ladder:
            self.update_ladder()

            # Update arena actives
            self.update_actives()

            # Reset daily variables
            self.df_count = 0
            self.hero_match_result = None
