init -6 python:
    # Provides living space, not sure if this or the building should be bound as home locations!
    class SlaveQuarters(Business):
        def __init__(self):
            super(SlaveQuarters, self).__init__()
            self.habitable = True
