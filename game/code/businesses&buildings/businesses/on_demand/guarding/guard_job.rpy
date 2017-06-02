init -5 python:
    class GuardJob(Job):
        def __init__(self):
            """Creates reports for GuardJob.
            """
            super(GuardJob, self).__init__()
            self.id = "Guarding"
            self.type = "Combat"

            # Traits/Job-types associated with this job:
            self.occupations = ["Warrior"] # General Strings likes SIW, Warrior, Server...
            self.occupation_traits = [traits["Warrior"], traits["Mage"], traits["Knight"], traits["Shooter"]] # Corresponding traits...

            # Relevant skills and stats:
            self.skills = ["cleaning"]
            self.stats = ["agility"]

            workermod = {}
            self.locmod = {}

        def __call__(self, workers_original, workers, location, action, flag=None):
            self.all_workers = workers_original
            workers = workers
            self.loc = location
            self.flag = flag

            if action == "patrol":
                self.patrol()
            elif action == "intercept":
                self.intercept()

        def patrol(self):
            """Builds ND event for Guard Job.

            This one is simpler... it just logs the stats, picks an image and builds a report...
            """
            self.img = Fixed(xysize=(820, 705))
            self.img.add(Transform(self.loc.img, size=(820, 705)))
            vp = vp_or_fixed(self.all_workers, ["fighting"], {"exclude": ["sex"], "resize": (150, 150)}, xmax=820)
            self.img.add(Transform(vp, align=(.5, .9)))

            self.team = self.all_workers

            log = ["{} intercepted {} today!".format(", ".join([w.nickname for w in self.all_workers]), self.loc.name)]

            # Stat mods
            self.logloc('dirt', 25 * len(self.all_workers)) # 25 per guard? Should prolly be resolved in SimPy land...
            for w in self.all_workers:
                log.logws('vitality', -randint(15, 25), w)  # = ? What to do here?
                log.logws('exp', randint(15, 25), w) # = ? What to do here?
                for stat in ['attack', 'defence', 'magic', 'joy']:
                    if dice(20):
                        log.logws(stat, 1, w)

            self.event_type = "jobreport" # Come up with a new type for team reports?
            self.apply_stats()
            self.finish_job()

        def intercept(self):
            """Builds ND event for Guard Job.

            This one is simpler... it just logs the stats, picks an image and builds a report...
            """
            self.img = Fixed(xysize=(820, 705))
            self.img.add(Transform(self.loc.img, size=(820, 705)))
            vp = vp_or_fixed(self.all_workers, ["fighting"], {"exclude": ["sex"], "resize": (150, 150)}, xmax=820)
            self.img.add(Transform(vp, align=(.5, .9)))

            self.team = self.all_workers

            log = ["{} intercepted a bunch of drunk miscreants in {}! ".format(", ".join([w.nickname for w in self.all_workers]), self.loc.name)]
            if self.flag.flag("result"):
                log.append("They managed to subdue them!")
            else:
                log.append("They failed to subdue them, that will cause you some issues with your clients and {} reputation will suffer!".format(self.loc.name))

            # Stat mods (Should be moved/split here).
            self.logloc('dirt', 25 * len(self.all_workers)) # 25 per guard? Should prolly be resolved in SimPy land...
            for w in self.all_workers:
                log.logws('vitality', -randint(15, 25), w)  # = ? What to do here?
                log.logws('exp', randint(15, 25), w) # = ? What to do here?
                for stat in ['attack', 'defence', 'magic', 'joy']:
                    if dice(20):
                        log.logws(stat, 1, w)

            self.event_type = "jobreport" # Come up with a new type for team reports?
            self.apply_stats()
            self.finish_job()

        def get_events(self):
            """
            Get the guard events this girl will respond to.
            """
            log.append(choice(["%s worked as guard in %s! \n"%(worker.fullname, self.loc.name),
                                    "%s did guard duty in %s! \n"%(worker.fullname, self.loc.name)]))

            log.append("\n")
            self.img = "battle"

            if worker.guard_relay['bar_event']['count']:
                if worker.has_image("fighting"):
                    self.img = "fighting"

                g_events = plural("event", worker.guard_relay["bar_event"]["count"])

                log.append("She responded to %d brawl %s. "%(worker.guard_relay['bar_event']['count'], g_events))
                log.append("That resulted in victory(ies): %d and loss(es): %d! "%(worker.guard_relay['bar_event']['won'], worker.guard_relay['bar_event']['lost']))
                log.append("\n")

                workermod = dict( (n, workermod.get(n, 0)+worker.guard_relay['bar_event']['stats'].get(n, 0)) for n in set(workermod)|set(worker.guard_relay['bar_event']['stats']) )

            if worker.guard_relay['whore_event']['count']:
                if worker.has_image("fighting"):
                    self.img = "fighting"

                g_events = plural("attack", worker.guard_relay["whore_event"]["count"])

                log.append("With %d victory(ies) and %d loss(es) she settled %d %s on your prostitutes. \n"%(worker.guard_relay['whore_event']['won'],
                                                                                                                  worker.guard_relay['whore_event']['lost'],
                                                                                                                  worker.guard_relay['whore_event']['count'],
                                                                                                                  g_events))

                workermod = dict( (n, workermod.get(n, 0)+worker.guard_relay['whore_event']['stats'].get(n, 0)) for n in set(workermod)|set(worker.guard_relay['whore_event']['stats']) )
                log.append("\n")

        def post_job_activities(self):
            """
            Solve the post job events.
            """

            if worker.AP <= 0:
                log.append(choice(["Nothing else happened during her shift.", "She didn't have the stamina for anything else today."]))

            else:
                gbu = self.loc.get_upgrade_mod("guards")
                if gbu == 3:
                    guardlist = [girl for girl in hero.chars if girl.location == self.loc and girl.action == 'Guard' and girl.health > 60]
                    guards = len(guardlist)

                    if guards > 0:
                        if guards >= 3:
                            log.append(", ".join(girl.name for girl in guardlist[:guards-1]))
                            log.append(" and %s "%guardlist[guards-1].nickname)
                            log.append("spent the rest of the day dueling each other in Sparring Quarters. \n")

                            while worker.AP > 0:
                                workermod['attack'] = workermod.get('attack', 0) + choice([0, 0, 0, 0, 1, guards])
                                workermod['defence'] = workermod.get('defence', 0) + choice([0, 0, 0, 0, 1, guards])
                                workermod['magic'] = workermod.get('magic', 0) + choice([0, 0, 0, 0, 1, guards])
                                workermod['joy'] = workermod.get('joy', 0) + choice([0, 1, 2, 3])
                                workermod['vitality'] = workermod.get('vitality', 0) - randint(15, 20)
                                worker.AP -=  1

                            workermod['exp'] = workermod.get('exp', 0) + worker.AP * randint(8, 12) + 5 * (guards-1) # Moved to prevent insane exp increases at higher levels.

                        elif guards == 2:
                            log.append("%s and %s spent time dueling each other! \n"%(guardlist[0].name, guardlist[1].name))

                            while worker.AP > 0:
                                workermod['attack'] = workermod.get('attack', 0) + choice([0,0,0,0,1,guards])
                                workermod['defence'] = workermod.get('defence', 0) + choice([0,0,0,0,1,guards])
                                workermod['magic'] = workermod.get('magic', 0) + choice([0,0,0,0,1,guards])
                                workermod['joy'] = workermod.get('joy', 0) + choice([0,1,2,3])
                                workermod['vitality'] = workermod.get('vitality', 0) - randint(15, 20)
                                worker.AP -=  1

                            workermod['exp'] = workermod.get('exp', 0) + worker.AP * randint(8, 12) + 5

                        elif guards == 1:
                            log.append("%s had the whole Sparring Quarters to herself! \n"%(guardlist[0].name))

                            while worker.AP > 0:
                                workermod['attack'] = workermod.get('attack', 0) + choice([0,0,0,0,1,guards])
                                workermod['defence'] = workermod.get('defence', 0) + choice([0,0,0,0,1,guards])
                                workermod['magic'] = workermod.get('magic', 0) + choice([0,0,0,0,1,guards])
                                workermod['joy'] = workermod.get('joy', 0) + choice([0,1,2,3])
                                workermod['vitality'] = workermod.get('vitality', 0) - randint(15, 20)
                                worker.AP -=  1

                            workermod['exp'] = workermod.get('exp', 0) + worker.AP * randint(8, 12)

                elif gbu == 2:
                    log.append("She spent remainder of her shift practicing in Training Quarters. \n")

                    while worker.AP > 0:
                        workermod['attack'] = workermod.get('attack', 0) + choice([0,0,0,1])
                        workermod['defence'] = workermod.get('defence', 0) + choice([0,0,0,1])
                        workermod['magic'] = workermod.get('magic', 0) + choice([0,0,0,1])
                        workermod['joy'] = workermod.get('joy', 0) + choice([0,1,1,2])
                        workermod['vitality'] = workermod.get('vitality', 0) - randint(15, 20)
                        worker.AP -= 1

                    workermod['exp'] = workermod.get('exp', 0) + worker.AP * randint(8, 12)

                elif self.loc.upgrades['guards']['1']['active']:
                    if dice(50):
                        log.append("She spent time relaxing in Guard Quarters. \n")
                        workermod['vitality'] = workermod.get('vitality', 0) + randint(15, 20) * worker.AP
                        worker.AP = 0

                    else:
                        log.append("She did some rudimentary training in Guard Quarters. \n")
                        workermod['attack'] = workermod.get('attack', 0) + choice([0,0,0,0,1])
                        workermod['defence'] = workermod.get('defence', 0) + choice([0,0,0,0,1])
                        workermod['magic'] = workermod.get('magic', 0) + choice([0,0,0,0,1])
                        workermod['joy'] = workermod.get('joy', 0) + choice([0,1,1,1])
                        workermod['exp'] = workermod.get('exp', 0) +  randint(15, 25)
                        workermod['vitality'] = workermod.get('vitality', 0) - randint(15, 20)
                        worker.AP = 0

                else:
                    if dice(50):
                        log.append("She spent time relaxing. \n")

                        #display rest only if they did not fight
                        if not worker.guard_relay['bar_event']['count'] and not worker.guard_relay['whore_event']['count']:
                            self.img = "rest"

                        workermod['vitality'] = workermod.get('vitality', 0) + randint(7, 12) * worker.AP
                        worker.AP = 0

                    else:
                        log.append("She did some rudimentary training. \n")
                        workermod['attack'] = workermod.get('attack', 0) + choice([0,0,0,0,0,1])
                        workermod['defence'] = workermod.get('defence', 0) + choice([0,0,0,0,0,1])
                        workermod['magic'] = workermod.get('magic', 0) + choice([0,0,0,0,0,1])
                        workermod['joy'] = workermod.get('joy', 0) + choice([0,1])
                        workermod['exp'] = workermod.get('exp', 0) +  randint(8, 15)
                        workermod['vitality'] = workermod.get('vitality', 0) - randint(15, 20)
                        worker.AP = 0
