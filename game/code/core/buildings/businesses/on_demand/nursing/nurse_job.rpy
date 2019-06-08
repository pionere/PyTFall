init -5 python:
    class NurseJob(Job):
        id = "Nurse"
        desc = "Tends to injured customers, cures their sickness."
        type = "Service"

        per_client_payout = 50

        aeq_purpose = "Nurse"

        # Relevant skills and stats:
        base_stats = {"intelligence": 80, "magic": 60,
                           "charisma": 20, "agility": 20}
        base_skills = {"service": 20, "refinement": 10}

        traits = {"Aggressive", "Neat", "Messy", "Adventurous",
                  "Big Boobs", "Great Arse", "Bad Eyesight", "Indifferent", "Vicious", 
                  "Virtuous", "Clumsy", "Sadist", "Peaceful"}

        @staticmethod
        def want_work(worker):
            return any(t.id == "Healer" for t in worker.basetraits)

        @staticmethod
        def willing_work(worker):
            return any("Caster" in t.occupations for t in worker.basetraits)

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
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (name, worker.pp))
                effectiveness -= 50
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 40
            elif 'Drunk' in effects:
                log.append("%s is drunk. Not the best thing when you need take care of others." % name)
                effectiveness -= 20
            elif 'Revealing Clothes' in effects:
                log.append("%s revealing clothes attract unneeded attention, interfering with work." % worker.ppC)
                effectiveness -= 10

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = NurseJob.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Peaceful":
                    log.append("The peaceful atmosphere of %s help the patients to relax." % name)
                    effectiveness += 40
                elif trait == "Virtuous":
                    log.append("The patients of %s are happy, because their caretaker never turns them down." % name)
                    effectiveness += 35
                elif trait == "Great Arse" or trait == "Big Boobs":
                    log.append("The big qualities of %s distracts the patients from their suffer and pain." % name)
                    effectiveness += 15
                elif trait == "Neat":
                    log.append("The clean environment around %s prevents the spread of diseases." % name)
                    effectiveness += 10
                elif trait == "Bad Eyesight":
                    log.append("%s keeps mixing the prescibed pills." % name)
                    effectiveness -= 10
                elif trait == "Adventurous":
                    log.append("%s would rather be outside then closed in with sick people." % name)
                    effectiveness -= 10
                elif trait == "Indifferent":
                    log.append("Patients do not like when it is obvious %s do not care about them." % name)
                    effectiveness -= 15
                elif trait == "Clumsy":
                    log.append("The daily routine of the patients is often messed up by %s." % name)
                    effectiveness -= 20
                elif trait == "Messy":
                    log.append("The mess from %s is a rich soil for diseases." % name)
                    effectiveness -= 25
                elif trait == "Aggressive":
                    log.append("%s keeps disturbing the patients. Maybe it's not the best job for %s." % (name, worker.op))
                    effectiveness -= 40
                elif trait == "Vicious":
                    log.append("Sometimes %s turns even the easiest cases into a nightmare." % name)
                    effectiveness -= 45
                elif trait == "Sadist":
                    log.append("%s intentionally prolongs the suffering of the patients." % name)
                    effectiveness -= 50
            return effectiveness

        @staticmethod
        def settle_workers_disposition(workers, business, log):
            for worker in workers:
                if NurseJob.want_work(worker):
                    continue
                sub = check_submissivity(worker)
                name = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")
                if worker.status != 'slave':
                    if sub < 0:
                        temp = "%s doesn't enjoy working as nurse, but %s will get the job done."
                        sub = 15
                    elif sub == 0:
                        temp = "%s will work as a nurse, but %s would prefer to do something else."
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
                    dispo_req = NurseJob.calculate_disposition_level(worker)
                    if sub < 0:
                        if dispo < dispo_req:
                            temp = "%s is a slave so no one really cares, but being forced to work as a nurse, %s's quite upset." % (name, worker.p)
                        else:
                            temp = "%s will do as %s's told, but this doesn't mean that %s'll be happy about %s nursing duties." % (name, worker.p, worker.p, worker.pp)
                        sub = 25
                    elif sub == 0:
                        if dispo < dispo_req:
                            temp = "%s will do as you command, but %s will hate every second of being forced to work as a nurse..." % (name, worker.p)
                        else:
                            temp = "%s was very displeased by %s order to work as a nurse, but didn't dare to refuse." % (name, worker.pp)
                        sub = 35
                    else:
                        if dispo < dispo_req:
                            temp = "%s was very displeased by %s order to work as a nurse." % (name, worker.pp)
                        else:
                            temp = "%s will do as you command and work as a nurse, but not without a lot of grumbling and complaining." % name
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
