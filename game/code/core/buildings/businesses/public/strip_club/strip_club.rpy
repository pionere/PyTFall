init -5 python:
    class StripClub(PublicBusiness):
        # For now, before we'll have to split the method.
        intro_string = "{color=pink}%s{/color} comes out to do striptease!"
        # Looks weird but until we have a better way to debug SimPy :(
        job_method = "work_strip_club"

        def __init__(self):
            super(StripClub, self).__init__()

            self.jobs = [simple_jobs["Striptease Job"]]
