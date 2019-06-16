init -9 python:
    def get_random_event_image(eventfolder):
        dir = content_path('events')
        if eventfolder in listdirs(dir):
            dir = os.path.join(dir, eventfolder)
            images = [file for file in listfiles(dir) if check_image_extension(file)]
            if images:
                image = os.path.join(dir, choice(images))
                return ProportionalScale(image, config.screen_width, config.screen_height)

    # Utility funcs to alias otherwise long command lines:
    def register_event(*args, **kwargs):
        """
        Registers a new event in an init block (and now in labels as well!).
        """
        event = WorldEvent(*args, **kwargs)
        if hasattr(store, "pytfall"):
            we = pytfall.world_events.events
        else:
            we = world_events
        we.append(event)
        return event

    def kill_event(event):
        pytfall.world_events.kill_event(event)

    class WorldEventsManager(_object):
        """Manager of all events in PyTFall.
        """
        def __init__(self, data):
            """
            Manages the events making sure that everything runs smoothly. Basically a smart list :)
            data = A list of WorldEvent instances.
            """
            self.events = deepcopy(data) # all events
            self.events_cache = list() # events that should be actually checked
            self.label_cache = None

        def event_instance(self, event):
            """
            Returns the named event if it is not already an event.
            """
            if not isinstance(event, basestring): return event
            for i in self.events:
                if i.name == event: return i
            return None

        def kill_event(self, event):
            """
            Stop an event from triggering.
            event_name = The name of the event.
            cached = Whether to also remove cached events.
            """
            event = self.event_instance(event)
            if event in self.events: self.events.remove(event)
            if event in self.events_cache: self.events_cache.remove(event)

        def run_events(self, trigger_type, default=None, cost=0):
            """
            Functions an available event with the given trigger.
            trigger_type = The trigger to proc.
            default = The label to go to if there are no available events.
            cost = The cost of triggering the event.
            """
            if not hero.take_ap(cost):
                renpy.show_screen("message_screen", "Not enough AP left")
                return

            self.label_cache = last_label

            for event in self.events_cache:
                if event.trigger_type == trigger_type and \
                   ("all" in event.locations or last_label in event.locations) and \
                   event.check_conditions() and \
                   event.run_event():
                    return
            if default: renpy.call_in_new_context(default)

        def finish_event(self):
            """
            Finishes the current event.
            """
            jump(self.label_cache)

        def next_day(self):
            """
            Filters events to be triggered and removes the garbage.
            Being called on main screen, NOT during the next day transition.
            """
            self.events_cache = list()

            garbage = list()

            # Prepare the event list:
            for event in self.events:
                # Max runs
                if event.max_runs and event.max_runs <= event.runs:
                    garbage.append(event)
                    continue

                # Priority skip:
                # This also restores the priority if required
                if not event.priority:
                    if event.day_to_restore_priority <= day:
                        event.priority = event.priority_cache
                    else:
                        continue
                    # else: event.priority = event.priority_cache

                # Day range
                if event.end_day <= day:
                    garbage.append(event)
                    continue

                elif event.start_day > day:
                    continue

                # Times per day:
                if event.tpd and not event.resolve_tpd():
                    continue

                # Custom Condition:
                # Could simply check is method exists?
                if event.custom_condition and not event.custom_conditions():
                    continue

                # Simple Conditions:
                if event.simple_conditions and not all(list(bool(renpy.python.py_eval_bytecode(c)) for c in event.simple_conditions)):
                    continue

                # We got to the final part:
                self.events_cache.append(event)

            # Clean-up
            self.events[:] = [e for e in self.events if e not in garbage]

            # And finally, sorting by priority:
            self.events_cache.sort(key=attrgetter("priority"), reverse=True)


    class WorldEvent(Flags):
        """Container for the world event.
        """
        def __init__(self, name, priority=100, restore_priority=5, start_day=1, end_day=float('inf'), max_runs=0,
                    jump=False, screen=False, label=undefined, locations=list(), trigger_type="look_around",
                    times_per_days=(), custom_condition=False, simple_conditions=(), dice=0, run_conditions=(),
                    stop_music=False):
            """
            name = name of the event, will be used as label if label if not specified.
            priority = higher number will ensure higher priority. Should never be set to 0 by a user!
                      (Anything above 0 is fair game. Rate you own events :) )
            restore_priority = how many days should pass until priority is restored after the event is ran
                               0 will ensure that event runs at the same priority until disabled.
            start_day = day to start checking triggers for the event.
            end_day = day to stop checking triggers for the event.

            max_runs = maximum amount of times this event can run until it is removed from the game.
            jump = jumps instead of running in new context.
            screen = will show a screen (bound to self.label) if True, ignored if false
            label = if label doesn't equal name.
            locations = to trigger the event.
            trigger_type = type of interaction that triggers the event, currently we have:
                            - look_around - button
                            - auto - on label entry
                            - custom (custom event trigger)

            times_per_days = maximum amount of times that event may trigger in an amount of days, expects a tuple/list of amount, days.
            custom_condition (Edited condition method) ==> For complex conditioning, inherit from this class and add custom_conditions() method to return True or False
            simple_conditions = container of strings to be evaluated, if all return True, event will be added to list of possible event for the day. If any of those returns false, event will skip until all the conditions are met.
            dice = chance to execute. must be an integer or float between 0 and 100 (check dice function),
                   use run_conditions otherwise. dice has priority over run_conditions
            run_conditions = evaluated before execution of the event, should be a list of strings.
            stop_music = stop the "music" channel when the event is executed
            """
            super(WorldEvent, self).__init__()

            # Names/Label
            self.name = name
            self.jump = jump
            self.screen = screen
            self.label = name if label is undefined else label
            # Prority related
            self.priority = priority
            self.priority_cache = priority
            self.restore_priority = restore_priority
            self.day_to_restore_priority = 0
            # Day range
            self.start_day = start_day
            self.end_day = end_day
            self.tpd = times_per_days
            self.days = list() # list of all days when the event has been executed
            # Locations time:
            self.locations = locations
            self.trigger_type = trigger_type
            # Runs
            self.max_runs = max_runs
            self.runs = 0

            # Conditions to run
            self.custom_condition = custom_condition
            self.simple_conditions = simple_conditions
            self.dice = dice
            self.run_conditions = run_conditions

            # Rest
            self.stop_music = stop_music

        def check_conditions(self):
            """
            Check before the actual run of the event. This should return a boolean.
            """
            if self.tpd:
                if not self.resolve_tpd(): return False

            if self.max_runs:
                if self.runs >= self.max_runs: return False

            if self.dice:
                if not dice(self.dice): return False

            if self.run_conditions:
                if not all(list(bool(renpy.python.py_eval_bytecode(c)) for c in self.run_conditions)): return False

            return True

        def resolve_tpd(self):
            """
            Resolves the amount many times event has been run in given amount of previous days.
            Returns true to run the event.
            """
            range_of_days = range(day-self.tpd[1], day+1)
            matched_days = list()

            for i in self.days[:]:
                if i in range_of_days:
                    matched_days.append(i)
                # and clean-up:
                if i < day-self.tpd[1]: self.days.remove(i)

            return len(matched_days) < self.tpd[0]

        def run_event(self):
            """
            Runs the event after all conditions have been met.
            """
            if self.tpd: self.days.append(day)
            self.runs += 1

            if self.restore_priority:
                self.priority = 0
                self.day_to_restore_priority = day + self.restore_priority

            if not self.label:
                return False # just a background event, no need block other events

            if self.stop_music: renpy.music.stop(channel="music", fadeout=1.0)
            if self.screen:
                renpy.show_screen(self.label)
            elif self.jump:
                jump(self.label)
            else:
                renpy.call_in_new_context(self.label, self)
            return True
