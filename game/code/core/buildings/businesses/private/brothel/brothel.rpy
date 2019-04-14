init -5 python:
    class BrothelBlock(PrivateBusiness):
        def __init__(self):
            super(BrothelBlock, self).__init__()

            self.jobs = [simple_jobs["Whore Job"]]

        def request_resource(self, client, worker):
            """Requests a room from Sim'Py, under the current code,
               this will not be called if there are no rooms available...
            """
            simpy_debug("Entering BrothelBlock.request_resource after-yield at %s (W:%s/C:%s)", self.env.now, worker.name, client.name)

            # All is well and the client enters:
            temp0 = "{} and {} enter the room.".format(
                set_font_color(client.name, "beige"),
                set_font_color(worker.name, "pink"))
            temp1 = "{} and {} find a very private room for themselves.".format(
                set_font_color(worker.name, "pink"),
                set_font_color(client.name, "beige"))
            self.log(choice([temp0, temp1]), True)

            # This line will make sure code halts here until run_job ran it's course...
            yield self.env.timeout(self.time)

            result = self.run_job(client, worker)

            if result >= 150:
                line = "The service was excellent!"
            elif result >= 100:
                line = "The service was good!"
            elif result >= 50:
                line = "The service was 'meh'."
            else:
                line = "The service was shit."
            temp = "{} 'did' {}... {}".format(
                        set_font_color(worker.name, "pink"),
                        set_font_color(client.name, "beige"),
                        line)
            self.log(temp, True)
            temp = "{} leaves the {}.".format(set_font_color(client.name, "beige"), self.name)
            self.log(temp, False)

            simpy_debug("Exiting BrothelBlock.request_resource after-yield at %s (W:%s/C:%s)", self.env.now, worker.name, client.name)

        def run_job(self, client, worker):
            """Handles the job and job report.
            """
            simpy_debug("Entering BrothelBlock.run_job after-yield at %s (W:%s/C:%s)", self.env.now, worker.name, client.name)

            # Execute the job/log results/handle finances and etc.:
            job = simple_jobs["Whore Job"]
            building = self.building
            log = NDEvent(job=job, char=worker, loc=building, business=self)

            job.settle_workers_disposition(worker, log)

            difficulty = building.tier
            effectiveness = job.effectiveness(worker, difficulty, log, building.manager_effectiveness)

            # Upgrade mods:
            effectiveness += self.job_effectiveness_mod

            effectiveness = job.work_brothel(worker=worker, client=client, building=building,
                                             log=log, effectiveness=effectiveness)

            worker.PP -= job.calc_jp_cost(manager_effectiveness=building.manager_effectiveness, cost=100)

            earned = payout(job, effectiveness, difficulty,
                            building, self, worker, client, log)

            # Dirt:
            building.moddirt(randint(3, 6))

            # Log everything:
            log.after_job()
            NextDayEvents.append(log)

            # We return the char to the nd list:
            building.available_workers.insert(0, worker)

            simpy_debug("Exiting BrothelBlock.run_job after-yield at %s (W:%s/C:%s)", self.env.now, worker.name, client.name)

            return effectiveness
