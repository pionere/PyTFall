init -5 python:
    class GladiatorTask(Job):
        id = "Gladiator"
        desc = "Fights in the arena for you"
        type = "Combat"

        aeq_purpose = "Fighting"

        @staticmethod
        def want_work(worker):
            return any("Combatant" in t.occupations for t in worker.basetraits)

        @staticmethod
        def willing_work(worker):
            return any("Combatant" in t.occupations for t in worker.basetraits)

        """
        @classmethod
        def settle_workers_disposition(cls, workers, log):
            log(set_font_color("Your team is ready for action!", "cadetblue"))

            for worker in workers:
                if cls.want_work(worker):
                    continue
                sub = check_submissivity(worker)
                if sub < 0:
                    log("%s doesn't enjoy going on exploration, but %s will get the job done." % (worker.name, worker.p))
                    sub = 15
                elif sub == 0:
                    log("%s would prefer to do something else." % worker.nickname)
                    sub = 25
                else:
                    log("%s makes it clear that %s wants to do something else." % (worker.name, worker.p))
                    sub = 35
                if dice(sub):
                    worker.logws('character', 1)
                worker.logws("joy", -randint(3, 5))
                worker.logws("disposition", -randint(5, 10))
                worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
        """