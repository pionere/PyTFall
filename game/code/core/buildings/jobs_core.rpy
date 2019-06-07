init -10 python:
    class NDEvent(_object):
        """Next Day Report. Logs in a single event to be read in next_day label.

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
            if team is not None:
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
                    data[key] = char.mod_stat(key, value)
                elif is_skill(key):
                    data[key] = char.mod_skill(key, 0, value)

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

            char = self.char
            earned = self.earned
            if char:
                self.update_char_data(char)
                self.charmod.update(char.stats_skills)
                char.stats_skills = {}
                self.log_tips(char)
                self.reset_workers_flags(char)
                if earned:
                    char.fin.log_logical_income(earned, fin_source)
            else:
                team = self.team
                if team:
                    if not len(team):
                        raise Exception("Zero Modulo Division Detected #03")
                    char_earned = round_int(earned/float(len(team)))
                    for char in team:
                        self.update_char_data(char)
                        self.team_charmod[char] = char.stats_skills.copy() # FIXME copy necessary?
                        char.stats_skills = {}
                        self.log_tips(char)
                        self.reset_workers_flags(char)
                        if char_earned:
                            char.fin.log_logical_income(char_earned, fin_source)

            # Location related:
            if earned:
                loc = self.loc
                if hasattr(loc, "fin"):
                    loc.fin.log_logical_income(earned, fin_source)
                store.hero.add_money(earned, str(loc))
                #self.append("{color=gold}A total of %d Gold was earned!{/color}" % earned)
                self.append("You've earned {color=gold}%d Gold{/color}!" % earned) # use the line above if there are multiple shifts in one NDEvent
            else:
                self.append("{color=gold}No Gold{/color} was earned!")
            self.txt = self.log
            self.log = []

        def reset_workers_flags(self, char):
            for flag in char.flags.keys():
                if flag.startswith("jobs"):
                    char.del_flag(flag)


    class Job(_object):
        """Baseclass for jobs and tasks.
        """
        id = "Undefined"
        desc = "Add Description." # String we can use to describe the Job.
        type = None # job group to use in the report

        # Payout per single client, this is passed to Economy class and modified if needs be.
        per_client_payout = 5

        # Traits/Job-types associated with this job:
        aeq_purpose = "Casual"

        event_type = "jobreport"

        # Each job should have two dicts of stats/skills to evaluate chars ability of performing it:
        base_skills = dict()
        base_stats = dict()
        # Where key: value are stat/skill: weight!

        @classmethod
        def auto_equip(cls, worker):
            """
            Auto-equip a worker for this job.
            """
            if not worker.autoequip:
                return

            purpose = cls.aeq_purpose
            last_known = worker.last_known_aeq_purpose

            if purpose == last_known:
                return

            # Special considerations:
            if purpose == "Fighting":
                if last_known in STATIC_ITEM.FIGHTING_AEQ_PURPOSES:
                    return

            # Otherwise, let us AEQ:
            worker.auto_equip(purpose)

        @staticmethod
        def calculate_disposition_level(worker):
            return 0

        @classmethod
        def settle_workers_disposition(cls, char=None):
            # Formerly check_occupation
            """Settles effects of worker who already agreed to do the job.

            Normaly deals with disposition, joy and vitality (for some reason?)
            """
            return True

        @staticmethod
        def normalize_required_stat(worker, stat, effectiveness, difficulty):
            value = worker.get_stat(stat)
            max_value = worker.get_max_stat(stat, tier=difficulty)
            if max_value == 0:
                raise Exception("Zero Dev #1 (%s)", stat)

            value = min(value, max_value*1.05)
            return value/float(max_value)*effectiveness

        @staticmethod
        def normalize_required_skill(worker, skill, effectiveness, difficulty):
            value = worker.get_skill(skill)
            max_value = worker.get_max_skill(skill, tier=difficulty)
            if max_value == 0:
                raise Exception("Zero Dev #2 (%s)", skill)

            value = min(value, max_value*1.05)
            return value/float(max_value)*effectiveness

        @classmethod
        def effectiveness(cls, worker, difficulty, log, manager_effectiveness=0):
            """We check effectiveness here during jobs from SimPy land.

            difficulty is used to counter worker tier.
            100 is considered a score where worker does the task with acceptable performance.
            min = 0 and max is 200
            """
            # Class traits and Occs (Part 1)
            if cls.want_work(worker):
                bt_bonus = 50
            elif cls.willing_work(worker):
                bt_bonus = 15
            else:
                bt_bonus = 0

            # Tiers:
            diff = worker.tier - difficulty
            tier_bonus = diff*10

            # Class traits and Occs (Part 2)
            if diff < 0: # Tier lower than the Building (difficulty)
                bt_bonus /= 1-diff
            elif diff > 0:
                bt_bonus += tier_bonus*2

            # Skills/Stats:
            total_skills_stats = 0
            skills = cls.base_skills
            for skill, weight in skills.iteritems():
                sp = worker.get_skill(skill)
                sp_required = worker.get_max_skill(skill, tier=difficulty)
                # if not sp_required:
                #     raise Exception("Zero Dev #4 (%s)", skill)
                total_skills_stats += weight * min(float(sp)/sp_required, 1.1)

            stats = cls.base_stats
            for stat, weight in stats.iteritems():
                sp = worker.get_stat(stat)
                sp_required = worker.get_max_stat(stat, tier=difficulty)
                if sp_required == 0:
                    raise Exception("Zero Dev #6 (%s)", stat)
                total_skills_stats += weight * min(float(sp)/sp_required, 1.1)

            total_skills_stats = 50.0 * total_skills_stats / sum(chain(skills.itervalues(), stats.itervalues()))

            # Bonuses:
            traits_bonus = cls.traits_and_effects_effectiveness_mod(worker, log)

            # Manager passive effect:
            if cls.id == "Manager":
                manager_bonus = 15
            else:
                if manager_effectiveness >= 175:
                    manager_bonus = 20
                elif manager_effectiveness >= 130 and dice(manager_effectiveness-100):
                    manager_bonus = 10
                else:
                    manager_bonus = 0

            total = bt_bonus + tier_bonus + total_skills_stats + traits_bonus + manager_bonus

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
                for stat in cls.base_stats:
                    temp[stat] = worker.get_stat(stat)
                devlog.info("Calculating Jobs Relative Ability, Char/Job: {}/{}:".format(worker.name, cls.id))
                devlog.info("Stats: {}:".format(temp))
                args = (bt_bonus, tier_bonus, traits_bonus, total_skills_stats, manager_bonus, disposition_multiplier, total)
                devlog.info("Gen Occ/BT: {}, Tier: {}, Traits: {}, Skills+Stats: {}, Mgr: {}, Disposition Multiplier {} ==>> {}".format(*args))

            return total

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Modifies workers effectiveness depending on traits and effects.

            returns an integer to be added to base calculations!
            """
            return 0

        @staticmethod
        def calc_jp_cost(manager_effectiveness, cost):
            # a good manager can reduce the original cost by 50%. (passive effect)
            if manager_effectiveness > 80:        # original effectiveness is between 0 and 200
                manager_effectiveness *= randint(75, 125)   # a bit of random -> 60(00) <= me <= 250(00)
                manager_effectiveness -= 6000     # 60 * 100                  ->   (00) <= me <= 190(00)
                if manager_effectiveness > 16000: # 160 * 100   me over 160 does not help further
                    manager_effectiveness = 16000           #                 ->   (00) <= me <= 160(00)
                manager_effectiveness /= 32000.0            #                 ->    0.0 <= me <= 0.5
                cost *= 1.0 - manager_effectiveness

            return cost
