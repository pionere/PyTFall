init -10 python:
    class NDEvent(_object):
        """Next Day Report. Logs in a single event to be read in next_day label.

        The load_image method will always return the same image. If you want to
        do another search, you have to set the 'img' attribute to 'None'.

        MONEY:
        During jobs, we log cash that players gets to self.earned
        Cash that workers may get during the job:
        worker.up_counter("_jobs_tips", value) # tips
        #worker.mod_flag("jobs_earned", value) # Normal stuff other than tips?
        #worker.mod_flag("jobs_earned_dishonestly", value) # Stole a wallet from client?

        DevNote: We used to create this at the very end of an action,
        now, we are creating the event as the action starts and pass it around
        between both normal methods and funcs and simpy events. This needs to
        be kept in check because older parts of code still just create this
        object at the end of their lifetime.
        """
        def __init__(self, type='', txt='', img='', char=None, charmod=None,
                     loc=None, locmod=None, red_flag=False, green_flag=False,
                     team=None, job=None, business=None):
            super(NDEvent, self).__init__()

            self.log = []
            if txt: self.log.append(txt)

            self.job = job
            if not type and job:
                self.type = job.event_type
            else:
                self.type = type

            self.txt = txt
            self.img = img

            self.char = char
            self.team = team
            if charmod is None:
                charmod = {}
            if team:
                self.team_charmod = charmod.copy()
                self.charmod = None
            else:
                self.charmod = charmod.copy()
                self.team_charmod = None

            # the location of the event (optional):
            self.loc = loc
            self.locmod = {} if locmod is None else locmod

            self.business = business

            self.green_flag = green_flag
            self.red_flag = red_flag

            self.earned = 0

        def append(self, text):
            # Adds a text to the log.
            self.log.append(text)

        def load_image(self):
            """
            Returns a renpy image showing the event.

            The image is selected based on the event type and the character.
            """
            # select/load an image according to img
            d = self.img
            # Try to analyze self.img in order to figure out what it represents:
            if isinstance(d, renpy.display.core.Displayable):
                return d

            size = ND_IMAGE_SIZE
            if isinstance(d, basestring):
                if not d:
                    raise Exception("Basestring Supplied as img {}: Ev.type: {}, Ev.loc.name: {}".format(
                                d,
                                self.type,
                                self.loc.name if self.loc else "Unknown"))
                elif "." in d:
                    return ProportionalScale(d, *size)
                else:
                    return self.char.show(self.img, resize=size, cache=True)
            nd_debug("Unknown Image Type: {} Provided to Event (Next Day Events class)".format(self.img), "warning")
            return ProportionalScale("content/gfx/interface/images/no_image.png", *size)

        # Data logging and application:
        def logws(self, s, value, char=None):
            # Logs stats changes.
            # Uses internal dict on chars namespace
            if char is None:
                char = self.char
            char.logws(s, value)

        def logloc(self, key, value):
            # Logs a stat for the location:
            self.locmod[key] = self.locmod.get(key, 0) + value
            """Updates stats for the building."""
            if key == 'fame':
                self.loc.modfame(value)
            elif key == 'reputation':
                self.loc.modrep(value)
            elif key == 'dirt':
                self.loc.moddirt(value)
            elif key == 'threat':
                self.loc.modthreat(value)
            else:
                raise Exception("Stat: {} does not exits for Businesses".format(key))

        def update_char_data(self, char):
            """Settles stats, exp and skills for workers.

            # After a long conversation with Dark and CW, we've decided to prevent workers dieing during jobs
            # I am leaving the code I wrote before that decision was reached in case
            # we change our minds or add jobs like exploration where it makes more sense.
            # On the other hand just ignoring it is bad, so let's at least reduce some stuff,
            # pretending that she lost consciousness for example.
            """
            data = char.stats_skills
            for key, value in data.iteritems():
                if key == "exp":
                    char.mod_exp(value)
                elif is_stat(key):
                    char.mod_stat(key, value)
                elif is_skill(key):
                    char.mod_skill(key, 0, value)

        def log_tips(self, worker):
            # logically logs tips as income of this business.
            # We settle later, in char.next_day()
            tips = worker.flag("_jobs_tips")
            if tips:
                loc = self.loc
                job = self.job

                worker.del_flag("_jobs_tips")
                worker.up_counter("dnd_accumulated_tips", tips)

                temp = "%s gets {color=gold}%d Gold{/color} in tips!" % (worker.name, tips)
                self.append(temp)
                loc.fin.log_logical_income(tips, job.id + " Tips")

        def after_job(self):
            # We run this after job but before ND reports
            # Figure out source for finlogs:
            fin_source = getattr(self.job, "id", "Unspecified Job")

            if self.char:
                self.update_char_data(self.char)
                self.charmod.update(self.char.stats_skills)
                self.char.stats_skills = {}
                self.log_tips(self.char)
                self.reset_workers_flags(self.char)
                if self.earned:
                    self.char.fin.log_logical_income(self.earned, fin_source)
            elif self.team:
                if not len(self.team):
                    raise Exception("Zero Modulo Division Detected #03")
                earned = round_int(self.earned/float(len(self.team)))
                for char in self.team:
                    self.update_char_data(char)
                    self.team_charmod[char] = char.stats_skills.copy()
                    self.log_tips(char)
                    char.stats_skills = {}
                    self.reset_workers_flags(char)
                    if earned:
                        char.fin.log_logical_income(earned, fin_source)

            # Location related:
            if hasattr(self.loc, "fin") and self.earned:
                self.loc.fin.log_logical_income(self.earned, fin_source)
            if self.earned:
                store.hero.add_money(self.earned, str(self.loc))
                #self.append("{color=gold}A total of %d Gold was earned!{/color}" % self.earned)
                self.append("You've earned {color=gold}%d Gold{/color}!" % self.earned) # use the line above if there are multiple shifts in one NDEvent
            else:
                self.append("{color=gold}No Gold{/color} was earned!")
            self.txt = self.log
            self.log = []

        def reset_workers_flags(self, char):
            for flag in char.flags.keys():
                if flag.startswith("jobs"):
                    char.del_flag(flag)


    class Job(_object):
        """Baseclass for jobs and other next day actions with some defaults.

        - Presently is used in modern Job Classes. Very similar to Job.
        """
        def __init__(self, event_type="jobreport"):
            """Creates a new Job.
            """
            self.id = "Base Job"
            self.type = None # job group to use in the report

            # Payout per single client, this is passed to Economy class and modified if needs be.
            self.per_client_payout = 5

            # Traits/Job-types associated with this job:
            self.occupations = list() # General Strings likes SIW, Combatant, Server...
            self.occupation_traits = list() # Corresponding traits...
            self.aeq_purpose = 'Casual'

            # Status we allow (workers):
            self.allowed_status = ["free", "slave"]
            self.allowed_genders = ["male", "female"]

            self.event_type = event_type

            # Each job should have two dicts of stats/skills to evaluate chars ability of performing it:
            self.base_skills = dict()
            self.base_stats = dict()
            # Where key: value are stat/skill: weight!

            self.desc = "Add Description." # String we can use to describe the Job.

        def __str__(self):
            return str(self.id)

        def auto_equip(self, worker):
            """
            Auto-equip a worker for this job.
            """
            if not worker.autoequip:
                return

            purpose = self.aeq_purpose
            last_known = worker.last_known_aeq_purpose

            if purpose == last_known:
                return

            # Special considerations:
            if purpose == "Fighting":
                if last_known in STATIC_ITEM.FIGHTING_AEQ_PURPOSES:
                    return

            # Otherwise, let us AEQ:
            worker.equip_for(purpose)

        @property
        def all_occs(self):
            # All Occupations:
            return set(self.occupations + self.occupation_traits)

        def calculate_disposition_level(self, worker):
            return 0

        def settle_workers_disposition(self, char=None):
            # Formerly check_occupation
            """Settles effects of worker who already agreed to do the job.

            Normaly deals with disposition, joy and vitality (for some reason?)
            """
            return True

        def normalize_required_stat(self, worker, stat, effectiveness, difficulty):
            value = worker.get_stat(stat)
            max_value = worker.get_max_stat(stat, tier=difficulty)
            if max_value == 0:
                raise Exception("Zero Dev #1 (%s)", stat)

            value = min(value, max_value*1.05)
            return value/float(max_value)*effectiveness

        def normalize_required_skill(self, worker, skill, effectiveness, difficulty):
            value = worker.get_skill(skill)
            max_value = worker.get_max_skill(skill, tier=difficulty)
            if max_value == 0:
                raise Exception("Zero Dev #2 (%s)", skill)

            value = min(value, max_value*1.05)
            return value/float(max_value)*effectiveness

        # We should also have a number of methods or properties to evaluate new dicts:
        def effectiveness(self, worker, difficulty, log=None, return_ratio=True,
                          manager_effectiveness=0):
            """We check effectiveness here during jobs from SimPy land.

            difficulty is used to counter worker tier.
            100 is considered a score where worker does the task with acceptable performance.
            min = 0 and max is 200

            return_ratio argument, when True, returns a multiplier of .1 to 2.0 instead...
            """
            ability = 0

            matched_gen_occ = len(worker.occupations.intersection(self.occupations))
            matched_base_traits = len(worker.basetraits.intersection(self.occupation_traits))

            # Class traits and Occs (Part 1)
            bt_bonus = 0
            if matched_base_traits:
                bt_bonus += 35
                if len(worker.basetraits) == 2 and matched_base_traits == 1:
                    bt_bonus *= .5
            bt_bonus += matched_gen_occ*15

            # Tiers:
            diff = worker.tier - difficulty
            tier_bonus = diff*10

            # Class traits and Occs (Part 2)
            if diff < 0: # Tier lower than the Building (difficulty)
                bt_bonus /= 1+abs(diff)
            elif diff > 0:
                bt_bonus += tier_bonus*2


            # Skills/Stats:
            default_points = 25
            skills = self.base_skills
            if not skills:
                total_skills = default_points*.33
            else:
                total_weight_points = sum(skills.values())
                #if total_weight_points == 0:
                #    raise Exception("Zero Dev #3 sum")
                total_skills = 0
                for skill, weight in skills.items():
                    weight_ratio = float(weight)/total_weight_points
                    max_p = default_points*weight_ratio

                    sp = worker.get_skill(skill)
                    sp_required = worker.get_max_skill(skill, tier=difficulty)
                    # if not sp_required:
                    #     raise Exception("Zero Dev #4 (%s)", skill)
                    total_skills += min(sp*max_p/sp_required, max_p*1.1)

            stats = self.base_stats
            if not stats:
                total_stats = default_points*.33
            else:
                total_weight_points = sum(stats.values())
                if total_weight_points == 0:
                    raise Exception("Zero Dev #5 sum")
                total_stats = 0
                for stat, weight in stats.items():
                    weight_ratio = float(weight)/total_weight_points
                    max_p = default_points*weight_ratio

                    sp = worker.get_stat(stat)
                    sp_required = worker.get_max_stat(stat, tier=difficulty)
                    if sp_required == 0:
                        raise Exception("Zero Dev #6 (%s)", stat)
                    total_stats += min(sp*max_p/sp_required, max_p*1.1)

            # Bonuses:
            traits_bonus = self.traits_and_effects_effectiveness_mod(worker, log)

            # Manager passive effect:
            if self.id == "Manager":
                manager_bonus = 15
            else:
                if manager_effectiveness >= 175:
                    manager_bonus = 20
                elif manager_effectiveness >= 130 and dice(manager_effectiveness-100):
                    manager_bonus = 10
                else:
                    manager_bonus = 0

            total = sum([bt_bonus, tier_bonus, manager_bonus,
                         traits_bonus, total_skills, total_stats])

            # Disposition Bonus (Percentage bonus):
            disposition_multiplier = worker.get_stat("disposition")*.0001 + 1.0
            total = round_int(total*disposition_multiplier)

            # Normalize:
            if total < 0:
                total = 0
            elif total > 200:
                total = 200

            if DEBUG_SIMPY:
                temp = {}
                for stat in self.base_stats:
                    temp[stat] = worker.get_stat(stat)
                devlog.info("Calculating Jobs Relative Ability, Char/Job: {}/{}:".format(worker.name, self.id))
                devlog.info("Stats: {}:".format(temp))
                args = (bt_bonus, tier_bonus, traits_bonus, total_skills, total_stats, disposition_multiplier, total)
                devlog.info("Gen Occ/BT: {}, Tier: {}, Traits: {}, Skills: {}, Stats: {}, Disposition Multiplier {} ==>> {}".format(*args))

            if return_ratio:
                total /= 100.0
                if total < .1:
                    total = .1

            return total

        def traits_and_effects_effectiveness_mod(self, worker, log):
            """Modifies workers effectiveness depending on traits and effects.

            returns an integer to be added to base calculations!
            """
            return 0

        def calc_jp_cost(self, manager_effectiveness, cost):
            # a good manager can reduce the original cost by 50%. (passive effect)
            if manager_effectiveness > 80:        # original effectiveness is between 0 and 200
                manager_effectiveness *= randint(75, 125)   # a bit of random -> 60(00) <= me <= 250(00)
                manager_effectiveness -= 6000     # 60 * 100                  ->   (00) <= me <= 190(00)
                if manager_effectiveness > 16000: # 160 * 100   me over 160 does not help further
                    manager_effectiveness = 16000           #                 ->   (00) <= me <= 160(00)
                manager_effectiveness /= 32000.0            #                 ->    0.0 <= me <= 0.5
                cost *= 1.0 - manager_effectiveness

            return cost
