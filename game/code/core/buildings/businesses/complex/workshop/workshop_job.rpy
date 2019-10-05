init -5 python:
    class WorkshopTask(Job):
        id = "Manufacturer"
        desc = "Crafts items and/or potions in the workshop"
        type = "Service"

        aeq_purpose = "Crafting"

        # Relevant skills and stats:
        base_stats = {"attack": 40, "agility": 40, "intelligence": 20}
        base_skills = {"crafting": 30, "refinement": 10}

        traits = {"Neat", "Messy", "Adventurous", "Bad Eyesight", "Clumsy"}

        @staticmethod
        def want_work(worker):
            return not {"Combatant", "Server"}.isdisjoint(worker.gen_occs)

        @staticmethod
        def willing_work(worker):
            return True

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.
            """
            effectiveness = 0
            name = worker.name
            effects = worker.effects
            if 'Exhausted' in effects:
                log.append("%s is exhausted and is in need of some rest." % name)
                effectiveness -= 75
            elif 'Injured' in effects:
                log.append("%s is injured and is in need of some rest." % name)
                effectiveness -= 70
            elif 'Food Poisoning' in effects:
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (name, worker.pd))
                effectiveness -= 50
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 40
            elif 'Drunk' in effects:
                log.append("%s is drunk. Not the best thing when you need precision." % name)
                effectiveness -= 20
            elif 'Revealing Clothes' in effects:
                log.append("The revealing clothes of %s are interfering with work." % name)
                effectiveness -= 10

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = WorkshopTask.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Neat":
                    log.append("The clean environment around %s helps to proceed faster." % name)
                    effectiveness += 10
                elif trait == "Bad Eyesight":
                    log.append("%s keeps mixing the tools and materials." % name)
                    effectiveness -= 10
                elif trait == "Adventurous":
                    log.append("%s would rather be outside then closed in with dust and dirt." % name)
                    effectiveness -= 10
                elif trait == "Clumsy":
                    log.append("%s creates a lot of waste in the workshop." % name)
                    effectiveness -= 20
                elif trait == "Messy":
                    log.append("The mess from %s makes it hard to find the required tools and materials." % name)
                    effectiveness -= 25
            return effectiveness

        @staticmethod
        def settle_workers_disposition(workers, business, log):
            for worker in workers:
                if WorkshopTask.want_work(worker):
                    continue
                sub = check_submissivity(worker)
                name = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")
                if worker.status != 'slave':
                    if sub > 0:
                        temp = "%s doesn't enjoy crafting, but %s will get the job done."
                        sub = 15
                    elif sub == 0:
                        temp = "%s will work in the workshop, but %s would prefer to do something else."
                        sub = 25
                    else:
                        temp = "%s makes it clear that %s wants another job."
                        sub = 35
                    log.append(temp % (name, worker.p))
                    if dice(sub):
                        worker.logws('character', 1)
                    worker.logws("joy", -randint(3, 5))
                    worker.logws("disposition", -randint(5, 10))
                    worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
                else:
                    dispo = worker.get_stat("disposition")
                    dispo_req = 0 # WorkshopTask.calculate_disposition_level(worker)
                    if sub > 0:
                        if dispo < dispo_req:
                            temp = "%s is a slave so no one really cares, but being forced to do crafting, %s's quite upset." % (name, worker.p)
                        else:
                            temp = "%s will do as %s's told, but this doesn't mean that %s'll be happy about %s crafting duties." % (name, worker.p, worker.p, worker.pd)
                        sub = 25
                    elif sub == 0:
                        if dispo < dispo_req:
                            temp = "%s will do as you command, but %s will hate every second of being forced to work in the workshop..." % (name, worker.p)
                        else:
                            temp = "%s was very displeased by %s order to work in the workshop, but didn't dare to refuse." % (name, worker.pd)
                        sub = 35
                    else:
                        if dispo < dispo_req:
                            temp = "%s was very displeased by %s order to work in the workshop." % (name, worker.pd)
                        else:
                            temp = "%s will do as you command and work in the workshop, but not without a lot of grumbling and complaining." % name
                        sub = 45
                    log.append(temp)
                    if dice(sub):
                        worker.logws('character', 1)
                    if worker.get_stat("disposition") < dispo_req:
                        worker.logws("joy", -randint(4, 8))
                        worker.logws("disposition", -randint(5, 10))
                        worker.logws('vitality', -randint(5, 10))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(1, 4))
