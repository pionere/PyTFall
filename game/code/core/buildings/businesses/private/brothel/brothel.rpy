init -5 python:
    class BrothelBlock(PrivateBusiness):
        def __init__(self):
            super(BrothelBlock, self).__init__()

            self.jobs = [WhoreJob]

        def client_control(self, client):
            """Handles the client after a room is reserved...
            """
            simpy_debug("Entering BrothelBlock.client_control iteration at %s", self.env.now)

            client_name = set_font_color(client.name, "beige")

            # find a worker
            job = WhoreJob
            result = 0
            while 1:
                worker = self.get_workers(job, amount=1, client=client)
                if not worker:
                    yield self.env.timeout(1)
                    client.up_counter("business_waited")
                    result += 1
                    if result >= 5:
                        self.building.modfame(-randint(1, 2))

                        temp = "%s lost %s patience to wait for someone to satisfy %s needs, so %s leaves the %s cursing..." % (client_name, client.pp, client.pp, client.p, self.name)
                        self.log(temp, True)
                        return
                    if self.env.now + self.time > 100: # MAX_DU
                        temp = "There is not much for %s to do before closing, so %s leaves the %s." % (client_name, client.p, self.name)
                        self.log(temp, True)
                        return
                    continue

                # We presently work just with the one char only, so:
                worker = worker.pop()
                self.building.available_workers.remove(worker)
                break

            worker_name = set_font_color(worker.name, "pink")

            # All is well and the client enters:
            client.up_counter("business_used", 2)

            result = random.random()
            if result < .5:
                temp = "%s and %s enter the room." 
            else:
                temp = "%s and %s find a very private room for themselves." 
            if result < .25 or result >= .75:
                temp = temp % (client_name, worker_name)
            else:
                temp = temp % (worker_name, client_name)
            self.log(temp, True)

            simpy_debug("Exiting BrothelBlock.client_control iteration at %s", self.env.now)
            # This line will make sure code halts here until run_job ran it's course...
            yield self.env.timeout(self.time)

            simpy_debug("Entering BrothelBlock.client_control after-yield at %s (W:%s/C:%s)", self.env.now, worker.name, client.name)

            result = self.run_job(job, client, worker)

            if result >= 150:
                line = "The service was excellent!"
            elif result >= 100:
                line = "The service was good!"
            elif result >= 50:
                line = "The service was 'meh'."
            else:
                line = "The service was shit."
            temp = "%s 'did' %s... %s" % (worker_name, client_name, line)
            self.log(temp, True)
            temp = "%s leaves the %s." % (client_name, self.name)
            self.log(temp, False)

            simpy_debug("Exiting BrothelBlock.client_control after-yield at %s (W:%s/C:%s)", self.env.now, worker.name, client.name)

        def run_job(self, job, client, worker):
            """Handles the job and job report.
            """
            # Execute the job/log results/handle finances and etc.:
            building = self.building
            log = NDEvent(job=job, char=worker, loc=building, business=self)

            job.settle_workers_disposition(worker, log)

            pp_use = job.calc_jp_cost(manager_effectiveness=building.manager_effectiveness, cost=100)
            worker.PP -= pp_use

            difficulty = building.tier
            effectiveness = job.effectiveness(worker, difficulty, log, building.manager_effectiveness)

            # Upgrade mods:
            effectiveness += self.job_effectiveness_mod

            effectiveness = job.log_work(worker, client, pp_use/100.0, effectiveness, log) # PP_PER_AP

            earned = payout(job, effectiveness, difficulty,
                            building, self, worker, client, log)

            # Log everything:
            log.after_job()
            NextDayEvents.append(log)

            # We return the char to the nd list:
            building.available_workers.insert(0, worker)
            return effectiveness
