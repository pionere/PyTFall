init -9 python:
    class FG_Object(_object):
        """Dummy class for objects in camps (for now).
        """
        def __init__(self):
            self.pos = (0, 0)   # position on the screen
            self.img = None     # image of the object
            self.name = ""      # name of the object (shown as tooltip)

    # FG Area
    class FG_Area(_object):
        """Dummy class for areas (for now).

        Tracks the progress in SE areas as well as storing their data.
        """
        def __init__(self):
            self.unlocked = False
            self.area = None      # parent area

            # Statistics:
            self.mobs_defeated = dict()
            self.found_items = dict()
            self.chars_captured = 0
            self.cash_earned = 0

        def init(self):
            self.stage = getattr(self, "stage", 0) # For Sorting.
            if self.area:
                # add required field for sub-areas
                self.tier = getattr(self, "tier", 0)   # Difficulty
                self.daily_modifier = getattr(self, "daily_modifier", 0.1)     # modifer when spending the night on the site
                self.maxdays = getattr(self, "maxdays", 15)                    # maximum number of days to spend on site
                self.maxexplored = getattr(self, "maxexplored", 1000)          # the required points to fully explore an area
                self.items_price_limit = getattr(self, "items_price_limit", 0) # limit on the price of items which can be found in the area
                self.cash_limit = getattr(self, "cash_limit", 0)               # limit on the cash to be found on site

                # Traveling to and from: Input is in number of days which is converted to KM units
                # 20KM is what we expect the team to be able to travel in a day.
                # This may be offset through traits and stats/skills.
                self.travel_time = round_int(getattr(self, "travel_time", 0) * 20)

                self.unlocks = getattr(self, "unlocks", dict())# maps which are unlocked from this map
                self.hazard = getattr(self, "hazard", dict())  # possible hazads on site
                self.items = getattr(self, "items", dict())    # possible items to be found
                self.mobs = getattr(self, "mobs", dict())      # possible mobs to encounter
                #self.allowed_objects = ...                    # possible camp objects, set at loading time
                # Special fields for quests, keys are chars or items and values are
                # exploration progress required to get them. Later we might add
                # some complex conditions instead, like fighting mobs.
                self.special_items = getattr(self, "special_items", dict())
                self.special_chars = getattr(self, "special_chars", dict())

                # Chars capture:
                self.chars = getattr(self, "chars", dict())    # id: [explored, chance_per_day]
                self.rchars = getattr(self, "rchars", dict())  # id can be 'any' here, meaning any rChar.

                # the initial state of the area
                self.explored = 0         # the counter to keep track of the exploration
                self.camp_build_points= 0 # the counter to keep track of construction
                self.camp_objects = []    # built objects on site
                self.camp_queue = []      # objects to be built on site

                # Flags for exploration tasks on "area" scope.
                self.building_camp = False
                self.capture_chars = False
                self.use_horses = False
                self.days = 3
                self.risk = 50

                # Trackers exploring the area at any given time, this can be used for easy access!
                self.trackers = []

                # Generated Content:
                self.logs = collections.deque(maxlen=26)

        def get_explored_percentage(self):
            return self.explored * 100 / self.maxexplored

        def dequeue(self, obj):
            if self.camp_queue[0] == obj:
                self.camp_build_points = 0
            self.camp_queue.remove(obj)
            for idx, o in enumerate(self.allowed_objects):
                if o.idx > obj.idx:
                    self.allowed_objects.insert(idx, obj)
                    break
            else:
                self.allowed_objects.append(obj)

        def queue(self, obj):
            self.camp_queue.append(obj)
            self.allowed_objects.remove(obj)

