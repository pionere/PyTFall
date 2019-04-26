# Support classes:
init -9 python:
    ######## Game logic classes ########
    class PyTFallStatic(_object):
        """This class should(in the future...) hold all static information which should not be stored in the save files
        """
        world_music = dict()

        @staticmethod
        def load_music(key):
            if key not in PyTFallStatic.world_music:
                PyTFallStatic.world_music[key] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith(key)]
        @staticmethod
        def play_music(key, fadein=0):
            PyTFallStatic.load_music(key)
            renpy.play(choice(PyTFallStatic.world_music[key]), channel="world", fadein=fadein)

    class PyTFallWorld(_object):
        '''This class will guide all AI/Logic inside of the world
            that is not controlled by the player.
        This really looks like this should be a function at the moment,
            but we will add more relevant methods in the future.
        '''
        RCD = {"SIW": 0, "Specialist": 0,
               "Combatant": 0, "Server": 0,
               "Caster": 0} # All general occupations for rchar population
        def __init__(self):

            # Maps
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
            self.afterlife = AfterLife()

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
                                      "Caster": 5}
            self.rc_free_population = 40
            self.rc_slave_pop_distr = {"SIW": 60, "Server": 40}
            self.rc_slave_population = 30

        def init_shops(self):
            # Shops:
            self.shops = ['General Store', 'Cafe', 'Work Shop', 'Witches Hut', 'Tailor Store', 'Tavern', 'Ninja Tools Shop', 'Peevish Shop', 'Witch Spells Shop', 'Aine Shop', 'Angelica Shop']
            self.general_store = ItemShop('General Store', sells=["any"], sell_margin=.7)
            self.cafe = ItemShop('Cafe', sells=["food"], sell_margin=1.1)
            self.tavern = ItemShop('Tavern', sells=["alcohol"], sell_margin=1.1)
            self.workshop = ItemShop('Work Shop', sells=["axe", "armor", "special", "dagger", "fists", "rod", "claws", "sword", "bow", "shield", "tool", "whip", "throwing", "crossbow", "scythe", "other"])
            self.witches_hut = ItemShop('Witches Hut', sells=["amulet", "ring", "restore", "other", "rod", "dagger", "treasure"])
            self.witch_spells_shop = ItemShop("Witch Spells Shop", gold=5000, sells=["scroll"], sell_margin=1, buy_margin=5.0)
            self.tailor_store = ItemShop('Tailor Store', sells=["dress", "special"])
            self.hidden_village_shop = ItemShop("Ninja Tools Shop", location="Ninja Shop", gold=1000, sells=["armor", "dagger", "fists", "rod", "claws", "scroll", "sword", "bow", "amulet", "ring", "restore", "dress", "treasure"], buy_margin=3.0)
            self.peevish_shop = ItemShop("Peevish Shop", gold=5000, visible=False, sells=["scroll"], sell_margin=1, buy_margin=5.0)
            self.aine_shop = ItemShop("Aine Shop", gold=5000, visible=False, sells=["scroll"], sell_margin=1, buy_margin=5.0)
            self.angelica_shop = ItemShop("Angelica Shop", gold=5000, visible=False, sells=["scroll"], sell_margin=1, buy_margin=5.0)

        def init_arena(self):
            self.arena.setup_arena()
            self.arena.update_matches()
            self.arena.update_teams()
            self.arena.find_opfor()
            self.arena.update_dogfights()

        # World AI ----------------------------->
        def populate_world(self, tier_offset=.0):
            # Get all rchars in the game and sort by status.
            rc_free = []
            rc_slaves = []
            for c in chars.values():
                if c.__class__ != rChar:
                    continue
                if c.arena_active:
                    continue
                if c in hero.chars:
                    continue

                if c.status == "free":
                    rc_free.append(c)
                else:
                    rc_slaves.append(c)

            limit = day - 10
            for c in rc_slaves[:]:
                if c.flag("from_day_in_game") < limit:
                    rc_slaves.remove(c)
                    remove_from_gameworld(c)

            limit = day - 20
            for c in rc_free[:]:
                if c.flag("from_day_in_game") < limit and c.get_stat("disposition") <= 0 and c.get_stat("affection") <= 0:
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
            for bt_go_base, amount in distibution.items():
                for i in range(amount):
                    tier = hero.tier + tier_offset
                    if dice(1): # Super char!
                        tier += uniform(2.5, 4.0)
                    elif dice(20): # Decent char.
                        tier += uniform(1.0, 2.5)
                    else: # Ok char...
                        tier += uniform(.1, 1.0)

                    build_rc(bt_go_base=bt_go_base,
                             set_status=status,
                             tier=tier, tier_kwargs=None,
                             give_civilian_items=True,
                             give_bt_items=give_bt_items)

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
            tl.start("Girlsmeets ND")
            gm.next_day()
            tl.end("Girlsmeets ND")

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
                tl.start("PyTFall population ND")
                self.populate_world(tier_offset=.0)
                tl.end("PyTFall population ND")

    class Gazette(_object):
        def __init__(self):
            self.clear()

        def clear(self):
            self.show = "first_view"

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
        pass # FIXME obsolete

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
            return round_int(percentage)

        def moonphase(self):
            '''Returns the lunar phase according to daycount.

            Phases:
            new moon -> waxing crescent -> first quarter -> waxing moon ->
                full moon -> waning moon -> last quarter -> waning crescent -> ...
            '''
            # calculate days into the cycle
            newmoonidx = self.newmoonday - 1
            dayidx = self.daycount_from_gamestart - newmoonidx
            moonidx = dayidx % self.mooncycle
            # substract the number of named days
            unnamed_days = self.mooncycle - 4
            # calculate the days per quarter
            quarter = unnamed_days / 4.0
            # determine phase
            cq = 1
            if moonidx < cq:
                return "new moon"
            cq += quarter
            if moonidx < cq:
                return "waxing crescent"
            cq += 1
            if moonidx < cq:
                return "first quarter"
            cq += quarter
            if moonidx < cq:
                return "waxing moon"
            cq += 1
            if moonidx < cq:
                return "full moon"
            cq += quarter
            if moonidx < cq:
                return "waning moon"
            cq += 1
            if moonidx < cq:
                return "last quarter"
            else:
                return "waning crescent"

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
