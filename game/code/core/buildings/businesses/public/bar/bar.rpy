init -5 python:
    class BarBusiness(PublicBusiness):
        def __init__(self):
            super(BarBusiness, self).__init__()

            self.jobs = [simple_jobs["Bartending"]]

            # For now, before we'll have to split the method.
            self.intro_string = "{color=[pink]}%s{/color} comes out to tend the Bar!"
            self.log_intro_string = "{color=[pink]}%s{/color} is working the bar!"
            self.job_method = "work_bar"
