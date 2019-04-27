init -5 python:
    class StripClub(PublicBusiness):
        # For now, before we'll have to split the method.
        intro_string = "{color=pink}%s{/color} comes out to do striptease!"

        def __init__(self):
            super(StripClub, self).__init__()

            self.jobs = [StripJob]
