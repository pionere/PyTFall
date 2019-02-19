# Support classes:
init -9 python:
    ######## Game logic classes ########
    class PyTFallWorld(_object):
        '''This class will guide all AI/Logic inside of the world
            that is not controlled by the player.
        This really looks like this should be a function at the moment,
            but we will add more relevant methods in the future.
        '''
        RCD = {"SIW": 0, "Specialist": 0,
               "Combatant": 0, "Server": 0,
               "Healer": 0} # All general occupations for rchar population
        def __init__(self):
            # Descriptions for: *Elements
            self.desc = object()
            self.desc.elements = {
                "fire": str("The wildest of all elements bringing a change that can never be undone. In a blink of an eye, it can turn any obstacle to dust leaving nothing but scorched earth in its path. In unskilled hands, it can be more dangerous to its wielders than to their enemies. Fire Element regardless to its power, is weak against Water but have the advantage versus Air."),
                "air": str("The most agile of the elements. Utilizing its transparency and omnipresence to maximum. Wielders of this element are also capable of performing lighting based spells. Being able to strike swiftly and undetected, in capable hands this element does not give opponents much time to defend themselves. The Air Element excels against Earth but struggles greatly when dealing with Fire."),
                "earth": str("The slowest and sturdiest among the elements. Known for sacrificing speed in exchange for overwhelming destructive power. Unlike other elements that leaves evidence of their devastating acts, Earth is capable of literally burying the truth. The Earth Element have the upper hand against Water, but have a hard time against the swift Air."),
                "water": str("The most mysterious among the elements. Hiding it twisted and destructive nature under the calm surface. Leaving behind only rumble and bodies as proof of it fatal capabilities. Dominating Fire with ease, the Water Element is relatively weak against Earth."),
                "darkness": str("One of the two elements born from men desires, thoughts and deeds. Fuelling itself from anger, impure thoughts and evil acts. Dwelling deep in everyone'?s soul, patiently expanding, slowly consuming ones soul. Evenly matched and locked in the ethereal struggle Light and Darkness, these opposites can cause chaotic damage against each other."),
                "neutral": str("Neutral alignment is the most popular option among warriors that do not rely on use of magic. It will ensure good degree of resistance from anything some silly mage may throw at its wielder. On other hand, this is possibly the worst choice for any magic user."),
                "light": str("One of the two elements born from men desires, thoughts and deeds. Light nests itself inside everyone souls. Gaining its force from good acts and pure thoughts. Evenly matched and locked in the ethereal struggle Light and Darkness, these opposites can cause chaotic damage against each other.")
            }

            # Maps
            self.map_pattern = "content/gfx/bg/locations/map_buttons/gismo/"
            self.maps = OnScreenMap()
            self.economy = Economy()

            # locations
            self.arena = Arena()
            self.jail = CityJail()
            self.sm = SlaveMarket()
            self.ra = RunawayManager() 
            self.school = School()

            self.city = HabitableLocation(id="City Apartments", daily_modifier=.2, desc="Girls apartments somewhere in the city")
            self.streets = HabitableLocation(id="Streets", daily_modifier=-.1, desc="Cold and unneighborly city alleys")
            self.afterlife = HabitableLocation(id="After Life", daily_modifier=.0, desc="No one knows where is this place and what's going on there")

            self.hp = GuiHeroProfile()

            # Exploration
            # self.tiles = load_tiles()
            # self.forest_1 = object()

            # Events:
            self.world_events = WorldEventsManager(world_events)

            # Quests:
            self.world_quests = WorldQuestManager(world_quests)

            # Actions:
            self.world_actions = WorldActionsManager()

            # Random Chars distribution:
            self.rc_free_pop_distr = {"SIW": 30, "Specialist": 10,
                                      "Combatant": 30, "Server": 15,
                                      "Healer": 5}
            self.rc_free_population = 40
            self.rc_slave_pop_distr = {"SIW": 60, "Server": 40}
            self.rc_slave_population = 30

        def init_shops(self):
            # Shops:
            self.shops = ['General Store', 'Cafe', 'Work Shop', 'Witches Hut', 'Tailor Store', 'Tavern', 'Ninja Tools Shop', 'Peevish Shop', 'Witch Spells Shop', 'Aine Shop', 'Angelica Shop']
            self.general_store = GeneralStore('General Store', 18, ['General Store'], sell_margin=.7)
            self.cafe = ItemShop('Cafe', 18, ['Cafe'], sells=["food"], sell_margin=1.1)
            self.tavern = ItemShop('Tavern', 18, ['Tavern'], sells=["alcohol"], sell_margin=1.1)
            self.workshop = ItemShop('Work Shop', 18, ['Work Shop'], sells=["axe", "armor", "special", "dagger", "fists", "rod", "claws", "sword", "bow", "shield", "tool", "whip", "throwing", "crossbow", "scythe", "other"])
            self.witches_hut = ItemShop('Witches Hut', 18, ['Witches Hut'], sells=["amulet", "ring", "restore", "other", "rod", "dagger", "treasure"])
            self.tailor_store = ItemShop('Tailor Store', 18, ['Tailor Store'], sells=["dress", "special"])
            self.hidden_village_shop = ItemShop("Ninja Tools Shop", 18, ["Ninja Shop"], gold=1000, sells=["armor", "dagger", "fists", "rod", "claws", "scroll", "sword", "bow", "amulet", "ring", "restore", "dress", "treasure"], buy_margin=3.0)
            self.peevish_shop = ItemShop("Peevish Shop", 18, ["Peevish Shop"], gold=5000, sells=["scroll"], sell_margin=1, buy_margin=5.0)
            self.witch_spells_shop = ItemShop("Witch Spells Shop", 18, ["Witch Spells Shop"], gold=5000, sells=["scroll"], sell_margin=1, buy_margin=5.0) # for scrolls
            self.aine_shop = ItemShop("Aine Shop", 18, ["Aine Shop"], gold=5000, sells=["scroll"], sell_margin=1, buy_margin=5.0)
            self.angelica_shop = ItemShop("Angelica Shop", 18, ["Angelica Shop"], gold=5000, sells=["scroll"], sell_margin=1, buy_margin=5.0)

        def init_arena(self):
            self.arena.setup_arena()
            self.arena.update_matches()
            self.arena.update_teams()
            self.arena.find_opfor()
            self.arena.update_dogfights()

        # World AI ----------------------------->
        def populate_world(self, tier_offset=.0):
            # Get all rcahrs in the game and sort by status.
            rc_free = []
            rc_slaves = []
            for c in chars.values():
                if c.__class__ != rChar:
                    continue
                if c.arena_active: # Check if this is correct...
                    continue
                if c in hero.chars:
                    continue

                if c.status == "free":
                    rc_free.append(c)
                else:
                    rc_slaves.append(c)

            for c in rc_slaves[:]:
                if c.get_flag("days_in_game", 0) > 10:
                    rc_slaves.remove(c)
                    remove_from_gameworld(c)

            for c in rc_free[:]:
                if c.get_flag("days_in_game", 0) > 20 and c.get_stat("disposition") <= 0:
                    rc_free.remove(c)
                    remove_from_gameworld(c)

            self.populate_rchars(rc_free, "free", tier_offset=tier_offset)
            self.populate_rchars(rc_slaves, "slave", tier_offset=tier_offset)

        def populate_rchars(self, ingame_rchars, status, tier_offset=.0):
            if status == "free":
                distibution_wanted = self.rc_free_pop_distr
                rchar_wanted = self.rc_free_population
            else:
                distibution_wanted = self.rc_slave_pop_distr
                rchar_wanted = self.rc_slave_population

            required = rchar_wanted - len(ingame_rchars)
            if required <= 0:
                return

            # Distribution of the above:
            current_distibution_raw = self.RCD.copy()

            for c in ingame_rchars:
                for occ in c.gen_occs:
                    if occ in current_distibution_raw:
                        current_distibution_raw[occ] += 1
                if "Healer" in c.traits:
                    current_distibution_raw["Healer"] += 1

            wanted_distibution_perc = {}
            total = sum(current_distibution_raw.values())
            if total == 0:
                wanted_distibution_perc = distibution_wanted
            else:
                for key, value in distibution_wanted.items():
                    value -= 100.0*current_distibution_raw[key]/total
                    wanted_distibution_perc[key] = max(0, value)

            total = float(sum(wanted_distibution_perc.values()))
            distibution = {}
            for key, value in wanted_distibution_perc.items():
                distibution[key] = round_int(required*value/total)

            # We are done with distibution, now tiers:
            give_bt_items = status == "free"
            for bt_group, amount in distibution.items():
                for i in range(amount):
                    if dice(1): # Super char!
                        tier = hero.tier + uniform(2.5, 4.0)
                    elif dice(20): # Decent char.
                        tier = hero.tier + uniform(1.0, 2.5)
                    else: # Ok char...
                        tier = hero.tier + uniform(.1, 1.0)
                    tier += tier_offset

                    build_rc(bt_group=bt_group,
                             set_status=status,
                             tier=tier, tier_kwargs=None,
                             give_civilian_items=True,
                             give_bt_items=give_bt_items,
                             spells_to_tier=False) # Do we want this for mages?

        # ----------------------------------------->
        def next_day(self):
            '''Next day logic for our PyTFall World
            '''
            global gazette
            gazette.clear()

            # Shops:
            tl.start("Shops ND")
            self.general_store.next_day()
            self.cafe.next_day()
            self.tavern.next_day()
            self.workshop.next_day()
            self.witches_hut.next_day()
            self.tailor_store.next_day()
            self.hidden_village_shop.next_day()
            self.peevish_shop.next_day()
            self.witch_spells_shop.next_day()
            self.aine_shop.next_day()
            self.angelica_shop.next_day()
            tl.end("Shops ND")

            # Slave Market:
            tl.start("SlaveMarket ND")
            self.sm.next_day()
            tl.end("SlaveMarket ND")

            # Employment Agency:
            tl.start("EmploymentAgency ND")
            populate_ea()
            tl.end("EmploymentAgency ND")

            # Runaways:
            tl.start("Runaway/Jail ND")
            self.ra.next_day()
            self.jail.next_day()
            tl.end("Runaway/Jail ND")

            # Girlsmeets:
            # Termination:
            cells = gm.girlcells
            for cell in cells.keys():
                if cells[cell].termination_day <= day:
                    del cells[cell]

            # Schools:
            tl.start("Schools ND")
            self.school.next_day()
            tl.end("Schools ND")

            # Arena:
            tl.start("Arena ND")
            self.arena.next_day()
            tl.end("Arena ND")

            # Girls, Buildings income and Hero:
            tl.start("MC's Chars ND")
            for char in chars.values():
                char.next_day()
            hero.next_day()
            for b in hero.buildings:
                b.nd_log_income()
            tl.end("MC's Chars ND")

            # Same for Arena Fighters:
            tl.start("Arena-Fighter's ND")
            for fighter in pytfall.arena.arena_fighters.values():
                fighter.next_day()
            tl.end("Arena-Fighter's ND")

            if not day % 14:
                self.populate_world(tier_offset=.0)

            # Gazette:
            gazette.first_view = True
            gazette.show = False


    class Gazette(_object):
        def __init__(self):
            self.show = False
            self.first_view = True

            self.clear()

        def clear(self):
            self.arena = []
            self.shops = []
            self.other = []
            self.stories = []
            self.global_events = []
            self.city_events = []
            self.obituaries = []


    class Difficulties(_object):
        """
        Adjusts gameplay values based on the difficulty setting.
        """
        def __init__(self):
            self.difficulty = "normal"

            self.easy = dict()
            self.normal = dict()
            self.hard = dict()

            self.easy["income_tax_1000+"] = 5
            self.normal["income_tax_1000+"] = 10
            self.hard["income_tax_1000+"] =  15

        def set_difficulty(self, difficulty):
            """
            Sets up difficulty values throughout the game.
            """
            self.difficulty = difficulty
            for i in self.__dict__[difficulty]:
                setattr(self, i, self.__dict__[difficulty][i])


    class ListHandler(_object):
        # Most of this class is obsolete at this point of development
        # Note: We should cut it to it's bare minimum and kill it later :)
        def __init__(self):
            # Dict for music locations ( :0 )
            self.world_music = dict()


    class Calendar(object):
        '''
        Cheers to Rudi for mooncalendar calculations.
        '''
        def __init__(self, day=1, month=1, year=1, leapyear=False):
            """
            Expects day/month/year as they are numbered in normal calender.
            If you wish to add leapyear, specify a number of the first Leap year to come.
            """
            self.day = day
            self.month = month - 1
            self.year = year
            if not leapyear:
                self.leapyear = self.year + 4
            else:
                self.leapyear = leapyear

            self.daycount_from_gamestart = 0

            self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            self.month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                               'August', 'September', 'October', 'November', 'December']
            self.days_count = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

            self.mooncycle = 29
            self.newmoonday = 1

        def game_day(self):
            """
            Returns amount of days player has spent in game.
            Counts first day as day 1.
            """
            return self.daycount_from_gamestart + 1

        def string(self):
            return "%s %d, %d"%(self.month_names[self.month], self.day, self.year)

        def next(self, days=1):
            """
            Next day counter.
            Now supports skipping.
            """
            global day
            self.daycount_from_gamestart += days
            day = self.daycount_from_gamestart + 1
            while days:
                self.day += 1
                days -= 1
                if self.leapyear == self.year and self.month == 1:
                    if self.day > self.days_count[self.month] + 1:
                        self.month += 1
                        self.day = 1
                        self.leapyear += 4
                elif self.day > self.days_count[self.month]:
                    self.month += 1
                    self.day = 1
                    if self.month > 11:
                        self.month = 0
                        self.year += 1


        def weekday(self):
            '''Returns the name of the current day according to daycount.'''
            daylistidx = self.daycount_from_gamestart % len(self.days)
            return self.days[daylistidx]

        def week(self):
            '''Returns the number of weeks, starting at 1 for the first week.
            '''
            weekidx = self.daycount_from_gamestart / len(self.days)
            return weekidx + 1

        def lunarprogress(self):
            '''Returns the progress in the lunar cycle since new moon as percentage.
            '''
            newmoonidx = self.newmoonday - 1
            dayidx = self.daycount_from_gamestart - newmoonidx
            moonidx = dayidx % self.mooncycle
            moondays = moonidx + 1
            percentage = moondays * 100.0 / self.mooncycle
            return int(round(percentage))

        def moonphase(self):
            '''Returns the lunar phase according to daycount.

            Phases:
            new moon -> waxing crescent -> first quater -> waxing moon ->
                full moon -> waning moon -> last quarter -> waning crescent -> ...
            '''
            # calculate days into the cycle
            newmoonidx = self.newmoonday - 1
            dayidx = self.daycount_from_gamestart - newmoonidx
            moonidx = dayidx % self.mooncycle
            moondays = moonidx + 1
            # substract the number of named days
            unnamed_days = self.mooncycle - 4
            # calculate the days per quarter
            quarter = unnamed_days / 4.0
            # determine phase
            if moonidx<1:
                phase = "new moon"
            elif moonidx<(quarter+1):
                phase = "waxing crescent"
            elif moonidx<(quarter+2):
                phase = "first quarter"
            elif moonidx<(2*quarter+2):
                phase = "waxing moon"
            elif moonidx<(2*quarter+3):
                phase = "full moon"
            elif moonidx<(3*quarter+3):
                phase = "waning moon"
            elif moonidx<(3*quarter+4):
                phase = "last quarter"
            else:
                phase = "waning crescent"
            return phase


    class OnScreenMap(_object):
        """
        Loads data from JSON, builds a map.
        To be used with screens.
        It either builds the map from cut out peaces or by placing icons on in.
        """
        def __init__(self):
            in_file = content_path("db/city_map.json")
            with open(in_file) as f:
                data = json.load(f)

            for i in data:
                setattr(self, i, data[i])

        def __call__(self, map):
            return getattr(self, map)

    class Economy(_object):
        """Core class that hold and modifies data about global economy.

        At first it will deal with income from jobs and it's global mods.
        In the future, plan is to make it more dynamic and eventful.
        """
        def __init__(self):
            self.state = 1.0 # Modifier for default economy state

            # Taxes related:
            self.income_tax = [(25000, .05), (50000, .1),
                               (100000, .15), (200000, .25),
                               (float("inf"), .35)]
            self.property_tax = {"slaves": .01,
                                 "real_estate": .015}
            self.confiscation_range = (.5, .7)

        def get_clients_pay(self, job, difficulty=1):
            if isinstance(job, basestring):
                job = store.simple_jobs[job]

            payout = job.per_client_payout
            payout *= max(difficulty, 1)
            payout *= self.state
            return payout


    class CharsSortingForGui(_object):
        """Class we use to sort and filter character for the GUI.

        - Reset is done by a separate function we bind to this class.
        """
        def __init__(self, reset_callable, container=None):
            """
            reset_callable: a funcion to be called without arguments that would return a full, unfiltered list of items to be used as a default.
            container: If not None, we set this contained to self.sorted every time we update. We expect a list with an object and a field to be used with setattr.
            """
            self.reset_callable = reset_callable
            self.target_container = container
            self.sorted = list()

            self.status_filters = set()
            self.action_filters = set()
            self.class_filters = set()
            self.occ_filters = set()
            self.location_filters = set()
            self.home_filters = set()
            self.work_filters = set()

            self.sorting_order = None

        def clear(self):
            self.update(self.reset_callable())
            self.status_filters = set()
            self.action_filters = set()
            self.class_filters = set()
            self.occ_filters = set()
            self.location_filters = set()
            self.home_filters = set()
            self.work_filters = set()

        def update(self, container):
            self.sorted = container
            if self.target_container:
                setattr(self.target_container[0], self.target_container[1], container)

        def filter(self):
            filtered = self.reset_callable()

            # Filters:
            if self.status_filters:
                filtered = [c for c in filtered if c.status in self.status_filters]
            if self.action_filters:
                filtered = [c for c in filtered if c.action in self.action_filters]
            if self.class_filters:
                filtered = [c for c in filtered if c.traits.basetraits.intersection(self.class_filters)]
            if self.occ_filters:
                filtered = [c for c in filtered if self.occ_filters.intersection(c.gen_occs)]
            if self.location_filters:
                filtered = [c for c in filtered if c.location in self.location_filters]
            if self.home_filters:
                filtered = [c for c in filtered if c.home in self.home_filters]
            if self.work_filters:
                filtered = [c for c in filtered if c.workplace in self.work_filters]

            # Sorting:
            if self.sorting_order == "alphabetical":
                filtered.sort(key=attrgetter("name"))
            elif self.sorting_order == "level":
                filtered.sort(key=attrgetter("level"), reverse=True)

            self.update(filtered)


    # Menu extensions:
    class MenuExtension(_dict):
        """Smarter Dictionary...
        """
        def add_extension(self, ext, matrix):
            self[ext].append(matrix)

        def remove_extension(self, ext, name):
            matrix = None
            for m in self[ext]:
                if m[0] == name:
                    matrix = m
                    break
            else:
                if DEBUG_LOG:
                    devlog.warning("Removal of matrix named: {} from Menu Extensions failed!".format(name))
            if matrix:
                self[ext].remove(matrix)

        def build_choices(self, ext):
            choices = []
            for i in self[ext]:
                # check if we have a condition in the matrix (2nd index)
                if len(i) == 3:
                    if eval(i[2]):
                        # We need to remove the second index because screens expects just the two:
                        i = i[:2]
                        choices.append(i)
                else:
                    choices.append(i)
            return choices
