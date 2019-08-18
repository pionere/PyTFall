init -1 python:
    class GmCell(_object):
        """
        Simple custom container for girls to be displayed to the player.
        Also responsible for sorting.
        Occupation = condition on which to sort.
        """
        def __init__(self, name, limited_location=False, **kwargs):
            goodoccupations = kwargs.get("goodoccupations", set())
            badoccupations = kwargs.get("badoccupations", set())
            has_tags = kwargs.get("has_tags", set())
            has_no_tags = kwargs.get("has_no_tags", set())
            goodtraits = kwargs.get("goodtraits", set())
            if goodtraits:
                goodtraits = set(traits[t] for t in goodtraits)

            badtraits = kwargs.get("badtraits", set())
            if badtraits:
                badtraits = set(traits[t] for t in badtraits)

            self.name = name
            self.termination_day = day + randint(3, 5)
            self.creation_day = day

            cell_chars = list()
            self.girls = cell_chars
            interactive_chars = set(iam.get_all_girls()) | set(hero.chars)
            possible_chars = [c for c in chars.itervalues() if c not in interactive_chars]

            # Get available characters and check stuff:
            #  filter chars out of city, in jail or active in the arena with too much tier difference
            tier_range = range(hero.tier-1, hero.tier+2)
            choices = [c for c in possible_chars if c.home == pytfall.city and c.location != pytfall.jail and (not c.arena_active or c.tier in tier_range)]
            #  filter by required tags
            if has_tags:
                choices = [c for c in choices if c.has_image(*has_tags, exclude=has_no_tags)]
            #  filter by location
            if limited_location:
                choices = [c for c in choices if c.location == name]
            #  filter by badtraits:
            if badtraits:
                choices = [i for i in choices if not any(trait in badtraits for trait in i.traits)]
            #  filter by badoccupations
            if badoccupations:
                choices = [i for i in choices if not i.occupations.intersection(badoccupations)]

            # Prioritize the choices
            if goodtraits or goodoccupations:
                temp = choices
                choices = []
                conditioned_choices = []
                for c in temp:
                    if c.occupations.intersection(goodoccupations) or any(trait in goodtraits for trait in c.traits):
                        conditioned_choices.append(c)
                    else:
                        choices.append(c)
            else:
                conditioned_choices = choices
                choices = []

            # Select the character with the best disposition+affection:
            if conditioned_choices:
                conditioned_choices.sort(key=lambda x: x.get_stat("disposition") + x.get_stat("affection"))
                if conditioned_choices[-1].get_stat("disposition") or conditioned_choices[-1].get_stat("affection"):
                    cell_chars.append(conditioned_choices.pop())
            elif choices:
                choices.sort(key=lambda x: x.get_stat("disposition") + x.get_stat("affection"))
                if choices[-1].get_stat("disposition") or choices[-1].get_stat("affection"):
                    cell_chars.append(choices.pop())
            else:
                return # no choice at all...

            # the rest is random 
            shuffle(conditioned_choices)
            for c in conditioned_choices:
                cell_chars.append(c)
                if len(cell_chars) == 3:
                    return

            shuffle(choices)
            for c in choices:
                cell_chars.append(c)
                if len(cell_chars) == 3:
                    return

        # and easy access:
        def __len__(self):
            return len(self.girls)

        def __iter__(self):
            return iter(self.girls)

        def __getitem__(self, index):
            return self.girls[index]

        def __nonzero__(self):
            return bool(self.girls)


    class GirlsMeets(InteractionsDecisions, InteractionsResponses, InteractionsHelper):
        """
        Girlsmeets control system, handles all related logic
        """

        # List of modes to use the girl_interactions label with.
        IMG_SIZE = (600, 515) # Img size we automatically use for girlsmeets.
        def __init__(self, data):
            """
            Creates a new GirlsMeets.
            """
            self.world_gossips = WorldGossipsManager(data)

            # Cells:
            self.girlcells = dict()

            # Location Info:
            self.show_girls = False
            self.coords = None # list of positions to show the portraits in the GmCell

            # Current Interaction:
            self.label_cache = ""
            self.reset()

        def reset(self):
            # reset self
            self.mode = None
            #self.label_cache = ""
            self.bg_cache = ""
            self.jump_cache = ""
            self.img_cache = None
            self.char = None
            self.img = None
            # Display flags
            self.see_greeting = True
            self.show_menu = False
            self.show_menu_givegift = False

        # Characters Control:
        def display_girls(self):
            """
            Should simply return a list of girls for display.
            """
            return self.girlcells.get(self.label_cache, list())

        def get_all_girls(self):
            """
            Returns a list of all girls currently in girl_meets.
            """
            l = list()
            for cell in self.girlcells.itervalues():
                l.extend(cell.girls)
            return l

        def remove_girl(self, char):
            """
            Removes a girl from the girl_meets.
            """
            for cell in self.girlcells.itervalues():
                if char in cell:
                    cell.girls.remove(char)

        def next_day(self):
            # Termination:
            self.girlcells = dict((k, v) for k, v in self.girlcells.iteritems() if v.termination_day > day)

        # Image Controls:
        def set_img(self, *args, **kwargs):
            """Sets the image, leaving the image cache untouched.
            """
            self.img = self.char.show(*args, **kwargs)

        def restore_img(self):
            """Restores the image to the cached one.
            """
            self.img = self.img_cache

        def get_image_tags(self):
            img = self.img
            if isinstance(img, basestring):
                pass
            elif isinstance(img, Movie):
                img = img._play
            else: # if instance(img, ImageBase)
                img = img.image.filename
            return tagdb.get_image_tags(img)

        # Interactions/GM Flow Controls:
        def jump(self, label, free=False, allow_unique=True, **kwargs):
            """Jumps to a GMIT label with the most specific name.

            label = The label to jump to.
            free = Whether the interaction is free.
            allow_unique Whether to allow girl.id specific labels.
            kwargs = Holder of the "allow_mode" arguments.
            """
            ls = list()

            # If we are allowed mode specific labels
            if kwargs.pop("allow_" + self.mode, True):
                # If we are allowed unique labels
                if allow_unique:
                    # Add the mode specific girl unique label
                    ls.append("{}_{}_{}".format(self.mode, label, self.char.id))

                # Add the mode specific label
                ls.append("{}_{}".format(self.mode, label))

            # If we are allowed unique labels
            if allow_unique:
                # Add the girl unique label
                ls.append("{}_{}".format(label, self.char.id))

            # Add the generic label
            ls.append("interactions_{}".format(label))

            # If we have labels
            for l in ls:
                # If the label exists
                if renpy.has_label(l):
                    break
            else:
                # Try just the label name...:
                if renpy.has_label(label):
                    l = label
                else:
                    # Notify and stop:
                    gui_debug("Unable to find GM label %s." % label)
                    return

            # If the action costs AP:
            if not free:
                # If we have no more points
                if hero.PP < 25:
                    return PyTGFX.message("You don't have time (Action Points) for that!")
                if not self.char.take_pp(25):
                    return PyTGFX.message("%s doesn't have time (Action Points) for that!" % self.char.pC)

                hero.take_pp(25)

            # Notify and jump
            self.show_menu = False
            self.jump_cache = l
            renpy.jump(l)

        def start(self, mode, char, bg=None, img=None, exit=None):
            """Starts a girl meet scenario.

            mode = The mode to use.
            char = The character to use.
            bg = The background to use. Use to override enter_location function. Set to True to select based on the char image.
            img = The image to use.
            exit = The exit label to use. Overrides enter_location.
            """
            self.mode = mode
            self.char = char

            hs() # Kill the current screen...

            # Routine to get the correct image for this interaction:
            if img is None:
                img = char.get_img_from_cache(str(last_label))
                if img is None:
                    img = char.show("girlmeets", gm_mode=True)
            self.img_cache = self.img = img

            if exit is not None:
                self.label_cache = exit
                if bg is None:
                    bg = exit

            if bg is not None:
                if bg is True:
                    # set bg based on the char image
                    bg = iam.select_char_location(char, self.get_image_tags())
                #else:
                    # direct set of the bg
                self.bg_cache = "bg " + bg

            if hasattr(store, "char"):
                self.prev_char = store.char
            elif hasattr(self, "prev_char"): # FIXME should not be necessary if the end is always called, but this is safer for now
                del self.prev_char
            store.char = char

            if mode == "custom":
                pass
            else:
                jump(mode)

        def start_int(self, char, bg=None, img=None, exit=None, keep_music=True):
            """
            Starts the girlsmeet scenario.
            char = The character to use.
            bg = The background to use. Use to override enter_location function. Set to True to select based on the char image.
            img = The image for the character.
            exit = The exit label to use. Use to override enter_location function.
            keep_music = Whether we need to set the keep_playing_music flag after ending the interaction
            """
            # Music flag:
            if keep_music is True:
                global_flags.set_flag("keep_playing_music")
            friends_disp_check(char)
            if char.has_flag("cnd_interactions_blowoff"):
                if exit is None:
                    exit = last_label
                renpy.call("interactions_blowoff", char=char, exit=exit)

            self.start("girl_interactions", char, bg, img, exit)

        def start_tr(self, char, img=None, exit="char_profile", bg="sex_dungeon_1"):
            """
            Starts the training scenario.
            char = The character to use.
            img = The image for the character.
            exit = The exit label to use. Defaults to "char_profile".
            bg = The background to use. Defaults to "dungeon".
            """
            self.start("girl_trainings", char, bg, img, exit)

        def enter_location(self, coords=None, **kwargs):
            """
            Enters the current location for the GM system.
            """
            label = str(last_label)
            self.label_cache = label
            self.bg_cache = "bg " + label
            self.show_girls = False
            self.coords = coords

            # Creation:
            if label not in self.girlcells:
                cell = GmCell(label, **kwargs)
                if cell.girls: # discard cell if no character found -> try to repopulate later
                    self.girlcells[label] = cell

        def end(self, safe=False):
            """
            Ends the current scenario.
            safe = Whether to prevent the label jump.
            """
            # Reset scene
            hs()

            # restore char
            if hasattr(self, "prev_char"):
                store.char = self.prev_char
                del self.prev_char
            else:
                del store.char

            # reset world-actions (necessary because of the U-Actions...)
            del pytfall.world_actions.locations["girl_interactions"]
            pytfall.world_actions.clear()

            # reset self
            self.reset()

            if not safe:
                renpy.jump(self.label_cache)

    class GMJump(Action):
        """
        Class to handle the jump logic for GM as an action.
        """
        def __init__(self, label, free=False, allow_unique=True, **kwargs):
            """
            Creates a new GMJump.
            label = The label to jump to.
            free = Whether the interaction is free.
            allow_unique = Whether to allow girl-specific labels.
            kwargs = Holder of the "allow_mode" arguments.
            """
            self.label = label
            self.free = free
            self.allow_unique = allow_unique
            self.kwargs = kwargs

        def __call__(self):
            """
            Functions the jump.
            """
            iam.jump(self.label, free=self.free, allow_unique=self.allow_unique, **self.kwargs)
