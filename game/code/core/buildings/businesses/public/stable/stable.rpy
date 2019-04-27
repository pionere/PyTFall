init -5 python:
    class StableBusiness(PublicBusiness):
        # For now, before we'll have to split the method.
        intro_string = "{color=pink}%s{/color} comes out to work in the Stable!"

        def __init__(self):
            super(StableBusiness, self).__init__()

            self.jobs = [WranglerJob]
            self.time = 30
            self.reserved_capacity = 0

        def pre_nd(self):
            super(StableBusiness, self).pre_nd()

            # reserve the capacity used by the ExplorationGuild
            for i in xrange(self.reserved_capacity):
                self.res.request()
            #self.res._capacity -= self.reserved_capacity

        def post_nd(self):
            # free the capacity used by the ExplorationGuild
            #for i in xrange(self.reserved_capacity):
            #    self.res.release()
            #self.res._capacity += self.reserved_capacity

            super(StableBusiness, self).post_nd()
