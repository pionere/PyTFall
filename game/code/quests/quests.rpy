# Quests:
init -9 python:
    # Utility funcs to alias otherwise long command lines:
    def advance_quest(quest, *args, **kwargs):
        quest = pytfall.world_quests.quest_instance(quest)
        quest.next_stage(*args, **kwargs)

    def finish_quest(quest, *args, **kwargs):
        quest = pytfall.world_quests.quest_instance(quest)
        quest.finish(*args, **kwargs)

    def register_quest(*args, **kwargs):
        """
        Registers a new quest in an init block (and now in labels as well!).
        """
        q = WorldQuest(*args, **kwargs)
        if hasattr(store, "pytfall"):
            wq = pytfall.world_quests.quests
            # FIXME auto start?
        else:
            wq = world_quests
        wq.append(q)
        return q

    class WorldQuestManager(_object):
        """
        Manager for the easy tracking of active, complete, failed and inactive quests.
        """

        def __init__(self, data):
            """
            Creates the manager and copies the pre-existsing quests into itself.
            """
            self.active = list()
            self.complete = list()
            self.failed = list()
            self.squelch = list()
            self.quests = deepcopy(data)

        def activate_quest(self, quest):
            """
            Activates (starts) a quest.
            """
            quest = self.quest_instance(quest)
            if quest in self.quests: self.active.append(quest)
            if quest in self.complete: self.complete.remove(quest)
            if quest in self.failed: self.failed.remove(quest)

        def complete_quest(self, quest):
            """
            Completes a quest.
            """
            quest = self.quest_instance(quest)
            if quest in self.quests: self.complete.append(quest)
            if quest in self.active: self.active.remove(quest)
            if quest in self.failed: self.failed.remove(quest)

        def fail_quest(self, quest):
            """
            Fails a quest.
            """
            quest = self.quest_instance(quest)
            if quest in self.quests: self.failed.append(quest)
            if quest in self.active: self.active.remove(quest)
            if quest in self.complete: self.complete.remove(quest)

        def first_day(self):
            """
            Auto-starts the needed quests on the first day.
            """
            uqp = persistent.use_quest_popups
            persistent.use_quest_popups = False # disable popups
            for i in self.quests:
                if i.auto is not None: i.start()
            persistent.use_quest_popups = uqp

        def quest_instance(self, quest):
            """
            Returns the named quest if it is not already a quest.
            """
            if not isinstance(quest, basestring): return quest
            for i in self.quests:
                if i.name == quest: return i
            return None

        def has_failed(self, quest):
            """Whether a quest has been failed.
            """
            quest = self.quest_instance(quest)
            return quest in self.failed

        def is_active(self, quest):
            """Whether a quest is active.
            """
            quest = self.quest_instance(quest)
            return quest in self.active

        def is_complete(self, quest):
            """Whether a quest is complete.
            """
            quest = self.quest_instance(quest)
            return quest in self.complete

        def is_squelched(self, quest):
            """Whether a quest has been squelched.
            """
            quest = self.quest_instance(quest)
            return quest in self.squelch

        def next_day(self):
            """Fails quests that have no valid events.
            """
            garbage = list()

            # Find incomplete quests with no existing events
            for i in self.active:
                if not i.manual:
                    for j in pytfall.world_events.events_cache:
                        if j.quest == i.name:
                            garbage.append(i)
                            break

            while garbage:
                qe_debug("Garbage Quest found! \"%s\" was failed."%garbage[-1].name, "warning")
                self.fail_quest(garbage.pop())

        def run_quests(self, param=None):
            """Unsquelches all quests so they can report for a new location if needed.
            Definition same as WorldEventsManager.run_quests for convenience.

            param = Optional for mirroring of WorldEventsManager, currently doesn't do anything.
            """
            del self.squelch[:]

        def squelch_quest(self, quest):
            """Squelches a quest so it doesn't provide any more updates.
            """
            quest = self.quest_instance(quest)
            if quest in self.active: self.squelch.append(quest)

        def unsquelch_quest(self, quest):
            """Unsquelches a quest so it can provide updates.
            """
            quest = self.quest_instance(quest)
            if quest in self.squelch: self.squelch.remove(quest)


    class WorldQuest(Flags):
        """
        Class to hold the current status of a quest.
        """
        def __init__(self, name, auto=None, manual=True):
            """
            Creates a new Quest.
            name = The name of the quest. Use to refer to this quest, and shows up in the Quest log.
            auto = Whether to automatically start the quest on day 1.
                Valid auto formats:
                    auto="prompt"
                    auto=("prompt",)
                    auto=("prompt", ["flags"])
                    auto=("prompt", 17)
                    auto=("prompt", "flag")
                    auto=("prompt", ["flags"], 17)
                    auto=("prompt", "flag1", "flag2", "flagN", 17)
                    auto=("prompt", "flag1", "flag2", "flagN")
                Note: 17 = 'to' param

            manual = Whether the quest will be manually updated, instead of by event. Prevents garbage failing.
            """
            super(WorldQuest, self).__init__()

            self.name = name
            self.prompts = list()
            self.stage = 0
            self.auto = auto
            self.manual = manual

        def __str__(self):
            return "Quest(%s)" % self.name

        @property
        def active(self):
            """
            Whether this quest is active.
            """
            return pytfall.world_quests.is_active(self)

        def check(self, stage, strict, *flags):
            """
            Checks whether the quest is at a certain state.
            Used for easy checking through WorldEvent.run_conditions.
            """
            if self.stage < stage: return False
            if strict and self.stage != stage: return False
            for i in flags:
                if i not in self.flags: return False

            return True

        @property
        def complete(self):
            """
            Whether this quest is complete.
            """
            return pytfall.world_quests.is_complete(self)

        def condition(self, stage, strict=False, *flags):
            """
            Builds a condition check string for WorldEvent.run_conditions.
            """
            if flags is not None and len(flags) > 0:
                flags = ", \"" + "\", \"".join(flags) + "\""
            else:
                flags = ""
            return "pytfall.world_quests.quest_instance(\"%s\").check(%s, %s%s)" % (self.name, str(stage), bool(strict), flags)

        @property
        def failed(self):
            """
            Whether this quest has been failed.
            """
            return pytfall.world_quests.has_failed(self)

        def finish(self, prompt, to=None, **kwargs):
            """
            Finishes the quest in menus, labels, etc.
            prompt = Prompt to add to the Quest log.
            flags = List of strings to add to the Quest as flags.
            to = Stage to jump to instead of current+1.
            """
            if not self.complete: pytfall.world_quests.complete_quest(self)

            self.prompts.append(prompt)
            self.flags.update(kwargs)
            if to is None:
                self.stage += 1
            else:
                self.stage = to

            qe_debug("Quest Complete: %s"%self.name)

            if persistent.use_quest_popups:
                if renpy.get_screen("quest_notifications"):
                    renpy.hide_screen("quest_notifications")

                renpy.show_screen("quest_notifications", self.name, "Complete")

                # No squelch, as only works on active quests

        def fail(self, prompt, **kwargs):
            """
            Fails the quest while making a note about it in the quest log.
            prompt = Prompt to add to the Quest log.
            """
            if not self.failed: pytfall.world_quests.fail_quest(self)

            self.prompts.append(prompt)
            self.flags.update(kwargs)

            qe_debug("Quest Failed: %s"%self.name)

            if persistent.use_quest_popups:
                if renpy.get_screen("quest_notifications"):
                    renpy.hide_screen("quest_notifications")

                renpy.show_screen("quest_notifications", self.name, "Failed")

        def next_stage(self, prompt, clear_logs=False, to=None, manual=None, **kwargs):
            """
            Adds a stage to the quest in menus, labels, etc.
            prompt = Prompt to add to the Quest log.
            flags = List of strings to add to the Quest as flags.
            to = Stage to jump to instead of current+1.
            clear_logs = True will clear all previous logs from the quest.
            """
            if not self.active: pytfall.world_quests.activate_quest(self)
            if clear_logs:
                self.prompts = list()

            self.prompts.append(prompt)
            self.flags.update(kwargs)

            if to is None:
                self.stage += 1
            else:
                self.stage = to
            if manual is not None:
                self.manual = manual

            qe_debug("Update Quest: %s to %s"%(self.name, str(self.stage)))

            if persistent.use_quest_popups:
                if renpy.get_screen("quest_notifications"):
                    renpy.hide_screen("quest_notifications")

                if len(self.prompts) == 1:
                    renpy.show_screen("quest_notifications", self.name, "New")

                elif not pytfall.world_quests.is_squelched(self): # TODO squelched?
                    renpy.show_screen("quest_notifications", self.name, "Updated")

                # pytfall.world_quests.squelch_quest(self)

        def start(self):
            """
            Starts a quest using its auto property.
            """
            if not self.active: pytfall.world_quests.activate_quest(self)

            params = self.auto
            if isinstance(params, (tuple,list)):
                if params:
                    # check for auto parameter with int at the end -> the 'to' parameter
                    if isinstance(params[-1], int):
                        to = params[-1]
                        params = params[:-1]
                        # auto parameter with a single int -> prompt is empty
                        if not params:
                            params = [""]
                    else:
                        to = None
                    prompt = params[0]
                    params = params[1:]
                    if params:
                        if len(params) == 1 and isinstance(params[0], (tuple, list)):
                            # auto=("prompt", ["flags"], 17)
                            # auto=("prompt", ["flags"])
                            params = params[0]

                        params = dict([(p, True) for p in params])
                        if to is not None:
                            # auto=("prompt", ["flags"], 17)
                            # auto=("prompt", "flag1", "flag2", "flagN", 17)
                            self.next_stage(prompt, to=to, *params)
                        else:
                            # auto=("prompt", ["flags"])
                            # auto=("prompt", "flag")
                            # auto=("prompt", "flag1", "flag2", "flagN")
                            self.next_stage(prompt, *params)
                    else:
                        if to is not None:
                            # auto=("prompt", 17)
                            self.next_stage(prompt, to=to)
                        else:
                            # auto=("prompt",)
                            self.next_stage(prompt)
                else:
                    # auto=[]
                    self.next_stage("")
            else:
                # auto="prompt"
                self.next_stage(params)

            qe_debug("Auto-Start Quest: %s"%self.name)