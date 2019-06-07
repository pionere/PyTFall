init -5 python:
    class Clinic(OnDemandBusiness):
        def __init__(self):
            super(Clinic, self).__init__()
            self.jobs = [NurseJob]
            self.patients = list()     # the list of patients currently at the clinic
            self.reserved_capacity = 0 # the number of patients (+ injured hero.chars ?)

        def can_close(self):
            return self.reserved_capacity == 0

        def can_reduce_capacity(self):
            if self.capacity <= self.reserved_capacity:
                return False
            return super(Clinic, self).can_reduce_capacity()

        def log(self, text, time=None):
            # Logs the text for next day event... # FIXME similar as log of Building
            # try to create a timestamp between 9:00 and 19:00 assuming env.now is between 0 and 100 MAX_DU
            text = "%02d:%02d - %s" % (9+time/10,(time*6)%60, text)
            self.nd_log.append(text)

        def business_control(self):
            """We decided for this to work similarly (or the same as cleaning routines)

            For now, goal is to get this to work reliably.
            """
            building = self.building

            power_flag_name = "dnd_nursing_power"
            job = NurseJob

            # Pure workers, container is kept around for checking during all_on_deck scenarios
            nurses = set()
            log = NDEvent(job=job, loc=building, team=nurses, business=self)
            self.nd_log = log

            temp = "Report of %s in %s!\n" % (self.name, building.name)
            log.append(temp)

            # workers on active duty
            pre_log = []
            workers = self.get_strict_workers(job, power_flag_name, log=pre_log)

            wlen = len(workers)
            temp = "%s %s tended to the patients." % (set_font_color(wlen, "lightgreen"), plural("Worker", wlen))
            log.append(temp)

            # add log from preparation
            for l in pre_log:
                log.append(l)

            curr_patients = self.patients

            # release healed patients
            today = day
            difficulty = building.tier
            for p in curr_patients[:]:
                if p.release_day == today:
                    curr_patients.remove(p)
                    self.reserved_capacity -= 1

                    # TODO manager effectiveness?
                    earned = pytfall.economy.get_clients_pay(job, difficulty)
                    earned *= p.num_weeks * 7
                    temp = ("%s is healed now, and %s is leaving your clinic.",
                            "The recovery of %s is complete. Now %s is ready to leave.",
                            "The prescribed treatment for %s is ended. Finally %s can go home.")
                    temp = choice(temp) % (p.name, p.p)
                    log.append(temp)
                    log.earned += earned

            # upset patients leave
            dirt = building.get_dirt_percentage()
            if dirt > 70 and curr_patients:
                p = choice(curr_patients)
                curr_patients.remove(p)
                self.reserved_capacity -= 1
                temp = "%s can't stay any longer in this dirt. %s is leaving prematurely (and without paying a dime)" % (p.name, p.pC)
                log.append(temp)

            # add possible new patients
            new_patients = self.capacity * building.get_fame_percentage() * building.get_rep_percentage() * (100 - building.get_dirt_percentage())
            new_patients /= 1000000.0
            new_patients = round_int(new_patients)
            
            free_capacity = self.capacity - self.reserved_capacity

            while 1:
                now = self.env.now
                simpy_debug("Entering Clinic.business_control at %s", now)

                if DSNBR:
                    temp = "DEBUG: Number of patients: {}, Number of nurses: {}!".format(len(curr_patients), len(workers))
                    self.log(set_font_color(temp, "red"), now)

                # Add new patient:
                if new_patients > 0 and dice(20):
                    new_patients -= 1
                    patient = building.create_customer()
                    temp = "A new patient arrived"
                    if free_capacity <= 0:
                        temp += ", but there was no empty bed available. %s left the building." % patient.pC
                    else:
                        free_capacity -= 1
                        self.reserved_capacity += 1
                        curr_patients.append(patient)
                        num_weeks = randint(1, 4)
                        patient.num_weeks = num_weeks
                        patient.release_day = today + num_weeks * 7
                        temp += ". %s is going to stay for %d %s." % (patient.pC, num_weeks, plural("week", num_weeks))
                    self.log(temp, now)

                # Actually handle the patients:
                num_patients = len(curr_patients)
                if num_patients != 0:
                    shuffle(workers)
                    to_tend = num_patients
                    nurses_done = []
                    for w in workers:
                        value = w.flag(power_flag_name)

                        to_tend += value
                        nurses.add(w)

                        # TODO tips?

                        # Adjust PP
                        w.up_counter("jp_nurse", 10)
                        w.PP -= 10
                        if w.PP <= 0:
                            nurses_done.append(w)
                        if to_tend <= 0:
                            break
                    else:
                        # not enough nurses: -> patients starts to leave
                        if dice(to_tend*10):
                            p = choice(curr_patients)
                            curr_patients.remove(p)
                            self.reserved_capacity -= 1
                            temp = "%s is leaving because %s does not feel like %s is being taken care of. And refuses to pay for the non-service." % (p.name, p.p, p.p)
                        else:
                            temp = "The unattended %s became slightly unruly, but this time the situation did not escalate." % plural("patient", num_patients)
                        self.log(temp, now)

                    # Remove the workers after running out of action points:
                    for w in nurses_done:
                        temp = "%s is done nursing for the day!" % w.nickname
                        temp = set_font_color(temp, "cadetblue")
                        self.log(temp, now)
                        workers.remove(w)

                if now >= 100: # MAX_DU
                    break

                simpy_debug("Exiting Clinic.business_control at %s", now)
                yield self.env.timeout(5)

            # Create actual report:
            if DSNBR:
                self.log("Writing ND-Report at %s", now)

            difficulty = building.tier
            for w in nurses:
                ap_used = w.get_flag("jp_nurse", 0)/100.0
                log.logws("vitality", round_int(ap_used*-2), char=w)
                log.logws("service", randint(0, 1), char=w)
                log.logws("refinement", randint(0, 1), char=w)
                if dice(30):
                    log.logws("intelligence", 1, char=w)
                if dice(20):
                    log.logws("magic", 1, char=w)
                if dice(10):
                    log.logws("agility", 1, char=w)
                log.logws("exp", exp_reward(w, difficulty, exp_mod=ap_used), char=w)
                w.del_flag("jp_nurse")

            log.img = nd_report_image(building.img, nurses, "healing", exclude=["sex"])

            log.after_job()
            NextDayEvents.append(log)
            del self.nd_log
