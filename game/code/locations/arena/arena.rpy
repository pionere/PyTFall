init -9 python:
    # ========================= Arena and related ===========================>>>
    class Arena(_object):
        """
        First prototype of Arena, will take care of most related logic and might have to be split in the future.
        :notes: - priority order: matchfight-dogfight-chainfight(survival) 
                - it is expected that a team/fighter is ready for at least one encounter per day
                - a fighter can participate in maximum one match on a single day
                - multiple dogfights are possible for a single fighter, but there must be a fitness check between the encounters
                - at the end of the day (ND) a fighter might be selected for additional encounters, but only if they are ready for it

        -------------------------->
        """
        PERMIT_REP = 5000    # the required arena reputation to buy an arena permit
        PERMIT_PRICE = 10000 # the price of an arena permit
        EMPTY_TEAM = Team()
        def __init__(self):
            super(Arena, self).__init__()
            # ----------------------------->
            self.king = None

            # Scheduled matches:
            #                       Off Team          Def Team      Day
            self.matches_1v1 = [[Arena.EMPTY_TEAM, Arena.EMPTY_TEAM, 0] for i in xrange(12)]
            self.matches_2v2 = [[Arena.EMPTY_TEAM, Arena.EMPTY_TEAM, 0] for i in xrange(8)]
            self.matches_3v3 = [[Arena.EMPTY_TEAM, Arena.EMPTY_TEAM, 0] for i in xrange(8)]
            # 'Scheduled' dogfights:
            self.dogfights_1v1 = list() # list of teams
            self.dogfights_2v2 = list()
            self.dogfights_3v3 = list()
            # Ladders and their team members.
            #  The separate list is necessary because a team can be changed.
            #  At the moment only the hero-teams can change, so the initial team members are not copied. 
            self.ladder_1v1 = [Team() for i in xrange(20)]
            self.ladder_2v2 = [Team() for i in xrange(10)]
            self.ladder_3v3 = [Team() for i in xrange(10)]
            self.ladder_1v1_members = [t._members for t in self.ladder_1v1]
            self.ladder_2v2_members = [t._members for t in self.ladder_2v2]
            self.ladder_3v3_members = [t._members for t in self.ladder_3v3]
            self.ladder = None # list of chars - initialized later

            # Prebuilt teams for dogfights and matchfights
            self.dogteams_2v2 = list()
            self.dogteams_3v3 = list()
            self.matchteams_2v2 = list()
            self.matchteams_3v3 = list()

            # ND-Report
            self.df_count = 0
            self.daily_match_results = [] # list of (winner, loser) pairs
            self.daily_report = []

        # -------------------------- Sorting ---------------------------------------------------------->
        def get_matches_fighters(self):
            '''
            Returns all fighters that are set to participate at official maches.
            '''
            return set(f for ladder in chain(self.matches_1v1, self.matches_2v2, self.matches_3v3) for f in chain(ladder[0], ladder[1]))

        def get_teams_fighters(self):
            """
            Returns fighters that are in the Arena teams.
            """
            return set(f for team in chain(self.dogteams_2v2, self.dogteams_3v3, self.matchteams_2v2, self.matchteams_3v3) for f in team)

        def get_ladders_fighters(self):
            """
            Returns fighters currently in Arena lineups (heavyweights basically)
            """
            return set(f for team in chain(self.ladder_1v1, self.ladder_2v2, self.ladder_3v3) for f in team)

        def get_dogfights_fighters(self):
            """
            All fighters that are currently in dogfights!
            """
            return set(f for team in chain(self.dogfights_1v1, self.dogfights_2v2, self.dogfights_3v3) for f in team)

        def get_arena_fighters(self):
            """
            Returns all fighters active at the arena.
            """
            return [f for f in chain(chars.itervalues(), fighters.itervalues()) if f.arena_active]

        def get_arena_candidates(self):
            """
            Returns a list of all characters available/willing to fight in the Arena.
            Excludes all girls participating in girl_meets to avoid them being at multiple locations (this needs better handling)
            """
            interactions_chars = set(iam.get_all_girls())
            interactions_chars.update(hero.chars)
            return [c for c in chars.itervalues() if c.arena_willing and c not in interactions_chars] + fighters.values()

        # -------------------------- Teams control/checks -------------------------------------->
        def remove_team_from_dogfights(self, fighter):
            for group in (self.dogfights_1v1, self.dogfights_2v2, self.dogfights_3v3):
                group[:] = [team for team in group if fighter not in team]

        @staticmethod
        def ready_for_fight(f):
            """
            Checks if a fighter is ready for fight by eliminating them on grounds of health/mp/vitality or lack of AP.
            :param f: the fighter to check
            """
            for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                if f.get_stat(stat) < f.get_max(stat)*9/10:
                    return False
            return f.PP >= 200 # PP_PER_AP

        # -------------------------- Update Methods ---------------------------------------------->
        def update_setups(self, winner, loser):
            """
            Repositions the winners + losers in the ladders.
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

            idx = 0
            if loser in ladder:
                index = ladder.index(loser)
                if index != len(ladder)-1:
                    ladder[index], ladder[index+1] = ladder[index+1], loser
                    members[index], members[index+1] = members[index+1], loser._members[:]
                    idx = index

            if winner in ladder:
                index = ladder.index(winner)
                if index != idx and index != 0:
                    ladder[index], ladder[index-1] = ladder[index-1], winner
                    members[index], members[index-1] = members[index-1], winner._members[:]
            else:
                # check if the hero has an another team in the ladder
                if winner == hero.team:
                    for idx, t in enumerate(ladder):
                        if t.leader == hero:
                            # another team in the ladder -> replace it with the current one
                            ladder[idx] = winner
                            members[idx] = winner._members[:]
                            winner_added = True
                            return
                ladder[-1] = winner
                members[-1] = winner._members[:]

        def update_teams(self):
            """
            Prepares teams to be used as source for dogfights and matchfights.
            using arena candidates in a weighted random (by arena rep) order
            @note teams with different sizes might have shared members 
            """
            # Matchteams:
            for teams, source in [(self.matchteams_2v2, self.dogteams_2v2), (self.matchteams_3v3, self.dogteams_3v3)]:
                # remove useless teams
                for t in teams[:]:
                    if any(not f.arena_permit for f in t):
                        teams.remove(t)

                # add new teams
                amount = 20 - len(teams)
                if amount > 0:
                    dt = [t for t in source if all(f.arena_permit for f in t)]

                    amount = min(amount, len(dt))
                    dt = weighted_sample([[t, t.get_rep()] for t in dt], amount)

                    for t in dt:
                        source.remove(t)
                    teams.extend(dt)

            # Dogteams:
            source = None
            for teams, mteams, size in [(self.dogteams_2v2, self.matchteams_2v2, 2), (self.dogteams_3v3, self.matchteams_3v3, 3)]:
                # remove useless teams
                for t in teams[:]:
                    if any(f.arena_rep < 0 for f in t):
                        teams.remove(t)

                # add new teams
                amount = 30 - len(teams)
                if amount > 0:
                    if source is None:
                        source = [f for f in self.get_arena_candidates() if f.arena_rep >= 0]
                    fl = set(f for team in chain(teams, mteams) for f in team)
                    fl = [f for f in source if f not in fl]

                    amount = min(amount, len(fl)/size)
                    fl = weighted_sample([[f, f.arena_rep+1] for f in fl], amount*size)

                    for __ in xrange(amount):
                        team = Team(name=get_team_name())
                        for __ in xrange(size):
                            f = fl.pop()
                            f.arena_active = True
                            team.add(f)
                        teams.append(team)

        def update_dogfights(self, fday):
            """
            Populates dogfights checking for fighting days of the team members
            using arena candidates and the prepared teams as source in a random order
            :param fday: the day for which the dogfights are prepared
            """
            # 1v1
            fights = self.dogfights_1v1
            # remove entries which have matches
            for t in fights[:]:
                if any(fday in f.fighting_days for f in t):
                    fights.remove(t)

            amount = 20 - len(fights)
            if amount > 0:
                source = [f[0] for f in fights]
                source = [f for f in self.get_arena_candidates() if f not in source and fday not in f.fighting_days]

                source = random.sample(source, min(amount, len(source)))

                for f in source: 
                    f.arena_active = True
                    team = Team(implicit=[f])
                    fights.append(team)

            # 2v2, 3v3
            for fights, source in [(self.dogfights_2v2, self.dogteams_2v2),
                                  (self.dogfights_3v3, self.dogteams_3v3)]:
                # remove entries which have matches
                for t in fights[:]:
                    if any(fday in f.fighting_days for f in t):
                        fights.remove(t)

                # add new entries
                amount = 15 - len(fights)
                if amount:
                    source = [team for team in source if team not in fights and all(fday not in f.fighting_days for f in team)]

                    source = random.sample(source, min(amount, len(source)))

                    fights.extend(source)

        def update_matches(self):
            """
            Populates matchfights making sure there is only one match-fight for any fighter
            using arena candidates and the prepared teams as source in a weighted random (by arena rep) order
            """
            # 1vs1:
            tmap = defaultdict(list)
            for setup in self.matches_1v1:
                if setup[1]:
                    continue
                fday = day + randint(3, 14)
                tmap[fday].append(setup)

            teams = source = None
            for fday, setups in tmap.iteritems():
                if source is None:
                    source = [f for f in self.get_arena_candidates() if f.arena_permit]
                df = [f for f in source if fday not in f.fighting_days]

                df = weighted_sample([[f, f.arena_rep] for f in df], min(len(df), len(setups)))

                for f, setup in zip(df, setups):
                    f.fighting_days.append(fday)
                    f.arena_active = True
                    # find the team of the fighter
                    if teams is None:
                        teams = dict((t.leader, t) for t in self.ladder_1v1)
                        teams.update((f, t) for s in self.matches_1v1 for t in (s[0], s[1]) for f in t)
                    t = teams.get(f, None)
                    if t is None:
                        t = Team(implicit=[f])
                        teams[f] = t
                    setup[1] = t
                    setup[2] = fday

            # 2vs2, 3vs3
            for matches, source in [(self.matches_2v2, self.matchteams_2v2), (self.matches_3v3, self.matchteams_3v3)]:
                tmap = defaultdict(list)
                for setup in matches:
                    if setup[1]:
                        continue
                    fday = day + randint(3, 14)
                    tmap[fday].append(setup)

                if not tmap:
                    continue
                for fday, setups in tmap.iteritems():
                    dt = [t for t in source if all(fday not in f.fighting_days for f in t)]

                    dt = weighted_sample([[t, t.get_rep()] for t in dt], min(len(dt), len(setups)))

                    for t, setup in zip(dt, setups):
                        for f in t:
                            f.fighting_days.append(fday)
                        setup[1] = t
                        setup[2] = fday

        def find_opfor(self):
            """
            Find a team to fight as a challenger in the official arena matches
            using arena candidates and the prepared teams as source in a random order
            """
            # 1vs1:
            today = day
            tmap = defaultdict(list)
            for setup in self.matches_1v1:
                if setup[0]:
                    continue
                fday = setup[2]
                if dice(100/(fday - today + 1)):
                    tmap[fday].append(setup)

            dogs = teams = source = None
            for fday, setups in tmap.iteritems():
                if source is None:
                    source = [f for f in self.get_arena_candidates() if f.arena_permit]
                df = source
                if fday == today:
                    if dogs is None:
                        dogs = self.get_dogfights_fighters()
                    df = [f for f in df if f not in dogs and self.ready_for_fight(f)]
                df = [f for f in df if fday not in f.fighting_days]

                df = random.sample(df, min(len(df), len(setups)))

                for f, setup in zip(df, setups):
                    f.fighting_days.append(fday)
                    f.arena_active = True
                    # find the team of the fighter
                    if teams is None:
                        teams = dict((t.leader, t) for t in self.ladder_1v1)
                        teams.update((f, t) for s in self.matches_1v1 for t in (s[0], s[1]) for f in t)
                    t = teams.get(f, None)
                    if t is None:
                        t = Team(implicit=[f])
                        teams[f] = t
                    setup[0] = t

            # 2vs2, 3vs3
            for matches, source in [(self.matches_2v2, self.matchteams_2v2), (self.matches_3v3, self.matchteams_3v3)]:
                tmap = defaultdict(list)
                for setup in matches:
                    if setup[0] or not setup[1]:
                        continue
                    fday = setup[2]
                    if dice(100/(fday - today + 1)):
                        tmap[fday].append(setup)

                for fday, setups in tmap.iteritems():
                    dt = source
                    if fday == today:
                        if dogs is None:
                            dogs = self.get_dogfights_fighters()
                        dt = [t for t in dt if all(f not in dogs and self.ready_for_fight(f) for f in t)]
                    dt = [t for t in dt if all(fday not in f.fighting_days for f in t)]

                    dt = random.sample(dt, min(len(dt), len(setups)))

                    for t, setup in zip(dt, setups):
                        for f in t:
                            f.fighting_days.append(fday)
                        setup[0] = t

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
            return max(50, (len(off_team)*off_team.get_level()+len(def_team)*def_team.get_level())/10*10)

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
            temp = [f for f in chain(self.get_arena_fighters(), [hero]) if f.arena_rep > 0] 

            temp.sort(reverse=True, key=attrgetter("arena_rep"))

            self.ladder = temp[:100]

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

                a_team = Team(name=name)
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
                            self.ladder_1v1_members[lineups] = a_team._members
                            continue
                    elif teamsize == 2:
                        ladder = self.ladder_2v2
                        if not ladder[lineups]:
                            ladder[lineups] = a_team
                            self.ladder_2v2_members[lineups] = a_team._members
                            self.matchteams_2v2.append(a_team)
                            continue
                    else: # if teamsize == 3:
                        ladder = self.ladder_3v3
                        if not ladder[lineups]:
                            ladder[lineups] = a_team
                            self.ladder_3v3_members[lineups] = a_team._members
                            self.matchteams_3v3.append(a_team)
                            continue
                    raise Exception("Team %s failed to take place %d " \
                        "in %dv%d lineups. It is already taken by another team (%s), " \
                        "check your arena_teams.json file."%(a_team.name, lineups+1,
                        teamsize, teamsize, ladder[lineups].name))
                else:
                    if teamsize == 1:
                        raise Exception("Single member teams are only available for lineups!")
                    elif teamsize == 2:
                        self.matchteams_2v2.append(a_team)
                    else: # if teamsize == 3:
                        self.matchteams_3v3.append(a_team)


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
            apr = Arena.PERMIT_REP

            # Add da King!
            king = self.king
            if not king:
                tier_kwargs = {"level_bios": (1.0, 1.2), "stat_bios": (1.0, 1.2)}
                if candidates:
                    king = candidates.pop()
                    tier_up_to(king, 7, **tier_kwargs)
                    give_tiered_magic_skills(king)
                    give_tiered_items(king, False, True)
                else:
                    king = build_rc(bt_group="Combatant", tier=7,
                                    tier_kwargs=tier_kwargs, give_bt_items=True)

                self.king = king

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
            # 1v1 Ladder:
            ladder = set(f for t in self.ladder_1v1 for f in t) 
            source = [f for f in candidates if f not in ladder]
            source = source[:30]
            shuffle(source)
            if king not in ladder:
                source.append(king)

            arena_rep = int(apr * len(self.ladder_1v1) * random.uniform(1.0, 1.2))
            for team in self.ladder_1v1:
                f = team.leader
                if f is None:
                    f = source.pop()
                    team.add(f)
                # initial arena_rep, flags
                f.arena_active = f.arena_permit = True
                f.arena_rep = arena_rep
                arena_rep -= int(apr * random.uniform(.8, 1.0))

            # 2v2 Ladder:
            ladder = set(f for t in chain(self.ladder_2v2, self.matchteams_2v2) for f in t) 
            source = [f for f in candidates if f not in ladder]
            source = source[:50]
            shuffle(source)
            if king not in ladder:
                source.append(king)

            team_rep = apr * (len(self.ladder_2v2)+1)
            for team in self.ladder_2v2:
                if not team.name:
                    team.name = get_team_name()
                while len(team) < 2:
                    f = source.pop()
                    team.add(f)
                # initial arena_rep, flags
                for f in team:
                    f.arena_active = f.arena_permit = True
                    frep = f.arena_rep
                    if team_rep > frep:
                        frep = team_rep
                    f.arena_rep = int(frep * random.uniform(.9, 1.1))
                team_rep -= int(apr * random.uniform(.8, 1.0))

            # 3v3 Ladder:
            ladder = set(f for t in chain(self.ladder_3v3, self.matchteams_3v3) for f in t) 
            source = [f for f in candidates if f not in ladder]
            source = source[:60]
            shuffle(source)
            if king not in ladder:
                source.append(king)

            team_rep = apr * (len(self.ladder_3v3)+1)
            for team in self.ladder_3v3:
                if not team.name:
                    team.name = get_team_name()
                while len(team) < 3:
                    f = source.pop()
                    team.add(f)
                # initial arena_rep, flags
                for f in team:
                    f.arena_active = f.arena_permit = True
                    frep = f.arena_rep
                    if team_rep > frep:
                        frep = team_rep
                    f.arena_rep = int(frep * random.uniform(.9, 1.1))
                team_rep -= int(apr * random.uniform(.8, 1.0))

            # initial arena_rep for candidates I.
            ladder = [f for f in candidates if f.arena_rep != 0]
            source = [f for f in candidates if f.arena_rep == 0]
            source = source[:120-len(ladder)]
            arena_rep = min(f.arena_rep for f in ladder)
            for f in source:
                f.arena_active = True
                f.arena_rep = int(arena_rep * random.uniform(.7, .95))

            for source, ladder in ((self.matchteams_2v2, self.ladder_2v2), (self.matchteams_3v3, self.ladder_3v3)):
                # initial arena_rep for candidates II.
                team_rep = ladder[-1].get_rep()
                for t in source:
                    if t not in ladder:
                        for f in t:
                            f.arena_active = f.arena_permit = True
                            f.arena_rep = int(team_rep * random.uniform(.7, .95))

                # Add ladder teams to the sources:
                source.extend([t for t in ladder if t not in source])

            self.update_ladder()       # Populate the reputation ladder
            self.update_teams()        # Build teams 
            self.update_matches()      # Add new matches
            self.find_opfor()          #  find opponent for matches
            self.update_dogfights(day) # Add new dogfights

        # -------------------------- ChainFights vs Mobs ------------------------>
        def run_chainfight(self, setup, off_team, logical, nd_run=False):
            """Running a chainfight.
            """
            num_opps = len(off_team)
            combat_log = []
            for encounter in xrange(1, 6):
                combat_log.append("--------------- Round %d ---------------" % encounter)

                # Picking an opponent(s):
                enemy_team = Team(name=setup["id"])

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
                if off_team is hero.team:
                    # Get team luck:
                    luck = sum((member.get_stat("luck") for member in off_team)) 
                    luck = float(luck)/len(off_team)

                    # Bonus:
                    if dice((encounter-1)*(25+luck/2)*.2):
                        self.run_minigame(luck)

                if logical:
                    result = True
                else:
                    result = renpy.call_screen("confirm_chainfight", setup, encounter, off_team.leader, enemy_team.leader)
                    if result == "break":
                        return (enemy_team, off_team), combat_log

                # the actual battle
                member_aps = {member: member.PP for member in off_team}

                global battle
                if result is True:
                    battle = run_auto_be(off_team, enemy_team, simple_ai=nd_run)
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

                        rew_rep = dice_int(skill_reward(member, enemy_team, skill_mod=2))
                        if rew_rep:
                            member.arena_rep += rew_rep
                            statdict["Arena Rep"] = rew_rep
                    combat_stats[member] = statdict

                if not nd_run:
                    # Ladder
                    self.update_ladder()

                    for member in enemy_team:
                        defeated_mobs.add(member.id)
                        combat_stats[member] = OrderedDict([("K.O.", "Yes")])

                if encounter <= 4:
                    if not logical:
                        renpy.call_screen("arena_aftermatch", off_team, enemy_team, combat_stats, True)
                    continue

            # end of the chainfight
            # rewards
            leader = off_team.leader
            amount = 2
            amount += min(round_int(leader.arena_rep/max(15000.0, self.ladder[0].arena_rep / 3.0)), 3)
            tier = mob_level/40.0
            #types = ['scroll', 'restore', 'armor', 'weapon'] 
            types = None
            rewards = get_item_drops(types=types, tier=tier, locations=["Arena"], amount=amount)

            if not logical:
                renpy.call_screen("arena_finished_chainfight", off_team, enemy_team, combat_stats, rewards)

            if nd_run:
                return (off_team, enemy_team), rewards

            for i in rewards:
                leader.inventory.append(i)

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
 
            #        color,  range value
            data = (("black", black, ""), ("red", hpbar, "health"), ("blue", mpbar, "mp"), ("green", vpbar, "vitality"), ("black", black, ""))

            # Pass the minigame screen:
            result = renpy.call_screen("arena_minigame", data, length)
            if result:
                for member in hero.team:
                    member.set_stat(result, member.get_max(result))

        # -------------------------- Battle/Next Day ------------------------------->
        @staticmethod
        def arena_rep_reward(loser, winner):
            return max(0.0, (loser.get_rep() - (winner.get_rep() / 2)) / 10.0)

        def run_dogfight(self, def_team, off_team, logical, nd_run=False):
            '''
            Bridge to battle engine + rewards/penalties
            '''
            member_aps = {member: member.PP for member in chain(off_team, def_team)}
            member_hps = {member: member.get_stat("health") for member in chain(off_team, def_team)}

            global battle
            if logical is True:
                battle = run_auto_be(off_team, def_team, simple_ai=nd_run)
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

            # Awards: 
            #  - Decent cash, low a-rep and normal EXP. -
            #  Max gold as a constant with added blood money:
            wlvl, llvl = winner.get_level(), loser.get_level()
            rew_gold = (wlvl+llvl)*5
            rew_gold = round_int(rew_gold*(float(llvl)/max(1, wlvl)))
            blood = sum((member_hps[member] - member.get_stat("health") for member in winner))
            if blood > 0:
                rew_gold += blood
            #  a bit of reputation
            rep = min(50, self.arena_rep_reward(loser, winner))

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

                    rew_r = int(rep)
                    if rew_r:
                        member.arena_rep += rew_r
                        statdict["Arena Rep"] = rew_r

                    if dice(llvl):
                        if random.random() > .5:
                            member.mod_stat("fame", 1)
                            statdict["Fame"] = 1
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

            if not logical:
                renpy.call_screen("arena_aftermatch", off_team, def_team, combat_stats, off_team is winner)

            if not nd_run:
                # Ladder
                self.update_ladder()

                for f in def_team:
                    if not self.ready_for_fight(f):
                        self.remove_team_from_dogfights(f)

            # record the event
            self.df_count += 1

            return (winner, loser), list(battle.combat_log)

        @staticmethod
        def shallow_copy_team(team):
            """
            Create a shallow copy of the team to preserve the important team informations for today's report
            """ 
            return Team(name=team.name, implicit=team)

        def run_matchfight(self, def_team, off_team, logical, nd_run=False):
            """
            Bridge to battle engine + rewards/penalties.
            """
            member_aps = {member: member.PP for member in chain(off_team, def_team)}

            global battle
            if logical:
                battle = run_auto_be(off_team, def_team, simple_ai=nd_run)
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
            rep = self.arena_rep_reward(loser, winner)
            wlvl, llvl = winner.get_level(), loser.get_level()
            rew_gold = int(max(200, 250*(float(llvl) /max(1, wlvl))))

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

                    rew_r = int(rep)
                    if rew_r:
                        member.arena_rep += rew_r
                        statdict["Arena Rep"] = rew_r

                    if dice(llvl):
                        rew_fame = randrange(3)
                        if rew_fame:
                            member.mod_stat("fame", rew_fame)
                            statdict["Fame"] = rew_fame
                combat_stats[member] = statdict

            rep = -int(1.2 * rep)
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

            if not logical:
                renpy.call_screen("arena_aftermatch", off_team, def_team, combat_stats, off_team is winner)

            # Update match
            setup = self.get_arena_match(team=def_team)
            setup[0] = setup[1] = Arena.EMPTY_TEAM

            # Line-up positioning:
            self.update_setups(winner, loser)

            if not nd_run:
                # Ladder
                self.update_ladder()

                # record the event
                self.daily_match_results.append((self.shallow_copy_team(winner), self.shallow_copy_team(loser)))

            return (winner, loser), list(battle.combat_log)

        def watch_matchfight(self, off_team, def_team):
            member_aps = {f: f.PP for f in chain(off_team, def_team)}
            off_team.setup_controller()

            self.run_matchfight(def_team, off_team, False)

            off_team.reset_controller()
            # adjust hero's ap
            hero.PP -= min(200, max((aps - f.PP) for f, aps in member_aps.iteritems())) # PP_PER_AP

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

        def nd_run_chainfight(self, off_team):
            """
            Run a chainfight for with an NPC-team based on the flags of its leader
            :param off_team: the team to fight in the chainfight
            """
            temp = len(off_team)
            flag_name = "arena_cf_%d" % temp
            fail_flag_name = "arena_cf_bad_%d" % temp
            success_name = "arena_cf_good_%d" % temp

            leader = off_team.leader
            flagval = leader.get_flag(flag_name, None)
            if flagval is None:
                lvl = min(len(self.all_chain_fights), leader.tier)/2 # start on a reasonable level
                flagval = lvl*5
            else:
                lvl = flagval/5
            result = self.run_chainfight(self.all_chain_fights[lvl], off_team, True, True)

            fails = leader.get_flag(fail_flag_name, None)
            if result[0][0] is off_team:
                if fails is not None:
                    temp = fails.get(lvl, 0)
                    if temp != 0:
                        # the encounter failed before -> reduce the damage
                        if temp == 1:
                            fails.pop(lvl)
                            if not fails:
                                leader.del_flag(fail_flag_name)
                        else:
                            fails[lvl] = temp - 1
                # handle rewards:
                rewards = result[1]
                temp = EQUIP_SLOTS.keys()
                temp.append("consumable")
                #equip = False
                for i in rewards:
                    s = i.slot
                    if s in temp:
                        n = count_owned_items(i, leader)
                        if s == "consumable":
                            n -= 4
                        elif s == "ring":
                            n -= 2
                        if n <= 0:
                            leader.inventory.append(i)
                            #equip = True
                            continue
                    # sell unusable items
                    leader.add_money(i.price, "Items")
                # equip the new items - not really the best time, since the char might be damaged...
                #if equip and leader.autoequip:
                #    leader.auto_equip(leader.last_known_aeq_purpose)
                flagval += 1
                if len(self.all_chain_fights) == flagval/5:
                    return # no more opponent to fight against
                leader.set_flag(success_name, max(leader.get_flag(success_name, 0), lvl))
            else:
                if fails is None:
                    fails = dict()
                    leader.set_flag(fail_flag_name, fails)
                temp = fails[lvl] = fails.get(lvl, 0) + 1
                if lvl*5 == flagval:
                    if temp > 4:
                        # first try failed many times -> try to skip
                        while fails.get(lvl, 0) > 4:
                            lvl += 1
                        if len(self.all_chain_fights) == lvl:
                            # no more opponent to fight against -> fall back to the last success
                            flagval = leader.get_flag(success_name, 0)*5
                        else:
                            flagval = lvl*5
                    else:
                        # the first try failed -> fall back a lot and practice (to the last success)
                        #flagval = max(0, flagval-5)
                        flagval = leader.get_flag(success_name, 0)*5
                else:
                    # one of the many try failed -> try to fall back a bit
                    flagval = max(0, flagval-1)
            leader.set_flag(flag_name, flagval)

        def next_day(self):
            # For the daily report:
            txt = []

            # Normalizing amount of teams available for the Arena.
            fday = store.day
            if not fday % 5:
                self.update_teams()

            self.find_opfor()

            # Add results run during the day
            for result in self.daily_match_results:
                self.append_match_result(txt, len(result[0]) == 1, result)

                # update fighting_days
                for f in chain(result[0], result[1]):
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
                                result = self.run_matchfight(def_team, off_team, True, True)
                                self.append_match_result(txt, size == 1, result[0])
                            else:
                                self.missed_match_result(txt, off_team, def_team)

                        setup[0] = setup[1] = Arena.EMPTY_TEAM

                        # update fighting_days
                        for f in chain(off_team, def_team):
                            f.fighting_days.remove(fday)

            self.update_matches()
            tl.end("Arena: Matches")

            # Some random dogfights
            # 1v1:
            tl.start("Arena: Dogfights")
            dogfights = self.dogfights_1v1
            dogfighters = set(f for t in dogfights for f in t)
            opfor_pool = [f for f in self.get_arena_candidates() if f not in dogfighters and self.ready_for_fight(f)]

            num = min(min(randint(4, 7), len(dogfights)), len(opfor_pool))

            opfor_pool = random.sample(opfor_pool, num)
            dogfights = random.sample(dogfights, num)

            for def_team, off_team in zip(dogfights, opfor_pool):
                off_team = Team(implicit=[off_team])
                self.run_dogfight(def_team, off_team, True, True)

            # 2v2:
            dogfights = self.dogfights_2v2
            opfor_pool = [t for t in self.dogteams_2v2 if t not in dogfights and all(self.ready_for_fight(f) for f in t)]
            dogfights = [t for t in dogfights if all(self.ready_for_fight(f) for f in t)]

            num = min(min(randint(2, 4), len(dogfights)), len(opfor_pool))

            opfor_pool = random.sample(opfor_pool, num)
            dogfights = random.sample(dogfights, num)

            for def_team, off_team in zip(dogfights, opfor_pool):
                self.run_dogfight(def_team, off_team, True, True)

            # 3v3:
            dogfights = self.dogfights_3v3
            opfor_pool = [t for t in self.dogteams_3v3 if t not in dogfights and all(self.ready_for_fight(f) for f in t)]
            dogfights = [t for t in dogfights if all(self.ready_for_fight(f) for f in t)]

            num = min(min(randint(2, 4), len(dogfights)), len(opfor_pool))

            opfor_pool = random.sample(opfor_pool, num)
            dogfights = random.sample(dogfights, num)

            for def_team, off_team in zip(dogfights, opfor_pool):
                self.run_dogfight(def_team, off_team, True, True)

            self.update_dogfights(fday+1)
            tl.end("Arena: Dogfights")

            txt.append("%d unofficial dogfights took place yesterday!" % self.df_count)

            # Some random chainfights
            # 1v1:
            tl.start("Arena: Chainfights")
            opfor_pool = [f for f in self.get_arena_candidates() if self.ready_for_fight(f)]
            num = min(randint(4, 7), len(opfor_pool))
            for off_team in random.sample(opfor_pool, num):
                off_team = Team(implicit=[off_team])
                self.nd_run_chainfight(off_team)

            # 2v2:
            opfor_pool = [t for t in chain(self.dogteams_2v2, self.matchteams_2v2) if all(self.ready_for_fight(f) for f in t)]
            num = min(randint(2, 4), len(opfor_pool))
            for off_team in random.sample(opfor_pool, num):
                self.nd_run_chainfight(off_team)

            # 3v3:
            opfor_pool = [t for t in chain(self.dogteams_3v3, self.matchteams_3v3) if all(self.ready_for_fight(f) for f in t)]
            num = min(randint(2, 4), len(opfor_pool))
            for off_team in random.sample(opfor_pool, num):
                self.nd_run_chainfight(off_team)
            tl.end("Arena: Chainfights")

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
