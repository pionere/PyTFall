init -5 python:
    class WarriorQuarters(OnDemandBusiness):
        def __init__(self):
            super(WarriorQuarters, self).__init__()
            self.jobs = [GuardJob]

        def business_control(self):
            """We decided for this to work similarly (or the same as cleaning routines)

            For now, goal is to get this to work reliably.
            """
            building = self.building
            make_nd_report_at = 0 # We build a report every 25 ticks but only if this is True!
            threat_cleared = 0 # We only do this for the ND report!
            defenders = set() # Everyone that defended for the report

            using_all_workers = False

            power_flag_name = "dnd_guarding_power"
            job = GuardJob

            # Upgrades:
            EnforcedOrder_active = False
            SparringQuarters_active = False
            for u in self.upgrades:
                if isinstance(u, EnforcedOrder):
                    EnforcedOrder_active = True
                elif isinstance(u, SparringQuarters):
                    SparringQuarters_active = True

            # Brawl event:
            had_brawl_event = False

            # Pure workers, container is kept around for checking during all_on_deck scenarios
            log = []
            strict_workers = self.get_strict_workers(job, power_flag_name, log=log)
            workers = strict_workers.copy() # workers on active duty

            num_workers = len(strict_workers)
            if num_workers > 1:
                temp = set_font_color("Your guards are starting their shift!", "cadetblue")
                building.log(temp)
            elif num_workers == 1:
                temp = set_font_color("Your guard is starting %s shift!" % (next(iter(strict_workers)).pd), "cadetblue")
                building.log(temp)

            while 1:
                now = self.env.now
                simpy_debug("Entering WarriorQuarters.business_control at %s", now)

                threat = building.threat
                if DSNBR and not now % 5:
                    temp = "DEBUG: {0:.2f} Threat to THE BUILDING!".format(threat)
                    building.log(set_font_color(temp, "red"), True)

                if threat >= 200:
                    if threat >= 500:
                        if not using_all_workers:
                            using_all_workers = True
                            workers = self.all_on_deck(workers, job, power_flag_name, log=log)
                            temp = "Clients in building got too unruly! All free workers are called to serve as guards!"
                            building.log(set_font_color(temp, "red"), True)
                            SparringQuarters_active = False # no time for sparring in case of emergency

                    if not make_nd_report_at:
                        wlen = len(workers)
                        make_nd_report_at = min(now+25, 105) # MAX_DU
                        if wlen:
                            temp = "%s %s started to guard the building!" % (set_font_color(wlen, "tomato"), plural("Worker", wlen))
                            building.log(temp, True)

                # Actually handle threat:
                if make_nd_report_at and threat > 0:
                    guards_done = []
                    for w in workers:
                        value = w.flag(power_flag_name)
                        building.modthreat(value)

                        threat_cleared += value
                        defenders.add(w)

                        # Adjust PP and Remove the worker after running out of action points:
                        w.PP -= 10
                        w.up_counter("jp_guard", 10)
                        if w.PP <= 0:
                            guards_done.append(w)
                    for w in guards_done:
                        temp = "%s is done guarding for the day!" % w.nickname
                        building.log(set_font_color(temp, "cadetblue"), True)
                        workers.remove(w)

                    threat = building.threat

                if EnforcedOrder_active is True and now > 50:
                    building.log("Enforced order is making your civilian workers uneasy...")
                    for w in building.all_workers:
                        if not "Combatant" in w.gen_occs:
                            w.mod_stat("disposition", -randint(2, 5))
                            w.mod_stat("joy", -randint(2, 5))
                    EnforcedOrder_active = 1 # run only once per day

                # Create actual report:
                # No point in a report if no workers participated in the guarding.
                if now >= make_nd_report_at and defenders:
                    if DSNBR:
                        building.log("DEBUG! WRITING GUARDING REPORT!", True)

                    if SparringQuarters_active and dice(25):
                        use_SQ = True
                        SparringQuarters_active = False # run only once per day
                    else:
                        use_SQ = False
                    self.write_nd_report(strict_workers, defenders, log, threat_cleared, use_SQ)
                    if now >= 105: # MAX_DU
                        self.env.exit()
                    make_nd_report_at = 0
                    threat_cleared = 0
                    defenders = set()
                    log = list()

                # Release none-pure workers:
                if threat < 500 and using_all_workers:
                    using_all_workers = False
                    extra = workers - strict_workers
                    if extra:
                        workers -= extra
                        building.available_workers[0:0] = list(extra)

                simpy_debug("Exiting WarriorQuarters.business_control at %s", now)
                if EnforcedOrder_active is False and using_all_workers:
                    self.intercept(workers, power_flag_name)
                    EnforcedOrder_active = 0 # run only once per day
                    yield self.env.timeout(5)
                else:
                    yield self.env.timeout(1)

        def write_nd_report(self, strict_workers, all_workers, pre_log, threat_cleared, use_SQ):
            simpy_debug("Entering WarriorQuarters.write_nd_report at %s", self.env.now)

            threat_cleared = int(threat_cleared)

            job, loc = GuardJob, self.building
            log = NDEvent(type="jobreport", job=job, loc=loc, locmod={'threat':threat_cleared}, team=all_workers, business=self)

            temp = "%s Security Report!\n" % loc.name
            log.append(temp)

            simpy_debug("Guards.write_nd_report marker 1")

            wlen = len(all_workers)
            temp = "%s %s kept your businesses safe today." % (set_font_color(wlen, "tomato"), plural("Worker", wlen))
            log.append(temp)

            # add log from preparation
            for l in pre_log:
                log.append(l)

            log.img = nd_report_image(loc.img, all_workers, "fighting", exclude=["nude", "sex"])

            simpy_debug("Guards.write_nd_report marker 2")

            workers = all_workers
            extra_workers = workers - strict_workers
            xlen = len(extra_workers)
            if xlen != 0:
                temp = "Security threat became too high that non-combatant workers were called to mitigate it! "
                if xlen > 1:
                    temp += "%s were pulled off their duties to help out..." % (", ".join([w.nickname for w in extra_workers]))
                else:
                    w = next(iter(extra_workers))
                    temp += "%s was pulled off %s duty to help out..." % (w.nickname, w.pd)
                log.append(temp)

                workers -= extra_workers

            xlen = wlen - xlen
            if xlen != 0:
                if xlen > 1:
                    temp = "%s worked hard keeping your business safe as it is their direct job!" % (", ".join([w.nickname for w in workers]))
                else:
                    w = next(iter(workers))
                    temp = "%s worked hard keeping your business safe as it is %s direct job!" % (w.nickname, w.pd)
                log.append(temp)

            simpy_debug("Guards.write_nd_report marker 3")

            temp = "\nA total of %s threat was removed." % set_font_color(-threat_cleared, "tomato")
            log.append(temp)

            difficulty = loc.tier
            if use_SQ:
                log.append("Your guards managed to sneak in a friendly sparring match between their patrol duties!")
                for w in workers:
                    log.logws("vitality", -5, char=w)
                    log.logws("security", randfloat(.5), char=w)
                    log.logws("attack", randfloat(.25), char=w)
                    log.logws("defence", randfloat(.25), char=w)
                    log.logws("magic", randfloat(.25), char=w)
                    log.logws("agility", randfloat(.25), char=w)
                    log.logws("constitution", randfloat(.1), char=w)
                    log.logws("exp", exp_reward(w, difficulty, exp_mod=.1), char=w)
                    if dice(20): # Small chance to get hurt.
                        log.logws("health", round_int(-w.get_max("health")*.2), char=w)

            for w in workers:
                ap_used = w.get_flag("jp_guard", 0)/100.0
                log.logws("vitality", round_int(ap_used*-5), char=w)
                log.logws("security", randfloat(ap_used*2), char=w)
                log.logws("attack", randfloat(ap_used/2), char=w)
                log.logws("defence", randfloat(ap_used/2), char=w)
                log.logws("magic", randfloat(ap_used/2), char=w)
                log.logws("agility", randfloat(ap_used/2), char=w)
                log.logws("constitution", randfloat(ap_used/4), char=w)
                log.logws("exp", exp_reward(w, difficulty, exp_mod=ap_used), char=w)
                w.del_flag("jp_guard")
            for w in extra_workers:
                ap_used = w.get_flag("jp_guard", 0)/100.0
                log.logws("vitality", round_int(ap_used*-6), char=w)
                log.logws("security", randfloat(ap_used), char=w)
                log.logws("attack", randfloat(ap_used/4), char=w)
                log.logws("defence", randfloat(ap_used/4), char=w)
                log.logws("magic", randfloat(ap_used/4), char=w)
                log.logws("agility", randfloat(ap_used/4), char=w)
                log.logws("constitution", randfloat(ap_used/4), char=w)
                log.logws("exp", exp_reward(w, difficulty, exp_mod=ap_used*.5), char=w)
                w.del_flag("jp_guard")

            simpy_debug("Guards.write_nd_report marker 4")

            log.after_job()
            NextDayEvents.append(log)

            simpy_debug("Exiting WarriorQuarters.write_nd_report at %s", self.env.now)

        def intercept(self, workers, power_flag_name):
            """This intercepts a bunch of aggressive clients and
                    resolves the issue through combat or intimidation.

            For beta, this is a simple function we trigger when threat
                level is high from the business_control method.

            Ideally, this should interrupt other processes but that is
                very time-costly to setup and is not required atm.

            We will also make it a separate report for the time being.
            """
            simpy_debug("Entering WarriorQuarters.intercept at %s", self.env.now)

            building = self.building

            # gather the response forces:
            defenders = workers

            temp = "A number of clients got completely out of hand!"
            building.log(set_font_color(temp, "red"), True)

            num_defenders = len(defenders) 
            if num_defenders != 0:
                temp = "%s Guards and employees are responding!" % set_font_color(num_defenders, "red")
                building.log(temp)

                # Prepare the teams:
                # Enemies:
                enemies = building.get_max_client_capacity()/5
                enemies = min(10, max(enemies, 1)) # prolly never more than 10 enemies...

                # Note: We could draw from client pool in the future, for now,
                # we'll just generate offenders.
                enemy_team = Team(name="Hooligans", max_size=enemies)
                for e in range(enemies):
                    # Tier + 2.0 cause we don't give them any items so it's a brawl!
                    enemy = build_client(gender="male", rank=1,
                                     name="Hooligan", last_name=str(e+1),
                                     bt_group="Combatant", tier=building.tier+2.0)
                    enemy.init() # TODO temporary solution, run this in build_client if it is necessary somewhere else (e.g. the PP field)
                    enemy.front_row = 1
                    enemy.apply_trait("Fire")
                    enemy.controller = BE_AI(enemy)
                    enemy_team.add(enemy)

                defence_team = Team(name="Guardians Of The Galaxy", max_size=num_defenders)
                for i in defenders:
                    i.controller = BE_AI(i)
                    defence_team.add(i)

                # ImageReference("chainfights")
                global battle
                battle = BE_Core(logical=True, max_skill_lvl=6,
                            max_turns=(enemies+num_defenders)*4)
                battle.teams = [defence_team, enemy_team]

                battle.start_battle()

                # Reset the controllers:
                defence_team.reset_controller()
                enemy_team.reset_controller()

                # decided to add report in debug mode after all :)
                building.log(set_font_color("Battle Starts!", "crimson"))
                for entry in battle.combat_log:
                    building.log(entry)
                building.log(set_font_color("=== Battle Ends ===", "crimson"))

                if battle.winner == defence_team:
                    building.modthreat(-200)
                    building.moddirt(35*enemies)

                    temp = "Interception is a Success!"
                    building.log(set_font_color(temp, "lawngreen"))
                    # self.env.exit(True) # return True
                else:
                    dirt = 100
                    threat = 60*enemies
                    building.modthreat(dirt)
                    building.moddirt(threat)

                    temp = "Interception Failed, your Guards have been defeated!"
                    temp = set_font_color(temp, "crimson")
                    temp += "\n  +%d Dirt and +%d Threat!" % (dirt, threat)
                    building.log(temp)
                    # self.env.exit(False)
            else:
                # If there are no defenders, we're screwed:
                dirt = 400
                threat = 600
                building.moddirt(dirt)
                building.modthreat(threat)

                temp = "No one was available to put them down!"
                temp = set_font_color(temp, "red")
                temp += "\n  +%d Dirt and +%d Threat!" % (dirt, threat)
                building.log(temp)
                #self.env.exit(False)

            simpy_debug("Exiting WarriorQuarters.intercept at %s", self.env.now)
