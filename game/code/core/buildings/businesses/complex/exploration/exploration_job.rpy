init -5 python:
    class ExplorationJob(Job):
        pass # FIXME obsolete

    class ExplorationTask(Job):
        id = "Explorer"
        desc = "Explores the world for you"
        type = "Combat"

        aeq_purpose = "Fighting"

        # Relevant skills and stats:
        base_stats = {"attack": 25, "defence": 25,
                           "agility": 25, "magic": 25}
        base_skills = {"exploration": 100}

        traits = {"Aggressive", "Coward", "Stupid", "Psychic",
                 "Natural Leader", "Artificial Body", "Adventurous",
                 "Courageous", "Manly", "Nerd", "Smart", "Peaceful", "Neat"}

        @staticmethod
        def want_work(worker):
            return any("Combatant" in t.occupations for t in worker.basetraits)

        @staticmethod
        def willing_work(worker):
            return any("Combatant" in t.occupations for t in worker.basetraits)

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.

               Another 'team' job which we have individual lines for...
               Maybe unique reports should be a thing as well for on_demand businesses?
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
            elif 'Drunk' in effects:
                log.append("%s is drunk, which affects %s coordination. Not the best thing when you need to guard something." % (name, worker.pd))
                effectiveness -= 20
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 15

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = ExplorationTask.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Aggressive":
                    if dice(50):
                        log.append("%s can not sit still, which disrupts the plans of your team." % name)
                        effectiveness -= 35
                    else:
                        log.append("Looking for a good fight, %s patrols the area, scaring away the marauders." % name)
                        effectiveness += 50
                elif trait == "Natural Leader":
                    log.append("%s leads the way of your team." % name)
                    effectiveness += 50
                elif trait == "Manly":
                    log.append("%s is bigger than usual and does not shy away in dire situations." % name)
                    effectiveness += 35
                elif trait == "Psychic":
                    log.append("%s knows the enemy movements and always steps in the right direction." % name)
                    effectiveness += 30
                elif trait == "Adventurous":
                    log.append("%s is always looking for new adventures." % name)
                    effectiveness += 25
                elif trait == "Artificial Body":
                    log.append("%s is a construct and walk through bushes effortless." % name)
                    effectiveness += 25
                elif trait == "Courageous":
                    log.append("%s refuses to back down no matter the odds, making a great explorer." % name)
                    effectiveness += 25
                elif trait == "Nerd":
                    log.append("%s feels like a super hero while walking in the forest." % name)
                    effectiveness += 15
                elif trait == "Smart":
                    log.append("%s keeps learning new ways to track the enemy." % name)
                    effectiveness += 15
                elif trait == "Stupid":
                    log.append("%s has trouble adapting to the constantly evolving world." % name)
                    effectiveness -= 15
                elif trait == "Neat":
                    log.append("%s refuses to dirty %s hands on some of the uglier looking beasts." % (name, worker.pd))
                    effectiveness -= 15
                elif trait == "Coward":
                    log.append("%s keeps asking for backup every single time an incident arises." % name)
                    effectiveness -= 25
                elif trait == "Peaceful":
                    log.append("%s has to deal with some very unruly opponents that give %s a hard time." % (name, worker.op))
                    effectiveness -= 35
            return effectiveness

        """
        @classmethod
        def settle_workers_disposition(cls, workers, log):
            log(set_font_color("Your team is ready for action!", "cadetblue"))

            for worker in workers:
                if cls.want_work(worker):
                    continue
                sub = check_submissivity(worker)
                if sub > 0:
                    log("%s doesn't enjoy going on exploration, but %s will get the job done." % (worker.name, worker.p))
                    sub = 15
                elif sub == 0:
                    log("%s would prefer to do something else." % worker.nickname)
                    sub = 25
                else:
                    log("%s makes it clear that %s wants to do something else." % (worker.name, worker.p))
                    sub = 35
                if dice(sub):
                    worker.logws('character', 1)
                worker.logws("joy", -randint(3, 5))
                worker.logws("disposition", -randint(5, 10))
                worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
        """