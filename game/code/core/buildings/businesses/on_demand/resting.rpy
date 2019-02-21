init -5 python:
    ####################### Rest Job  #############################
    class Rest(Job):
        """Resting for character, technically not a job...
        """
        def __init__(self):
            """
            Creates a new Rest.
            """
            super(Rest, self).__init__()
            self.id = "Rest"
            self.type = "Resting"

            self.desc = "No one can work without taking a break sometimes. Rest restores health, vitality and mp and removes some negative effects"

        def __call__(self, char):
            loc = char.home
            log = NDEvent(job=self, char=char, loc=loc)
            self.rest(char, loc, log)
            self.after_rest(char, log)
            log.after_job()
            NextDayEvents.append(log)

        def rest(self, worker, loc, log):
            """Rests the worker.
            """
            worker.disable_effect('Exhausted') # rest immediately disables the effect and removes its counter

            # at first we set excluded tags
            kwargs = ["dungeon", "angry", "in pain", "after sex", "group", "normalsex", "bdsm"]
            if (worker.get_stat("disposition") < 500) and ("Exhibitionist" not in worker.traits) and not check_lovers(worker, hero):
                kwargs.append("nude") # with not too low disposition nude pics become available during rest
            kwargs = dict(exclude=kwargs, add_mood=False)

            # if vitality is really low, they try to sleep, assuming there is a sleeping picture
            if worker.get_stat("vitality") < worker.get_max("vitality")/5 and worker.has_image("sleeping", **kwargs):
                log.img = worker.show("sleeping", resize=ND_IMAGE_SIZE, **kwargs)
                log.append("%s is too tired to do anything but sleep at %s free time." % (worker.name, worker.pp))
            else:
            # otherwise we build a list of usable tags
                available = list()

                if worker.has_image("sleeping", **kwargs):
                    available.append("sleeping")
                if worker.has_image("reading", **kwargs):
                    available.append("reading")
                if worker.get_stat("vitality") >= worker.get_max("vitality")*.3: # not too tired for more active rest
                    if worker.has_image("shopping", **kwargs) and (worker.gold >= 200): # eventually there should be a real existing event about going to shop and buy a random item there for gold. after all we do have an algorithm for that. but atm it might be broken, so...
                        available.append("shopping")
                    if "Nymphomaniac" in worker.traits or "Horny" in worker.effects:
                        if worker.has_image("masturbation", **kwargs):
                            available.append("masturbation")
                if worker.get_stat("vitality") >= worker.get_max("vitality")/2: # not too tired for sport stuff
                    if worker.has_image("sport", **kwargs):
                        available.append("sport")
                    if worker.has_image("exercising", **kwargs):
                        available.append("exercising")
                if worker.has_image("eating", **kwargs):
                    available.append("eating")
                if worker.has_image("bathing", **kwargs):
                    available.append("bathing")
                if worker.has_image("rest", **kwargs):
                    available.append("rest")

                if not(available):
                    available = ["profile"] # no rest at all? c'mon...

                log.img = worker.show(choice(available), resize=ND_IMAGE_SIZE, **kwargs)
                image_tags = log.img.get_image_tags()
                if "sleeping" in image_tags:
                    if "living" in image_tags:
                        log.append("%s is enjoying additional bedtime in %s room." % (worker.name, worker.pp))
                    elif "beach" in image_tags:
                        log.append("%s takes a small nap at the local beach." % worker.name)
                    elif "nature" in image_tags:
                        log.append("%s takes a small nap in the local park." % worker.name)
                    else:
                        log.append("%s takes a small nap during %s free time." % (worker.name, worker.pp))
                elif "masturbation" in image_tags:
                    log.append(choice(["%s has some fun with %sself during %s free time." % (worker.name, worker.op, worker.pp),
                                                 "%s is relieving %s sexual tension at the free time." % (worker.name, worker.pp)]))
                elif "onsen" in image_tags:
                    log.append("%s relaxes in the onsen. The perfect remedy for stress!" % worker.name)
                elif "reading" in image_tags:
                    log.append(choice(["%s spends %s free time reading." % (worker.name, worker.pp),
                                                 "%s is enjoying a book and relaxing." % worker.name]))
                elif "shopping" in image_tags:
                    log.append(choice(["%s spends %s free time to visit some shops." % (worker.name, worker.pp),
                                                 "%s is enjoying a small shopping tour." % worker.name]))
                elif "exercising" in image_tags:
                    log.append("%s keeps %sself in shape doing some exercises during %s free time." % (worker.name, worker.op, worker.pp))
                elif "sport" in image_tags:
                    log.append("%s is in a good shape today, so %s spends %s free time doing sports." % (worker.name, worker.p, worker.pp))
                elif "eating" in image_tags:
                    log.append(choice(["%s has a snack during %s free time." % (worker.name, worker.pp),
                                                 "%s spends %s free time enjoying a meal." % (worker.name, worker.pp)]))
                elif "bathing" in image_tags:
                    if "pool" in image_tags:
                        log.append("%s spends %s free time enjoying swimming in the local swimming pool." % (worker.name, worker.pp))
                    elif "beach" in image_tags:
                        log.append("%s spends %s free time enjoying swimming at the local beach. The water is great today!" % (worker.name, worker.pp))
                    elif "living" in image_tags:
                        log.append("%s spends %s free time enjoying a bath." % (worker.name, worker.pp))
                    else:
                        log.append("%s spends %s free time relaxing in a water." % (worker.name, worker.pp))
                else:
                    if "living" in image_tags:
                        log.append(choice(["%s is resting in %s room." % (worker.name, worker.pp),
                                           "%s is taking a break in %s room to recover." % (worker.name, worker.pp)]))
                    elif "beach" in image_tags:
                            log.append(choice(["%s is relaxing at the local beach." % worker.name,
                                               "%s is taking a break at the local beach." % worker.name]))
                    elif "pool" in image_tags:
                            log.append(choice(["%s is relaxing in the local swimming pool." % worker.name,
                                               "%s is taking a break in the local swimming pool." % worker.name]))
                    elif "nature" in image_tags:
                        if ("wildness" in image_tags):
                            log.append(choice(["%s is resting in the local forest." % worker.name,
                                               "%s is taking a break in the local forest." % worker.name]))
                        else:
                            log.append(choice(["%s is resting in the local park." % worker.name,
                                               "%s is taking a break in the local park." % worker.name]))
                    elif ("urban" in image_tags) or ("public" in image_tags):
                            log.append(choice(["%s is relaxing somewhere in the city." % worker.name,
                                               "%s is taking a break somewhere in the city." % worker.name]))
                    else:
                        log.append(choice(["%s is relaxing during %s free time." % (worker.name, worker.pp),
                                           "%s is taking a break during %s free time." % (worker.name, worker.pp)]))

            if not log.img:
                log.img = worker.show("rest", resize=ND_IMAGE_SIZE)

            # Work with JP in order to try and waste nothing.
            # Any Char without impairments should recover health and vitality in 3 days fully.
            # About 5 days for full mp recovery.
            # TODO Maybe use home bonuses???
            convert_ap_to_jp(worker)
            jp = worker.jobpoints
            init_jp = worker.setAP*100

            ratio = float(jp)/(init_jp or 300)

            # maximum restoration:
            health = worker.get_max("health")*.33*ratio
            vit = worker.get_max("vitality")*.33*ratio
            mp = worker.get_max("mp")*.2*ratio

            # Effects malus:
            if 'Drowsy' in worker.effects:
                vit *= .5

            # We do it in three steps to try and save some JP if possible:
            jp_step = round_int(jp/3)
            if jp_step < 5: # To little JP to matter:
                return

            for i in range(3):
                worker.jobpoints -= jp_step
                if worker.jobpoints < 0:
                    worker.jobpoints = 0

                value = round_int(health/3)
                log.logws('health', value)

                value = round_int(vit/3)
                log.logws('vitality', value)

                value = round_int(mp/3)
                log.logws('mp', value)

                if jp_step > 5:
                    log.logws('joy', randrange(2))

                if self.is_rested(worker):
                    break

        def is_rested(self, worker):
            c0 = worker.get_stat("vitality") >= worker.get_max("vitality")*.95
            c1 = worker.get_stat("health") >= worker.get_max('health')*.95
            c2 = not 'Food Poisoning' in worker.effects

            if all([c0, c1, c2]):
                return True
            else:
                return False

        def after_rest(self, worker, log):
            # Must check for is_rested first always.
            if self.is_rested(worker) and log is not None:
                log.append("%s is both well rested and healthy so at this point this is simply called: {color=[red]}slacking off :){/color}" % worker.pC)


    class AutoRest(Rest):
        """Same as Rest but game will try to reset character to it's previous job."""
        def __init__(self):
            super(AutoRest, self).__init__()
            self.id = "AutoRest"
            self.desc = "Autorest is a type of rest which automatically return character to previous job after resting is no longer needed"

        def after_rest(self, worker, log):
            if self.is_rested(worker):
                worker.action = self # toggle action
                action = worker.action

                if log is not None:
                    if action:
                        log.append("%s is now both well rested and goes back to work as %s!" % (worker.name, action))
                    else:
                        log.append("%s is now both well rested and healthy!" % worker.name)

                if worker.autoequip:
                    aeq_purpose = getattr(action, "aeq_purpose", None)
                    if aeq_purpose and worker.last_known_aeq_purpose != aeq_purpose:
                        worker.equip_for(aeq_purpose)

    ####################### Training Job  #############################
    class StudyingJob(Job):
        """Studying at pytfall.school, technically not a job...
        """
        def __init__(self):
            """
            Constructor for the singleton.
            """
            super(StudyingJob, self).__init__()
            self.id = "Study"
            self.type = "Training"

            self.desc = ""
