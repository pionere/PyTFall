# Characters classes and methods:
init -9 python:
    class STATIC_CHAR():
        __slots__ = ("STATS", "SKILLS", "GEN_OCCS", "SLAVE_GEN_OCCS", "STATUS", "ORIGIN", "MOOD_TAGS", "UNIQUE_SAY_SCREEN_PORTRAIT_OVERLAYS", "BASE_UPKEEP", "BASE_WAGES", "TRAININGS", "FIXED_MAX", "DEGRADING_STATS", "SEX_SKILLS", "PREFS")
        STATS =  {"charisma", "constitution", "joy", "character", "fame", "reputation",
                  "health", "mood", "disposition", "affection", "vitality", "intelligence",
                  "luck", "attack", "magic", "defence", "agility", "mp"}
        SKILLS = {"vaginal", "anal", "oral", "sex", "strip", "service",
                      "refinement", "group", "bdsm", "dancing",
                      "bartending", "cleaning", "waiting", "management",
                      "exploration", "teaching", "swimming", "fishing",
                      "security", "riding"}
        GEN_OCCS = ["SIW", "Combatant", "Server", "Specialist"]
        SLAVE_GEN_OCCS = ["SIW", "Server"]
        STATUS = ["slave", "free"]
        ORIGIN = ["Alkion", "PyTFall", "Crossgate"]

        MOOD_TAGS = {"angry", "confident", "defiant", "ecstatic", "happy",
                         "indifferent", "provocative", "sad", "scared", "shy",
                         "tired", "uncertain"}
        UNIQUE_SAY_SCREEN_PORTRAIT_OVERLAYS = ["zoom_fast", "zoom_slow", "test_case"]
        BASE_UPKEEP = 2.5 # Per tier, conditioned in get_upkeep method.
        BASE_WAGES = {"SIW": 20, "Combatant": 30, "Server": 15, "Specialist": 40 }
        TRAININGS = {"Abby Training": "Abby the Witch",
                     "Aine Training": "Aine",
                     "Xeona Training": "Xeona"}
        FIXED_MAX = {"joy":200, "mood":1000, "disposition":1000, "affection":1000, "vitality":200, "luck":50, "fame":100, "reputation":100}
        DEGRADING_STATS = ["constitution", "fame", "reputation", "intelligence", "attack", "magic", "defence", "agility"]
        SEX_SKILLS = {"vaginal", "anal", "oral", "sex", "group", "bdsm"}
        PREFS = {"gold", "fame", "reputation", "arena_rep", "charisma", "constitution", # "character",
                  "intelligence", "attack", "magic", "defence", "agility", "luck",
                  "vaginal", "anal", "oral", "sex", "group", "bdsm"}

    ###### Character Classes ######
    class PytCharacter(Flags, Tier, JobsLogger, Pronouns):
        """Base Character class for PyTFall.
        """
        def __init__(self, details):
            super(PytCharacter, self).__init__()
            self.img = None
            self.portrait = None
            self.gold = 0

            self.name = None
            self.fullname = None
            self.nickname = None

            self._mc_ref = None # This is how characters refer to MC (hero). May depend on case per case basis and is accessed through obj.mc_ref property.
            self.height = "average"
            self.gender = "female"
            self.origin = None
            self.status = "free"
            #self.personality = None
            #self.race = None
            #self.gents = None
            #self.body = None
            #self.full_race = None

            self.basePP = 300   # PP_PER_AP
            #self.setPP = 1     # This is set to the PP calculated for that day.
            #self.PP = 0        # Remaining PP (partial AP) for the day (100PP == 1AP) PP_PER_AP - initialized later

            Tier.__init__(self)

            # Stat support Dicts:
            stats = {
                'charisma': [5, 0, 50, 60, 0, 0, 0],           # means [stat, min, max, lvl_max, imod, imin, imax]
                'constitution': [5, 0, 50, 60, 0, 0, 0],
                'joy': [50, 0, 100, 200, 0, 0, 0],             # FIXED_MAX
                'character': [5, 0, 50, 60, 0, 0, 0],
                'reputation': [0, 0, 100, 100, 0, 0, 0],       # FIXED_MAX
                'health': [100, 0, 100, 200, 0, 0, 0],
                'fame': [0, 0, 100, 100, 0, 0, 0],             # FIXED_MAX
                'mood': [0, 0, 1000, 1000, 0, 0, 0],           # FIXED_MAX not used...
                'disposition': [0, -1000, 1000, 1000, 0, 0, 0],# FIXED_MAX
                'affection': [0, -1000, 1000, 1000, 0, 0, 0],  # FIXED_MAX
                'vitality': [100, 0, 100, 200, 0, 0, 0],       # FIXED_MAX
                'intelligence': [5, 0, 50, 60, 0, 0, 0],

                'luck': [0, -50, 50, 50, 0, 0, 0],             # FIXED_MAX

                'attack': [5, 0, 50, 60, 0, 0, 0],
                'magic': [5, 0, 50, 60, 0, 0, 0],
                'defence': [5, 0, 50, 60, 0, 0, 0],
                'agility': [5, 0, 50, 60, 0, 0, 0],
                'mp': [30, 0, 30, 50, 0, 0, 0]
            }
            self.stats = Stats(self, stats)

            # Traits:
            self.upkeep = 0 # Required for some traits...

            self.traits = Traits(self)
            self.resist = SmartTracker(self, be_skill=False)  # A set of any effects this character resists. Usually it's stuff like poison and other status effects.

            if details:
                # Locations and actions, most are properties with setters and getters.
                #                    Home        Workplace         Job  Action  Task        Location 
                #    -    "fighter"  city            -               -            -             -    
                #   char   "free"    city            -               -            -        [loc/jail]
                #   char   "slave"    sm             -               -            -         [ra/jail]
                # hero:            b/streets         b               j            -          [jail]  
                #   char - "free"   b/city           b               j       [r/ar/s/x]      [jail]  
                #   char - "slave" b/streets         b               j       [r/ar/s/x]     [ra/jail]
                #                                                                        
                #      *loc: a place in the city      *b: building      *ra: runaway     
                #      *r: rest    *ar: auto rest    *s: study    *x: exploration
                self.location = None   # Present Location.
                self._workplace = None # Place of work.
                self._home = None      # Living location.
                self._job = None       # Permanent job to work in a building
                self._task = None      # Temporary task (Rest/Study/Exploration)

                # Relationships:
                self.friends = set()
                self.lovers = set()

                # Arena related:
                self.fighting_days = list() # Days of fights taking place
                self.arena_willing = None # Indicates the desire to fight in the Arena
                self.arena_permit = False # Has a permit to fight in main events of the arena.
                self.arena_active = False # Indicates that character fights at Arena at the time.
                self.arena_rep = 0 # Arena reputation

                # Items
                self.inventory = Inventory(15)
                eqslots = {
                    "head": None,
                    "body": None,
                    "cape": None,
                    "feet": None,
                    "amulet": None,
                    "wrist": None,
                    "weapon": None,
                    "smallweapon": None,
                    "ring": None,
                    "ring1": None,
                    "ring2": None,
                    "misc": None,
                    "consumable": None,
                }
                self.eqslots = eqslots
                self.eqsave = [] # saved equipment states
                self.consblock = dict()  # Dict (Counter) of blocked consumable items.
                self.constemp = dict()  # Dict of consumables with temp effects.
                self.miscitems = dict()  # Counter for misc items.
                self.miscblock = list()  # List of blocked misc items.
                self.last_known_aeq_purpose = None # We don't want to aeq needlessly, it's an expensive operation.
                # List to keep track of temporary effect
                # consumables that failed to activate on cmax **We are not using this or at least I can't find this in code!
                # self.maxouts = list()

                # For workers (like we may not want to run this for mobs :) )
                JobsLogger.__init__(self)

                # Effects assets:
                self.effects = _dict()

                # Image cache
                self.clear_img_cache()

                # Say style properties:
                self.say_style = {"color": "ivory"}
                self.say = None # Speaker...

            # BE fields
            self.controller = None # by default the player is in control in BE
            self.front_row = 1 # 1 for front row and 0 for back row.

            self.attack_skills = SmartTracker(self)  # Attack Skills
            self.magic_skills = SmartTracker(self)  # Magic Skills
            self.default_attack_skill = battle_skills["Fist Attack"] # This can be overwritten on character creation!

            # We add Neutral element here to all classes to be replaced later:
            #self.apply_trait(traits["Neutral"])

        # Post init
        def init(self):
            # Normalize character
            if not self.name:
                self.name = self.id
            if not self.fullname:
                self.fullname = self.name
            if not self.nickname:
                self.nickname = self.name
            # make sure there is at least one elemental trait
            self.apply_trait(traits["Neutral"])

            # Dark's Full Race Flag:
            if hasattr(self, "race") and not hasattr(self, "full_race"):
                self.full_race = str(self.race)

            # Always init the tiers:
            #self.recalculate_tier()

            # add Character:
            #if not self.say:
            #    self.update_sayer()

            if not self.origin:
                self.origin = choice(STATIC_CHAR.ORIGIN)

            # AP restore:
            self.restore_ap()

        # Money:
        def take_money(self, value, reason="Other"):
            if hasattr(self, "fin"):
                return self.fin.take_money(value, reason)
            else:
                if value <= self.gold:
                    self.gold -= value
                    return True
                else:
                    return False

        def add_money(self, value, reason="Other"):
            if hasattr(self, "fin"):
                self.fin.add_money(value, reason)
            else:
                self.gold += value

        def update_sayer(self):
            self.say = Character(self.nickname, show_two_window=True, show_side_image=self, **self.say_style)
            self.say_screen_portrait = DynamicDisplayable(self._portrait)
            self.say_screen_portrait_overlay_mode = None

        # Properties:
        @property
        def is_available(self):
            # False if we cannot reach the character.
            if self.home == pytfall.afterlife:
                return False
            if self.action == ExplorationTask:
                return False
            if self.location in (pytfall.jail, pytfall.ra):
                return False
            return True

        @property
        def basetraits(self):
            return self.traits.basetraits

        @property
        def gen_occs(self):
            # returns a list of general occupation from Base Traits only.
            return self.traits.gen_occs

        @property
        def occupations(self):
            """
            Formerly "occupation", will return a set of jobs that a worker may be willing to do based of her basetraits.
            Not decided if this should be strings, Trait objects of a combination of both.
            """
            allowed = set()
            for t in self.traits.basetraits:
                allowed.add(t)
                allowed.update(t.occupations)
            return allowed

        @property
        def action(self):
            return self._task if self._task is not None else self._job

        @property
        def job(self):
            return self._job

        def set_job(self, job):
            self._job = job

        @property
        def task(self):
            return self._task

        def set_task(self, task, *args):
            if self._task == StudyingTask:
                pytfall.school.remove_student(self)
            self._task = task
            if task == StudyingTask:
                pytfall.school.add_student(self, args[0])

        @property
        def workplace(self):
            return self._workplace
        def reset_workplace_action(self):
            # reset task and job
            self.set_task(None)
            self._job = None

            wp = self._workplace
            if isinstance(wp, Building):
                wp.all_workers.remove(self)
            self._workplace = None
        def mod_workplace(self, value):
            wp = self._workplace
            if wp == value:
                return
            if self._job not in getattr(value, "jobs", []):
                self._job = None
            if isinstance(wp, Building):
                wp.all_workers.remove(self)
            self._workplace = value
            if isinstance(value, Building):
                value.all_workers.append(self)

        @property
        def home(self):
            return self._home
        @home.setter
        def home(self, value):
            """Home setter needs to add/remove actors from their living place.

            Checking for vacancies should be handled at functions that are setting
            homes.
            """
            if isinstance(self._home, HabitableLocation):
                self._home.remove_inhabitant(self)
            if isinstance(value, HabitableLocation):
                value.add_inhabitant(self)
            self._home = value

        def get_valid_jobs(self):
            """Returns a list of jobs available at the current workplace that the character might be willing to do.

            Returns an empty list if no jobs is available for the character.
            """
            workplace = self._workplace
            if not isinstance(workplace, Building):
                return []
            return [job for job in workplace.jobs if job.willing_work(self)]

        def get_willing_jobs(self):
            """Returns a list of jobs the character is willing to do.
            """
            return [job for job in simple_jobs if hasattr(job, "willing_work") and job.willing_work(self)]

        def get_wanted_jobs(self):
            """Returns a list of jobs the character want to do.
            """
            return [job for job in simple_jobs if hasattr(job, "want_work") and job.want_work(self)]

        def settle_effects(self, key, value):
            if hasattr(self, "effects"):
                effects = self.effects

                if key == 'disposition':
                    if 'Insecure' in effects:
                        if value >= 5:
                            self.stats._mod_base_stat("joy", 1)
                        elif value <= -5:
                            self.stats._mod_base_stat("joy", -1)
                    if 'Introvert' in effects:
                        value = round_int(value*.8)
                    elif 'Extrovert' in effects:
                        value = round_int(value*1.2)
                    if 'Loyal' in effects and value < 0: # works together with other traits
                        value = round_int(value*.8)
                elif key == 'joy':
                    if 'Impressible' in effects:
                        value = round_int(value*1.5)
                    elif 'Calm' in effects:
                        value = round_int(value*.5)
            return value

        def mod_stat(self, stat, value):
            value = self.settle_effects(stat, value)
            return self.stats._mod_base_stat(stat, value)
        def gfx_mod_stat(self, stat, value):
            value = self.settle_effects(stat, value)
            value = self.stats._mod_base_stat(stat, value)
            if value != 0:
                gfx_overlay.mod_stat(stat, value, self)

        # direct setter to ignore effects and everything
        def set_stat(self, stat, value):
            value -= self.stats._get_stat(stat)
            self.stats._mod_base_stat(stat, value)

        def get_stat(self, stat):
            return self.stats._get_stat(stat)

        def mod_skill(self, skill, at, value):
            return self.stats._mod_raw_skill(skill, at, value)
        def gfx_mod_skill(self, skill, at, value):
            value = self.stats._mod_raw_skill(skill, at, value)
            if value != 0:
                gfx_overlay.mod_stat(skill, value, self)

        def get_max(self, stat):
            return self.stats.get_max(stat)

        def get_skill(self, skill):
            return self.stats.get_skill(skill)

        @property
        def elements(self):
            return [e for e in self.traits if e.elemental]

        @property
        def exp(self):
            return self.stats.exp

        def mod_exp(self, value):
            self.stats.mod_exp(value)
        def gfx_mod_exp(self, value):
            if value == 0:
                return
            gfx_overlay.mod_stat("exp", value, self)
            self.stats.mod_exp(value)

        @property
        def level(self):
            return self.stats.level
        @property
        def goal(self):
            return self.stats.goal

        # -------------------------------------------------------------------------------->
        # Show to mimic chars method behavior:
        def get_sprite_size(self, tag="vnsprite"):
            # First, lets get correct sprites:
            if tag == "battle_sprite":
                if self.height == "average":
                    resize = (200, 180)
                elif self.height == "tall":
                    resize = (200, 200)
                elif self.height == "short":
                    resize = (200, 150)
                else:
                    char_debug("Unknown height setting for %s" % self.id)
                    resize = (200, 180)
            elif tag == "vnsprite":
                if self.height == "average":
                    resize = (1000, 520)
                elif self.height == "tall":
                    resize = (1000, 600)
                elif self.height == "short":
                    resize = (1000, 400)
                else:
                    char_debug("Unknown height setting for %s" % self.id)
                    resize = (1000, 500)
            else:
                raise Exception("get_sprite_size got unknown type for resizing!")
            return resize

        ### Displaying images:
        @property
        def path_to_imgfolder(self):
            if isinstance(self, rChar):
                return rchars[self.id]["_path_to_imgfolder"]
            else:
                return self._path_to_imgfolder

        def _portrait(self, st, at):
            if self.has_flag("fixed_portrait"):
                return self.flag("fixed_portrait"), None
            else:
                return self.show("portrait", self.get_mood_tag(), type="first_default", add_mood=False, cache=True, resize=(120, 120)), None

        def override_portrait(self, *args, **kwargs):
            kwargs["resize"] = kwargs.get("resize", (120, 120))
            kwargs["cache"] = kwargs.get("cache", True)
            # if we have the needed portrait, we just show it
            if self.has_image(*args, **kwargs):
                self.set_flag("fixed_portrait", self.show(*args, **kwargs))
                return
            # if not... then we replace some portraits with similar ones
            mood = None
            if "confident" in args: 
                if self.has_image("portrait", "happy"):
                    mood = "happy"
                elif self.has_image("portrait", "indifferent"):
                    mood = "indifferent"
            elif "suggestive" in args:
                if self.has_image("portrait", "shy"):
                    mood = "shy"
                elif self.has_image("portrait", "happy"):
                    mood = "happy"
            elif "ecstatic" in args:
                if self.has_image("portrait", "happy"):
                    mood = "happy"
                elif self.has_image("portrait", "shy"):
                    mood = "shy"
            elif "shy" in args:
                if self.has_image("portrait", "uncertain"):
                    mood = "uncertain"
            elif "uncertain" in args:
                if self.has_image("portrait", "shy"):
                    mood = "shy"
            else: # most portraits will be replaced by indifferent
                if self.has_image("portrait", "indifferent"):
                    mood = "indifferent"
            if mood is not None:
                self.set_flag("fixed_portrait", self.show("portrait", mood, **kwargs))

        def show_portrait_overlay(self, s, mode="normal"):
            self.say_screen_portrait_overlay_mode = s

            if not s in STATIC_CHAR.UNIQUE_SAY_SCREEN_PORTRAIT_OVERLAYS:
                interactions_portraits_overlay.change(s, mode)

        def hide_portrait_overlay(self):
            interactions_portraits_overlay.change("default")
            self.say_screen_portrait_overlay_mode = None

        def restore_portrait(self):
            self.say_screen_portrait_overlay_mode = None
            self.del_flag("fixed_portrait")

        def get_mood_tag(self):
            """
            This should return a tag that describe characters mood.
            We do not have a proper mood flag system at the moment so this is currently determined by joy and
            should be improved in the future.
            """
            # tags = list()
            # if self.fatigue < 50:
                # return "tired"
            # if self.get_stat("health") < 15:
                # return "hurt"
            if self.get_stat("joy") > 75:
                return "happy"
            elif self.get_stat("joy") > 40:
                return "indifferent"
            else:
                return "sad"

        def select_image(self, *tags, **kwargs):
            '''Returns the path to an image with the supplied tags or "".
            '''
            tags = list(tags)
            tags.append(self.id)
            exclude = kwargs.get("exclude", None)

            # search for images
            imgset = tagdb.get_imgset_with_all_tags(tags)
            if exclude:
                imgset = tagdb.remove_excluded_images(imgset, exclude)

            # randomly select an image
            if imgset:
                return choice(tuple(imgset))
            else:
                return ""

        def has_image(self, *tags, **kwargs):
            """
            Returns True if image is found.
            exclude k/w argument (to exclude undesired tags) is expected to be a list.
            """
            tags = list(tags)
            tags.append(self.id)
            exclude = kwargs.get("exclude", None)

            # search for images
            imgset = tagdb.get_imgset_with_all_tags(tags)
            if exclude:
                imgset = tagdb.remove_excluded_images(imgset, exclude)

            return bool(imgset)

        def show(self, *tags, **kwargs):
            '''Returns an image with the supplied tags.

            Under normal type of images lookup (default):
            First tag is considered to be most important.
            If no image with all tags is found,
            game will look for a combination of first and any other tag from second to last.

            Valid keyword arguments:
                resize = (maxwidth, maxheight)
                    Both dimensions are required
                default = any object (recommended: a renpy image)
                    If default is set and no image with the supplied tags could
                    be found, the value of default is returned and a warning is
                    printed to "devlog.txt".
                cache = load image/tags to cache (can be used in screens language directly)
                type = type of image lookup order (normal by default)
                types:
                     - normal = normal search behavior, try all tags first, then first tag + one of each tags taken from the end of taglist
                     - any = will try to find an image with any of the tags chosen at random
                     - first_default = will use first tag as a default instead of a profile and only than switch to profile
                     - reduce = try all tags first, if that fails, pop the last tag and try without it. Repeat until no tags remain and fall back to profile or default.
                add_mood = Automatically adds proper mood tag. This will not work if a mood tag was specified on request OR this is set to False
                gm_mode = overwrite to add nude/not nude logic for GMs pictures no matter how and where we get them
            '''
            resize = kwargs.get("resize", None)
            cache = kwargs.get("cache", False)
            label_cache = kwargs.get("label_cache", False)
            exclude = kwargs.get("exclude", None)
            type = kwargs.get("type", "normal")
            default = kwargs.get("default", None)
            gm_mode = kwargs.get("gm_mode", False)

            if gm_mode:
                if check_lovers(self, hero) or "Exhibitionist" in self.traits:
                    if dice(40):
                        if not "nude" in tags:
                            tags += ("nude",)
                        if not "revealing" in tags:
                            tags += ("revealing",)
                else:
                    if not exclude:
                        exclude = ["nude"]
                    elif not "nude" in exclude:
                        exclude.append("nude")


            # Direct image request:
            if "-" in tags[0]:
                _path = os.path.join(self.path_to_imgfolder, tags[0])
                if not renpy.loadable(_path):
                    _path = IMG_NOT_FOUND_PATH
                return _path if resize is None else ProportionalScale(_path, *resize)

            # Mood will never be checked in auto-mode when that is not sensible
            add_mood = kwargs.get("add_mood", True)
            if not STATIC_CHAR.MOOD_TAGS.isdisjoint(set(tags)):
                add_mood = False

            pure_tags = list(tags)
            tags = list(tags)
            if add_mood:
                mood_tag = self.get_mood_tag()
                tags.append(mood_tag)

            if label_cache:
                for entry in self.label_cache:
                    if entry[1] == last_label and entry[0] == tags:
                        entry = entry[2]
                        return entry if resize is None else ProportionalScale(entry, *resize)

            if cache:
                for entry in self.cache:
                    if entry[0] == tags:
                        entry = entry[1]
                        return entry if resize is None else ProportionalScale(entry, *resize)

            imgpath = ""
            if type in ["normal", "first_default", "reduce"]:
                imgpath = self.select_image(*tags, exclude=exclude)
                if not imgpath and add_mood:
                    imgpath = self.select_image(*pure_tags, exclude=exclude)

                if not imgpath and len(pure_tags) > 1:
                    if type in ["normal", "first_default"]:
                        main_tag = None
                        for tag in pure_tags:
                            if main_tag is None:
                                main_tag = tag
                                continue

                            # Try with the mood first:
                            if add_mood:
                                imgpath = self.select_image(main_tag, tag, mood_tag, exclude=exclude)
                            # Without mood
                            if not imgpath:
                                imgpath = self.select_image(main_tag, tag, exclude=exclude)
                            if imgpath:
                                break

                        if type == "first_default" and not imgpath: # In case we need to try first tag as default (instead of profile/default) and failed to find a path.
                            if add_mood:
                                imgpath = self.select_image(main_tag, mood_tag, exclude=exclude)
                            if not imgpath:
                                imgpath = self.select_image(main_tag, exclude=exclude)

                    elif type == "reduce":
                        _tags = pure_tags[:]
                        while not imgpath:
                            _tags.pop()
                           
                            # Do not try with empty tags TODO why not? 
                            if not _tags:
                                break
                            # Try with mood first:
                            if add_mood:
                                imgpath = self.select_image(mood_tag, *_tags, exclude=exclude)
                            if not imgpath:
                                imgpath = self.select_image(*_tags, exclude=exclude)


            elif type == "any":
                _tags = pure_tags[:] 
                shuffle(_tags)
                # Try with the mood first:
                if add_mood:
                    for tag in _tags:
                        imgpath = self.select_image(tag, mood_tag, exclude=exclude)
                        if imgpath:
                            break
                # Then try 'any' behavior without the mood:
                if not imgpath:
                    for tag in _tags:
                        imgpath = self.select_image(tag, exclude=exclude)
                        if imgpath:
                            break

            if not imgpath:
                char_debug("could not find image with tags %s" % sorted(tags))
                if default is None:
                    # New rule (Default Battle Sprites):
                    if "battle_sprite" in pure_tags:
                        force_battle_sprite = True
                    else:
                        if add_mood:
                            imgpath = self.select_image('profile', mood_tag)
                        if not imgpath:
                            imgpath = self.select_image('profile')
                else:
                    return default

            # If we got here without being able to find an image ("profile" lookup failed is the only option):
            if "force_battle_sprite" in locals(): # New rule (Default Battle Sprites):
                imgpath = os.path.join("content", "gfx", "images", "default_%s_battle_sprite.png" % self.gender)
            elif not imgpath:
                char_debug(str("Total failure while looking for image with %s tags!!!" % tags))
                imgpath = IMG_NOT_FOUND_PATH
            else: # We have an image, time to convert it to full path.
                imgpath = os.path.join(self.path_to_imgfolder, imgpath)

            # FIXME regardless of type ???
            if label_cache:
                self.label_cache.append([tags, last_label, imgpath])

            if cache:
                self.cache.append([tags, imgpath])

            return imgpath if resize is None else ProportionalScale(imgpath, *resize)

        def get_img_from_cache(self, label):
            """
            Returns imgpath!!! from cache based on the label provided.
            """
            for entry in self.label_cache:
                if entry[1] == label:
                    return entry[2]

            return ""

        def get_tags_from_cache(self, label):
            """
            Returns tags from cache based on the label provided.
            """
            for entry in self.tags_cache:
                if entry[0] == label:
                    return entry[1]
            
            entry = [label, []]
            self.tags_cache.append(entry)
            return entry[1]

        def clear_img_cache(self):
            self.cache = list()
            self.label_cache = list()
            self.tags_cache = list()

        def get_vnsprite(self, mood=None):
            """
            Returns VN sprite based on characters height.
            Useful for random events that use NV sprites, heigth in unique events can be set manually.
            ***This is mirrored in galleries testmode, this method is not actually used.
            """
            if mood:
                return self.show("vnsprite", mood, resize=self.get_sprite_size())
            else:
                return self.show("vnsprite", resize=self.get_sprite_size())

        # AP + Training ------------------------------------------------------------->
        def restore_ap(self):
            pp = self.basePP
            base = 60
            c = self.get_stat("constitution")
            while c >= base:
                pp += 100
                base *= 2

            self.setPP = pp

            self.PP = pp

        def has_ap(self, value=1):
            return self.PP >= value*100 # PP_PER_AP

        def take_ap(self, value):
            """
            Removes AP of the amount of value and returns True.
            Returns False if there is not enough Action points.
            This one is useful for game events.
            """
            value *= 100 # PP_PER_AP
            if self.PP < value:
                return False
            self.PP -= value
            return True

        def take_pp(self, value):
            if self.PP < value:
                return False
            self.PP -= value
            return True

        @property
        def ap_pp(self):
            pp = self.PP
            ap = pp/100 # PP_PER_AP
            pp %= 100
            return ap, pp

        # Logging and updating daily stats change on next day:
        def log_stats(self):
            # Devnote: It is possible to mod this as stats change
            # Could be messier to code though...
            self.stats.log = shallowcopy(self.stats.stats)
            self.stats.log["exp"] = self.exp
            self.stats.log["level"] = self.level
            for skill in STATIC_CHAR.SKILLS:
                self.stats.log[skill] = self.stats.get_skill(skill)

        # Items/Equipment related, Inventory is assumed!
        def eq_items(self):
            """Returns a list of all equiped items."""
            if hasattr(self, "eqslots"):
                return self.eqslots.values()
            else:
                return []

        def add_item(self, item, amount=1):
            self.inventory.append(item, amount=amount)

        def remove_item(self, item, amount=1):
            self.inventory.remove(item, amount=amount)

        #def remove_all_items(self):
        #    self.inventory.clear()
        #    TODO eqlots?

        def equip(self, item, remove=True, aeq_mode=False): # Equips the item
            """
            Equips an item to a corresponding slot or consumes it.
            remove: Removes from the inventory (Should be False if item is equipped from directly from a foreign inventory)
            aeq_mode: If we came here because of 'AI' auto equipment function or through players actions.
            **Note that the remove is only applicable when dealing with consumables, game will not expect any other kind of an item.
            """
            if isinstance(item, list):
                for it in item:
                    self.equip(it, remove, aeq_mode)
                return

            # This is a temporary check, to make sure nothing goes wrong:
            # Code checks during the equip method should make sure that the unique items never make it this far:
            if item.unique and item.unique != self.id:
                raise Exception("A character attempted to equip a unique item that was not meant for him/her. \
                                   Character: %s/%s, Item:%s/%s" % self.id, self.__class__, item.id, item.unique)

            temp = self.gender
            if getattr(item, "gender", temp) != temp:
                raise Exception("A character attempted to equip an item that was not meant for him/her gender. \
                                   Character: %s/%s/%s, Item:%s/%s" % self.id, self.__class__, temp, item.id, item.gender)

            slot = item.slot
            eqslots = self.eqslots
            if slot not in eqslots:
                raise Exception("A character attempted to equip on a wrong slot for a character. \
                                   Character: %s/%s, Item:%s/%s" % self.id, self.__class__, item.id, slot)

            if slot == 'consumable':
                if item in self.consblock:
                    return

                if item.cblock:
                    self.consblock[item] = item.cblock
                if item.ctemp:
                    self.constemp[item] = item.ctemp
                if remove: # Needs to be infront of effect application for jumping items.
                    self.inventory.remove(item)
                self.apply_item_effects(item)
                return
            # AEQ considerations:
            # Basically we manually mess with inventory and have
            #  no way of knowing what was done to it.
            if not aeq_mode:
                self.last_known_aeq_purpose = None

            if slot == 'misc':
                if item in self.miscblock:
                    return

                curr_item = eqslots['misc']
                if curr_item: # Unequip if equipped.
                    self.inventory.append(curr_item)
            elif slot == "ring":
                if not eqslots["ring"]:
                    slot = "ring"
                elif not eqslots["ring1"]:
                    slot = "ring1"
                elif not eqslots["ring2"]:
                    slot = "ring2"
                else:
                    self.remove_item_effects(eqslots["ring"])
                    self.inventory.append(eqslots["ring"])
                    eqslots["ring"] = eqslots["ring1"]
                    eqslots["ring1"] = eqslots["ring2"]
                    slot = "ring2"
                self.apply_item_effects(item)
            else:
                # Any other slot:
                curr_item = eqslots[slot]
                if curr_item: # If there is any item equipped:
                    self.remove_item_effects(curr_item) # Remove equipped item effects
                    self.inventory.append(curr_item) # Add unequipped item back to inventory
                self.apply_item_effects(item) # Apply item effects
            # Assign new item to the slot
            eqslots[slot] = item
            # Remove item from the inventory
            if remove:
                self.inventory.remove(item)

        def unequip(self, item=None, slot=None, aeq_mode=False):
            '''
            Unequip the item or slot. Consumables can not be unequipped.
            '''
            # AEQ considerations:
            # Basically we manually mess with inventory and have
            # no way of knowing what was done to it.
            if slot is None:
                slot = item.slot
                if slot == "ring":
                    if self.eqslots["ring"] == item:
                        slot = "ring"
                    elif self.eqslots["ring1"] == item:
                        slot = "ring1"
                    elif self.eqslots["ring2"] == item:
                        slot = "ring2"
                    else:
                        raise Exception("Error while unequiping a ring!")
            elif item is None:
                item = self.eqslots[slot]
                if not item:
                    return

            if not aeq_mode:
                self.last_known_aeq_purpose = None

            if slot != "misc":
                self.remove_item_effects(item)

            self.eqslots[slot] = None
            self.inventory.append(item)

        def auto_equip(self, purpose):
            """
            This method will try to auto-equip items for some purpose!
            :param purpose: the purpose to equip for
            """
            purpose = self.guess_aeq_purpose(purpose)
            if DEBUG_AUTO_ITEM:
                aeq_debug("Auto Equipping for -- {}".format(purpose))
            self.last_known_aeq_purpose = purpose

            # Prepare data:
            inv = self.inventory

            # Go over all slots and unequip items:
            for s in EQUIP_SLOTS:
                if s == "ring":
                    for r in ["ring", "ring1", "ring2"]:
                        self.unequip(slot=r, aeq_mode=True)
                else:
                    self.unequip(slot=s, aeq_mode=True)

            # select relevant items from the inventory
            base_purpose = STATIC_ITEM.AEQ_PURPOSES[purpose]
            fighting = base_purpose.get("fighting")
            target_stats = base_purpose.get("target_stats")
            target_skills = base_purpose.get("target_skills")
            base_purpose = base_purpose.get("base_purpose")

            picks = eval_inventory(self, inv, EQUIP_SLOTS, base_purpose)

            # traits that may influence the item selection process
            upto_skill_limit = False
            for t in self.traits:
                t = t.id
                # a clumsy or bad eyesighted person may cause select items not in target stat/skill
                if t == "Bad Eyesight" or t == "Clumsy":
                    t = choice(self.stats.stats.keys())
                    if t not in target_stats:
                        target_stats = target_stats.copy()
                        target_stats[t] = 50
                    t = choice(self.stats.skills.keys())
                    if t not in target_skills:
                        target_skills = target_skills.copy()
                        target_skills[t] = 50
                # a stupid person may also select items regardless of target stats
                elif t == "Stupid":
                    target_stats = {s: 50 for s in self.stats.stats}
                elif t == "Smart":
                    upto_skill_limit = True

            returns = list() # We return this list with all items used during the method.

            rings_to_equip = 3
            while 1:
                weighted = self.stats.weight_items(picks, target_stats, target_skills, fighting, upto_skill_limit)

                # Select the best item
                best, limit = None, 0
                for _weight, item in weighted:
                    #_weight = sum(_weight)
                    if _weight > limit:
                        best = item
                        limit = _weight
                if best is None:
                    break

                # Actually equip the item
                inv.remove(best)
                self.equip(best, remove=False, aeq_mode=True)
                if DEBUG_AUTO_ITEM:
                    aeq_debug("     --> %s equipped %s to %s.", best.id, self.name, best.slot)
                returns.append(best.id)

                slot = best.slot
                if slot == "ring":
                    rings_to_equip -= 1
                    if rings_to_equip != 0:
                        continue
                picks = [pick for pick in picks if pick.slot != slot]

            return returns

        def auto_consume(self, target_stats, inv=None):
            """
            :param target_stats: expects a list of stats to pick the item
            :param inv: inventory to draw from.
            """

            # Prepare data:
            if inv is None:
                inv = self.inventory

            base_purpose = set()
            base_purpose.add("Any")
            base_purpose.update(bt.id for bt in self.traits.basetraits)
            base_purpose.update(str(t) for t in self.occupations)

            picks = eval_inventory(self, inv, ["consumable"], base_purpose)

            # traits that may influence the item selection process
            intelligence = 80
            for trait in self.traits:
                trait = trait.id
                # a clumsy or bad eyesighted person may cause select items not in target stat/skill
                if trait == "Bad Eyesight" or trait == "Clumsy":
                    intelligence = 50
                # a stupid person may also select items regardless of target stats
                elif trait == "Stupid":
                    intelligence = 10
                elif traits == "Smart":
                    intelligence = 100

            returns = list() # We return this list with all items used during the method.
            while 1:
                weighted = self.stats.weight_for_consume(picks, target_stats)
                if not weighted:
                    break

                if dice(intelligence):
                    # Select the best item
                    best, limit = None, 0
                    for _weight, item in weighted:
                        #_weight = sum(_weight)
                        if _weight > limit:
                            best = item
                            limit = _weight
                else:
                    # select randomly
                    best = choice(weighted)[1]

                # Actually consume the item
                inv.remove(best)
                self.equip(best, remove=False, aeq_mode=True)
                returns.append(best.id)

                if best not in inv:
                    picks.remove(best)

            return returns

        def guess_aeq_purpose(self, hint=None):
            """
            "Fighting": Generic purpose for combat.

            Other Options are:
             'Combat'
             'Barbarian'
             'Shooter'
             'Battle Mage'
             'Mage'

             'Casual'
             'Slave'

             'Striptease'
             'Sex'

             'Manager'
             'Service' (Maid)
             """

            if hint in STATIC_ITEM.AEQ_PURPOSES:
                return hint

            bt = self.traits.basetraits
            purpose = None # Needs to be defaulted to something.
            if hint == "Fighting":
                for t in bt:
                    if "Combatant" in t.occupations:
                        t = t.id
                        if t == "Healer":
                            t = "Mage"
                        elif t not in ["Shooter", "Mage"]:
                            t = "Barbarian"
                        if purpose is None:
                            purpose = t
                        elif purpose != t:
                            if t != "Shooter" and purpose != "Shooter":
                                purpose = "Battle Mage"
                            else:
                                purpose = "Shooter"
                if purpose is None:
                    purpose = "Barbarian"
            else: # We just guess...
                for t in bt:
                    t = STATIC_ITEM.TRAIT_TO_AEQ_PURPOSE[t.id]
                    if purpose is None:
                        purpose = t
                    elif purpose != t:
                        for p in ["Manager", "Service", "Striptease", "Bartender", "Sex", "Shooter"]:
                            if p == purpose:
                                break
                            if p == t:
                                purpose = t
                                break
                        else:
                            purpose = "Battle Mage"
            return purpose

        def auto_buy(self, amount=1, slots=None, purpose=None,
                     equip=False, container=None, check_money=True,
                     smart_ownership_limit=True):
            """Gives items a char, usually by 'buying' those,
            from the container that host all items that can be
            sold in PyTFall.

            amount: how many items to buy (used as a total instead of slots).
            slots: what slots to shop for, if None equipment slots and
                consumable will be used together with amount argument.
                Otherwise expects a dict of slot: amount.
            equip: Equip the items after buying them, if true we equip whatever
                we buy, if set to purpose (Casual, Barbarian, etc.), we auto_equip
                for that purpose.
            container: Container with items or Inventory to shop from. If None
                we use.
            smart_ownership_limit: Limit the total amount of item char can buy.
                if char has this amount or more of that item:
                    3 of the same rings max.
                    1 per any eq_slot.
                    5 cons items max.
                item will not be considered for purchase.

            Simplify!

            - Add items class_prefs and Casual.
            - Maybe merge with give_tiered_items somehow!
            """
            if container is None: # Pick the container we usually shop from:
                container = store.all_auto_buy_items
            if slots is None:
                # add slots with reasonable limits
                slots = {s: 2 for s in store.EQUIP_SLOTS}
                slots["ring"] = 5
                slots["consumable"] = 20
            else:
                amount = 0
                for a in slots.values():
                    amount += a

            if amount == 0:
                return []

            # Create dict gather data, we gather slot: ([30, 50], item) types:
            curr_equipped_items = self.eqslots.copy()
            # Go over all slots and unequip items:
            for s in slots:
                if s == "ring":
                    for r in ["ring", "ring1", "ring2"]:
                        self.unequip(slot=r, aeq_mode=True)
                elif s != "consumable":
                    self.unequip(slot=s, aeq_mode=True)

            if purpose is None: # Let's see if we can get a purpose from last known auto equip purpose:
                purpose = self.guess_aeq_purpose(self.last_known_aeq_purpose)

            base_purpose = STATIC_ITEM.AEQ_PURPOSES[purpose]
            fighting = base_purpose.get("fighting")
            target_stats = base_purpose.get("target_stats")
            target_skills = base_purpose.get("target_skills")
            base_purpose = base_purpose.get("base_purpose")

            picks = eval_inventory(self, container, slots, base_purpose)
            picks = self.stats.weight_items(picks, target_stats, target_skills, fighting, False)

            # filter the weighted items
            ignore_items = set()
            slot_limit = dict()
            if smart_ownership_limit is True:
                owned_slots = {s for s in slots if s not in ["ring", "misc", "consumable"]}
                owned_picks = eval_inventory(self, self.inventory, owned_slots, base_purpose)
                owned_picks = self.stats.weight_items(owned_picks, target_stats, target_skills, fighting, False)

                for _weight, item in owned_picks:
                    #_weight = sum(_weight)
                    slot = item.slot
                    if _weight > slot_limit.get(slot, 0):
                        limit = _weight
                        slot_limit[slot] = limit # TODO might want to add a multiplier like 80%

                for item, count in self.inventory.items.iteritems():
                    slot = item.slot
                    if slot == "consumable" and item.type != "scroll":
                        if count < 5:
                            continue
                    elif slot == "ring":
                        if count < 3:
                            continue
                    ignore_items.add(item)

            selected = []
            for _weight, item in picks:
                if item in ignore_items:
                    continue

                #_weight = sum(_weight)
                slot = item.slot
                if _weight > slot_limit.get(slot, 0):
                    selected.append([_weight, slot, item])

            # sort and select the best
            selected.sort(key=itemgetter(0), reverse=True)
            #  List of items we return in case we need to report what happened in this method to player.
            rv = []
            do_equip = False
            for w, slot, item in selected:
                if not (slots[slot] and dice(item.chance)):
                    continue
                if (not check_money) or self.take_money(item.price, reason="Items"):
                    rv.append(item)

                    self.inventory.append(item)

                    if slot == "consumable":
                        if equip and item.type == "scroll":
                            # TODO check for self.autoequip?
                            self.equip(item, True)
                        #else: TODO extend with other items which should be consumed right away (e.g. Leprechaun Pills)
                    else:
                        do_equip = True

                    slots[slot] -= 1
                    amount -= 1
                    if amount == 0:
                        break

            if equip and do_equip:
                self.auto_equip(purpose)
            else:
                # Re-equip the original items:
                self.eqslots = curr_equipped_items
                for slot, item in curr_equipped_items.iteritems():
                    if not item:
                        continue
                    if slot.startswith("ring"):
                        slot = "ring"
                    if slot in slots:
                        if slot != "misc":
                            self.apply_item_effects(item) # Apply item effects
                        self.inventory.remove(item) # Remove item from the inventory

            return rv

        def load_equip(self, eqsave, silent=False):
            # load equipment from save, if possible
            ordered = OrderedDict(sorted(self.eqslots.items()))

            for slot, current_item in ordered.iteritems():
                desired_item = eqsave[slot]
                if current_item == desired_item:
                    continue

                # rings can be on other fingers. swapping them is allowed in any case
                if slot == "ring":

                    # if the wanted ring is on the next finger, or the next finger requires current ring, swap
                    if self.eqslots["ring1"] == desired_item or eqsave["ring1"] == current_item:
                        (self.eqslots["ring1"], self.eqslots[slot]) = (self.eqslots[slot], self.eqslots["ring1"])

                        current_item = self.eqslots[slot]
                        if current_item == desired_item:
                            continue

                if slot == "ring" or slot == "ring1":

                    if self.eqslots["ring2"] == desired_item or eqsave["ring2"] == current_item:
                        (self.eqslots["ring2"], self.eqslots[slot]) = (self.eqslots[slot], self.eqslots["ring2"])

                        current_item = self.eqslots[slot]
                        if current_item == desired_item:
                            continue

                # if we have something equipped, see if we're allowed to unequip
                if current_item:
                    if equipment_access(self, item=current_item, silent=True, unequip=True):
                        self.unequip(item=current_item, slot=slot)
                    else:
                        continue

                if desired_item:
                    # if we want something else and have it in inventory..
                    if not self.inventory[desired_item]:
                        continue

                    # ..see if we're allowed to equip what we want
                    if equipment_access(self, item=desired_item, silent=True):
                        equip_item(item=desired_item, char=self, silent=silent)

        # Applies Item Effects:
        def apply_item_effects(self, item):
            """Deals with applying items effects on characters.

            :param item: the effects of the item to be applied
            """
            slot = item.slot
            # check if the effects are permanent
            true_add = slot == "misc" or (slot == "consumable" and not item.ctemp)

            # Attacks/Magic -------------------------------------------------->
            # Attack Skills:
            if item.attacks is not None:
                attack_skills = self.attack_skills
                for battle_skill in item.attacks:
                    attack_skills.append(battle_skill, true_add)

                # Settle the default attack skill:
                default = self.default_attack_skill
                if len(attack_skills) > 1 and default in attack_skills:
                    attack_skills.remove(default)

            # Combat Spells:
            for battle_skill in item.add_be_spells:
                self.magic_skills.append(battle_skill, true_add)

            # Taking care of stats/skills: ----------------------------------->
            self.stats.apply_item_effects(item, True, true_add)

            # Traits: -------------------------------------------------------->
            for trait in item.removetraits:
                self.remove_trait(trait, true_add)

            for trait in item.addtraits:
                self.apply_trait(trait, true_add)

            # Effects: ------------------------------------------------------->
            if hasattr(self, "effects"):
                if slot == 'consumable':
                    type = item.type
                    if type == 'food':
                        self.up_counter("dnd_food_poison_counter", 1)
                        if self.get_flag("dnd_food_poison_counter", 0) >= 7:
                            self.enable_effect('Food Poisoning')

                    elif type == 'alcohol':
                        self.up_counter("dnd_drunk_counter", item.mod["joy"])
                        if self.get_flag("dnd_drunk_counter", 0) >= (45 if "Heavy Drinker" in self.traits else 30):
                            self.enable_effect('Drunk')

                    for effect in item.removeeffects:
                        self.disable_effect(effect)

                for effect in item.addeffects:
                    self.enable_effect(effect)

            # Jump away from equipment screen if appropriate:
            if item.jump_to_label and getattr(store, "eqtarget", None) is self:
                renpy.scene(layer="screens") # hides all screens
                jump(item.jump_to_label)

        def remove_item_effects(self, item):
            """Deals with removing items effects on characters.

            :param item: the effects of the item to be removed
            """
            # Attacks/Magic -------------------------------------------------->
            # Attack Skills:
            if item.attacks is not None:
                attack_skills = self.attack_skills
                for battle_skill in item.attacks:
                    attack_skills.remove(battle_skill, False)

                # Settle the default attack skill:
                if len(attack_skills) == 0:
                    attack_skills.append(self.default_attack_skill)

            # Combat Spells:
            for battle_skill in item.add_be_spells:
                self.magic_skills.remove(battle_skill, False)

            # Taking care of stats/skills: ----------------------------------->
            self.stats.apply_item_effects(item, False, False)

            # Traits: -------------------------------------------------------->
            for trait in item.removetraits:
                self.apply_trait(trait, False)

            for trait in item.addtraits:
                self.remove_trait(trait, False)

            # Effects: ------------------------------------------------------->
            if hasattr(self, "effects"):
                for effect in item.addeffects:
                    self.disable_effect(effect)

        def item_counter(self):
            # Timer to clear consumable blocks
            drops = []
            for item, value in self.consblock.iteritems():
                value -= 1
                if value <= 0:
                    drops.append(item)
                    continue
                self.consblock[item] = value
            for item in drops:
                del self.consblock[item]

            # Timer to remove effects of a temp consumer items
            drops = []
            for item, value in self.constemp.iteritems():
                value -= 1
                if value <= 0:
                    self.remove_item_effects(item)
                    drops.append(item)
                    continue
                self.constemp[item] = value
            for item in drops:
                del self.constemp[item]

            # Counter to apply misc item effects and settle misc items conditions:
            item = self.eqslots["misc"]
            if item:
                # Figure out if we can pay the piper:
                # FIXME why check if we do not pay?
                #  do we pay only at the end of the 'session', or daily till the end?
                for stat, val in item.mod.items():
                    if val < 0:
                        if stat == "exp":
                            pass
                        elif stat == "gold":
                            if self.status == "slave" and self in hero.chars:
                                temp = hero
                            else:
                                temp = self
                            if temp.gold + val < 0:
                                break
                        else:
                            if self.get_stat(stat) + val < self.stats.get_stat_min(stat):
                                break
                else:
                    value = self.miscitems.get(item, 0) + 1
                    if value >= item.mtemp:
                        self.apply_item_effects(item)

                        # collect self-destruct or not reusable items
                        if (not item.mreusable) or item.mdestruct:
                            if not item.mreusable:
                                self.miscblock.append(item)
                            self.unequip(item, "misc", True)
                            if item.mdestruct:
                                self.inventory.remove(item)
                            if self.autoequip:
                                self.auto_equip(self.last_known_aeq_purpose)
                        self.miscitems.pop(item, None)
                    else:
                        self.miscitems[item] = value

        # Trait methods *now for all characters:
        # Traits methods
        def apply_trait(self, trait, truetrait=True): # Applies trait effects
            self.traits.apply(trait, truetrait=truetrait)

        def remove_trait(self, trait, truetrait=True):  # Removes trait effects
            if trait.id == "Virgin" and "Chastity" in self.effects:
                pass
            else:
                self.traits.remove(trait, truetrait=truetrait)

        # Effects:
        ### Effects Methods
        def enable_effect(self, name, **kwargs):
            # Prevent same effect from being enable twice (and handle exceptions)
            if name in self.effects:
                return

            if name == "Poisoned":
                if "Artificial Body" in self.traits:
                    return
                ss_mod = kwargs.get("ss_mod", None)
                duration = kwargs.get("duration", 10)
                if ss_mod is None:
                    ss_mod = {"health": -locked_random("randint", 5, 10)}
            elif name == "Unstable":
                ss_mod = randrange(22)
                ss_mod = {"joy": (9+ss_mod) if ss_mod > 10 else -(20+ss_mod)}
                duration = randint(2, 4)
            elif name == "Down with Cold":
                ss_mod = {"health": -randint(2, 5),
                          "vitality": -randint(5, 15),
                          "joy": -randint(2, 5)}
                duration = locked_random("randint", 6, 14)
            elif name == "Food Poisoning":
                ss_mod = {"health": -randint(8, 12),
                          "vitality": -randint(10, 25),
                          "joy": -randint(8, 12)}
                duration = locked_random("randint", 6, 14)
            else:
                ss_mod = kwargs.get("ss_mod", None)
                duration = kwargs.get("duration", None)
            obj = CharEffect(name, duration=duration, ss_mod=ss_mod)
            obj.enable(self)

        def disable_effect(self, name):
            effect = self.effects.get(name, None)
            if effect is not None:
                effect.end(self)

        def nd_effects(self):
            # Run the effects if they are available:
            for effect in self.effects.values():
                effect.next_day(self)

            # 3+ days with low joy lead to Depression effect, removed if joy raises above a limit
            joy = self.get_stat("joy")
            if "Depression" in self.effects:
                self.PP -= 100 # PP_PER_AP
                if joy > 30:
                    self.disable_effect("Depression")
            elif joy > 30:
                self.del_flag("depression_counter")
            else:
                if joy <= randint(15, 20) and not "Pessimist" in self.traits:
                    self.up_counter("depression_counter", 1)
                if self.get_flag("depression_counter", 0) >= 3:
                    self.enable_effect("Depression")

            # 3+ days with high joy lead to Elation effect, removed if joy falls below a limit
            if "Elation" in self.effects:
                if dice(10):
                    self.PP += 100 # PP_PER_AP
                if joy < 85:
                    self.disable_effect("Elation")
            elif joy < 85:
                self.del_flag("elation_counter")
            else:
                if joy >= 95:
                    self.up_counter("elation_counter", 1)
                    if self.flag("elation_counter") >= 3:
                        self.enable_effect('Elation')

            # 5+ days with vitality < .3 max lead to Exhausted effect, can be removed by one day of rest or some items
            vit = self.get_stat("vitality")
            max = self.get_max("vitality")
            if "Exhausted" in self.effects:
                self.mod_stat("vitality", -max/5)
            elif vit > max * .8:
                self.del_flag("exhausted_counter")
            else:
                if vit < max * .3:
                    self.up_counter("exhausted_counter", 1)
                    if self.flag("exhausted_counter") >= 5:
                        self.enable_effect('Exhausted')

            if "Horny" in self.effects: # horny effect which affects various sex-related things and scenes
                self.disable_effect("Horny")
            else:
                if interactions_silent_check_for_bad_stuff(self):
                    if "Nymphomaniac" in self.traits:
                        chance = 60
                    elif "Frigid" in self.traits:
                        chance = 1
                    else:
                        chance = 30
                    if locked_dice(chance):
                        self.enable_effect("Horny")

        # Relationships:
        def is_friend(self, char):
            return char in self.friends

        def is_lover(self, char):
            return char in self.lovers

        def next_day(self):
            self.restore_ap()

            self.clear_img_cache()

            self.log_stats()

            # Next day morning --------------------------------------->
            #  Resets and Counters:
            self.item_counter()
            #  Effects
            self.nd_effects()

        def auto_training(self, kind):
            """
            Training, right now by NPCs.
            *kind = is a string referring to the NPC
            """
            # Any training:
            self.mod_exp(exp_reward(self, self))

            if kind == "Abby Training":
                self.mod_stat("magic", randint(1, 3))
                self.mod_stat("intelligence", randint(1, 2))
                mod_by_max(self, "mp", .5)
                if dice(50):
                    self.mod_stat("agility", randint(1, 2))

            elif kind == "Aine Training":
                self.mod_stat("charisma", randint(1, 3))
                mod_by_max(self, "vitality", .5)
                if dice(max(10, self.get_stat("luck"))):
                    self.mod_stat("reputation", 1)
                    self.mod_stat("fame", 1)
                if dice(1 + self.get_stat("luck")*.05):
                    self.mod_stat("luck", randint(1, 2))
            elif kind == "Xeona Training":
                self.mod_stat("attack", randint(1, 2))
                self.mod_stat("defence", randint(1, 2))
                if dice(50):
                    self.mod_stat("agility", 1)
                mod_by_max(self, "health", .5)
                if dice(25 + max(5, int(self.get_stat("luck")/3))):
                    self.mod_stat("constitution", randint(1, 2))

        @property
        def npc_training_price(self):
            return 250 * (self.tier+1)

        def nd_auto_train(self):
            for key, trainer in STATIC_CHAR.TRAININGS.items():
                if key in self.traits:
                    if self.PP >= 100: # PP_PER_AP
                        if hero.take_money(self.npc_training_price, "Training"):
                            self.auto_training(key)
                            self.PP -= 100 # PP_PER_AP
                            temp = "Successfully completed scheduled training with %s!" % trainer
                        else:
                            self.remove_trait(traits[key])
                            temp = "Not enough funds to train with %s. Auto-Training is disabled!" % trainer
                    else:
                        temp = "Not enough AP left to train with %s. Auto-Training will not be disabled." % trainer
                    self.txt.append(temp)

        def nd_log_report(self, txt, img, flag_red, type):
            # Change in stats during the day:
            charmod = dict()
            for stat, value in self.stats.log.items():
                if stat == "exp":
                    charmod[stat] = self.exp - value
                elif stat == "level":
                    charmod[stat] = self.level - value
                elif stat in STATIC_CHAR.SKILLS:
                    charmod[stat] = round_int(self.stats.get_skill(stat) - value)
                else:
                    charmod[stat] = self.stats.stats[stat] - value

            # Create the event:
            evt = NDEvent(red_flag = flag_red,
                          charmod = charmod,
                          type = type,
                          char = self,
                          img = img,
                          txt = txt)
            NextDayEvents.append(evt)


    class Mob(PytCharacter):
        """
        I will use ArenaFighter for this until there is a reason not to...
        """
        def __init__(self):
            super(Mob, self).__init__(False)

            # Basic Images:
            self.battle_sprite = ""

            self.controller = None

        def init(self):
            # Normalize character
            # If there are no basetraits, we add Warrior by default:
            if not self.traits.basetraits:
                bt = traits["Warrior"]
                self.traits.basetraits.add(bt)
                self.apply_trait(bt)

            #self.arena_willing = True # Indicates the desire to fight in the Arena
            #self.arena_permit = True # Has a permit to fight in main events of the arena.
            #self.arena_active = True # Indicates that character fights at Arena at the time.

            if not self.portrait:
                self.portrait = self.battle_sprite

            super(Mob, self).init()

        def has_image(self, *tags):
            """
            Returns True if image is found.
            """
            return True

        def show(self, *args, **kwargs):
            what = args[0]
            resize = kwargs.get("resize", (100, 100))

            if what == "portrait":
                what = self.portrait
            elif what == "battle_sprite":
                # See if we can find idle animation for this...
                webm_spites = mobs[self.id].get("be_webm_sprites", None)
                if webm_spites:
                    return ImageReference(webm_spites["idle"][0])
                else:
                    what = self.battle_sprite
            else:
                what = self.battle_sprite

            if isinstance(what, ImageReference):
                return pscale(what, resize[0], resize[1])
            else:
                return ProportionalScale(what, resize[0], resize[1])

        def restore_ap(self):
            self.PP = self.basePP + self.get_stat("constitution")*5 # FIXME too much?

    class Player(PytCharacter):
        def __init__(self):
            super(Player, self).__init__(True)

            self.img_db = None
            self.id = "mc" # Added for unique items methods.
            self.name = 'Player'
            self.fullname = 'Player'
            self.nickname = 'Player'
            self.location = pytfall.streets
            self.status = "free"
            self.gender = "male"

            self.autoequip = False # Player can manage his own shit.

            self._buildings = list()
            self._chars = list()

            self.txt = list()
            self.fin = Finances(self)

            # Team:
            self.team = Team(implicit=[self])
            self.team.name = "Player Team"
            self.teams = [self.team]

        def init(self):
            # Set Human trait for the MC: (We may want to customize this in the future)
            if not hasattr(self, "race"):
                self.apply_trait(traits["Human"])

            self.update_sayer()

            super(Player, self).init()

        def update_sayer(self):
            self.say = Character(self.nickname, show_two_window=True, show_side_image=self.show("portrait", resize=(120, 120)), **self.say_style)

        # Girls/Brothels/Buildings Ownership
        @property
        def buildings(self):
            """
            Returns a list of all buildings in heros ownership.
            """
            return self._buildings

        @property
        def dirty_buildings(self):
            """
            The buildings that can be cleaned.
            """
            return [building for building in self.buildings if building.maxdirt != 0]

        @property
        def upgradable_buildings(self):
            """
            The buildings that can be upgraded.
            """
            return [b for b in self.buildings if len(b.all_possible_extensions()) != 0]

        def add_building(self, building):
            if building not in self._buildings:
                self._buildings.append(building)

            self.sort_buildings()

        def sort_buildings(self):
            workable = []
            habitable = []
            rest = []

            for b in self._buildings:
                if b.workable:
                    workable.append(b)
                elif b.habitable:
                    habitable.append(b)
                else:
                    rest.append(b)

            workable.sort(key=attrgetter("tier"), reverse=True)
            habitable.sort(key=attrgetter("tier"), reverse=True)

            self._buildings = workable + habitable + rest

        def get_guild_businesses(self):
            return [u for b in self._buildings for u in b.businesses if u.__class__ == ExplorationGuild]

        def remove_building(self, building):
            try:
                self._buildings.remove(building)
            except ValueError:
                raise Exception("{} building does not belong to the player!".format(str(building)))

            retire_chars_from_building(self.chars + [self], building)

            # 'cleanup' the building
            for ad in building.adverts:
                ad['active'] = False
            building.dirt = 0
            building.threat = 0
            if building.needs_manager:
                building.available_workers = list()  # TODO should be part of post_nd?
                building.available_managers = list() # TODO should be part of post_nd?
                building.all_clients = list()
                building.regular_clients = set()
                building.clients = list()
            if hasattr(building, "inventory"):
                building.inventory.clear()
                building.given_items = dict()

        @property
        def chars(self):
            """List of owned/employed characters
            :returns: @todo
            """
            return self._chars

        def add_char(self, char):
            if char in self._chars:
                raise Exception, "This char (ID: %s) is already in service to the player!!!" % char.id

            self._chars.append(char)

            char.basePP -= 100 # reduce available AP (the char spends it on shopping, self-time, etc...) - PP_PER_AP

        def remove_char(self, char):
            try:
                self._chars.remove(char)
            except ValueError:
                raise Exception, "This char (ID: %s) is not in service to the player!!!" % char.id

            # remove from the teams as well
            for team in self.teams:
                if char in team:
                    team.remove(char)

            for fg in self.get_guild_businesses():
                for team in fg.teams:
                    if char in team:
                        team.remove(char)

            char.basePP += 100 # restore available AP - PP_PER_AP

            char.home = pytfall.sm if char.status == "slave" else pytfall.city
            char.reset_workplace_action()
            set_location(char, None)

        def new_team(self):
            t = Team(implicit=[self])
            self.team = t
            self.teams.append(t)

        def remove_team(self, team):
            if self.team != team:
                self.teams.remove(team)

        def select_team(self, team):
            self.team = team

        # ----------------------------------------------------------------------------------
        def nd_pay_taxes(self, txt, flag_red):
            txt.append("It's time to pay taxes!")
            fin = self.fin

            if fin.income_tax_debt:
                temp = "Your standing income tax debt to the government: {color=gold}%d Gold{/color}." % fin.income_tax_debt
                txt.append(temp)

            # Income Taxes:
            income, tax = fin.get_income_tax(log_finances=True)
            temp = "Over the past week your taxable income amounted to: {color=gold}%d Gold{/color}.\n" % income
            txt.append(temp)

            if tax or fin.income_tax_debt:
                temp = "Your income tax for this week is {color=gold}%d Gold{/color}. " % tax
                txt.append(temp)

                fin.income_tax_debt += tax
                if tax != fin.income_tax_debt:
                    temp = "That makes it a total amount of: {color=gold}%d Gold{/color}. " % fin.income_tax_debt
                    txt.append(temp)

                if self.take_money(fin.income_tax_debt, "Income Taxes"):
                    fin.income_tax_debt = 0
                    temp = "\nYou were able to pay that in full!"
                    txt.append(temp)
                else:
                    flag_red = True
                    s0 = "\nYou've did not have enough money..."
                    s1 = "Be advised that if your debt to the government reaches 50000,"
                    s2 = "they will indiscriminately confiscate your property until it is paid in full."
                    s3 = "(meaning that you will lose everything that you own at repo prices)."
                    temp = " ".join([s0, s1, s2, s3])
                    txt.append(temp)
            else:
                s0 = "You may consider yourself lucky as any sum below 5000 Gold is not taxable."
                s1 = "Otherwise the government would have totally ripped you off :)"
                temp = " ".join([s0, s1])
                txt.append(temp)

            # Property taxes:
            temp = choice(["\nWe're not done yet...\n",
                           "\nProperty tax:\n",
                           "\nProperty taxes next!\n"])
            txt.append(temp)
            b_tax, s_tax, tax = fin.get_property_tax(log_finances=True)
            if tax:
                if b_tax:
                    temp = "Real Estate Tax: {color=gold}%d Gold{/color}." % b_tax
                    txt.append(temp)
                if s_tax:
                    temp = "Slave Tax: {color=gold}%d Gold{/color}." % s_tax
                    txt.append(temp)
                    if b_tax:
                        temp = "\nThat makes it a total of {color=gold}%d Gold{/color}" % tax
                        txt.append(temp)
                fin.property_tax_debt += tax
                if fin.property_tax_debt != tax:
                    s0 = " Don't worry, we didn't forget about your debt of %d Gold either." % fin.property_tax_debt
                    s1 = "Yeap, there are just the two inevitable things in life:"
                    s2 = "Death and Paying your tax on Monday!"
                    temp = " ".join([s0, s1, s2])
                    txt.append(temp)

                if self.take_money(fin.property_tax_debt, "Property Taxes"):
                    fin.property_tax_debt = 0
                    temp = "\nYou settled the payment successfully, but your wallet feels a lot lighter now :)"
                    txt.append(temp)
                else:
                    temp = "\nYour payment failed..."
                    txt.append(temp)
            else:
                temp = "\nHowever you do not have taxable property. How fortunate..."
                txt.append(temp)

            total_debt = fin.income_tax_debt + fin.property_tax_debt
            if total_debt:
                temp = "Your current total debt to the government is {color=gold}%d Gold{/color}!" % total_debt
                txt.append(temp)
            if total_debt > 50000:
                flag_red = True
                temp = " {color=red}... And you're pretty much screwed because it is above 50000!{/color} Your property will now be confiscated!"
                txt.append(temp)

                all_properties = [b for b in self.buildings if b.can_sell()] + \
                        [c for c in self.chars if c.status == "slave" and c.is_available]
                shuffle(all_properties)
                cr = store.pytfall.economy.confiscation_range
                while all_properties:
                    confiscate = all_properties.pop()
                    if isinstance(confiscate, Building):
                        price = confiscate.get_price()
                        self.remove_building(confiscate)
                    else: # instance(confiscate, Char):
                        price = confiscate.get_price()
                        self.remove_char(confiscate)

                    multiplier = round(uniform(*cr), 2)
                    temp = choice(["{} has been confiscated for {}% of its original value. ".format(
                                                                                    confiscate.name, multiplier*100),
                                   "Those sobs took {} from you! ".format(confiscate.name),
                                   "You've lost {}! If only you were better at managing your business... ".format(
                                                                                    confiscate.name)])
                    txt.append(temp)
                    total_debt -= int(price*multiplier)
                    if total_debt > 0:
                        temp = "You are still required to pay {color=gold}%s Gold{/color}." % total_debt
                        txt.append(temp)
                    else:
                        txt.append("Your debt has been paid in full!")
                        if total_debt < 0:
                            total_debt = -total_debt
                            temp = " You get a sum of {color=gold}%d Gold{/color} returned to you from the last repo!" % total_debt
                            txt.append(temp)
                            hero.add_money(total_debt, reason="Tax Returns")
                            total_debt = 0
                        break
                if total_debt:
                    temp = "\n You do not own anything that might be repossessed by the government..."
                    txt.append(temp)
                    temp = " You've been declared bankrupt and your debt is now Null and Void!"
                    txt.append(temp)
                fin.income_tax_debt = 0
                fin.property_tax_debt = 0

            return flag_red

        def next_day(self):
            # auto-degrading stats/skills
            # FIXME should be done for all chars, but non-workers do not gain stats at the moment
            #        might be merged with the degrading disposition/affection
            for stat in STATIC_CHAR.DEGRADING_STATS:
                value = self.get_stat(stat)/100
                if value >= 1 and dice(value):
                    self.stats._mod_base_stat(stat, -1)
            for skill in STATIC_CHAR.SKILLS:
                value = self.get_skill(skill)/100
                if value >= 1 and dice(value):
                    self.stats.mod_full_skill(skill, -1)
            if self.get_stat("joy") > 60:
                self.mod_stat("joy", -1)
            elif self.get_stat("joy") < 40:
                self.mod_stat("joy", 1)

            txt = self.txt
            flag_red = False

            # -------------------->
            txt.append("Hero Report:\n\n")

            if self.location == pytfall.jail:
                # Currently in jail
                txt.append("You've spent the night in the jail.")
            else:
                # Home location nd mods:
                loc = self.home

                mod = loc.get_daily_modifier()
                if mod > 0:
                    txt.append("You've comfortably spent a night.")
                elif mod < 0:
                    flag_red = True
                    txt.append("{color=red}You should find some shelter for the night... it's not healthy to sleep outside.{/color}")

                mod_battle_stats(self, mod)

            # Taxes:
            if calendar.weekday() == "Monday" and day != 1:
                flag_red = self.nd_pay_taxes(txt, flag_red)

            if self.arena_rep <= -500 and self.arena_permit:
                txt.append("{color=red}You've lost your Arena Permit... Try not to suck at it so much!{/color}")
                self.arena_permit = False
                self.arena_rep = 0
                flag_red = True

            # Finances related ---->
            self.fin.next_day()

            # ------------>
            self.nd_log_report(txt, 'profile', flag_red, type='mcndreport')
            self.txt = list()

            super(Player, self).next_day()

            # Next day morning --------------------------------------->
            # hero-only trait which heals everybody
            if "Life Beacon" in self.traits:
                if self.location != pytfall.jail:
                    for i in self.chars:
                        if i.is_available:
                            mod_by_max(i, "health", .1)
                            i.mod_stat("joy", 1)

                mod_by_max(self, "health", .1)
            # Training with NPCs
            if self.location != pytfall.jail:
                self.nd_auto_train()

    class Char(PytCharacter):
        # wranks = {
                # 'r1': dict(id=1, name=('Rank 1: Kirimise', '(Almost beggar)'), price=0),
                # 'r2': dict(id=2, name=("Rank 2: Heya-Mochi", "(Low-class prostitute)"), price=1000, ref=45, exp=10000),
                # 'r3': dict(id=3, name=("Rank 3: Zashiki-Mochi", "(Middle-class Prostitute"), price=3000, ref=60, exp=25000),
                # 'r4': dict(id=4, name=("Rank 4: Tsuke-Mawashi", "(Courtesan)"), price=5000, ref=80, exp=50000),
                # 'r5': dict(id=5, name=("Rank 5: Chûsan", "(Famous)"), price=7500, ref=100, exp=100000),
                # 'r6': dict(id=6, name=("Rank 6: Yobidashi", "(High-Class Courtesan)"), price=10000, ref=120, exp=250000),
                # 'r7': dict(id=7, name=("Rank 7: Koshi", "(Nation famous)"), price=25000, ref=200, exp=400000),
                # 'r8': dict(id=8, name=("Rank 8: Tayu", "(Legendary)"), price=50000, ref=250, exp=800000)
            # }
        #RANKS = {}
        def __init__(self):
            super(Char, self).__init__(True)
            # Game mechanics assets
            self.desc = ""
            self.location = None

            self.rank = 1

            # Relays for game mechanics
            #self.wagemod = 100 # Percentage to change wage payout

            # Unhappy counter:
            self.days_unhappy = 0

            # Trait assets
            #self.init_traits = list() # List of traits to be enabled on game startup (should be deleted in init method)

            # Autocontrol of workers action (during the next day mostly)
            # TODO lt: Enable/Fix (to work with new skills/traits) this!
            # TODO lt: (Move to a separate instance???)
            self.autocontrol = {
                "Rest": True,
                "Tips": False,
                "SlaveDriver": False,
                "Acts": {"normalsex": True, "anal": True, "blowjob": True, "lesbian": True},
                "S_Tasks": {"clean": True, "bar": True, "waitress": True},
            }

            # Auto-equip/buy:
            #self.autobuy = False
            #self.autoequip = False
            self.given_items = dict()

            # Preferences
            #self.preferences = {}

            self.txt = list()
            self.fin = Finances(self)

        def init(self):
            """Normalizes after __init__"""

            # Base Class | Status normalization:
            if not self.traits.basetraits:
                pattern = create_traits_base(STATIC_CHAR.GEN_OCCS)
                for i in pattern:
                    self.traits.basetraits.add(i)
                    self.apply_trait(i)

            # Location + Home
            if self.status == "free":
                if self.location == "city":
                    set_location(self, None)
                self.home = pytfall.city
            else:
                set_location(self, None)
                self.home = pytfall.sm

            # Wagemod + auto-buy + auto-equip:
            if self.status == 'free':
                self.wagemod = 100
                self.autobuy = True
            else:
                self.wagemod = 0
                self.autobuy = False
            self.autoequip = True

            # FOUR BASE TRAITS THAT EVERY GIRL SHOULD HAVE AT LEAST ONE OF:
            if not hasattr(self, "personality"):
                self.apply_trait(traits["Deredere"])
            if not hasattr(self, "race"):
                self.apply_trait(traits["Unknown"])
            if not hasattr(self, "gents"):
                self.apply_trait(traits["Average Boobs" if self.gender == "female" else "Average Dick"])
            if not hasattr(self, "body"):
                self.apply_trait(traits["Slim"])

            # generate random preferences if none provided
            if not hasattr(self, "preferences"):
                self.preferences = {p: random.random() for p in STATIC_CHAR.PREFS}

            # Second round of stats normalization:
            restore_battle_stats(self)

            # Battle and Magic skills:
            if not self.attack_skills:
                self.attack_skills.append(self.default_attack_skill)

            # Arena:
            if not isinstance(self.arena_willing, bool):
                self.arena_willing = self.status == "free" and "Combatant" in self.gen_occs

            # add ADVCharacter:
            self.update_sayer()

            # Calculate wage and upkeep. (TODO call update_tier_info?)
            self.calc_expected_wage()
            self.calc_upkeep()

            super(Char, self).init()

        # Logic assists:
        @property
        def allowed_to_view_personal_finances(self):
            return self.status == "slave" or self.get_stat("disposition") >= 900
        @property
        def allowed_to_define_autobuy(self):
            return self.status == "slave" or self.get_stat("disposition") >= 950
        @property
        def allowed_to_define_autoequip(self):
            return self.status == "slave" or self.get_stat("disposition") >= 850

        ### Next Day Methods
        def can_do_work(self, check_ap):
            """Checks whether the character is injured/tired/has AP.

            AP check is optional and if True, also checks for action points.
            """
            # We do not want workers in school to AutoRest,
            # Idea is that the school is taking care of this.
            if self._task == StudyingTask:
                return True

            if self.get_stat("health") < self.get_max("health")/4:
                return "health"
            if self.get_stat("vitality") <= self.get_max("vitality")/5:
                return "vitality"
            if "Exhausted" in self.effects:
                return "exhausted"
            if 'Food Poisoning' in self.effects:
                return "food"
            if check_ap:
                if self.PP <= 0:
                    return "pp"

            return True

        def nd_rest(self):
            """Implements a character reactions to tiring/injury/food poisoning etc...
                Called multiple times during the next day calculation.

               Checks the employee if she/he is in need of rest (using can_do_work).
               Turns on AutoRest and 'executes' the rest if there is PP available. 
            """
            if self._task in [RestTask, AutoRestTask]:
                # Char is already resting, call the action
                self._task.run(self) # <--- Looks odd and off?
                return

            # try to use our items to restore stats
            if self.autoequip:
                l = list() # BATTLE_STATS ?
                for stat, mod in [("health", 3), ("mp", 10), ("vitality", 5), ("joy", 2)]:
                    if self.get_stat(stat) < self.get_max(stat)/mod:
                        l.append(stat)
                if l:
                    l = self.auto_consume(l)
                    if l:
                        self.txt.append("%s consumed %s %s to make %sself feel better." % (self.pC, ", ".join(l), plural("item", len(l)), self.op))

            # check if rest is needed
            temp = self.can_do_work(False)
            if temp is True:
                return # no -> done

            # in need of rest
            if not self.autocontrol['Rest']:
                return # not in our control -> skip

            # report
            if temp == "vitality":
                temp = "%s is too tired! %s going to take a few days off to recover." % (self.name, self.pC)
            elif temp == "health":
                temp = "%s is in need of medical attention! %s going to take a few days off to heal." % (self.name, self.pC)
            elif temp == "exhausted":
                temp = "%s is exhausted! %s needs a day off to recover." % (self.name, self.pC)
            else:
                temp = "%s is suffering from food poisoning! %s is going to take a few days off to recover." % (self.name, self.pC)
            self.txt.append(temp)

            # switch to AutoRest
            self.set_task(AutoRestTask)
            # do the actual resting
            AutoRestTask.run(self) # <--- Looks odd and off?

        def nd_sleep(self, txt):
            # Home location nd mods:
            loc = self.home
            mod = loc.get_daily_modifier()

            pC = self.pC
            if mod > 0:
                flag_red = False
                temp = "%s comfortably spent the night in %s." % (pC, str(loc))
                if self.home == hero.home:
                    if self.get_stat("disposition") > -500:
                        self.mod_stat("disposition", 1)
                        self.mod_stat("joy", randint(1, 3))

                        if self.status == "slave":
                            temp += " %s is happy to live under the same roof as %s master!" % (pC, self.pp)
                        else:
                            temp += " %s is content living with you." % pC
                    else:
                        if self.status == "slave":
                            temp += " Even though you both live in the same house, %s hates you too much to really care." % self.name
                        else:
                            self.mod_stat("disposition", -100)
                            self.mod_stat("affection", -20)
                            self.mod_stat("joy", -20)
                            self.home = pytfall.city
                            temp += " After a rough fight %s moves out of your apartment." % self.name
                txt.append(temp)

            elif mod < 0:
                flag_red = True
                txt.append("{color=red}%s presently resides in the %s.{/color}" % (pC, str(loc)))
                txt.append("{color=red}It's not a comfortable or healthy place to sleep in.{/color}")
                txt.append("{color=red}Try finding better accommodations for your worker!{/color}")

            mod_battle_stats(self, mod)
            return flag_red


        def next_day(self):
            # Adjust disposition/affection
            temp = self.get_stat("disposition")
            if temp < 0:
                self.mod_stat("disposition", 1)
            elif temp > 0:
                self.mod_stat("disposition", -1)
            temp = self.get_stat("affection")
            if temp < 0:
                self.mod_stat("affection", 1)
            elif temp > 0:
                self.mod_stat("affection", -1)

            if self not in hero.chars:
                # character does not belong to the hero
                # Home location nd mods:
                #loc = self.home
                #mod = loc.get_daily_modifier()
                restore_battle_stats(self)

                # earn some money
                if self.location != pytfall.jail:
                    wage = self.expected_wage
                    if self.status == "slave":
                        wage = wage/10
                    wage = randrange(wage)
                    if wage != 0:
                        self.add_money(wage, reason="Wages")

                #self.nd_rest()
                # Adding joy mods:
                if self.get_stat("joy") < self.get_max("joy"):
                    self.mod_stat("joy", 5)

                super(Char, self).next_day()

                # Next day morning --------------------------------------->
                # Shopping (For now will not cost AP):
                self.nd_autoshop()
                return

            # hero's worker
            # Local vars
            mood = None
            txt = self.txt
            flag_red = False

            # header
            temp = "{u}%s{/u} (%s)\n" % (set_font_color(self.fullname, "pink"), set_font_color(self.status, "palegreen"))
            if self.job is None:
                temp += "{i}Not Assigned{/i}"
            else:
                temp += "{i}{b}%s{/b}, %s{/i}" % (self.job.id, set_font_color(self.workplace, "orange"))
            txt.insert(0, temp)

            if self.location is not None:
                if self.location == pytfall.ra:
                    # If escaped:
                    self.mod_stat("health", -randint(3, 5))
                    txt.append("{color=red}%s location is still unknown. You might want to increase your efforts to find %s, otherwise %s will be gone forever.{/color}" % (self.ppC, self.pp, self.p))
                else:
                    # your worker is in jail TODO might want to do this in the ND of the jail
                    mod_battle_stats(self, pytfall.jail.get_daily_modifier())

                    txt.append("{color=red}%s is spending the night in the jail!{/color}" % self.pC)
                flag_red = True
            elif self.action == ExplorationTask:
                if self.has_flag("dnd_back_from_track"):
                    txt.append("{color=green}%s arrived back from the exploration run!{/color}" % self.pC)
                    self.set_task(None)
                    flag_red = self.nd_sleep(txt)
                else:
                    txt.append("{color=green}%s is currently on the exploration run!{/color}" % self.pC)

                self.up_counter("daysemployed")

                # Settle wages:
                mood = self.fin.settle_wage(txt, mood)

                self.log_stats() # hide stats changes
            else:
                # normal employee
                self.up_counter("daysemployed")

                # Finances:
                # Upkeep:
                if self.action == StudyingTask:
                    # currently in school
                    txt.append("%s is currently in school. %s upkeep is included in price of the class %s is taking." % (self.pC, self.ppC, self.p))
                else:
                    # The whole upkeep thing feels weird, penalties to slaves are severe...
                    amount = self.get_upkeep()

                    if not amount:
                        pass
                    elif amount < 0:
                        txt.append("%s actually managed to save you some money ({color=gold}%d Gold{/color}) instead of requiring upkeep! Very convenient!" % (self.pC, -amount))
                        hero.add_money(-amount, reason="Workers Upkeep")
                    elif hero.take_money(amount, reason="Workers Upkeep"):
                        self.fin.log_logical_expense(amount, "Upkeep")
                        if hasattr(self.workplace, "fin"):
                            self.workplace.fin.log_logical_expense(amount, "Workers Upkeep")
                        txt.append("You paid {color=gold}%d Gold{/color} for %s upkeep." % (amount, self.pp))
                    else:
                        if self.status != "slave":
                            self.mod_stat("joy", -randint(3, 5))
                            self.mod_stat("disposition", -randint(5, 10))
                            self.mod_stat("affection", affection_reward(self, -1, stat="gold"))
                            txt.append("You failed to pay %s upkeep, %s is a bit cross with you because of that..." % (self.pp, self.p))
                        else:
                            self.mod_stat("joy", -20)
                            self.mod_stat("disposition", -randint(25, 50))
                            self.mod_stat("affection", affection_reward(self, -2, stat="gold"))
                            self.mod_stat("health", -10)
                            self.mod_stat("vitality", -25)
                            txt.append("You failed to provide even the most basic needs for your slave. This will end badly...")

                # This whole routine is basically fucked and done twice or more. Gotta do a whole check of all related parts tomorrow.
                # Settle wages:
                mood = self.fin.settle_wage(txt, mood)

                tips = self.flag("dnd_accumulated_tips")
                if tips:
                    temp = choice(["Total tips earned: {color=gold}%d Gold{/color}. " % tips,
                                   "%s got {color=gold}%d Gold{/color} in tips. " % (self.pC, tips)])
                    txt.append(temp)

                    if self.autocontrol["Tips"]:
                        temp = choice(["As per agreement, %s gets to keep all of it! This is a very good motivator." % self.p,
                                       "%s is happy to keep it." % self.pC])
                        txt.append(temp)

                        self.add_money(tips, reason="Tips")
                        self.fin.log_logical_expense(tips, "Tips")
                        if isinstance(self.workplace, Building):
                            self.workplace.fin.log_logical_expense(tips, "Tips")

                        self.mod_stat("disposition", 1 + tips/20)
                        self.mod_stat("affection", affection_reward(self, .1, stat="gold"))
                        self.mod_stat("joy", 1 + tips/40)
                    else:
                        temp = choice(["You take all of %s tips for yourself." % self.pp,
                                       "You keep all of it."])
                        txt.append(temp)
                        hero.add_money(tips, reason="Worker Tips")

                self.nd_rest()

                # Effects:
                if 'Poisoned' in self.effects:
                    txt.append("{color=red}%s is suffering from Poisoning!{/color}" % self.pC)
                    flag_red = True
                if (not self.autobuy) and not self.allowed_to_define_autobuy:
                    self.autobuy = True
                    txt.append("%s will go shopping whenever it may please %s from now on!" % (self.pC, self.pp))
                if (not self.autoequip) and not self.allowed_to_define_autoequip:
                    self.autoequip = True
                    txt.append("%s will be handling %s own equipment from now on!" % (self.pC, self.pp))

                # throw a red flag if the worker is not doing anything:
                if not self.action:
                    flag_red = True
                    txt.append("  {color=red}Please note that %s is not really doing anything productive!{/color}" % self.p)
                    NextDayEvents.unassigned_chars += 1

                # Unhappiness and related:
                mood, flag_red = self.nd_joy_disposition_checks(mood, flag_red)

                # Home location nd mods:
                if (flag_red is False or self in hero.chars) and self.nd_sleep(txt):
                    flag_red = True

                # Finances related:
                self.fin.next_day()

            img = 'profile' if mood is None else self.show("profile", mood)

            self.nd_log_report(txt, img, flag_red, type='girlndreport')
            self.txt = list()
            super(Char, self).next_day()

            # Next day morning ---------------------------------------------->
            # Training with NPCs and shopping
            if self.is_available:
                self.nd_auto_train()

                # Shopping (For now will not cost AP):
                self.nd_autoshop(self.txt)

        def nd_autoshop(self, txt=None):
            if self.autobuy is False or self.gold < 1000:
                return # can not afford it
            if self.has_flag("cnd_shopping_day"):
                return # recently shopped
            self.set_flag("cnd_shopping_day", day+4)

            if txt is not None:
                temp = choice(["%s decided to go on a shopping tour :)" % self.nickname,
                               "%s went to town to relax, take %s mind of things and maybe even do some shopping!" % (self.nickname, self.pp)])
                txt.append(temp)

            result = self.auto_buy(amount=randint(1, 2), equip=self.autoequip)
            if result:
                self.mod_stat("joy", 5 * len(result))

                if txt is None:
                    return
                temp = set_font_color(", ".join([item.id for item in result]), "cadetblue")
                temp = choice(("%s bought %sself %s %s.", 
                               "%s got %s hands on %s %s!")) % (self.pC, self.op, temp, plural("item", len(result)))
                temp += choice(("This brightened %s mood a bit!" % self.pp, "%s's definitely in better mood because of that!" % self.pC))

                temp = set_font_color(temp, "limegreen")
            else:
                if txt is None:
                    return
                temp = choice(["But %s ended up not doing much else than window-shopping..." % self.p,
                                "But %s could not find what %s was looking for..." % (self.p, self.p)])
            txt.append(temp)

        def nd_joy_disposition_checks(self, mood, flag_red):
            friends_disp_check(self, self.txt)

            if self.get_stat("joy") <= 25:
                temp = "%s is unhappy!" % self.pC
                self.txt.append(set_font_color(temp, "tomato"))
                mood = "sad"
                self.days_unhappy += 1
            else:
                if self.days_unhappy > 0:
                    self.days_unhappy -= 1

            if self.status == "slave":
                if self.days_unhappy > 7 or self.get_stat("disposition") < -200:
                    escaped, mode = pytfall.ra.try_escape(self, location=self.workplace) # FIXME check for home/location?
                    if escaped:
                        msg = "%s has escaped!" % self.fullname
                        if mode == pytfall.ra.FOUGHT:
                            msg += " Although the guards fought valiantly, they could not stop %s." % self.op
                        msg += " Now you have to search for %s yourself." % self.op
                    elif mode == pytfall.ra.CAUGHT:
                        msg = "%s tried to escape, but the guards were alert and stopped %s." % (self.name, self.op)
                    elif mode == pytfall.ra.FOUGHT:
                        msg = "%s tried to escape, but the guards subdued %s." % (self.name, self.op)
                    elif self.get_stat("disposition") < -500:
                        if dice(50):
                            msg = "Took %s own life because %s could no longer live as your slave!" % (self.pp, self.p)
                            kill_char(self)
                        else:
                            msg = "Tried to take %s own life because %s could no longer live as your slave!" % (self.pp, self.p)
                            self.set_stat("health", 1)
                    else:
                        msg = None

                    if msg is not None:
                        flag_red = True
                        mood = "sad"
                        self.txt.append(set_font_color(msg, "red"))
            else:
                # free char
                if self.days_unhappy > 7 or self.get_stat("disposition") < -100:
                    if self.days_unhappy > 7:
                        msg = "%s has left your employment because you do not give a rats ass about how %s feels!" % (self.pC, self.p)
                        mood = "sad"
                    else:
                        msg = "%s has left your employment because %s no longer trusts or respects you!" % (self.pC, self.pp)
                    self.txt.append(set_font_color(msg, "red"))
                    flag_red = True
                    hero.remove_char(self)

            return mood, flag_red


    class rChar(Char):
        '''Randomised chars (WM Style)
        Basically means that there can be a lot more than one of them in the game
        Different from clones we discussed with Dark, because clones should not be able to use magic
        But random chars should be as good as any of the unique chars in all aspects
        It will most likely not be possible to write unique scripts for random charz
        '''
        def __init__(self):
            super(rChar, self).__init__()


    class Customer(PytCharacter):
        def __init__(self, gender="male", rank=1):
            super(Customer, self).__init__(False)

            # Using direct access instead of a flag, looks better in code:
            self.served_by = None

            self.gender = gender
            self.rank = rank
            #self.caste = CLIENT_CASTES[rank]
            self.regular = False # Regular clients do not get removed from building lists as those are updated.

            # Alex, we should come up with a good way to set portrait depending on rank
            #self.portrait = "" # path to portrait

            # Preferences:
            self.likes = set() # These are simple sets containing objects and possibly strings of what this character likes or dislikes...
            self.dislikes = set() # ... more often than not, this is used to compliment same params based of traits. Also (for example) to set up client preferences.

    class NPC(Char):
        """There is no point in this other than an ability to check for instances of NPCs
        """
        def __init__(self):
            super(NPC, self).__init__()
