init -5 python:
    class BarBusiness(PublicBusiness):
        # For now, before we'll have to split the method.
        intro_string = "{color=pink}%s{/color} comes out to tend the Bar!"
        log_intro_string = "{color=pink}%s{/color} is working the bar!"
        job_method = "work_bar"

        def __init__(self):
            super(BarBusiness, self).__init__()

            self.jobs = [simple_jobs["Bartending"]]
