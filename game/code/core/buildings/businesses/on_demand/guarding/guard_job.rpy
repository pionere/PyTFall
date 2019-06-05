init -5 python:
    class GuardJob(Job):
        id = "Guard"
        desc = "Protects your business and girls from rivals and aggressive customers"
        type = "Combat"

        aeq_purpose = "Guard"

        # Relevant skills and stats:
        base_stats = {"attack": 20, "defence": 20,
                           "agility": 20, "magic": 20}
        base_skills = {"security": 100}

        traits = {"Abnormally Large Boobs", "Aggressive", "Coward", "Stupid", "Neat",
                  "Natural Leader", "Scars", "Artificial Body", "Sexy Air", "Adventurous",
                  "Courageous", "Manly", "Sadist", "Nerd", "Smart", "Peaceful", "Psychic"}

        @staticmethod
        def want_work(worker):
            return any(t.id in ["Warrior", "Knight", "Mage", "Assassin"] for t in worker.basetraits)

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
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (name, worker.pp))
                effectiveness -= 50
            elif 'Drunk' in effects:
                log.append("%s is drunk, which affects %s coordination. Not the best thing when you need to guard something." % (name, worker.pp))
                effectiveness -= 20
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 15
            elif 'Revealing Clothes' in effects:
                if dice(50):
                    log.append("%s revealing clothes attract unneeded attention, interfering with work." % worker.ppC)
                    effectiveness -= 10
                else:
                    log.append("%s revealing clothes help to pacify some aggressive customers." % worker.ppC)
                    effectiveness += 10

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = GuardJob.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if worker.height == "short":
                    traits.append(store.traits["Lolita"])

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Aggressive":
                    if dice(50):
                        log.append("%s keeps disturbing customers who aren't doing anything wrong. Maybe it's not the best job for %s." % (name, worker.op))
                        effectiveness -= 35
                    else:
                        log.append("Looking for a good fight, %s patrols the area, scaring away the rough customers." % name)
                        effectiveness += 50
                elif trait == "Natural Leader":
                    log.append("%s often manages to talk customers out of starting an incident." % name)
                    effectiveness += 50
                elif trait == "Manly":
                    log.append("%s is bigger than usual, %s prevents a lot of trouble just by being there." % (name, worker.p))
                    effectiveness += 35
                elif trait == "Psychic":
                    log.append("%s knows when customers are going to start something, and prevents it easily." % name)
                    effectiveness += 30
                elif trait == "Artificial Body":
                    log.append("%s makes no effort to hide the fact that %s was a construct, intimidating would-be violators." % (name, worker.p))
                    effectiveness += 25
                elif trait == "Courageous":
                    log.append("%s refuses to back down no matter the odds, making a great guard." % name)
                    effectiveness += 25
                elif trait == "Adventurous":
                    log.append("%s fought bandits as an adventurer. This makes working security relatively easy." % name)
                    effectiveness += 25
                elif trait == "Scars":
                    log.append("One look at %s scars is enough to tell the violators that %s means business." % (worker.pp, name))
                    effectiveness += 20
                elif trait == "Smart":
                    log.append("%s keeps learning new ways to prevent violence before it happens." % name)
                    effectiveness += 15
                elif trait == "Sexy Air":
                    log.append("People around %s back %s up just because of %s sexiness." % (name, worker.op, worker.pp))
                    effectiveness += 15
                elif trait == "Sadist":
                    log.append("%s gladly beats it out of any violators. Everyone deserves to be punished." % name)
                    effectiveness += 15
                elif trait == "Nerd":
                    log.append("%s feels like a super hero while protecting your workers." % name)
                    effectiveness += 15
                elif trait == "Neat":
                    log.append("%s refuses to dirty %s hands on some of the uglier looking criminals." % (name, worker.pp))
                    effectiveness -= 15
                elif trait == "Stupid":
                    log.append("%s has trouble adapting to the constantly evolving world of crime prevention." % name)
                    effectiveness -= 15
                elif trait == "Coward":
                    log.append("%s keeps asking for backup every single time an incident arises." % name)
                    effectiveness -= 25
                elif trait == "Abnormally Large Boobs":
                    log.append("Her massive tits get in the way and keep her off balance as %s tries to work security." % name)
                    effectiveness -= 25
                elif trait == "Peaceful":
                    log.append("%s has to deal with some very unruly patrons that give %s a hard time." % (name, worker.op))
                    effectiveness -= 35
                elif trait == "Lolita":
                    log.append("%s is too small to be taken seriously. Some of the problematic customers just laugh at %s." % (name, worker.op))
                    effectiveness -= 50
            return effectiveness

        @staticmethod
        def settle_workers_disposition(workers, business, all_on_deck=False):
            if not isinstance(workers, (set, list, tuple)):
                workers = [workers]

            log = business.log

            if all_on_deck:
                # Make sure we make a note that these are not dedicated guards
                log(set_font_color("Clients in building got too unruly! All free workers are called to serve as guards!", "red"))
            else:
                log(set_font_color("Your guards are starting their shift!", "cadetblue"))

            for worker in workers:
                if GuardJob.want_work(worker):
                    continue
                sub = check_submissivity(worker)
                name = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")
                if worker.status != 'slave':
                    if sub < 0:
                        log("%s doesn't enjoy working as guard, but %s will get the job done." % (name, worker.p))
                        sub = 15
                    elif sub == 0:
                        log("%s will work as a guard, but %s would prefer to do something else." % (name, worker.p))
                        sub = 25
                    else:
                        log("%s makes it clear that %s wants another job." % (name, worker.p))
                        sub = 35
                    if dice(sub):
                        worker.logws('character', 1)
                    worker.logws("joy", -randint(3, 5))
                    worker.logws("disposition", -randint(5, 10))
                    worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
                else:
                    dispo = worker.get_stat("disposition")
                    dispo_req = GuardJob.calculate_disposition_level(worker)
                    if sub < 0:
                        if dispo < dispo_req:
                            log("%s is a slave so no one really cares, but being forced to work as a guard, %s's quite upset." % (name, worker.p))
                        else:
                            log("%s will do as %s's told, but this doesn't mean that %s'll be happy about %s guarding duties." % (name, worker.p, worker.p, worker.pp))
                        sub = 25
                    elif sub == 0:
                        if dispo < dispo_req:
                            log("%s will do as you command, but %s will hate every second of being forced to work as a guard..." % (name, worker.p))
                        else:
                            log("%s was very displeased by %s order to work as a guard, but didn't dare to refuse." % (name, worker.pp))
                        sub = 35
                    else:
                        if dispo < dispo_req:
                            log("%s was very displeased by %s order to work as a guard." % (name, worker.pp))
                        else:
                            log("%s will do as you command and work as a guard, but not without a lot of grumbling and complaining." % name)
                        sub = 45
                    if dice(sub):
                        worker.logws('character', 1)
                    if worker.get_stat("disposition") < dispo_req:
                        worker.logws("joy", -randint(4, 8))
                        worker.logws("disposition", -randint(5, 10))
                        worker.logws('vitality', -randint(5, 10))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(1, 4))
