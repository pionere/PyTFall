init -6 python:
    # Provides living space, not sure if this or the building should be bound as home locations!
    class SlaveQuarters(Business):
        def __init__(self):
            super(SlaveQuarters, self).__init__()
            self.habitable = True

        @property
        def daily_modifier(self):
            value = self._daily_modifier
            for u in self.upgrades:
                value *= getattr(u, "daily_modifier_mod", 1)
            return value
