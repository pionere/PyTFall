init -5 python:
    class Cleaners(OnDemandBusiness):
        def __init__(self):
            super(Cleaners, self).__init__()

            self.jobs = [CleaningJob]

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
            job = CleaningJob

            # Pure cleaners, container is kept around for checking during all_on_deck scenarios
            log = []
            strict_workers = self.get_strict_workers(job, power_flag_name, log=log)
            workers = strict_workers.copy() # cleaners on active duty

            while 1:
                now = self.env.now
                simpy_debug("Entering Cleaners.business_control iteration at %s", now)

                if DSNBR and not now % 5:
                    temp = "{color=red}" + "DEBUG: {0:.2f} DIRT IN THE BUILDING!".format(building.dirt)
                    self.log(temp, True)

                dirt = building.dirt
                if dirt >= 200:
                    wlen_color = "green"
                    if dirt >= 500:
                        if dirt >= 900:
                            wlen_color = "red"

                        if not using_all_workers:
                            using_all_workers = True
                            workers = self.all_on_deck(workers, job, power_flag_name, log=log)

                    if not make_nd_report_at:
                        wlen = len(workers)
                        make_nd_report_at = min(now+25, 105) # MAX_DU
                        if wlen:
                            temp = "%s %s started to clean the building!" % (set_font_color(wlen, wlen_color), plural("Worker", wlen))
                            self.log(temp, True)

                # Actually handle dirt cleaning:
                if make_nd_report_at and dirt > 0:
                    for w in workers.copy():
                        value = w.flag(power_flag_name)
                        building.moddirt(value)

                        dirt_cleaned += value
                        cleaners.add(w)

                        w.PP -= 10
                        w.up_counter("jp_clean", 10)
                        if w.PP <= 0:
                            temp = "%s is done cleaning for the day!" % w.nickname
                            temp = set_font_color(temp, "cadetblue")
                            self.log(temp, True)
                            workers.remove(w)

                # Create actual report:
                # No point in a report if no workers worked the cleaning.
                if now >= make_nd_report_at and cleaners:
                    if DSNBR:
                        self.log("DEBUG! WRITING CLEANING REPORT!", True)

                    self.write_nd_report(strict_workers, cleaners, log, dirt_cleaned)
                    if now >= 105: # MAX_DU
                        self.env.exit()
                    make_nd_report_at = 0
                    dirt_cleaned = 0
                    cleaners = set()
                    log = list()

                # Release none-pure cleaners:
                if building.dirt < 500 and using_all_workers:
                    using_all_workers = False
                    extra = workers - strict_workers
                    if extra:
                        workers -= extra
                        building.available_workers[0:0] = list(extra)

                simpy_debug("Exiting Cleaners.business_control iteration at %s", now)
                yield self.env.timeout(1)

        def write_nd_report(self, strict_workers, all_workers, pre_log, dirt_cleaned):
            simpy_debug("Entering Cleaners.write_nd_report at %s", self.env.now)

            dirt_cleaned = int(dirt_cleaned)

            job, loc = CleaningJob, self.building
            log = NDEvent(type="jobreport", job=job, loc=loc, locmod={'dirt':dirt_cleaned}, team=all_workers, business=self)

            temp = "%s Cleaning Report!\n" % loc.name
            log.append(temp)

            simpy_debug("Cleaners.write_nd_report marker 1")

            wlen = len(all_workers)
            temp = "%s %s cleaned the building today." % (set_font_color(wlen, "tomato"), plural("Worker", wlen))
            log.append(temp)

            # add log from preparation
            for l in pre_log:
                log.append(l)

            log.img = nd_report_image(loc.img, all_workers, "maid", "cleaning", exclude=["sex"], type="any")

            simpy_debug("Cleaners.write_nd_report marker 2")

            workers = all_workers
            extra_workers = workers - strict_workers
            xlen = len(extra_workers)
            if xlen != 0:
                temp = "Dirt overwhelmed your building so extra staff was called to clean it! "
                if xlen > 1:
                    temp += "%s were pulled off their duties to help out..." % (", ".join([w.nickname for w in extra_workers]))
                else:
                    w = next(iter(extra_workers))
                    temp += "%s was pulled off %s duty to help out..." % (w.nickname, w.pp)
                log.append(temp)

                workers -= extra_workers

            xlen = wlen - xlen
            if xlen != 0:
                if xlen > 1:
                    temp = "%s worked hard keeping your business clean as it is their direct job!" % (", ".join([w.nickname for w in workers]))
                else:
                    w = next(iter(workers))
                    temp = "%s worked hard keeping your business clean as it is %s direct job!" % (w.nickname, w.pp)
                log.append(temp)

            simpy_debug("Cleaners.write_nd_report marker 3")

            temp = "\nA total of %s dirt was cleaned." % set_font_color(-dirt_cleaned, "tomato")
            log.append(temp)

            difficulty = loc.tier
            for w in workers:
                ap_used = w.get_flag("jp_clean", 0)/100.0
                log.logws("vitality", round_int(ap_used*-5), char=w)
                log.logws("cleaning", randint(1, 3), char=w)
                if dice(30):
                    log.logws("agility", 1, char=w)
                if dice(10):
                    log.logws("constitution", 1, char=w)
                log.logws("exp", exp_reward(w, difficulty, exp_mod=ap_used), char=w)
                w.del_flag("jp_clean")
            for w in extra_workers:
                ap_used = w.get_flag("jp_clean", 0)/100.0
                log.logws("vitality", round_int(ap_used*-6), char=w)
                log.logws("cleaning", 1, char=w)
                if dice(10):
                    log.logws("agility", 1, char=w)
                if dice(10):
                    log.logws("constitution", 1, char=w)
                log.logws("exp", exp_reward(w, difficulty, exp_mod=ap_used*.5), char=w)
                w.del_flag("jp_clean")

            simpy_debug("Cleaners.write_nd_report marker 4")

            log.after_job()
            NextDayEvents.append(log)

            simpy_debug("Exiting Cleaners.write_nd_report at %s", self.env.now)
