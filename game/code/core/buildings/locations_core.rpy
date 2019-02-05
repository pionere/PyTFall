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
    class Location(_object):
        """
        Usually a place or a building.
        This simply holds references to actors that are present @ the location.
        If a location is not a member of this class, it is desirable for it to have a similar setup or to be added to change_location() function manually.
        """
        pass # obsolete

    class HabitableLocation(_object):
        """Location where actors can live and modifier for health and items recovery.
        Other Habitable locations can be buildings which mimic this functionality or may inherit from it in the future.
        """
        def __init__(self, id, daily_modifier=.1, desc=""):
            super(HabitableLocation, self).__init__()

            self.id = id
            self.inhabitants = set()
            self.daily_modifier = daily_modifier
            self.desc = desc

        def get_all_chars(self):
            return self.inhabitants

        def __str__(self):
            if hasattr(self, "name"):
                return str(self.name)
            else:
                return str(self.id)

    class InvLocation(HabitableLocation):
        """Location with an inventory:

        Basically, a habitable location where one can store 'stuff'
        Also has a number of extra properties.
        """
        pass # obsolete
