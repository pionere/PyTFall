init -5 python:
    class Cleaners(OnDemandBusiness):
        def __init__(self):
            super(Cleaners, self).__init__()

            self.jobs = [simple_jobs["Cleaning"]]

        def business_control(self):
            """This checks if there are idle workers willing/ready to clean in the building.
            Cleaning is always active, checked on every tick.
            Cleaners are on call at all times.
            Whenever dirt reaches 200, they start cleaning till it’s 0 or are on standby on idle otherwise.
            If dirt reaches 600 (they cannot coop or there are simply no pure cleaners),
            all “Service Types” that are free help out and they are released when dirt reaches 50 or below.
            If dirt reaches 900, we check for auto-cleaning and do the “magical” thing if player has
            the money and is willing to pay (there is a checkbox for that already).
            If there is no auto-cleaning, we call all workers in the building to clean…
            unless they just refuse that on some principal (trait checks)...
            """
            building = self.building
            make_nd_report_at = 0 # We build a report every 25 ticks but only if this is True!
            dirt_cleaned = 0 # We only do this for the ND report!
            cleaners = set() # Everyone that cleaned for the report.

            using_all_workers = False

            power_flag_name = "dnd_cleaning_power"
            job = simple_jobs["Cleaning"]

            # Pure cleaners, container is kept around for checking during all_on_deck scenarios
            strict_workers = self.get_strict_workers(job, power_flag_name)
            workers = strict_workers.copy() # cleaners on active duty

            while 1:
                simpy_debug("Entering Cleaners.business_control iteration at %s", self.env.now)

                if DSNBR and not self.env.now % 5:
                    temp = "{color=[red]}" + "DEBUG: {0:.2f} DIRT IN THE BUILDING!".format(building.dirt)
                    self.log(temp, True)

                dirt = building.dirt
                if dirt >= 200:
                    wlen_color = "green"
                    if dirt >= 500:
                        if dirt >= 900:
                            wlen_color = "red"

                        if not using_all_workers:
                            using_all_workers = True
                            workers = self.all_on_deck(workers, job, power_flag_name)

                    if not make_nd_report_at:
                        wlen = len(workers)
                        make_nd_report_at = min(self.env.now+25, 105) # FIXME MAX_DU
                        if wlen:
                            temp = "%s Workers have started to clean %s!" % (set_font_color(wlen, wlen_color), building.name)
                            self.log(temp, True)

                # Actually handle dirt cleaning:
                if make_nd_report_at and dirt > 0:
                    for w in workers.copy():
                        value = int(w.flag(power_flag_name))
                        building.moddirt(value)

                        dirt_cleaned += value
                        cleaners.add(w)

                        w.jobpoints -= 5
                        w.up_counter("jobs_points_spent", 5)
                        if w.jobpoints <= 0:
                            temp = "%s is done cleaning for the day!" % w.nickname
                            temp = set_font_color(temp, "cadetblue")
                            self.log(temp, True)
                            workers.remove(w)

                # Create actual report:
                c0 = self.env.now >= make_nd_report_at
                c1 = cleaners # No point in a report if no workers worked the cleaning.
                if c0 and c1:
                    if DSNBR:
                        temp = "{}: DEBUG! WRITING CLEANING REPORT! ({}, {})".format(self.env.now, c0, c1)
                        self.log(temp)

                    self.write_nd_report(strict_workers, cleaners, -dirt_cleaned)
                    make_nd_report_at = 0
                    dirt_cleaned = 0
                    cleaners = set()

                # Release none-pure cleaners:
                if building.dirt < 500 and using_all_workers:
                    using_all_workers = False
                    extra = workers - strict_workers
                    if extra:
                        workers -= extra
                        building.available_workers[0:0] = list(extra)

                simpy_debug("Exiting Cleaners.business_control iteration at %s", self.env.now)
                yield self.env.timeout(1)

        def write_nd_report(self, strict_workers, all_workers, dirt_cleaned):
            simpy_debug("Entering Cleaners.write_nd_report at %s", self.env.now)

            job, loc = self.jobs[0], self.building
            log = NDEvent(job=job, loc=loc, locmod={'dirt':dirt_cleaned}, team=all_workers, business=self)

            extra_workers = all_workers - strict_workers

            temp = "{} Cleaning Report!\n".format(loc.name)
            log.append(temp)

            simpy_debug("Cleaners.write_nd_report marker 1")

            wlen = len(all_workers)
            temp = "{} Workers cleaned the building today.".format(set_font_color(wlen, "red"))
            log.append(temp)

            log.img = Fixed(xysize=ND_IMAGE_SIZE)
            log.img.add(Transform(loc.img, size=ND_IMAGE_SIZE))
            vp = vp_or_fixed(all_workers, ["maid", "cleaning"],
                             {"exclude": ["sex"], "resize": (150, 150),
                             "type": "any"})
            log.img.add(Transform(vp, align=(.5, .9)))

            log.team = all_workers

            simpy_debug("Cleaners.write_nd_report marker 2")

            workers = all_workers
            if extra_workers:
                temp = "Dirt overwhelmed your building so extra staff was called to clean it! "
                if len(extra_workers) > 1:
                    temp += "%s were pulled off their duties to help out..." % (", ".join([w.nickname for w in extra_workers]))
                else:
                    temp += "%s was pulled off %s duty to help out..." % (w.nickname, w.pp)
                log.append(temp)

                workers -= extra_workers

            temp = "{} worked hard keeping your business clean as it is their direct job!".format(", ".join([w.nickname for w in workers]))
            log.append(temp)

            simpy_debug("Cleaners.write_nd_report marker 3")

            temp = "\nA total of {} dirt was cleaned.".format(set_font_color(dirt_cleaned, "red"))
            log.append(temp)

            # exp = dirt_cleaned/wlen -> wlen MUST NOT be 0?
            for w in workers:
                ap_used = w.get_flag("jobs_points_spent", 0)/100.0
                log.logws("vitality", round_int(ap_used*-5), char=w)
                log.logws("cleaning", randint(1, 3), char=w)
                if dice(30):
                    log.logws("agility", 1, char=w)
                if dice(10):
                    log.logws("constitution", 1, char=w)
                log.logws("exp", exp_reward(w, loc.tier, ap_used=ap_used), char=w) # This is imperfect...
                w.del_flag("jobs_points_spent")
            for w in extra_workers:
                ap_used = w.get_flag("jobs_points_spent", 0)/100.0
                log.logws("vitality", round_int(ap_used*-6), char=w)
                log.logws("cleaning", 1, char=w)
                if dice(10):
                    log.logws("agility", 1, char=w)
                if dice(10):
                    log.logws("constitution", 1, char=w)
                # This is imperfect. We need to track jobpoints spent to get this right...
                log.logws("exp", exp_reward(w, loc.tier, ap_used=ap_used, final_mod=.5), char=w)
                w.del_flag("jobs_points_spent")

            log.type = "jobreport" # Come up with a new type for team reports?

            simpy_debug("Cleaners.write_nd_report marker 4")

            log.after_job()
            NextDayEvents.append(log)

            simpy_debug("Exiting Cleaners.write_nd_report at %s", self.env.now)
