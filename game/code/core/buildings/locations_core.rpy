init python:
    """
    These are used to track current location of any actor and some other object in the game.
    Assumption we make here is that no actor can be at two places at once.

    Above is unclear... idea is to have home location and work location so we have knowledge about
    where characters live and modifiers for next_day restoration calculations.
    Work is where they "work", all chars must have home location of some sort, even if it's afterlife
    or streets :) Work can be omitted, we don't have a dummy location for that atm so None can be used.

    change location functions just change the "current" location of the character.
    More often that not, it doesn't matter much and is mostly there for use in future codebase.
    """

init -20 python:
    # Core Logic:
    def set_location(actor, loc):
        """This plainly forces a location on an actor.
        """
        actor.location = loc
        # if isinstance(loc, Location):
        #     loc.add(actor)


    class Location(_object):
        """
        Usually a place or a building.
        This simply holds references to actors that are present @ the location.
        If a location is not a member of this class, it is desirable for it to have a similar setup or to be added to change_location() function manually.
        """
        def __init__(self, id=None):
            if id is None:
                self.id = self.__class__
            else:
                self.id = id
            # self.actors = set()

        def __str__(self):
            if hasattr(self, "name"):
                return str(self.name)
            else:
                return str(self.id)

        # def add(self, actor):
        #     self.actors.add(actor)
        #
        # def remove(self, actor):
        #     self.actors.remove(actor)


    class HabitableLocation(Location):
        """Location where actors can live and modifier for health and items recovery.
        Other Habitable locations can be buildings which mimic this functionality or may inherit from it in the future.
        """
        def __init__(self, id="Livable Location", daily_modifier=.1, rooms=1, desc=""):
            super(HabitableLocation, self).__init__(id=id)

            self._habitable = True
            self.rooms = rooms
            self.inhabitants = set()
            self._daily_modifier = daily_modifier
            self.desc = desc

        @property
        def daily_modifier(self):
            return self._daily_modifier

        @property
        def habitable(self):
            # Property as this is used in building to the same purpose,
            # we may need to
            return self._habitable

        @property
        def vacancies(self):
            # check if there is place to live in this building.
            if not self.habitable:
                return 0

            rooms = self.rooms - len(self.inhabitants)
            if rooms < 0:
                rooms = 0
            return rooms

        def get_all_chars(self):
            return self.inhabitants

    class InvLocation(HabitableLocation):
        """Location with an inventory:

        Basically, a habitable location where one can store 'stuff'
        Also has a number of extra properties.
        """
        pass # obsolete