init -6 python: # Guild, Tracker and Log.
    # ======================= (Simulated) Exploration code =====================>>>
    class ExplorationTracker(_object):
        """The class that stores data for an exploration run.

        Adapted from old FG, not sure what we can keep here..."""
        def __init__(self, team, area, guild):
            """Creates a new ExplorationTracker.

            :param team: The team that is exploring.
            :param area: The area that is being explored.
            :param guild: The guild to which this tracker belongs
            """
            super(ExplorationTracker, self).__init__()

            self.team = team
            self.area = area
            self.guild = guild # Guild this tracker was initiated from...

            # copy launch configuration from the area
            self.building_camp = area.building_camp and len(area.camp_queue) != 0
            self.capture_chars = area.capture_chars
            self.risk = area.risk
            self.days = max(area.days, 3) # Days team is expected to be exploring (without travel times)!

            self.day = 1 # Day since start.
            self.days_in_camp = 0 # Simple counter for the amount of days team is spending at camp. This is set back to 0 when team recovers inside of the camping method.

            self.exploration_items = [[i, d] for i, d in area.items.iteritems()]
            # This is the general items that can be found at any exploration location,
            # Limited by price:
            limit = area.items_price_limit
            if limit != 0:
                temp = area.tier
                tmp = [item for item in store.items.itervalues() if
                                          "Exploration" in item.locations and temp >= item.tier and limit >= item.price]  
                self.exploration_items.extend([item.id, item.chance] for item in tmp)

            if guild.has_extension(CartographyLab):
                self.cartography = True

            # We assume that it's never right outside of the city walls:
            self.base_distance = max(area.travel_time, 6)
            self.used_horses = None
            if area.use_horses:
                for u in guild.building.businesses:
                    if u.__class__ == StableBusiness:
                        num = team.mem_count
                        reserved = u.reserved_capacity + num
                        if u.capacity >= reserved:
                            u.reserved_capacity = reserved
                            self.base_distance /= 2
                            self.used_horses = (u, num)
            self.traveled = None # Distance traveled in "KM"...

            # Exploration:
            self.state = "traveling to" # Instead of a bunch of properties, we'll use just the state as string and set it accordingly.
            # Use dicts instead of sets as we want counters:
            self.mobs_defeated = defaultdict(int)
            self.found_items = list()
            self.captured_chars = list()
            self.found_areas = set()
            self.cash = list()
            self.daily_items = None

            self.flag_red = False
            self.flag_green = False
            self.logs = list() # List of all log object we create during this exploration run.
            self.team_charmod = {w: {} for w in team}
            self.died = list()

        def get_team_ability(self):
            # Effectiveness (Ability):
            ability = 0
            # Difficulty is tier of the area explored + 1/10 of the same value / 100 * risk.
            difficulty = self.area.tier*(1 + .001*self.risk)
            log = []
            for char in self.team:
                # Set their exploration capabilities as temp flag
                ability += char.task.effectiveness(char, difficulty, log)
            for l in log:
                self.log(l)
            return ability

        def log(self, txt, name="", suffix="", nd_log=True, ui_log=False, event_object=None):
            if DEBUG_SE:
                msg = "{}: {} at {}\n    {}".format(self.area.name,
                                    self.team.name, self.guild.env.now, txt)
                se_debug(msg)

            obj = ExplorationLog(name, suffix, txt, nd_log, ui_log, event_object)
            self.logs.append(obj)
            return obj

        def logws(self, stat_skill, value, char):
            # Similar to JobsLogger, but here we need to modify the stats as well 
            if stat_skill == "exp":
                char.mod_exp(value)
            elif is_stat(stat_skill):
                value = char.mod_stat(stat_skill, value)
            else: # is_skill
                value = char.mod_skill(stat_skill, 0, value)
            charmod = self.team_charmod[char]
            charmod[stat_skill] = charmod.get(stat_skill, 0) + value

        def finish_exploring(self):
            """
            Build one major report for next day!
            Log all the crap to Area and Main Area!
            Make sure that everything is cleaned up.
            """
            global fg_areas
            global items
            area = self.area
            guild = self.guild
            building = guild.building

            # finish off dead members
            for char in self.died:
                kill_char(char)

            # Settle rewards and update data:
            team = self.team
            if team.mem_count != 0:
                found_items = collections.Counter(self.found_items)
                cash_earned = sum(self.cash)
                if cash_earned:
                    reason = "Exploration Guild"
                    share = cash_earned/4
                    if share:
                        for char in team:
                            if char.autocontrol["Tips"]:
                                char.add_money(share, reason=reason)
                                cash_earned -= share

                                char.mod_stat("disposition", 1 + share/20)
                                char.mod_stat("affection", affection_reward(char, .1, stat="gold"))
                                char.mod_stat("joy", 1 + share/40)

                    hero.add_money(cash_earned, reason=reason)
                    building.fin.log_logical_income(cash_earned, reason)
                inv = getattr(building, "inventory", hero.inventory)
                for i, a in found_items.items():
                    item = items[i]
                    inv.append(item, a)
                for char, data in self.captured_chars:
                    pytfall.jail.add_capture(char) # FIXME special chars?

                chars_captured = len(self.captured_chars)

                # Main and Sub Area Stuff:
                merge_dicts(area.mobs_defeated, self.mobs_defeated)
                merge_dicts(area.found_items, found_items)
                area.cash_earned += cash_earned
                area.chars_captured += chars_captured

                main_area = fg_areas[area.area]
                merge_dicts(main_area.mobs_defeated, self.mobs_defeated)
                merge_dicts(main_area.found_items, found_items)
                main_area.cash_earned += cash_earned
                main_area.chars_captured += chars_captured

                defeated_mobs.update(self.mobs_defeated)

                for key in self.found_areas:
                    a = fg_areas[key]
                    if not a.unlocked:
                        a.unlocked = True
                        area.unlocks.pop(key)
                        temp = "As they arrived back to the Guild, they excitedly report about a new path they found in the wilderness. It leads to %s and might worth to explore!" % a.name
                        temp = set_font_color(temp, "lime")
                        self.log(temp)
                        self.green_flag = True

                ratio = guild.env.now/100.0 
                mod = self.days * self.risk / 100.0 # MAX_RISK
                for char in team:
                    self.logws("exp", exp_reward(char, area.tier, exp_mod=mod*char.setPP/100.0), char) # PP_PER_AP
                    self.logws("constitution", randrange(int(mod)), char)
                    char.PP -= round_int(char.setPP*ratio)
                    if char.PP < 0:
                        char.PP = 0 # TODO should not happen
                    char.set_flag("dnd_back_from_track")
                charmod = self.team_charmod

                # return the borrowed horses
                if self.used_horses is not None:
                    u, num  = self.used_horses
                    u.reserved_capacity -= num
            else:
                # all dead -> just report
                team = None
                # FIXME lost special items? 
                charmod = None

                # scramble the logs
                for l in self.logs:
                    if dice(50):
                        l.txt = [" . . . "]
                self.log("\n . . . \n")

                # pay for the lost horses
                if self.used_horses is not None:
                    u, num  = self.used_horses
                    u.reserved_capacity -= num

                    self.log("\n and the horses are gone as well...")
                    num *= 1000
                    if not hero.take_money(num, "Horses"):
                        hero.fin.property_tax_debt += num
                        self.log("You could not afford to pay for the new horses, so you borrowed money using the building as collateral.")
                    building.fin.log_logical_expense(num, "Horses")

            # Remove Tracker:
            area.trackers.remove(self)
            guild.explorers.remove(self)

            # update area log
            logs = []
            last_checked_idx = -1
            temp = self.logs
            last_idx = len(temp)-1
            for idx, l in enumerate(temp):
                if idx < last_checked_idx or not l.ui_log:
                    continue
                # merge consecutive item entries into a single entry with an ordered dict
                if isinstance(l.event_object, Item):
                    log_items = None
                    next_idx = idx + 1
                    while next_idx <= last_idx:
                        ln = temp[next_idx]
                        if ln.ui_log:
                            obj = ln.event_object
                            if not isinstance(obj, Item):
                                break
                            if log_items is None:
                                log_items = OrderedDict()
                                log_items[l.event_object] = 1
                                l = ExplorationLog("Items", "various", "", False, True, log_items)
                            log_items[obj] = log_items.get(obj, 0) + 1
                        next_idx += 1
                    last_checked_idx = next_idx

                logs.append(l)

            area.logs.extend(logs)

            # Next Day Stuff:
            # Not sure if this is required... we can add log objects and build
            # reports from them in real-time instead of replicating data we already have.
            txt = []

            # We need to create major report for nd to keep track of progress:
            last_checked_idx = -1
            logs = temp #self.logs
            #last_idx = len(temp)-1 
            for idx, l in enumerate(logs):
                if idx < last_checked_idx or not l.nd_log:
                    continue
                # merge consecutive hazard entries
                hazards = l.event_object
                l = l.txt
                if isinstance(hazards, dict):
                    next_idx = idx + 1
                    while next_idx <= last_idx:
                        ln = logs[next_idx]
                        if ln.nd_log:
                            haz = ln.event_object
                            if not isinstance(haz, dict):
                                break
                            for char, effects in haz.iteritems():
                                temp = hazards.get(char, None)
                                if temp is None:
                                    hazards[char] = effects
                                else:
                                    merge_dicts(temp, effects)
                        next_idx += 1
                    last_checked_idx = next_idx

                    if hazards:
                        temp = []
                        for char, effects in hazards.iteritems():  
                            stat_to_color_map = {"health": "orangered", "mp": "dodgerblue", "vitality": "greenyellow"}
                            #tmp = ["".join(["{color=", stat_to_color_map.get(stat, "ivory"), "}", "+" if var < 0 else "", str(-var), "{/color}"]) for stat, var in effects.iteritems()]
                            tmp = [set_font_color("%+g" % (-var), stat_to_color_map.get(stat, "ivory")) for stat, var in effects.iteritems()]
                            tmp = ", ".join(tmp)
                            #tmp = "".join(["{color=pink}", char.name, "{/color} (", tmp, ")"])
                            tmp = "%s (%s)" % (set_font_color(char.name, "pink"), tmp)
                            temp.append(tmp)
                        temp = "".join([itemize(temp), " were" if len(temp) > 1 else " was", " affected."])
                    else:
                        temp = "Nobody was affected."
                    l.append("{color=yellow}Hazardous area!{/color} " + temp)

                txt.append("\n".join(l))

            # Build an image combo for the report:
            img = area.img
            if team is not None:
                img = nd_report_image(img, team, "fighting", exclude=["nude", "sex"])

            evt = NDEvent(type='explorationndreport',
                          img=img,
                          txt=txt,
                          team=team,
                          charmod=charmod,
                          loc=building,
                          green_flag=self.flag_green,
                          red_flag=self.flag_red)
            NextDayEvents.append(evt)

    class ExplorationLog(_object):
        """Stores resulting text and data for SE.
        """
        def __init__(self, name, suffix, txt, nd_log, ui_log, event_object):
            """
            nd_log: Printed in next day report upon arrival.
            ui_log: Only reports worth of ui interface in FG.
            """
            self.name = name # Name of the event, to be used as a name of a button in gui. (maybe...)
            self.suffix = suffix # If there is no special condition in the screen, we add this to the right side of the event button!

            self.nd_log = nd_log
            self.ui_log = ui_log
            self.txt = [] # I figure we use list to store text.
            if txt:
                self.txt.append(txt)

            self.event_object = event_object # battle_log/Item/Char

        def add(self, text):
            # Adds a text to the log.
            self.txt.append(text)

    class ExplorationGuild(TaskBusiness):

        def __init__(self):
            super(ExplorationGuild, self).__init__()

            # Global Values that have effects on the whole business.
            self.teams = list() # List to hold all the teams formed in this guild.
            self.explorers = list() # List to hold all (active) exploring trackers.

            self.teams.append(Team(name="Avengers")) # sample team

            # gui
            self.team_to_launch_index = 0
            self.view_mode = "explore"
            self.selected_exp_area = self.selected_exp_area_sub = None
            self.selected_log_area = self.selected_log_area_sub = None 
            #self.workers initialized later
            #self.guild_teams initialized later

        def can_close(self):
            return not self.explorers

        def load_gui(self):
            # Looks pretty ugly... this might be worth improving upon just for the sake of esthetics.
            _teams = self.idle_teams()
            _chars = [w for w in self.building.all_workers if w != hero and ExplorationTask.willing_work(w) and w.is_available]

            # filter chars
            idle_chars = list(f for t in _teams for f in t)
            _chars = [w for w in _chars if w not in idle_chars]

            # load gui elements
            self.workers = CharsSortingForGui(_chars, 18, occ_filters="Combatant")
            self.guild_teams = PagerGui(_teams, page_size=9)

        def clear_gui(self):
            """Clear GUI-object to free memory and eliminate dead references
                @TODO merge with EG.clear_gui?
            """
            self.workers = None
            self.guild_teams = None

        @staticmethod
        def battle_ready(char):
            """
            Return whether the character is ready to be sent on an exploration run.
            """
            return char.employer is hero and char.is_available

        @staticmethod
        def dragged(drags, drop):
            # Simple func we use to manage drag and drop in team setups and maybe more in the future.
            drag = drags[0]
            x, y = drag.old_position[0], drag.old_position[1]

            if not drop:
                drag.snap(x, y, delay=.2)
                return

            item = drag.drag_name
            src_container = item.get_flag("dnd_drag_container")
            dest_container = drop.drag_name
            if dest_container == src_container:
                drag.snap(x, y, delay=.2)
                return

            if isinstance(dest_container, Team) and dest_container.mem_count >= 3:
                PyTGFX.message("Team cannot have more than three members!")
                drag.snap(x, y, delay=.4)
                return

            dest_container.add(item)
            src_container.remove(item)
            drag.snap(x, y)
            drag.unfocus()
            return True

        # Teams control/sorting/grouping methods:
        def new_team(self, name):
            t = Team(name=name)
            self.add_team(t)
            self.guild_teams.pager_content.append(t)

        def add_team(self, t):
            self.teams.append(t)

        def remove_team(self, t):
            self.teams.remove(t)
            self.guild_teams.pager_content.remove(t)

        def teams_to_launch(self):
            # Returns a list of teams that can be launched on an exploration run.
            # Must have at least one member and NOT already running exploration!
            return [t for t in self.idle_teams() if t and all((self.battle_ready(f) for f in t))]

        def prev_team_to_launch(self):
            index = self.team_to_launch_index
            index -= 1
            if index < 0:
                index = len(self.teams_to_launch())-1 
            self.team_to_launch_index = index

        def next_team_to_launch(self):
            index = self.team_to_launch_index
            index += 1
            if index >= len(self.teams_to_launch()):
                index = 0
            self.team_to_launch_index = index

        def idle_teams(self):
            # Teams avalible for setup in order to set them on exploration runs.
            exploring_teams = [tracker.team for tracker in self.explorers]
            return [t for t in self.teams if t not in exploring_teams]

        def launch_team(self, team, area):
            # self.teams.remove(team) # We prolly do not do this?

            # Setup Explorers:
            for char in team:
                # We effectively remove char from the game so this is prolly ok.
                char.set_task(ExplorationTask)
                for t in hero.teams:
                    if char in t:
                        t.remove(char)

            tracker = ExplorationTracker(team, area, self)
            area.trackers.append(tracker)
            self.explorers.append(tracker)

            self.guild_teams.pager_content.remove(team)

            PyTGFX.message("The team is going to explore this area for %d days!" % area.days)

        # SimPy methods:
        def business_control(self):
            """SimPy business controller.
            """
            # reset usage of objects with limited capacity
            for tracker in self.explorers:
                for o in tracker.area.camp_objects:
                    if hasattr(o, "capacity"):
                        setattr(o, "in_use", 0)

            # add the Eye effect
            if self.has_extension(TheEye):
                for area in store.fg_areas.values():
                    temp = getattr(area, "explored", 0)
                    max = getattr(area, "maxexplored", 0)
                    if temp != 0 and temp == max/2:
                        area.explored += 1

            for tracker in self.explorers:
                self.env.process(self.exploration_controller(tracker))

            yield self.env.timeout(105) # FIXME MAX_DU

            # use the HealingSprings
            if self.has_extension(HealingSprings):
                bathers = [w for team in self.idle_teams() for w in team if w.PP > 0 and w.is_available] 
                if bathers:
                    teammod = {}
                    for w in bathers:
                        charmod = {}
                        #mod_battle_stats(w, .25 * w.PP / w.setPP)
                        mod = .5 * w.PP / w.setPP
                        for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                            value = round_int(w.get_max(stat)*mod) # mod_battle_stats
                            value = w.mod_stat(stat, value)
                            charmod[stat] = value
                        teammod[w] = charmod
                        w.PP = 0

                    txt = choice(["The members of the guild-teams visited the Healing Springs of the %s.",
                                   "The members of the guild-teams took some time off to visit the Onsen in the %s."])
                    txt = txt % self.name

                    job, loc = RestTask, self.building
                    img = nd_report_image(HealingSprings.img, bathers, ("onsen", "no bg"), ("bathing", None), exclude=["nude", "sex"], type="ptls")

                    log = NDEvent(job=job, loc=loc, txt=txt, img=img, charmod=teammod, team=bathers, business=self)
                    NextDayEvents.append(log)

        def exploration_controller(self, tracker):
            # Controls the exploration by setting up proper simpy processes.
            # Prep aliases:
            process = self.env.process

            if DEBUG_SE:
                msg = "Entered exploration controller for {}.".format(tracker.team.name)
                se_debug(msg)

            # Log the day:
            temp = "{color=green}Day: %d{/color} | {color=lightgreen}%s{/color}" % (tracker.day, tracker.area.name)
            tracker.log(temp)

            if tracker.state == "traveling to":
                # The team is not there yet, keep tracking
                result = yield process(self.travel_to(tracker))
                if result == "arrived":
                    tracker.state = None
            elif tracker.state == "traveling back":
                if tracker.traveled is None and tracker.died:
                    died, injured = [], []
                    for d in tracker.died:
                        if dice(tracker.risk) and not dice(d.get_stat("luck")):
                            died.append(d)
                        else:
                            injured.append(d)
                            d.enable_effect("Injured", duration=randint(6, 12))
                            if dice(50):
                                d.apply_trait(traits["Scars"])
                    if injured:
                        temp = "The wounds of {color=red}%s{/color} were not fatal, but they require further medical care." % itemize([d.fullname for d in injured])
                        tracker.log(temp)

                    if died:
                        temp = "{color=red}%s{/color} did not make it through the night. RIP." % itemize([d.fullname for d in died])
                        tracker.log(temp)

                        # release captured chars
                        for char, data in tracker.captured_chars:
                            if isinstance(char, rChar):
                                remove_from_gameworld(char)
                            elif isinstance(char, Char):
                                temp = getattr(char, "dict_id", char.id)
                                data = [data[0], max(1, data[1]/2)] # 'reduced' chance from now on
                                tracker.area.chars[temp] = data
                            else:
                                # special char -> add back to area
                                data = [data[0], max(1, data[1]/2)] # 'reduced' chance from now on
                                tracker.area.special_chars[char] = data

                        if tracker.team.mem_count == len(died):
                            tracker.state = "died off"
                            tracker.traveled = 0
                            tracker.distance = 2*self.travel_distance(tracker) # delay ND report
                            self.env.exit() # They're done...

                    # The remaining team is heading home
                    tracker.died = died        # update deads-list
                    tracker.daily_items = None # lose the daily items # FIXME lost special items?

                # travel back
                result = yield process(self.travel_back(tracker))
                if result == "back2guild":
                    tracker.finish_exploring() # Build the ND report!
                    self.env.exit() # We're done...
            elif tracker.state == "died off":
                tracker.traveled += 20
                if tracker.traveled >= tracker.distance:
                    tracker.finish_exploring() # Build the ND report!
                self.env.exit() # We're done...

            if self.env.now < 75: # do not go on exploring if the day is mostly over
                if tracker.state is None:
                    # just arrived to the location -> decide what to do
                    if tracker.building_camp:
                        tracker.state = "build camp"
                    else:
                        tracker.state = "exploring"
                    tracker.traveled = tracker.day # number of days it took to get to the location

                while 1:
                    if tracker.state == "exploring":
                        result = yield process(self.explore(tracker))
                        if result == "back2camp":
                            break # We're done for today...
                        elif result == "camp2rest":
                            tracker.state = "camping"
                            break # We're done for today and rest is necessary
                        elif result == "rest":
                            tracker.state = "camping"
                    elif tracker.state == "camping":
                        result = yield process(self.camping(tracker))
                        if result == "restored":
                            tracker.state = "exploring"
                    elif tracker.state == "build camp":
                        result = yield process(self.build_camp(tracker))
                        if result == "done":
                            tracker.state = "exploring"
                    if self.env.now >= 99: # FIXME MAX_DU
                        break

            # Go to rest
            result = self.overnight(tracker)
            tracker.day += 1
            # Set the state to traveling back if we're done:
            if result == "go2guild":
                tracker.state = "traveling back"
                tracker.traveled = None # Reset for traveling back.

        @staticmethod
        def travel_distance(tracker):
            # setup the distance. This can be offset by traits and stats in the future. (except when the team dies off)
            return int(tracker.base_distance * (.7 + 0.6*random.random())) # base distance +- 30% 

        def travel_to(self, tracker):
            # Env func that handles the travel to routine.
            team_name = tracker.team.name
            if DEBUG_SE:
                msg = "{} is traveling to {}.".format(team_name, tracker.area.name)
                se_debug(msg)

            # Figure out how far we can travel in steps of 5 DU:
            # Understanding here is that any team can travel 20 KM per day on average.
            time_to_travel = 100 # FIXME MAX_DU
            if tracker.traveled is None:
                # Starting day
                #ExplorationTask.settle_workers_disposition(tracker.team, tracker.log)

                # check the members
                injured, time_mod = False, 1
                for char in tracker.team:
                    if "Injured" in char.effects:
                        injured = True
                    if char.PP != char.setPP:
                        char_mod = char.PP / float(char.setPP)
                        time_mod = min(time_mod, char_mod)

                time_to_travel *= time_mod

                # setup the distance.
                tracker.distance = self.travel_distance(tracker)
                temp = "{color=green}%s{/color} is en route to {color=lightgreen}%s{/color}." % (team_name, tracker.area.name)
                if injured:
                    tracker.distance *= 2
                    temp += " The progression of the team is slowed due to injuries."
                tracker.log(temp)

                tracker.traveled = 0

            while 1:
                yield self.env.timeout(5) # We travel...

                tracker.traveled += 1

                # Team arrived:
                if tracker.traveled >= tracker.distance:
                    if DEBUG_SE:
                        msg = "{} arrived at {} ({}).".format(team_name, tracker.area.name, tracker.area.id)
                        se_debug(msg)

                    temp = "{color=green}%s{/color} arrived at its destination!" % team_name
                    if tracker.day > 1:
                        temp += " It took %d %s to get there." % (tracker.day, plural("day", tracker.day))
                    else:
                        temp += " The trip took less then one day."
                    tracker.log(temp, name="Arrival")
                    self.env.exit("arrived")

                if self.env.now >= time_to_travel: # We couldn't make it there before the days end...
                    temp = "Your team spent the entire day traveling."
                    tracker.log(temp)
                    if DEBUG_SE:
                        se_debug(temp)
                    self.env.exit("not_arrived")

        def travel_back(self, tracker):
            # Env func that handles the travel to routine.
            team_name = tracker.team.name

            if DEBUG_SE:
                msg = "{} is traveling back.".format(team_name)
                se_debug(msg)

            # Figure out how far we can travel in 5 du:
            # Understanding here is that any team can travel 20 KM per day on average.
            if tracker.traveled is None:
                # setup the distance.
                tracker.distance = self.travel_distance(tracker)

                temp = "{color=green}%s{/color} is traveling back home." % team_name
                for char in tracker.team:
                    if "Injured" in char.effects:
                        tracker.distance *= 2
                        temp += " The progression of the team is slowed due to injuries."
                        break
                tracker.log(temp)

                tracker.traveled = 0

            while 1:
                yield self.env.timeout(5) # We travel...

                tracker.traveled += 1

                # Team arrived:
                if tracker.traveled >= tracker.distance:
                    temp = "{color=green}%s{/color} returned to the guild!" % team_name
                    tracker.log(temp, name="Return")
                    self.env.exit("back2guild")

                if self.env.now >= 99: # FIXME MAX_DU We couldn't make it there before the days end...
                    temp = "The team spent the entire day traveling back to the guild."
                    tracker.log(temp)
                    self.env.exit("on the way back")

        def camping(self, tracker):
            """Camping will allow restoration of health/mp/agility and so on. Might be forced on low health.
            """
            team = tracker.team
            auto_equip_counter = 0 # We don't want to run over autoequip on every iteration, two times is enough.

            if DEBUG_SE:
                msg = "{} is Camping. State: {}".format(team.name, tracker.state)
                se_debug(msg)

            if not tracker.days_in_camp:
                temp = "{color=green}%s{/color} set up a camp to get some rest and recover!" % team.name
                tracker.log(temp)

            while 1:
                yield self.env.timeout(5) # We camp...

                # Base stats:
                for c in team:
                    c.mod_stat("health", randint(8, 12)) # BATTLE_STATS
                    c.mod_stat("mp", randint(8, 12))
                    c.mod_stat("vitality", randint(20, 50))

                # Apply items:
                if auto_equip_counter < 2:
                    for explorer in team:
                        l = list()
                        for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                            if explorer.get_stat(stat) <= explorer.get_max(stat)*.8:
                                l.append(stat)
                        if not l:
                            continue
                        cl = []
                        for c in team:
                            cl.extend(explorer.auto_consume(l, inv=c.inventory))
                        if cl:
                            temp = collections.Counter(cl)
                            temp = itemize([alpha(i, a) for i, a in temp.items()])
                            temp = "%s used: {color=lawngreen}%s %s{/color} to recover!" % (explorer.nickname, temp, plural("item", len(cl)))
                            tracker.log(temp)
                    auto_equip_counter += 1

                for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                    for c in team:
                        if c.get_stat(stat) <= c.get_max(stat)*.9:
                            break
                    else:
                        continue
                    break
                else:
                    tracker.days_in_camp = 0
                    temp = "Your team is now rested and ready for more action!"
                    tracker.log(temp)
                    self.env.exit("restored")

                if self.env.now >= 99: # FIXME MAX_DU
                    tracker.days_in_camp += 1

                    if DEBUG_SE:
                        msg = "{} finished Camping. (Day Ended)".format(team.name)
                        se_debug(msg)

                    self.env.exit("still camping")

        def overnight(self, tracker):
            # overnight: More effective heal. Spend the night resting.
            team = tracker.team

            if DEBUG_SE:
                msg = "{} is overnighting. State: {}".format(team.name, tracker.state)
                se_debug(msg)

            if tracker.daily_items is not None and len(tracker.died) < team.mem_count:
                # This basically means that team spent some time on exploring -> create a summary
                found_items = tracker.daily_items
                cash = tracker.daily_cash
                if found_items:
                    temp = collections.Counter(found_items)
                    temp = ", ".join([alpha(i, a) for i, a in temp.items()])
                    temp += " (%s)" % plural("item", found_items) 
                    if cash:
                        tracker.log("During the day the team has found: %s and {color=gold}%d Gold{/color}!" % (temp, cash))
                        tracker.cash.append(cash)
                    else:
                        tracker.log("During the day the team has found: %s!" % temp)
                    tracker.found_items.extend(found_items)
                elif cash:
                    tracker.log("During the day the team has found: {color=gold}%d Gold{/color}!" % cash)
                    tracker.cash.append(cash)
                else:
                    tracker.log("Your team has not found anything of interest...")

                tracker.daily_items = None

                if DEBUG_SE:
                    msg = "{} has finished an exploration scenario. (Day Ended)".format(team.name)
                    se_debug(msg)

            rv = "ok"
            team_name = set_font_color(team.name, "green")
            in_camp = True
            if tracker.state is None:
                temp = "After their journey %s spends the night in the camp!" % team_name
            elif tracker.state == "traveling to":
                temp = "The members of %s are sleeping in their tents en route to the destination!" % team_name
                in_camp = False
            elif tracker.state == "exploring":
                temp = "%s are done with exploring for the day and will now rest and recover!" % team_name
            elif tracker.state == "camping":
                temp = "%s cozied up in their camp for the night!" % team_name
            elif tracker.state == "build camp":
                temp = "The members of %s are taking their well deserved rest from building the camp!" % team_name
            elif tracker.state == "traveling back":
                temp = "%s set up their tents for the overnight en route to the guild!" % team_name
                in_camp = False
            else:
                if DEBUG_SE:
                    msg = "State '{}' unrecognized while team {} is overnighting in camp".format(tracker.state, team.name)
                    se_debug(msg, mode="warn")
                temp = "Tracker of team '%s' is in unrecognized state '%s'" % (tracker.state, team.name)
            if in_camp is True:
                if tracker.died:
                    # some member(s) of the team died -> no rest for the remaining team, if any
                    if len(tracker.died) == team.mem_count:
                        # all members died -> just wait for the dawn to see if their make it
                        tracker.log("The members of %s suffered fatal wounds. It is going to be a miracle if they make it through the night." % team_name)
                    else:
                        # some members are alive -> send them back to the guild
                        tracker.log("The remaining of %s has a sleepless night at the base camp." % team_name)
                    return "go2guild"

                # check if exploration time is over
                if (tracker.day - tracker.traveled + 1) >= tracker.days:
                    rv = "go2guild"
            tracker.log(temp)

            multiplier = tracker.area.daily_modifier * (200 - self.env.now) / 100.0
            if in_camp is True:
                for o in tracker.area.camp_objects:
                    if hasattr(o, "daily_modifier_mod"):
                        if hasattr(o, "capacity"):
                            used_capacity = getattr(o, "in_use", 0) + team.mem_count
                            if o.capacity < used_capacity:
                                continue
                            setattr(o, "in_use", used_capacity)
                        multiplier *= o.daily_modifier_mod

                num_chars = len(tracker.captured_chars)
                if num_chars != 0:
                    capt_multiplier = [1.0] * num_chars

                    for o in tracker.area.camp_objects:
                        if hasattr(o, "capt_daily_modifier_mod"):
                            if hasattr(o, "capacity"):
                                used_capacity = getattr(o, "in_use", 0)
                                limit = min(num_chars, o.capacity - used_capacity)
                                if limit == 0:
                                    continue
                                setattr(o, "in_use", used_capacity + limit)
                            else:
                                limit = num_chars
                            mod = o.capt_daily_modifier_mod
                            for i in range(limit):
                                capt_multiplier[i] *= mod
                    for (c, data), mod in zip(tracker.captured_chars, capt_multiplier):
                        mod -= 1.15 - tracker.area.daily_modifier
                        mod_battle_stats(c, mod)
                        if mod < 0:
                            rv = "go2guild"
            else:
                multiplier *= .5

            for c in team:
                mod_battle_stats(c, multiplier)

            return rv

        def explore(self, tracker):
            """SimPy process that handles the exploration itself.

            Idea is to keep as much of this logic as possible and adapt it to work with SimPy...
            """
            team = tracker.team
            area = tracker.area
            risk = tracker.risk

            if tracker.daily_items is None:
                # first run during the day
                if DEBUG_SE:
                    msg = "{} is starting an exploration scenario.".format(team.name)
                    se_debug(msg)

                temp = "{color=green}%s{/color} is exploring {color=lightgreen}%s{/color}!" % (team.name, area.name)
                tracker.log(temp)

                tracker.daily_items = list()
                tracker.daily_cash = 0
                tracker.daily_mobs = 0

                # Effectiveness (Ability):
                ability = tracker.get_team_ability()
                # convert to reward multiplier
                ability = ability*risk*.0001           # (0-200)*(1-3) * (0-100) / 10000.0 -> 0 - 6.0
                ability += (tracker.day-tracker.traveled)*.2 #  + (0-15) / 5.0                   -> 3.0 - 9.0
                # Max cash to be found this day:
                tracker.max_cash = int(area.cash_limit*ability)

                # Get the max number of items that can be found in one day:
                max_items = round_int(ability)
                if DEBUG_SE:
                    msg = "Max Items: {}, Cash: {} to be found on Day: {}!".format(max_items, tracker.max_cash, tracker.day)
                    se_debug(msg)
                # Let's run the expensive item calculations once and just give
                # Items as we explore. This just figures what items to give.
                tracker.chosen_items = weighted_list(tracker.exploration_items, max_items)
                tracker.max_items = max_items
            else:
                if DEBUG_SE:
                    msg = "{} is continuing the exploration.".format(team.name)
                    se_debug(msg)

            while 1:
                yield self.env.timeout(5) # We'll go with 5 du per one iteration of "exploration loop".

                # record the exploration, unlock new maps
                if dice(5):
                    if area.explored < area.maxexplored:
                        mod = randint(6, 10)
                        if getattr(tracker, "cartography", False):
                            mod = mod * 3 / 2
                        area.explored = min(area.maxexplored, area.explored + mod)
                        ep = area.get_explored_percentage()
                        for key, value in area.unlocks.items():
                            if value <= ep and not fg_areas[key].unlocked:
                                tracker.found_areas.add(key)
                    for char in team:
                        tracker.logws("exploration", 1, char)

                # Hazzard:
                if area.hazard:
                    temp = dict()
                    for char in team:
                        tmp = dict()
                        for stat, value in area.hazard.items():
                            # value, because we calculated effects on daily base in the past...
                            var = value/20
                            val = value-(20*var)
                            if val != 0:
                                if val < 0:
                                    val = -val
                                if dice(val*5):
                                    var += 1 if value >= 0 else -1 
                            if var != 0:
                                if stat == "health" and var >= char.get_stat("health"):
                                    tracker.flag_red = True
                                    tracker.died.append(char)
                                char.mod_stat(stat, -var)
                                tmp[stat] = var
                        if tmp:
                            temp[char] = tmp
                    tracker.log(None, event_object=temp) # text is prepared when the exploration is finished

                    if tracker.died:
                        temp = "Your team is no longer complete. This concludes the exploration for the team."
                        tracker.log(temp)
                        if DEBUG_SE:
                            msg = "{} has finished an exploration scenario. (Lost a member due to hazards)".format(team.name)
                            se_debug(msg)
                        self.env.exit("back2camp") # member died -> back to camp

                    check_team = True # initiate a check at the end of the loop

                # Items:
                # Handle the special items (must be done here so it doesn't collide with other teams)
                special_items = area.special_items
                if special_items:
                    ep = area.get_explored_percentage()
                    special_items = [item for item, explored in special_items.items() if ep >= explored]

                if tracker.chosen_items or special_items:
                    chance = self.env.now
                    if chance < 50:
                        chance /= 5
                    elif chance > 80:
                        chance = 100
                    chance = chance * tracker.max_items / 9

                    if dice(chance):
                        if special_items:
                            item = special_items.pop()
                            del area.special_items[item]
                            temp = "Found %s (special item)!" % aoran(item)
                            temp = set_font_color(temp, "orange")
                        else:
                            item = tracker.chosen_items.pop()
                            temp = "Found %s (item)!" % aoran(item)
                            temp = set_font_color(temp, "lawngreen")

                        tracker.daily_items.append(item)
                        item = store.items[item]
                        tracker.log(temp, "Item", ui_log=True, suffix=item.type, event_object=item)
                        if DEBUG_SE:
                            msg = "{} Found item {}!".format(team.name, item.id)
                            se_debug(msg)

                # Cash:
                if tracker.max_cash > tracker.daily_cash and dice(risk/5):
                    give = max(1, int(tracker.max_cash * random.random() * .5))
                    tracker.daily_cash += give

                    temp = "Found {color=gold}%d Gold{/color}!" % give
                    tracker.log(temp)
                    if DEBUG_SE:
                        msg = "{} Found {} Gold!".format(team.name, give)
                        se_debug(msg)

                #  =================================================>>>
                if tracker.capture_chars and not self.env.now % 10:
                    # Special Chars:
                    ep = area.get_explored_percentage()
                    for char, data in area.special_chars.items():
                        explored, chance = data
                        if ep >= explored and dice(chance*.1):
                            del(area.special_chars[char])
                            tracker.captured_chars.append((char, data))

                            temp = "Your team has captured a 'special' character: %s!" % char.name
                            temp = set_font_color(temp, "orange")
                            tracker.log(temp, "Capture", ui_log=True, suffix=char.name, event_object=char)
                            if DEBUG_SE:
                                msg = "{} has finished an exploration scenario. (Captured a special char {})".format(team.name, char.id)
                                se_debug(msg)

                            self.env.exit("back2camp")

                    # uChars (also from Area):
                    for id, data in area.chars.items():
                        explored, chance = data
                        if ep >= explored and dice(chance*.1):
                            del(area.chars[id])

                            char = store.chars[id]
                            tracker.captured_chars.append((char, data))
                            temp = "Your team has captured {color=pink}%s{/color}!" % char.name
                            temp = set_font_color(temp, "lawngreen")
                            tracker.log(temp, "Capture", ui_log=True, suffix=char.name, event_object=char)
                            if DEBUG_SE:
                                msg = "{} has finished an exploration scenario. (Captured a uChar {})".format(team.name, char.id)
                                se_debug(msg)

                            self.env.exit("back2camp")
                    # rChars:
                    for id, data in area.rchars.items():
                        explored, chance = data
                        if ep >= explored and dice(chance*.1):
                            # Get tier:
                            tier = area.tier
                            if tier == 0:
                                tier = .5
                            tier = random.uniform(tier*.8, tier*1.2)

                            if id == "any":
                                id = None
                            char = build_rc(id=id, tier=tier, set_status="slave", set_locations=pytfall.streets, give_civilian_items=True)
                            tracker.captured_chars.append((char, data))
                            temp = "Your team has captured %s!" % char.name
                            temp = set_font_color(temp, "lawngreen")
                            tracker.log(temp, "Capture", ui_log=True, suffix=char.race, event_object=char)
                            if DEBUG_SE:
                                msg = "{} has finished an exploration scenario. (Captured an rChar {})".format(team.name, char.id)
                                se_debug(msg)

                            self.env.exit("back2camp")

                if area.mobs:
                    # The expected number of encounters per day is increased by one after every 25 point of risk,
                    # but never fight anyone with risk lower than 25..
                    encounter_chance = dice((risk-25) / 5.0) # 100 * ((risk-25)/25.0) / (day_length / iteration_DU)
                    if encounter_chance and tracker.daily_mobs < 4:  # no more than 4 encounter per day to allow whole day exploration with risk of 100
                        tracker.daily_mobs += 1

                        mob = choice(area.mobs)

                        enemy_team_size = randint(2, 4)

                        temp = "Your team was attacked by %d %s!" % (enemy_team_size, plural(mob, enemy_team_size))
                        temp = set_font_color(temp, "crimson")
                        log = tracker.log(temp, "Combat!", ui_log=True)
                        self.combat_mobs(tracker, mob, enemy_team_size, log)

                        check_team = True # initiate a check at the end of the loop

                if "check_team" in locals():
                    if tracker.died:
                        temp = "Your team is no longer complete. This concludes the exploration for the team."
                        tracker.log(temp)
                        if DEBUG_SE:
                            msg = "{} has finished an exploration scenario. (Lost a member)".format(team.name)
                            se_debug(msg)
                        self.env.exit("back2camp") # member died -> back to camp

                    # check if the team needs rest
                    needs_rest = False
                    temp = .8 - (risk/200.0)
                    for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                        for c in team:
                            if c.get_stat(stat) < c.get_max(stat)*temp:
                                needs_rest = True
                                break
                        else:
                            continue
                        break

                    if tracker.daily_mobs >= risk/20:
                        temp = "Your team decided to go back to the camp to avoid further {color=red}risk{/color}."
                        tracker.log(temp)
                        if DEBUG_SE:
                            msg = "{} has finished an exploration scenario. (Fought too much)".format(team.name)
                            se_debug(msg)
                        self.env.exit("camp2rest" if needs_rest else "back2camp") # too much risk -> back to camp

                    if needs_rest:
                        temp = "The team needs some rest before they can continue with the exploration."
                        tracker.log(temp)
                        if DEBUG_SE:
                            msg = "{} has finished an exploration scenario. (Needs rest)".format(team.name)
                            se_debug(msg)
                        self.env.exit("rest") # need to rest -> go to camping mode

                    del check_team

                if self.env.now >= 99: # FIXME MAX_DU
                    self.env.exit()

        def combat_mobs(self, tracker, mob, enemy_team_size, log):
            # log is the Exploration Log object we add be reports to!
            # Do we really need to pass team size to this method instead of figuring everything out here?
            team = tracker.team
            enemy_team = Team(name="Enemy Team")

            if DEBUG_SE:
                msg = "{} is stating a battle scenario.".format(team.name)
                se_debug(msg)

            # Get a level we'll set the mobs to:
            lvl = (tracker.area.tier+1)*20
            for i in xrange(enemy_team_size):
                temp = build_mob(id=mob, level=lvl)
                enemy_team.add(temp)


            # Logical battle scenario:
            battle = run_auto_be(team, enemy_team)

            # Add the battle report to log!:
            log.event_object = list(battle.combat_log)

            if dice(tracker.risk):
                for member in team:
                    if member in battle.corpses:
                        tracker.flag_red = True
                        tracker.died.append(member)

                        if DEBUG_SE:
                            msg = "{} died during a battle scenario.".format(member.name)
                            se_debug(msg)

            if battle.winner == team:
                for mob in enemy_team:
                    tracker.mobs_defeated[mob.id] += 1

                log.suffix = set_font_color("Victory", "lawngreen")
                for char in team:
                    if char in battle.corpses:
                        continue
                    if dice(10):
                        tracker.logws("attack", 1, char)
                    if dice(10):
                        tracker.logws("defence", 1, char)
                    if dice(10):
                        tracker.logws("magic", 1, char)
                    if dice(10):
                        tracker.logws("agility", 1, char)
                    if dice(10):
                        tracker.logws("constitution", 1, char)
                    tracker.logws("exp", exp_reward(char, enemy_team), char)

                log.add(set_font_color("Your team won!!", "lawngreen"))

                if DEBUG_SE:
                    msg = "{} finished a battle scenario. Result: victory".format(team.name)
                    se_debug(msg)

            else: # Defeat here...
                log.suffix = set_font_color("Defeat", "red")
                log.add(set_font_color("Your team got their asses kicked!!", "red"))

                if DEBUG_SE:
                    msg = "{} finished a battle scenario. Result: defeat".format(team.name)
                    se_debug(msg)

        def build_camp(self, tracker):
            # New type of shit, trying to get teams to coop here...
            area = tracker.area
            team = tracker.team
            teams = [t.team for t in area.trackers if t.state == "build camp"]

            if DEBUG_SE:
                msg = "Team %s is building the basecamp." % team.name
                se_debug(msg)

            # TODO: Make sure this is adapted to building skill(s) once we have it!
            # Effectiveness (Ability):
            build_power = max(1, tracker.get_team_ability())

            name = itemize([t.gui_name for t in teams])
            temp = "The basecamp is being built by the %s: %s!" % (plural("team", len(teams)), name)
            tracker.log(temp)

            while 1:
                yield self.env.timeout(5) # We build...

                if len(area.camp_queue) == 0:
                    # Nothing to build -> done
                    temp = "Team is moving onto exploration!"
                    tracker.log(temp)
                    self.env.exit("done")

                area.camp_build_points += build_power

                task = area.camp_queue[0]
                if area.camp_build_points >= task.cost:
                    # Finished with the first task
                    del area.camp_queue[0]
                    for idx, o in enumerate(area.camp_objects):
                        if o.type == task.type:
                            area.camp_objects[idx] = task
                            break
                    else:
                        area.camp_objects.append(task)

                    temp = "%s %s finished building a %s." % (plural("Team", len(teams)), name, task.name)
                    tracker.log(temp)

                    area.camp_build_points = 0
                    if len(area.camp_queue) == 0:
                        # Nothing more to build -> done
                        temp = "Team is moving onto exploration!"
                        tracker.log(temp)
                        self.env.exit("done")

                elif not self.env.now % 25:
                    temp = "%s is %d%% complete!" % (task.name, area.camp_build_points * 100 / task.cost)
                    tracker.log(temp)

                if self.env.now >= 99: # FIXME MAX_DU
                    self.env.exit()