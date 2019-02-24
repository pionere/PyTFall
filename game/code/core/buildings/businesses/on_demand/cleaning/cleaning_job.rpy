init -5 python:
    class CleaningJob(Job):
        def __init__(self):
            super(CleaningJob, self).__init__()
            self.id = "Cleaning"
            self.type = "Service"

            # Traits/Job-types associated with this job:
            self.occupations = ["Server"] # General Strings likes SIW, Combatant, Server...
            self.occupation_traits = [traits["Maid"], traits["Cleaner"]] # Corresponding traits...
            self.aeq_purpose = 'Service'
            self.desc = "Keeps the building clean and neat"

            # Relevant skills and stats:
            self.base_skills = {"cleaning": 100, "service": 50}
            self.base_stats = {"agility": 25, "constitution": 50}

        def traits_and_effects_effectiveness_mod(self, worker,
                                                 log=None):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.

               log is afk for the time being as this is now a team job.
            """
            if not log:
                log = []

            effectiveness = 0
            # effects always work
            if 'Food Poisoning' in worker.effects:
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (worker.name, worker.pp))
                effectiveness -= 50
            elif 'Exhausted' in worker.effects:
                log.append("%s is exhausted and is in need of some rest." % worker.name)
                effectiveness -= 75
            elif 'Down with Cold' in worker.effects:
                log.append("%s is not feeling well due to colds..." % worker.name)
                effectiveness -= 15

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = list(i.id for i in worker.traits if i.id in ["Adventurous", "Homebody",
                                "Neat", "Messy", "Shy", "Curious", "Indifferent", "Energetic",
                                "Smart", "Clumsy", "Vicious", "Virtuous", "Abnormally Large Boobs"])
                if traits:
                    trait = choice(traits)
                else:
                    return effectiveness

                if trait == "Adventurous":
                    log.append("%s got a little sad whenever %s cleaned a window because %s wanted to go out and explore, not clean." % (worker.name, worker.p, worker.p))
                    effectiveness -= 25
                elif trait == "Homebody" or trait == "Indifferent":
                    log.append("%s really enjoys the simple and predictable cleaning task." % worker.name)
                    effectiveness += 25
                elif trait == "Neat":
                    log.append("%s rearranged rooms to look a little more presentable on top of %s cleaning duties." % (worker.name, worker.pp))
                    effectiveness += 40
                elif trait == "Smart":
                    log.append("%s constantly finds new, more effective ways to tidy up the place." % worker.name)
                    effectiveness += 10
                elif trait == "Messy":
                    log.append("%s reluctantly does %s job, preferring to hide the dirt instead of cleaning it properly." % (worker.name, worker.pp))
                    effectiveness -= 40
                elif trait == "Shy":
                    log.append("%s took comfort in the fact that %s doesn't have to work too closely with people on the cleaning job." % (worker.name, worker.p))
                    effectiveness += 15
                elif trait == "Curious" or trait == "Energetic":
                    log.append("%s finds the cleaning duties too boring and repetitive to perform them properly." % worker.name)
                    effectiveness -= 15
                elif trait == "Clumsy":
                    log.append("%s spilled a full bucket of freshener. At least it'll smell extra nice, if you can get past the eye-watering chemicals." % worker.name)
                    effectiveness -= 20
                elif trait == "Vicious":
                    log.append("After cleaning %s set it up so that the next person to walk into the room would get a bucket of nasty stuff on their head..." % worker.name)
                    effectiveness -= 10
                elif trait == "Virtuous":
                    log.append("%s was happy to be useful regardless of the job." % worker.name)
                    effectiveness += 10
                elif trait == "Abnormally Large Boobs":
                    log.append("Her boobs get in the way so much that she may as well scrub down the walls with them instead...")
                    effectiveness -= 50

            return effectiveness

        def calculate_disposition_level(self, worker): # calculating the needed level of disposition
            sub = check_submissivity(worker)
            if "Shy" in worker.traits:
                disposition = 150 + 50 * sub
            else:
                disposition = 200 + 50 * sub
            if check_lovers(hero, worker):
                disposition -= 50
            elif check_friends(hero, worker):
                disposition -= 20
            if "Natural Follower" in worker.traits:
                disposition -= 25
            elif "Natural Leader" in worker.traits:
                disposition += 25
            if "Neat" in worker.traits:
                disposition -= 50
            if "Messy" in worker.traits:
                disposition += 100
            return disposition

        def settle_workers_disposition(self, cleaners, business, all_on_deck=False):
            if not isinstance(cleaners, (set, list, tuple)):
                cleaners = [cleaners]

            log = business.log

            if all_on_deck:
                # Make sure we make a note that these are not dedicated cleaners
                log(set_font_color("Building got too dirty to work at! All free workers were called on cleaning duty!", "red"))
            else:
                log(set_font_color("Your cleaners are starting their shift!", "cadetblue"))

            for worker in cleaners:
                if not("Server" in worker.gen_occs):
                    sub = check_submissivity(worker)
                    if worker.status != 'slave':
                        if sub < 0:
                            if dice(15):
                                worker.logws('character', 1)
                            log("%s is not very happy with %s current job as a cleaner, but %s will get the job done." % (worker.name, worker.pp, worker.p))
                        elif sub == 0:
                            if dice(25):
                                worker.logws('character', 1)
                            log("%s will work as a cleaner, but, truth be told, %s would prefer to do something else." % (worker.nickname, worker.p))
                        else:
                            if dice(35):
                                worker.logws('character', 1)
                            log("%s makes it clear that %s wants another job before beginning the cleaning." % (worker.name, worker.p))
                        worker.logws("joy", -randint(3, 5))
                        worker.logws("disposition", -randint(5, 10))
                        worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
                    else:
                        if sub < 0:
                            if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                                log("%s is a slave so no one really cares, but being forced to work as a cleaner, %s's quite upset." % (worker.name, worker.p))
                            else:
                                log("%s will do as %s is told, but doesn't mean that %s'll be happy about %s cleaning duties." % (worker.name, worker.p, worker.p, worker.pp))
                            if dice(25):
                                worker.logws('character', 1)
                        elif sub == 0:
                            if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                                log("%s will do as you command, but %s will hate every second of %s cleaning shift..." % (worker.name, worker.p, worker.pp))
                            else:
                                log("%s was very displeased by %s order to work as a cleaner, but didn't dare to refuse." % (worker.name, worker.pp))
                            if dice(35):
                                worker.logws('character', 1)
                        else:
                            if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                                log("%s was very displeased by %s order to work as a cleaner, and makes it clear for everyone before getting busy with clients." % (worker.name, worker.pp))
                            else:
                                log("%s will do as you command and work as a cleaner, but not without a lot of grumbling and complaining." % worker.name)
                            if dice(45):
                                worker.logws('character', 1)
                        if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                            worker.logws("joy", -randint(4, 8))
                            worker.logws("disposition", -randint(5, 10))
                            worker.logws('vitality', -randint(5, 10))
                        else:
                            worker.logws("joy", -randint(2, 4))
                            worker.logws('vitality', -randint(1, 4))
