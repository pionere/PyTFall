init -9 python: # FG Area
    class FG_Area(_object):
        """Dummy class for areas (for now).

        Tracks the progress in SE areas as well as storing their data.
        """
        def __init__(self):
            self.stage = 0 # For Sorting.
            self.tier = .2 # Difficulty
            self.days = 3
            self.max_days = 15
            self.risk = 50
            self._explored = 0

            self.main = False
            self.area = None

            self.travel_time = 0
            self.hazard = dict()
            self.items = dict()
            self.mobs = dict()

            # Special fields for quests, keys are chars or items and values are
            # exploration progress required to get them. Later we might add
            # some complex conditions instead, like fighting mobs.
            self.special_items = dict()
            self.special_chars = dict()

            # Chars capture:
            self.capture_chars = False
            self.chars = dict() # id: [explored, chance_per_day]
            self.rchars = dict() # id can be 'any' here, meaning any rChar.

            self.items_price_limit = 0

            # Use dicts instead of sets as we want counters:
            self.mobs_defeated = dict()
            self.found_items = dict()
            self.chars_captured = 0
            self.cash_earned = 0

            # Flags for exploration tasks on "area" scope.
            self.camp = None
            self.building_camp = False
            self.camp_build_points_current = 0
            self.camp_build_points_required = 1000

            # Generated Content:
            self.logs = collections.deque(maxlen=15)

            # Trackers exploring the area at any given time, this can be used for easy access!
            self.trackers = set()

        @property
        def camp_build_status(self):
            return "%d%%" % (100.0*self.camp_build_points_current/self.camp_build_points_required)

        @property
        def teams(self):
            # Teams presently exploring this area:
            return [t.team for t in self.trackers]

        @property
        def explored(self):
            return self._explored

        @explored.setter
        def explored(self, value):
            if value >= 100:
                self._explored = 100
            else:
                self._explored = value


