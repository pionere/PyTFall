init -5 python:
    class StripClub(PublicBusiness):
        def __init__(self):
            super(StripClub, self).__init__()

            self.jobs = [simple_jobs["Striptease Job"]]
            # For now, before we'll have to split the method.
            self.intro_string = "{color=[pink]}%s{/color} comes out to do striptease!"
            self.log_intro_string = "{color=[pink]}%s{/color} is performing Striptease!"
            # Looks weird but until we have a better way to debug SimPy :(
            self.job_method = "work_strip_club"
