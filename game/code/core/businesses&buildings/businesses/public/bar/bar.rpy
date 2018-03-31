init -5 python:
    class BarBusiness(PublicBusiness):
        COMPATIBILITY = []
        SORTING_ORDER = 4
        MATERIALS = {"Wood": 50, "Bricks": 30, "Glass": 5}
        NAME = "Bar"
        IMG = "content/buildings/upgrades/bar.jpg"
        DESC = "Serve drinks and snacks to your customers!"
        COST = 500
        IN_SLOTS = 3
        def __init__(self, **kwargs):
            super(BarBusiness, self).__init__(**kwargs)

            self.jobs = set([simple_jobs["Bartending"]])

            # For now, before we'll have to split the method.
            self.intro_string = "{} comes out to tend the Bar in {}!"
            self.log_intro_string = "{} is working the bar!"
            self.job_method = "work_bar"
