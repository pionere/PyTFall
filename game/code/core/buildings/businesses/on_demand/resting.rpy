init -5 python:
    ####################### Rest Job  #############################
    class Rest(Job):
        pass # FIXME obsolete

    class RestTask(Job):
        """Resting for character, technically not a job...
        """
        id = "Rest"
        type = "Resting"

        desc = "No one can work without taking a break sometimes. Rest restores health, vitality and mp and removes some negative effects"
        def __init__(self):
            """
            Creates a new Rest.
            """
            super(Rest, self).__init__() # FIXME obsolete

        @classmethod
        def run(cls, char):
            if char.PP < 15:
                # not enough PP for a meaningful rest 
                return
            if cls.is_rested(char):
                # already rested via some other ways -> inactivate AutoRest, but ignore the log
                cls.after_rest(char)
                return

            # the real rest 
            log = NDEvent(job=cls, char=char, loc=char.home)
            cls.rest(char, log)
            log.after_job()
            NextDayEvents.append(log)

        @classmethod
        def rest(cls, worker, log):
            """Rests the worker.
            """
            worker.disable_effect('Exhausted') # rest immediately disables the effect and removes its counter

            # at first we set excluded tags
            kwargs = ["dungeon", "angry", "in pain", "after sex", "group", "normalsex", "bdsm"]
            if (worker.get_stat("affection") < 500) and ("Exhibitionist" not in worker.traits) and not check_lovers(worker, hero):
                kwargs.append("nude") # with not too low affection nude pics become available during rest
            kwargs = dict(exclude=kwargs, add_mood=False)

            name = set_font_color(worker.name, "pink")

            vit_perc = worker.get_max("vitality")
            if vit_perc != 0:
                vit_perc = worker.get_stat("vitality") * 100 / vit_perc

            # if vitality is really low, they try to sleep, assuming there is a sleeping picture
            if vit_perc < 20 and worker.has_image("sleeping", **kwargs):
                log.img = worker.show("sleeping", **kwargs)
                log.append("%s is too tired to do anything but sleep at %s free time." % (name, worker.pp))
            else:
            # otherwise we build a list of usable tags
                available = list()

                if worker.has_image("sleeping", **kwargs):
                    available.append("sleeping")
                if worker.has_image("reading", **kwargs):
                    available.append("reading")
                if vit_perc > 30: # not too tired for more active rest
                    if worker.has_image("shopping", **kwargs) and (worker.gold >= 200): # eventually there should be a real existing event about going to shop and buy a random item there for gold. after all we do have an algorithm for that. but atm it might be broken, so...
                        available.append("shopping")
                    if "Nymphomaniac" in worker.traits or "Horny" in worker.effects:
                        if worker.has_image("masturbation", **kwargs):
                            available.append("masturbation")
                if vit_perc > 50: # not too tired for sport stuff
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

                log.img = worker.show(choice(available), **kwargs)
                image_tags = log.img.get_image_tags()
                if "sleeping" in image_tags:
                    if "living" in image_tags:
                        log.append("%s is enjoying additional bedtime in %s room." % (name, worker.pp))
                    elif "beach" in image_tags:
                        log.append("%s takes a small nap at the local beach." % name)
                    elif "nature" in image_tags:
                        log.append("%s takes a small nap in the local park." % name)
                    else:
                        log.append("%s takes a small nap during %s free time." % (name, worker.pp))
                elif "masturbation" in image_tags:
                    log.append(choice(["%s has some fun with %sself during %s free time." % (name, worker.op, worker.pp),
                                       "%s is relieving %s sexual tension at the free time." % (name, worker.pp)]))
                elif "onsen" in image_tags:
                    log.append("%s relaxes in the onsen. The perfect remedy for stress!" % name)
                elif "reading" in image_tags:
                    log.append(choice(["%s spends %s free time reading." % (name, worker.pp),
                                       "%s is enjoying a book and relaxing." % name]))
                elif "shopping" in image_tags:
                    log.append(choice(["%s spends %s free time to visit some shops." % (name, worker.pp),
                                       "%s is enjoying a small shopping tour." % name]))
                elif "exercising" in image_tags:
                    log.append("%s keeps %sself in shape doing some exercises during %s free time." % (name, worker.op, worker.pp))
                elif "sport" in image_tags:
                    log.append("%s is in a good shape today, so %s spends %s free time doing sports." % (name, worker.p, worker.pp))
                elif "eating" in image_tags:
                    log.append(choice(["%s has a snack during %s free time.",
                                       "%s spends %s free time enjoying a meal."]) % (name, worker.pp))
                elif "bathing" in image_tags:
                    if "pool" in image_tags:
                        log.append("%s spends %s free time enjoying swimming in the local swimming pool." % (name, worker.pp))
                    elif "beach" in image_tags:
                        log.append("%s spends %s free time enjoying swimming at the local beach. The water is great today!" % (name, worker.pp))
                    elif "living" in image_tags:
                        log.append("%s spends %s free time enjoying a bath." % (name, worker.pp))
                    else:
                        log.append("%s spends %s free time relaxing in a water." % (name, worker.pp))
                else:
                    if "living" in image_tags:
                        log.append(choice(["%s is taking a break in %s room to recover.",
                                           "%s is resting in %s room."]) % (name, worker.pp))
                    elif "beach" in image_tags:
                            log.append(choice(["%s is taking a break at the local beach.",
                                               "%s is relaxing at the local beach."]) % name)
                    elif "pool" in image_tags:
                            log.append(choice(["%s is taking a break in the local swimming pool.",
                                               "%s is relaxing in the local swimming pool."]) % name)
                    elif "nature" in image_tags:
                        if ("wildness" in image_tags):
                            log.append(choice(["%s is taking a break in the local forest.",
                                               "%s is resting in the local forest."]) % name)
                        else:
                            log.append(choice(["%s is taking a break in the local park.",
                                               "%s is resting in the local park."]) % name)
                    elif ("urban" in image_tags) or ("public" in image_tags):
                            log.append(choice(["%s is taking a break somewhere in the city.",
                                               "%s is relaxing somewhere in the city."]) % name)
                    else:
                        log.append(choice(["%s is taking a break during %s free time.",
                                           "%s is relaxing during %s free time."]) % (name, worker.pp))

            # Work with JP in order to try and waste nothing.
            # Any Char without impairments should recover health and vitality in 3 days fully.
            # About 5 days for full mp recovery.
            # TODO Maybe use home bonuses???
            jp = worker.PP
            init_jp = worker.setPP

            ratio = float(jp)/(init_jp or 300)

            # maximum restoration:
            health = worker.get_max("health")*.33*ratio
            vit = worker.get_max("vitality")*.33*ratio
            mp = worker.get_max("mp")*.2*ratio

            # Effects malus:
            if 'Drowsy' in worker.effects:
                vit *= .5

            # We do it in three steps to try and save some JP if possible:
            jp /= 3
            health = round_int(health/3)
            vit = round_int(vit/3)
            mp = round_int(mp/3)

            for i in range(3):
                worker.PP -= jp

                log.logws('health', health)
                log.logws('vitality', vit)
                log.logws('mp', mp)

                if jp > 5:
                    log.logws('joy', randrange(2))

                if cls.is_rested(worker):
                    cls.after_rest(worker, log)
                    break

        @staticmethod
        def is_rested(worker):
            if worker.get_stat("vitality") < worker.get_max("vitality"):
                return False
            if worker.get_stat("health") < worker.get_max('health'):
                return False
            if "Exhausted" in worker.effects:
                return False
            if 'Food Poisoning' in worker.effects:
                return False
            return True

        @staticmethod
        def after_rest(worker, log=None):
            if log is not None:
                log.append("%s is both well rested and healthy so at this point this is simply called: {color=red}slacking off :){/color}" % worker.pC)


    class AutoRest(Job):
        pass # FIXME obsolete

    class AutoRestTask(Rest):
        """Same as Rest but game will try to reset character to it's previous job."""
        id = "AutoRest"
        desc = "Autorest is a type of rest which automatically return character to previous job after resting is no longer needed"

        @staticmethod
        def is_rested(worker):
            if worker.get_stat("vitality") < worker.get_max("vitality")*.95:
                return False
            if worker.get_stat("health") < worker.get_max('health')*.95:
                return False
            if "Exhausted" in worker.effects:
                return False
            if 'Food Poisoning' in worker.effects:
                return False
            return True

        @staticmethod
        def after_rest(worker, log=None):
            worker.set_task(None)
            action = worker.job

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
        pass # FIXME obsolete

    class StudyingTask(Job):
        id = "Study"
        type = "Training"

        desc = ""