init -6 python: # Guild, Tracker and Log.
    # ======================= (Simulated) Exploration code =====================>>>
    class ExplorationTracker(Job):
        # Added inheritance for Job so we can use the required methods.
        """The class that stores data for an exploration job.

        *Not really a Job, it stores data and doesn't write any reports to ND. **Maybe it should create ND report once the run is done!
        Adapted from old FG, not sure what we can keep here..."""
        def __init__(self, team, area, guild):
            """Creates a new ExplorationJob.

            team = The team that is exploring.
            area = The area that is being explored.
            """
            super(ExplorationTracker, self).__init__()
            self.id = "Exploration"
            self.type = "Combat"

            # Traits/Job-types associated with this job:
            self.occupations = ["Combatant"] # General Strings likes SIW, Combatant, Server...
            self.occupation_traits = [traits["Warrior"], traits["Mage"]] # Corresponding traits...

            self.base_stats = {"attack": 20, "defence": 20,
                               "agility": 60, "magic": 20}
            self.base_skills = {"exploration": 100}

            self.desc = "Explore the world, find new places, meet new people... and take their shit!"

            self.team = team
            self.area = area
            self.guild = guild # Guild this tracker was initiated from...

            # copy launch configuration from the area
            self.building_camp = area.building_camp
            self.capture_chars = area.capture_chars
            self.risk = area.risk
            self.days = max(area.days, 3) # Days team is expected to be exploring (without travel times)!

            self.day = 1 # Day since start.
            self.days_in_camp = 0 # Simple counter for the amount of days team is spending at camp. This is set back to 0 when team recovers inside of the camping method.

            # This is the general items that can be found at any exploration location,
            # Limited by price:
            self.exploration_items = dict([(item.id, item.chance) for item in store.items.values() if
                                          "Exploration" in item.locations and
                                          area.items_price_limit >= item.price])

            # Traveling to and from + Status flags:
            # We may be setting this directly in the future.
            # Distance in KM as units. 20 is what we expect the
            # team to be able to travel in a day.
            # This may be offset through traits and stats/skills.
            # We assume that it's never right outside of the
            # freaking city walls:
            self.base_distance = max(round_int(area.travel_time * 20), 6)

            self.traveled = None # Distance traveled in "KM"...

            # Exploration:
            # Used to be effectiveness, but that would collide with a method of parent class
            self.ability = 0 # How well the team can perform any given exploration task.

            self.state = "traveling to" # Instead of a bunch of properties, we'll use just the state as string and set it accordingly.
            # Use dicts instead of sets as we want counters:
            self.mobs_defeated = defaultdict(int)
            self.found_items = list()
            self.captured_chars = list()
            self.cash = list()
            self.daily_items = None

            self.flag_red = False
            self.flag_green = False
            self.logs = list() # List of all log object we create during this exploration run.
            self.died = list()

        @property
        def obj_area(self):
            # "Global" area object, we usually update this where we're done.
            return fg_areas[self.area.id]

        def log(self, txt, name="", nd_log=True, ui_log=False, **kwargs):
            if DEBUG_SE:
                msg = "{}: {} at {}\n    {}".format(self.area.name,
                                    self.team.name, self.guild.env.now, txt)
                se_debug(msg, mode="info")

            obj = ExplorationLog(name, txt, nd_log, ui_log, **kwargs)
            self.logs.append(obj)
            return obj

        def finish_exploring(self):
            """
            Build one major report for next day!
            Log all the crap to Area and Main Area!
            Make sure that everything is cleaned up.
            """
            global fg_areas
            global items
            area = self.area

            # Main and Sub Area Stuff:
            area.logs.extend([l for l in self.logs if l.ui_log])
            area.trackers.remove(self)

            # Settle rewards and update data:
            for i in self.found_items:
                item = items[i]
                hero.add_item(item)

            found_items = collections.Counter(self.found_items)
            cash_earned = sum(self.cash)
            chars_captured = len(self.captured_chars)

            area.mobs_defeated = add_dicts(area.mobs_defeated, self.mobs_defeated)
            area.found_items = add_dicts(area.found_items, found_items)
            area.cash_earned += cash_earned
            area.chars_captured += chars_captured

            main_area = fg_areas[area.area]
            main_area.mobs_defeated = add_dicts(main_area.mobs_defeated, self.mobs_defeated)
            main_area.found_items = add_dicts(main_area.found_items, found_items)
            main_area.cash_earned += cash_earned
            main_area.chars_captured += chars_captured

            defeated_mobs.update(self.mobs_defeated)

            # Restore Chars and Remove from guild:
            self.guild.explorers.remove(self)
            for char in self.team:
                char.action = char.flag("loc_backup")
                char.del_flag("loc_backup")

            # Next Day Stuff:
            # Not sure if this is required... we can add log objects and build
            # reports from them in real-time instead of replicating data we already have.
            txt = []
            event_type = "explorationndreport"

            # Build an image combo for the report:
            img = Fixed(xysize=(820, 705))
            img.add(Transform(area.img, size=(820, 705)))
            vp = vp_or_fixed(self.team, ["fighting"],
                             {"exclude": ["sex"],
                             "resize": (150, 150)}, xmax=820)
            img.add(Transform(vp, align=(.5, .9)))

            # We need to create major report for nd to keep track of progress:
            for log in [l for l in self.logs if l.nd_log]:
                txt.append("\n".join(log.txt))

            evt = NDEvent(type=event_type,
                          img=img,
                          txt=txt,
                          char=self.team[0],
                          team=self.team,
                          charmod={},
                          loc=self.guild.building,
                          locmod={},
                          green_flag=self.flag_green,
                          red_flag=self.flag_red)
            NextDayEvents.append(evt)


    class ExplorationLog(Action):
        """Stores resulting text and data for SE.

        Also functions as a screen action for future buttons. Maybe...
        """
        def __init__(self, name="", txt="", nd_log=True, ui_log=False, item=None):
            """
            nd_log: Printed in next day report upon arrival.
            ui_log: Only reports worth of ui interface in FG.
            """
            self.name = name # Name of the event, to be used as a name of a button in gui. (maybe...)
            self.suffix = "" # If there is no special condition in the screen, we add this to the right side of the event button!

            self.nd_log = nd_log
            self.ui_log = ui_log
            self.txt = [] # I figure we use list to store text.
            if txt:
                self.txt.append(txt)

            self.battle_log = [] # Used to log the event.
            self.found_items = []
            self.item = item # Item object for the UI log if one was found!

        def add(self, text, newline=True):
            # Adds a text to the log.
            self.txt.append(text)

        def __call__(self):
            renpy.show_screen("...") # Whatever the pop-up screen with info in gui is gonna be.

        def is_sensitive(self):
            # Check if the button has an action.
            return self.battle_log or self.found_items


    class ExplorationGuild(TaskBusiness):
        SORTING_ORDER = 10
        COMPATIBILITY = []
        MATERIALS = {"Wood": 70, "Bricks": 50, "Glass": 5}
        NAME = "Exploration Guild"
        IMG = "content/gfx/bg/buildings/Chorrol_Fighters_Guild.webp"
        DESC = "Travel to exotic places, meet new monsters and people... and take their shit!"

        def __init__(self, **kwargs):
            super(ExplorationGuild, self).__init__(**kwargs)

            # Global Values that have effects on the whole business.
            self.teams = list() # List to hold all the teams formed in this guild. We should add at least one team or the guild will be useless...
            self.explorers = list() # List to hold all the (active) exploring trackers.

            self.teams.append(Team("Avengers", free=True))

            self.workable = True
            self.focus_team = None
            self.team_to_launch_index = 0

        # Teams control/sorting/grouping methods:
        def new_team(self, name):
            team = Team(name, free=True)
            self.teams.append(team)
            return team

        def remove_team(self, t):
            self.teams.remove(t)

        def teams_to_launch(self):
            # Returns a list of teams that can be launched on an exploration run.
            # Must have at least one member and NOT already running exploration!
            return [t for t in self.idle_teams() if t]

        def prev_team_to_launch(self):
            teams = self.teams_to_launch()
            index = self.team_to_launch_index

            index = (index-1) % len(teams)

            self.team_to_launch_index = index
            self.focus_team = teams[index]

        def next_team_to_launch(self):
            teams = self.teams_to_launch()
            index = self.team_to_launch_index

            index = (index+1) % len(teams)

            self.team_to_launch_index = index
            self.focus_team = teams[index]

        def exploring_teams(self):
            # Teams that are busy with exploration runs.
            return [tracker.team for tracker in self.explorers]

        def idle_teams(self):
            # Teams avalible for setup in order to set them on exploration runs.
            return [t for t in self.teams if t not in self.exploring_teams()]

        def idle_explorers(self):
            # Returns a list of idle explorers:
            return list(chain.from_iterable(t.members for t in self.idle_teams()))

        def launch_team(self, area, _team=None):
            # Moves the team to appropriate list, removes from main one and makes sure everything is setup right from there on out:
            team = self.focus_team if not _team else _team
            # self.teams.remove(team) # We prolly do not do this?

            # Setup Explorers:
            for char in team:
                # We effectively remove char from the game so this is prolly ok.
                char.action = "Exploring"
                char.set_flag("loc_backup", char.location)
                for t in hero.teams:
                    if char in t:
                        t.remove(char)

            tracker = ExplorationTracker(team, area, self)
            area.trackers.add(tracker)
            self.explorers.append(tracker)

            if not _team:
                self.focus_team = None
                self.team_to_launch_index = 0

            renpy.show_screen("message_screen", "Team %s was sent out on %d days exploration run!" % (team.name, area.days))

        # SimPy methods:
        def business_control(self):
            """SimPy business controller.
            """
            for tracker in self.explorers:
                self.env.process(self.exploration_controller(tracker))

            while 1:
                yield self.env.timeout(100)

        def exploration_controller(self, tracker):
            # Controls the exploration by setting up proper simpy processes.
            # Prep aliases:
            process = self.env.process

            if DEBUG_SE:
                msg = "Entered exploration controller for {}.".format(tracker.team.name)
                se_debug(msg, mode="info")

            # Log the day:
            temp = "{color=[green]}Day: %d{/color} | {color=[green]}%s{/color} is exploring %s!" % (tracker.day, tracker.team.name, tracker.area.name)
            tracker.log(temp)

            if tracker.state == "traveling to":
                # The team is not there yet, keep tracking
                result = yield process(self.travel_to(tracker))
                if result == "arrived":
                    tracker.state = None
            elif tracker.died:
                tracker.died -= team.members
                if tracker.died:
                    temp = "{color=[red]}%s{/color} did not make it through the night. RIP." % ", ".join([d.fullname for d in tracker.died])
                    tracker.log(temp)
                if len(tracker.team) == 0:
                    # The team died out during the night
                    tracker.finish_exploring() # Build the ND report!
                    self.env.exit() # They're done...
                # The remaining team is heading home -> reset the died list so they can sleep during the nights
                tracker.died = list()

            if self.env.now < 75: # do not go on exploring if the day is mostly over
                if tracker.state is None:
                    # just arrived to the location -> decide what to do
                    if tracker.building_camp:
                        tracker.state = "build camp"
                    else:
                        tracker.state = "exploring"
                    tracker.traveled = tracker.day # number of days it took to get to the location
                # Set the state to traveling back if we're done:
                elif tracker.day - tracker.traveled >= tracker.days:
                    tracker.state = "traveling back"
                    tracker.traveled = None # Reset for traveling back.

                while 1:
                    if tracker.state == "exploring":
                        result = yield process(self.explore(tracker))
                        if result == "back2camp":
                            break # We're done for today...
                        elif result == "rest":
                            tracker.state = "camping"
                    elif tracker.state == "camping":
                        result = yield process(self.camping(tracker))
                        if result == "restored":
                            tracker.state = "exploring"
                    elif tracker.state == "traveling back":
                        result = yield process(self.travel_back(tracker))
                        if result == "back2guild":
                            tracker.finish_exploring() # Build the ND report!
                            self.env.exit() # We're done...
                    elif tracker.state == "build camp":
                        yield process(self.build_camp(tracker))
                    if self.env.now >= 99:
                        break

            # Go to rest
            result = self.overnight(tracker)
            if result == "go2guild":
                tracker.state = "traveling back"
                tracker.traveled = None # Reset for traveling back.
            tracker.day += 1

        def travel_to(self, tracker):
            # Env func that handles the travel to routine.
            team_name = tracker.team.name
            area_name = tracker.area.name

            if DEBUG_SE:
                msg = "{} is traveling to {}.".format(team_name, area_name)
                se_debug(msg, mode="info")

            # Figure out how far we can travel in steps of 5 DU:
            # Understanding here is that any team can travel 20 KM per day on average.
            if tracker.traveled is None:
                temp = "{} is on route to {}!".format(team_name, area_name)
                tracker.log(temp)

                # setup the distance. This can be offset by traits and stats in the future.
                tracker.distance = tracker.base_distance
                delta = int(tracker.base_distance * .3)
                tracker.distance += randint(0, delta) - delta/2

                tracker.traveled = 0

            while 1:
                yield self.env.timeout(5) # We travel...

                tracker.traveled += 1

                # Team arrived:
                if tracker.traveled >= tracker.distance:
                    if DEBUG_SE:
                        msg = "{} arrived at {} ({}).".format(team_name, area_name, tracker.area.id)
                        se_debug(msg, mode="info")

                    temp = "{} arrived at {}!".format(team_name, area_name)
                    if tracker.day > 1:
                        temp = temp + " It took {} {} to get there.".format(tracker.day, plural("day", tracker.day))
                    else:
                        temp = temp + " The trip took less then one day!"
                    tracker.log(temp, name="Arrival")
                    self.env.exit("arrived")

                if self.env.now >= 99: # We couldn't make it there before the days end...
                    temp = "{} spent the entire day traveling to {}! ".format(team_name, area_name)
                    tracker.log(temp)
                    if DEBUG_SE:
                        se_debug(temp, mode="info")
                    self.env.exit("not_arrived")

        def travel_back(self, tracker):
            # Env func that handles the travel to routine.
            team_name = tracker.team.name

            if DEBUG_SE:
                msg = "{} is traveling back.".format(team_name)
                se_debug(msg, mode="info")

            # Figure out how far we can travel in 5 du:
            # Understanding here is that any team can travel 20 KM per day on average.
            # This can be offset by traits and stats in the future.
            if tracker.traveled is None:
                temp = "{} is traveling back home!".format(team_name)
                tracker.log(temp)

                # setup the distance. This can be offset by traits and stats in the future.
                tracker.distance = tracker.base_distance
                delta = int(tracker.base_distance * .3)
                tracker.distance += randint(0, delta) - delta/2

                tracker.traveled = 0
            while 1:
                yield self.env.timeout(5) # We travel...

                tracker.traveled += 1

                # Team arrived:
                if tracker.traveled >= tracker.distance:
                    temp = "{} returned to the guild!".format(team_name)
                    tracker.log(temp, name="Return")
                    self.env.exit("back2guild")

                if self.env.now >= 99: # We couldn't make it there before the days end...
                    temp = "{} spent the entire day traveling back to the guild from {}! ".format(team_name, tracker.area.name)
                    tracker.log(temp)
                    self.env.exit("on the way back")

        def camping(self, tracker):
            """Camping will allow restoration of health/mp/agility and so on. Might be forced on low health.
            """
            team = tracker.team
            auto_equip_counter = 0 # We don't want to run over autoequip on every iteration, two times is enough.

            if DEBUG_SE:
                msg = "{} is Camping. State: {}".format(team.name, tracker.state)
                se_debug(msg, mode="info")

            if not tracker.days_in_camp:
                temp = "{} setup a camp to get some rest and recover!".format(team.name)
                tracker.log(temp)

            while 1:
                yield self.env.timeout(5) # We camp...

                # Base stats:
                for c in team:
                    c.health += randint(8, 12)
                    c.mp += randint(8, 12)
                    c.vitality += randint(20, 50)

                # Apply items:
                if auto_equip_counter < 2:
                    invlist = list(c.inventory for c in team)
                    random.shuffle(invlist)
                    for explorer in team:
                        l = list()
                        if explorer.health <= explorer.get_max("health")*.8:
                            for inv in invlist:
                                l.extend(explorer.auto_equip(["health"], inv=inv))
                        if explorer.vitality <= explorer.get_max("vitality")*.8:
                            for inv in invlist:
                                l.extend(explorer.auto_equip(["vitality"], inv=inv))
                        if explorer.mp <= explorer.get_max("mp")*.8:
                            for inv in invlist:
                                l.extend(explorer.auto_equip(["mp"], inv=inv))
                        if l:
                            temp = "%s used: {color=[lawngreen]}%s %s{/color} to recover!" % (explorer.nickname, ", ".join(l), plural("item", len(l)))
                            self.log(temp)
                    auto_equip_counter += 1

                for c in team:
                    if c.health <= c.get_max("health")*.9:
                        break
                    if c.mp <= c.get_max("mp")*.9:
                        break
                    if c.vitality <= c.get_max("vitality")*.8:
                        break
                else:
                    tracker.days_in_camp = 0
                    temp = "{} are now ready for more action in {}! ".format(team.name, tracker.area.name)
                    tracker.log(temp)
                    self.env.exit("restored")

                if self.env.now >= 99:
                    tracker.days_in_camp += 1

                    if DEBUG_SE:
                        msg = "{} finished Camping. (Day Ended)".format(team.name)
                        se_debug(msg, mode="info")

                    self.env.exit("still camping")

        def overnight(self, tracker):
            # overnight: More effective heal. Spend the night resting.
            team = tracker.team

            if DEBUG_SE:
                msg = "{} is overnighting. State: {}".format(team.name, tracker.state)
                se_debug(msg, mode="info")

            if tracker.daily_items is not None and len(tracker.died) < len(team):
                # This basically means that team spent some time on exploring -> create a summary
                items = tracker.daily_items
                cash = tracker.daily_cash
                if items and cash:
                    tracker.log("The team has found: %s %s and {color=[gold]}%d Gold{/color} in loot!" % (", ".join(items), plural("item", len(items)), cash))
                    tracker.found_items.extend(items)
                    tracker.cash.append(cash)
                elif cash and not items:
                    tracker.log("The team has found: {color=[gold]}%d Gold{/color} in loot." % cash)
                    tracker.cash.append(cash)
                elif items and not cash:
                    tracker.log("The team has found: %s %s" % (", ".join(items), plural("item", len(items))))
                    tracker.found_items.extend(items)
                elif not items and not cash:
                    tracker.log("Your team has not found anything of interest...")

                tracker.daily_items = None

                if DEBUG_SE:
                    msg = "{} has finished an exploration scenario. (Day Ended)".format(team.name)
                    se_debug(msg, mode="info")

            if tracker.died:
                # some member(s) of the team died -> no rest for the remaining team, if any
                if len(tracker.died) == len(team):
                    # all members died -> just wait for the dawn to see if their make it
                    tracker.log("The members of % suffered fatal wounds. It is going to be a miracle if they make it through the night." % team.name)
                else:
                    # some members are alive -> send them back to the guild
                    tracker.log("The remaining of % has a sleepless night at the base camp." % team.name)
                return "go2guild"

            multiplier = .1 * (200 - self.env.now) / 100

            if tracker.state is None:
                temp = "After their journey {} spends the night in the camp!".format(team.name)
            elif tracker.state == "traveling to":
                temp = "The members of {} are sleeping in their tents en route to the destination! ".format(team.name)
                multiplier *= .5
            elif tracker.state == "exploring":
                temp = "{} are done with exploring for the day and will now rest and recover! ".format(team.name)
            elif tracker.state == "camping":
                temp = "{} cozied up in their camp for the night! ".format(team.name)
            elif tracker.state == "build camp":
                temp = "The members of {} are taking their well deserved rest from building the camp! ".format(team.name)
            elif tracker.state == "traveling back":
                temp = "{} set up their tents for the overnight en route to the guild! ".format(team.name)
                multiplier *= .5
            else:
                if DEBUG_SE:
                   msg = "State '{}' unrecognized while team {} is overnighting in camp".format(tracker.state, team.name)
                   se_debug(msg, mode="warn")
                temp = ""
            tracker.log(temp)

            for c in team:
                c.health += round_int(c.get_max("health")*multiplier)
                c.mp += round_int(c.get_max("mp")*multiplier)
                c.vitality += round_int(c.get_max("vitality")*multiplier)

            if tracker.captured_chars and tracker.state != "traveling back":
                return "go2guild"

        def explore(self, tracker):
            """SimPy process that handles the exploration itself.

            Idea is to keep as much of this logic as possible and adapt it to work with SimPy...
            """
            team = tracker.team
            area = tracker.area

            if tracker.daily_items is None:
                # first run during the day
                if DEBUG_SE:
                    msg = "{} is starting an exploration scenario.".format(team.name)
                    se_debug(msg, mode="info")

                tracker.daily_items = list()
                tracker.daily_cash = 0
                tracker.daily_mobs = 0

                # Effectiveness (Ability):
                ability = 0
                # Difficulty is tier of the area explored + 1/10 of the same value / 100 * risk.
                difficulty = area.tier*(1 + .001*tracker.risk)
                for char in team:
                    # Set their exploration capabilities as temp flag
                    ability += tracker.effectiveness(char, difficulty, log=None, return_ratio=False)
                ability = (ability+tracker.risk)*.01
                # Max cash to be found this day:
                tracker.max_cash = int(area.cash_limit*ability*(1 + .1*tracker.day))

                # Get the max number of items that can be found in one day:
                max_items = round_int(ability+(tracker.day*.2))
                if DEBUG_SE:
                    msg = "Max Items ({}) to be found on Day: {}!".format(max_items, tracker.day)
                    se_debug(msg, mode="info")
                # Let's run the expensive item calculations once and just give
                # Items as we explore. This just figures what items to give.

                chosen_items = [] # Picked items:
                # Local Items:
                local_items = []
                for i, d in area.items.iteritems():
                    if dice(d):
                        local_items.append(i)

                area_items = []
                for i, d in tracker.exploration_items.iteritems():
                    if dice(d):
                        area_items.append(i)

                if DEBUG_SE:
                    msg = "Local Items: {}|Area Items: {}".format(len(local_items), len(area_items))
                    se_debug(msg, mode="info")

                while len(chosen_items) < max_items and (area_items or local_items):
                    # always pick from local item list first!
                    if local_items:
                        chosen_items.append(choice(local_items))

                    if area_items and len(chosen_items) < max_items:
                        chosen_items.append(choice(area_items))

                if DEBUG_SE:
                    msg = "({}) Items were picked for choice!".format(len(chosen_items))
                    se_debug(msg, mode="info")

                tracker.chosen_items = chosen_items
            else:
                if DEBUG_SE:
                    msg = "{} is continuing the exploration.".format(team.name)
                    se_debug(msg, mode="info")

            items = tracker.daily_items

            while 1:
                yield self.env.timeout(5) # We'll go with 5 du per one iteration of "exploration loop".

                # record the exploration, unlock new maps
                if area.explored < 100 and dice(5):
                    area.explored += 1
                    for key, value in area.unlocks.items():
                        if value <= area.explored and not fg_areas[key].unlocked:
                            fg_areas[key].unlocked = True
                            temp = "Found a new path in the wilderness. It might worth to explore %s!" % key
                            temp = set_font_color(temp, "green")
                            tracker.log(temp)

                # Hazzard:
                if area.hazard:
                    temp = "{color=[yellow]}Hazardous area!{/color} The team has been effected."
                    tracker.log(temp)
                    for char in team:
                        for stat, value in area.hazard:
                            # value, because we calculated effects on daily base in the past...
                            var = max(1, round_int(value*.05))
                            char.mod_stat(stat, -var)
                    check_team = True # initiate a check at the end of the loop

                # Items:
                # Handle the special items (must be done here so it doesn't collide with other teams)
                special_items = []
                if area.special_items:
                    for item, explored in area.special_items.items():
                        if area.explored >= explored:
                            special_items.append(item)

                if tracker.chosen_items or special_items:
                    if self.env.now < 50:
                        chance = self.env.now/5
                    elif self.env.now < 80:
                        chance = self.env.now
                    else:
                        chance = 100

                    if dice(chance):
                        if special_items:
                            item = special_items.pop()
                            temp = "Found a special item %s!" % item
                            temp = set_font_color(temp, "orange")
                            tracker.log(temp, "Item", ui_log=True, item=store.items[item])
                            if DEBUG_SE:
                                msg = "{} Found a special item {}!".format(team.name, item)
                                se_debug(msg, mode="info")
                        else:
                            item = tracker.chosen_items.pop()
                            temp = "Found an item %s!" % item
                            temp = set_font_color(temp, "lawngreen")
                            tracker.log(temp, "Item", ui_log=True, item=store.items[item])
                            if DEBUG_SE:
                                msg = "{} Found an item {}!".format(team.name, item)
                                se_debug(msg, mode="info")
                        items.append(item)

                # Cash:
                if tracker.max_cash > tracker.daily_cash and dice(tracker.risk/5):
                    give = max(1, randint(1, tracker.max_cash/2))
                    tracker.daily_cash += give

                    temp = "{color=[gold]}Found %d Gold!{/color}" % give
                    tracker.log(temp)
                    if DEBUG_SE:
                        msg = "{} Found {} Gold!".format(team.name, give)
                        se_debug(msg, mode="info")

                #  =================================================>>>
                # Copied area must be used for checks here as it preserves state.
                if tracker.capture_chars and not self.env.now % 10:
                    # Special Chars:
                    if area.special_chars:
                        for char, explored in area.special_chars.items():
                            if area.explored >= explored:
                                del(area.special_chars[char])
                                tracker.captured_chars.append(char)

                                temp = "Your team has captured a 'special' character: {}!".format(char.name)
                                temp = set_font_color(temp, "orange")
                                tracker.log(temp)
                                if DEBUG_SE:
                                    msg = "{} has finished an exploration scenario. (Captured a special char {})".format(team.name, char.id)
                                    se_debug(msg, mode="info")

                                self.env.exit("back2camp")

                    # uChars (also from Area):
                    if area.chars:
                        for id, data in area.chars.items():
                            explored, chance = data
                            if area.explored >= explored and dice(chance*.1):
                                del(area.chars[id])

                                char = store.chars[id]
                                tracker.captured_chars.append(char)
                                temp = "Your team has captured a character: {}!".format(char.name)
                                temp = set_font_color(temp, "lawngreen")
                                tracker.log(temp)
                                if DEBUG_SE:
                                    msg = "{} has finished an exploration scenario. (Captured a uChar {})".format(team.name, char.id)
                                    se_debug(msg, mode="info")

                                self.env.exit("back2camp")

                    # rChars:
                    if area.rchars:
                        for id, data in area.rchars.items():
                            explored, chance = data
                            if area.explored >= explored and dice(chance*.1):
                                # Get tier:
                                if area.tier == 0:
                                    tier = random.uniform(.1, .3)
                                else:
                                    tier = random.uniform(area.tier*.8, area.tier*1.2)
                                tier = min(.1, tier)
                                tier = max(8, tier) # never build rChars over tier 8?

                                kwargs = {"tier": tier, "set_status": True}
                                if id != "any":
                                    kwargs["id"] = id

                                char = build_rc(**kwargs)
                                tracker.captured_chars.append(char)
                                temp = "Your team has captured a character: {}!".format(char.name)
                                temp = set_font_color(temp, "lawngreen")
                                tracker.log(temp)
                                if DEBUG_SE:
                                    msg = "{} has finished an exploration scenario. (Captured an rChar {})".format(team.name, char.id)
                                    se_debug(msg, mode="info")

                                self.env.exit("back2camp")

                if area.mobs:
                    # The expected number of encounters per day is increased by one after every 25 point of risk,
                    # but never fight anyone with risk lower than 25..
                    encounter_chance = dice((tracker.risk-25) / 5.0) # 100 * ((risk-25)/25.0) / (day_length / iteration_DU)
                    if encounter_chance:
                        tracker.daily_mobs += 1

                        mob = choice(area.mobs)

                        min_enemies = max(1, len(team) - 1)
                        max_ememies = max(3, len(team) + randrange(2))
                        enemies = randint(min_enemies, max_ememies)

                        temp = "{} were attacked by ".format(team.name)
                        temp = temp + "%d %s!" % (enemies, plural("mob", enemies))
                        log = tracker.log(temp, "Combat!", ui_log=True)
                        self.combat_mobs(tracker, mob, enemies, log)

                        check_team = True # initiate a check at the end of the loop

                if "check_team" in locals():
                    if tracker.died:
                        temp = "Your team is no longer complete. This concludes the exploration for the team."
                        tracker.log(temp)
                        if DEBUG_SE:
                            msg = "{} has finished an exploration scenario. (Lost a member)".format(team.name)
                            se_debug(msg, mode="info")
                        self.env.exit("back2camp") # member died -> back to camp

                    if tracker.daily_mobs >= tracker.risk/25:
                        temp = "Your team decided to go back to the camp to avoid further {color=[red]}risk{/color}."
                        tracker.log(temp)
                        if DEBUG_SE:
                            msg = "{} has finished an exploration scenario. (Fought too much)".format(team.name)
                            se_debug(msg, mode="info")
                        self.env.exit("back2camp") # too much risk -> back to camp

                    temp = .8 - (tracker.risk/200.0)
                    for c in team:
                        if c.health > c.get_max("health")*temp and c.mp > c.get_max("mp")*temp and c.vitality > c.get_max("vitality")*temp:
                            continue

                        temp = "Your team needs some rest before they can continue with the exploration."
                        tracker.log(temp)
                        if DEBUG_SE:
                            msg = "{} has finished an exploration scenario. (Needs rest)".format(team.name)
                            se_debug(msg, mode="info")
                        self.env.exit("rest") # need to rest -> got to camping mode

                if self.env.now >= 99:
                    self.env.exit()

        def combat_mobs(self, tracker, mob, opfor_team_size, log):
            # log is the Exploration Log object we add be reports to!
            # Do we really need to pass team size to this method instead of figuring everything out here?
            team = tracker.team
            opfor = Team(name="Enemy Team", max_size=opfor_team_size)

            if DEBUG_SE:
                msg = "{} is stating a battle scenario.".format(team.name)
                se_debug(msg, mode="info")

            # Get a level we'll set the mobs to:
            min_lvl = max(mobs[mob]["min_lvl"], tracker.area.tier*20)
            for i in xrange(opfor_team_size):
                temp = build_mob(id=mob, level=randint(min_lvl, min_lvl+10))
                temp.controller = BE_AI(temp)
                opfor.add(temp)

            for i in team:
                i.controller = BE_AI(i)

            # Logical battle scenario:
            battle = BE_Core(logical=True)
            store.battle = battle # Making battle global... I need to make sure this is not needed.
            battle.teams.append(team)
            battle.teams.append(opfor)
            battle.start_battle()

            # Add the battle report to log!:
            log.battle_log = list(reversed(battle.combat_log))

            # Reset the controllers:
            team.reset_controller()
            opfor.reset_controller()

            # No death below risk 40:
            if tracker.risk > 40 and dice(tracker.risk):
                for member in team:
                    if member in battle.corpses:
                        tracker.flag_red = True
                        tracker.died.append(member)

            for mob in opfor:
                if mob in battle.corpses:
                    tracker.mobs_defeated[mob.id] += 1

            if battle.winner == team:
                log.suffix = "{color=[lawngreen]}Victory{/color}"
                for member in team:
                    if member in battle.corpses:
                        continue
                    member.attack += randrange(3)
                    member.defence + randrange(3)
                    member.agility += randrange(3)
                    member.magic += randrange(3)
                    member.exp += exp_reward(member, opfor)

                temp = "{color=[lawngreen]}Your team won!!{/color}"
                log.add(temp)

                if DEBUG_SE:
                    msg = "{} finished a battle scenario. Result: victory".format(team.name)
                    se_debug(msg, mode="info")

            else: # Defeat here...
                log.suffix = "{color=[red]}Defeat{/color}"
                temp = "{color=[red]}Your team got their asses kicked!!{/color}"
                log.add(temp)

                if DEBUG_SE:
                    msg = "{} finished a battle scenario. Result: defeat".format(team.name)
                    se_debug(msg, mode="info")

        def build_camp(self, tracker):
            # New type of shit, trying to get teams to coop here...
            area = tracker.obj_area
            team = tracker.team
            teams = [t.team for t in area.trackers if t.state == "build camp"]

            if DEBUG_SE:
                msg = "Team {} is setting up basecamp.".format(team.name)
                se_debug(msg, mode="info")

            # TODO: Make sure this is adapted to building skill(s) once we have it!
            build_power = max(1, tracker.ability/20)

            if len(teams) > 1:
                temp = "Teams: {} are setting up basecamp!".format(", ".join([t.name for t in teams]))
            else:
                temp = "Team {} is setting up basecamp!".format(team.name)
            tracker.log(temp)

            while 1:
                if area.camp_build_points_current >= area.camp_build_points_required:
                    # Team done setting up the encampment:
                    temp = "Encampment is finished! Team is moving onto exploration!"
                    area.camp = True
                    tracker.log(temp)
                    self.env.exit()

                area.camp_build_points_current += build_power
                yield self.env.timeout(5) # We build...

                if not self.env.now % 25:
                    temp = "Basecamp is {} complete!".format(area.camp_build_status)
                    tracker.log(temp)

                if self.env.now >= 99:
                    self.env.exit()