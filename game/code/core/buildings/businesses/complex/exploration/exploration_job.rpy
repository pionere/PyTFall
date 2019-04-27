init -5 python:
    class ExplorationJob(Job):
        pass # FIXME obsolete

    class ExplorationTask(Job):
        id = "Exploring"
        type = "Combat"

        # Traits/Job-types associated with this job:
        occupations = ["Combatant"] # General Strings likes SIW, Combatant, Server...
        occupation_traits = ["Warrior", "Mage", "Knight", "Shooter", "Healer"] # Corresponding traits, later replaced by the corresponding instances
        aeq_purpose = 'Fighting'

        # Relevant skills and stats:
        base_stats = {"attack": 20, "defence": 20,
                           "agility": 20, "magic": 20}
        base_skills = {"exploration": 100}

        desc = "Explores the world for you"

        allowed_status = ["free"]

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.

               Another 'team' job which we have individual lines for...
               Maybe unique reports should be a thing as well for on_demand businesses?
            """
            effectiveness = 0
            name = worker.name
            if 'Exhausted' in worker.effects:
                log.append("%s is exhausted and is in need of some rest." % name)
                effectiveness -= 75
            elif 'Injured' in worker.effects:
                log.append("%s is injured and is in need of some rest." % name)
                effectiveness -= 70
            elif 'Food Poisoning' in worker.effects:
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (name, worker.pp))
                effectiveness -= 50
            elif 'Drunk' in worker.effects:
                log.append("%s is drunk, which affects %s coordination. Not the best thing when you need to guard something." % (name, worker.pp))
                effectiveness -= 20
            elif 'Down with Cold' in worker.effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 15

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = ["Abnormally Large Boobs", "Aggressive", "Coward", "Stupid", "Psychic",
                          "Natural Leader", "Scars", "Artificial Body", "Sexy Air", "Adventurous",
                          "Courageous", "Manly", "Sadist", "Nerd", "Smart", "Peaceful", "Neat"]
                traits = list(i.id for i in worker.traits if i.id in traits)

                if "Lolita" in worker.traits and worker.height == "short":
                    traits.append("Lolita")
                if traits:
                    trait = choice(traits)
                else:
                    return effectiveness

                if trait == "Abnormally Large Boobs":
                    log.append("Her massive tits get in the way and keep her off balance as %s tries to work security." % name)
                    effectiveness -= 25
                elif trait == "Aggressive":
                    if dice(50):
                        log.append("%s can not sit still, which disrupts the plans of your team." % name)
                        effectiveness -= 35
                    else:
                        log.append("Looking for a good fight, %s patrols the area, scaring away the marauders." % name)
                        effectiveness += 50
                elif trait == "Coward":
                    log.append("%s keeps asking for backup every single time an incident arises." % name)
                    effectiveness -= 25
                elif trait == "Stupid":
                    log.append("%s has trouble adapting to the constantly evolving world." % name)
                    effectiveness -= 15
                elif trait == "Smart":
                    log.append("%s keeps learning new ways to track the enemy." % name)
                    effectiveness += 15
                elif trait == "Neat":
                    log.append("%s refuses to dirty %s hands on some of the uglier looking beasts." % (name, worker.pp))
                    effectiveness -= 15
                elif trait == "Psychic":
                    log.append("%s knows the enemy movements and always steps in the right direction." % name)
                    effectiveness += 30
                elif trait == "Adventurous":
                    log.append("%s is always looking for new adventures." % name)
                    effectiveness += 25
                elif trait == "Natural Leader":
                    log.append("%s leads the way of your team." % name)
                    effectiveness += 50
                elif trait == "Artificial Body":
                    log.append("%s is a construct and walk through bushes effortless." % name)
                    effectiveness += 25
                elif trait == "Courageous":
                    log.append("%s refuses to back down no matter the odds, making a great explorer." % name)
                    effectiveness += 25
                elif trait == "Manly":
                    log.append("%s is bigger than usual and does not shy away in dire situations." % name)
                    effectiveness += 35
                elif trait == "Nerd":
                    log.append("%s feels like a super hero while walking in the forest." % name)
                    effectiveness += 15
                elif trait == "Peaceful":
                    log.append("%s has to deal with some very unruly opponents that give %s a hard time." % (name, worker.op))
                    effectiveness -= 35
            return effectiveness

        @classmethod
        def settle_workers_disposition(cls, workers, log):
            log(set_font_color("Your team is ready for action!", "cadetblue"))

            for worker in workers:
                if not("Combatant" in worker.gen_occs):
                    sub = check_submissivity(worker)
                    if sub < 0:
                        if dice(15):
                            worker.logws('character', 1)
                        log("%s doesn't enjoy going on exploration, but %s will get the job done." % (worker.name, worker.p))
                    elif sub == 0:
                        if dice(25):
                            worker.logws('character', 1)
                        log("%s would prefer to do something else." % worker.nickname)
                    else:
                        if dice(35):
                            worker.logws('character', 1)
                        log("%s makes it clear that %s wants to do something else." % (worker.name, worker.p))
                    worker.logws("joy", -randint(3, 5))
                    worker.logws("disposition", -randint(5, 10))
                    worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
