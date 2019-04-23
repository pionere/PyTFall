init -5 python:
    class BarBusiness(PublicBusiness):
        # For now, before we'll have to split the method.
        intro_string = "{color=pink}%s{/color} comes out to tend the Bar!"

        def __init__(self):
            super(BarBusiness, self).__init__()

            self.jobs = [simple_jobs["Bartending"]]
