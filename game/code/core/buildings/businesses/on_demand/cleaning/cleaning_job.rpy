init -5 python:
    class CleaningJob(Job):
        id = "Cleaner"
        desc = "Keeps the building clean and neat"
        type = "Service"

        aeq_purpose = "Service"

        # Relevant skills and stats:
        base_skills = {"cleaning": 100, "service": 50}
        base_stats = {"agility": 25, "constitution": 50}

        traits = {"Adventurous", "Homebody", "Neat", "Messy", "Shy", "Curious", "Indifferent",
                  "Energetic", "Smart", "Clumsy", "Vicious", "Virtuous", "Abnormally Large Boobs"}

        @staticmethod
        def want_work(worker):
            return any(t.id in ["Cleaner", "Maid"] for t in worker.basetraits)

        @staticmethod
        def willing_work(worker):
            return any("Server" in t.occupations for t in worker.basetraits)

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.

               log is afk for the time being as this is now a team job.
            """
            effectiveness = 0
            name = worker.name
            effects = worker.effects
            # effects always work
            if 'Exhausted' in effects:
                log.append("%s is exhausted and is in need of some rest." % name)
                effectiveness -= 75
            elif 'Injured' in effects:
                log.append("%s is injured and is in need of some rest." % name)
                effectiveness -= 70
            elif 'Food Poisoning' in effects:
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (name, worker.pd))
                effectiveness -= 50
            elif 'Drunk' in effects:
                log.append("%s is drunk, which affects %s coordination. The occasional vomitting does not help either." % (name, worker.pd))
                effectiveness -= 30
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 15

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = CleaningJob.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Neat":
                    log.append("%s rearranged rooms to look a little more presentable on top of %s cleaning duties." % (name, worker.pd))
                    effectiveness += 40
                elif trait == "Homebody" or trait == "Indifferent":
                    log.append("%s really enjoys the simple and predictable cleaning task." % name)
                    effectiveness += 25
                elif trait == "Shy":
                    log.append("%s took comfort in the fact that %s doesn't have to work too closely with people on the cleaning job." % (name, worker.p))
                    effectiveness += 15
                elif trait == "Smart":
                    log.append("%s constantly finds new, more effective ways to tidy up the place." % name)
                    effectiveness += 10
                elif trait == "Virtuous":
                    log.append("%s was happy to be useful regardless of the job." % name)
                    effectiveness += 10
                elif trait == "Vicious":
                    log.append("After cleaning %s set it up so that the next person to walk into the room would get a bucket of nasty stuff on their head..." % name)
                    effectiveness -= 10
                elif trait == "Curious" or trait == "Energetic":
                    log.append("%s finds the cleaning duties too boring and repetitive to perform them properly." % name)
                    effectiveness -= 15
                elif trait == "Clumsy":
                    log.append("%s spilled a full bucket of freshener. At least it'll smell extra nice, if you can get past the eye-watering chemicals." % name)
                    effectiveness -= 20
                elif trait == "Adventurous":
                    log.append("%s got a little sad whenever %s cleaned a window because %s wanted to go out and explore, not clean." % (name, worker.p, worker.p))
                    effectiveness -= 25
                elif trait == "Messy":
                    log.append("%s reluctantly does %s job, preferring to hide the dirt instead of cleaning it properly." % (name, worker.pd))
                    effectiveness -= 40
                elif trait == "Abnormally Large Boobs":
                    log.append("Her boobs get in the way so much that she may as well scrub down the walls with them instead...")
                    effectiveness -= 50

            return effectiveness

        @staticmethod
        def calculate_disposition_level(worker, sub):
            """
            calculating the needed level of disposition;
            """
            disposition = 200 + 50 * sub

            if check_lovers(worker):
                disposition -= 50
            elif check_friends(worker):
                disposition -= 20

            traits = worker.traits
            if "Shy" in traits:
                disposition -= 50
            if "Natural Follower" in traits:
                disposition -= 25
            elif "Natural Leader" in traits:
                disposition += 25
            if "Neat" in traits:
                disposition -= 50
            if "Messy" in traits:
                disposition += 100
            return disposition

        @staticmethod
        def settle_workers_disposition(cleaners, business, log):
            for worker in cleaners:
                if CleaningJob.want_work(worker):
                    continue
                sub = check_submissivity(worker)
                name = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")
                if worker.status != 'slave':
                    if sub < 0:
                        temp = "%s doesn't enjoy working as a cleaner, but %s will get the job done."
                        sub = 15
                    elif sub == 0:
                        temp = "%s will work as a cleaner, but, truth be told, %s would prefer to do something else."
                        sub = 25
                    else:
                        temp = "%s makes it clear that %s wants another job before beginning the cleaning."
                        sub = 35
                    log.append(temp % (name, worker.p))
                    if dice(sub):
                        worker.logws('character', 1)
                    worker.logws("joy", -randint(3, 5))
                    worker.logws("disposition", -randint(5, 10))
                    worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
                else:
                    dispo = worker.get_stat("disposition")
                    dispo_req = CleaningJob.calculate_disposition_level(worker, sub)
                    if sub < 0:
                        if dispo < dispo_req:
                            temp = "%s is a slave so no one really cares, but being forced to work as a cleaner, %s's quite upset." % (name, worker.p)
                        else:
                            temp = "%s will do as %s is told, but doesn't mean that %s'll be happy about %s cleaning duties." % (name, worker.p, worker.p, worker.pd)
                        sub = 25
                    elif sub == 0:
                        if dispo < dispo_req:
                            temp = "%s will do as you command, but %s will hate every second of %s cleaning shift..." % (name, worker.p, worker.pd)
                        else:
                            temp = "%s was very displeased by %s order to work as a cleaner, but didn't dare to refuse." % (name, worker.pd)
                        sub = 35
                    else:
                        if dispo < dispo_req:
                            temp = "%s was very displeased by %s order to work as a cleaner, and makes it clear for everyone before getting busy with clients." % (name, worker.pd)
                        else:
                            temp = "%s will do as you command and work as a cleaner, but not without a lot of grumbling and complaining." % name
                        sub = 45
                    log.append(temp)
                    if dice(sub):
                        worker.logws('character', 1)
                    if dispo < dispo_req:
                        worker.logws("joy", -randint(4, 8))
                        worker.logws("disposition", -randint(5, 10))
                        worker.logws('vitality', -randint(5, 10))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(1, 4))
