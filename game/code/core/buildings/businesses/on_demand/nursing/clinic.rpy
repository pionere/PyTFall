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

        def log(self, text, time):
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
            workers = list(self.get_strict_workers(job, power_flag_name, log=pre_log))

            wlen = len(workers)
            temp = "%s %s are assigned to work as a nurse." % (set_font_color(wlen, "lightgreen"), plural("Employee", wlen))
            log.append(temp)

            # add log from preparation
            for l in pre_log:
                log.append(l)

            if wlen > 1:
                log.append(set_font_color("Your nurses are starting their day!", "cadetblue"))
            elif wlen == 1:
                log.append(set_font_color("You nurse is starting %s day!" % workers[0].pd, "cadetblue"))

            curr_patients = self.patients

            # release healed patients
            today = day
            difficulty = building.tier
            released_patients = [p for p in curr_patients if p.release_day == today] 
            for p in released_patients:
                curr_patients.remove(p)
                self.reserved_capacity -= 1

                # TODO manager effectiveness?
                earned = pytfall.economy.get_clients_pay(job, difficulty)
                earned *= p.num_weeks
                temp = ("%s is healed now, and %s is leaving your clinic.",
                        "The recovery of %s is complete. Now %s is ready to leave.",
                        "The prescribed treatment for %s is ended. Finally %s can go home.")
                temp = choice(temp) % (p.name, p.p)
                log.append(temp)
                log.earned += earned

            temp = self.reserved_capacity
            if temp > 1:
                log.append("For the day %d beds are occupied." % temp)
            elif temp == 1:
                log.append("For the day one bed is occupied.")
            else:
                if self.capacity == 1:
                    log.append("The room is empty.")
                else:
                    log.append("The rooms are empty.")

            if DSNBR:
                for p in curr_patients:
                    temp = "Patient {} is staying till {}. Today is {}!".format(p.name, p.release_day, today)
                    log.append(temp)

            # add possible new patients (about 1 new patient every 15 days if everyting is perfect)
            new_patients = self.capacity
            new_patients *= building.get_fame_percentage() * building.get_rep_percentage()
            new_patients /= 3000000.0 # quality (0-1) / (20 * 15)

            if not self.active:
                new_patients = 0
                temp = "New patients are not admitted at the moment!"
                log.append(temp)

            while 1:
                now = self.env.now
                simpy_debug("Entering Clinic.business_control at %s", now)

                if DSNBR:
                    temp = "DEBUG: Number of patients: {}, Number of nurses: {}!".format(len(curr_patients), len(workers))
                    self.log(set_font_color(temp, "red"), now)

                # upset patients leave
                dirt = building.get_dirt_percentage()
                if dirt > 70 and curr_patients:
                    p = choice(curr_patients)
                    curr_patients.remove(p)
                    self.reserved_capacity -= 1
                    temp = "%s can't stay any longer in this dirt. %s is leaving prematurely (and without paying a dime)!" % (p.name, p.pC)
                    self.log(temp, now)

                # Add new patient:
                if dice(new_patients * (125 - max(25, dirt))):
                    p = building.create_customer()
                    temp = "A new patient arrived"
                    if self.capacity <= self.reserved_capacity:
                        temp += ", but there was no empty bed available. %s left the building." % p.pC
                    else:
                        curr_patients.append(p)
                        self.reserved_capacity += 1
                        num_weeks = randint(1, 4)
                        p.num_weeks = num_weeks
                        p.release_day = today + num_weeks * 7
                        temp += ". %s is going to stay for %d %s." % (p.pC, num_weeks, plural("week", num_weeks))
                    self.log(temp, now)

                # Actually handle the patients:
                to_tend = len(curr_patients)
                if to_tend != 0:
                    # add dirt and threat
                    dirt = random.random() * 5 * sum((p.dirtmod for p in curr_patients))
                    building.moddirt(dirt)
                    threat = random.random() * .25 * sum((p.threatmod for p in curr_patients))
                    if building.has_garden:
                        threat /= 1.5
                    building.modthreat(threat)

                    # tend to the patients
                    shuffle(workers)
                    nurses_done = []
                    curr_nurses = []
                    for w in workers:
                        value = w.flag(power_flag_name)

                        to_tend += value
                        curr_nurses.append(w)

                        # TODO tips?

                        # Adjust PP
                        w.up_counter("jp_nurse", 20)
                        w.PP -= 20
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
                            temp = "The unattended %s became slightly unruly, but this time the situation did not escalate." % plural("patient", len(curr_patients))
                        self.log(temp, now)

                    # report the activity
                    temp = len(curr_nurses)
                    if temp > 1:
                        temp = "%s tended to the patients." % ", ".join([w.name for w in curr_nurses])
                        self.log(temp, now)
                    elif temp == 1:
                        temp = "%s tended to the patients." % curr_nurses[0].name
                        self.log(temp, now)

                    # collect nurses for the summary
                    nurses.update(curr_nurses)

                    # Remove the workers after running out of action points:
                    for w in nurses_done:
                        temp = "%s is done nursing for the day!" % w.nickname
                        self.log(set_font_color(temp, "cadetblue"), now)
                        workers.remove(w)

                if now >= 100: # MAX_DU
                    break

                simpy_debug("Exiting Clinic.business_control at %s", now)
                yield self.env.timeout(5)

            # Create the report:
            if DSNBR:
                self.log("Writing ND-Report at %s", now)

            difficulty = building.tier
            for w in nurses:
                ap_used = w.get_flag("jp_nurse", 0)/100.0
                log.logws("vitality", round_int(ap_used*-5), char=w)
                log.logws("service", randfloat(ap_used), char=w)
                log.logws("refinement", randfloat(ap_used), char=w)
                log.logws("magic", randfloat(ap_used), char=w)
                log.logws("intelligence", randfloat(ap_used*2), char=w)
                log.logws("agility", randfloat(ap_used/2), char=w)
                log.logws("exp", exp_reward(w, difficulty, exp_mod=ap_used), char=w)
                w.del_flag("jp_nurse")

            log.img = nd_report_image(building.img, nurses, "healing", exclude=["nude", "sex"])

            log.after_job()
            NextDayEvents.append(log)
            del self.nd_log

        inactive_process = business_control # clinic is always active, it just does not accept new patients if it is 'inactive'
