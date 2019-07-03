init -950 python:
    ##################### Import Modules #####################
    import os
    import sys
    import inspect
    from inspect import isclass
    import re
    import pygame
    from pygame import scrap, SCRAP_TEXT
    import time
    import string
    import logging
    import fnmatch
    import json
    import math
    from math import sin, cos, radians
    import random
    from random import choice, shuffle, uniform
    import copy
    from copy import deepcopy, copy as shallowcopy
    import itertools
    from itertools import chain, izip_longest
    import functools
    from functools import partial
    import operator
    from operator import attrgetter, itemgetter, methodcaller
    import collections
    from collections import OrderedDict, defaultdict, deque
    import xml.etree.ElementTree as ET
    import simpy
    #import cPickle as pickle
    import bisect
    import types

    ############## Settings and other useful stuff ###############
    # absolute path to the pytfall/game directory, which is formatted according
    # to the conventions of the local OS
    gamedir = os.path.normpath(config.gamedir)

    if persistent.use_quest_popups is None:
        persistent.use_quest_popups = True
    if persistent.tooltips is None:
        persistent.tooltips = True
    if persistent.unsafe_mode is None:
        persistent.unsafe_mode = True
    if persistent.battle_results is None:
        persistent.battle_results = False
    if persistent.battle_speed is None:
        persistent.battle_speed = 1.0
    if persistent.auto_saves is None:
        persistent.auto_saves = False
    if persistent.intro is None:
        persistent.intro = False
    if persistent.use_be_menu_targeting is None:
        persistent.use_be_menu_targeting = False
    if persistent.showed_pyp_hint is None:
        persistent.showed_pyp_hint = False

    def content_path(*args):
        '''Returns proper path for a file in the content directory *To be used with os module.'''
        path = os.path.join("content", *args)
        #path = "/".join(["content"] + list(args))
        #if os.pathsep+"content"+os.pathsep in path:
        #    renpy.error("content already in path: "+path)
        return renpy.loader.transfn(path)

    # enable logging via the 'logging' module
    if DEBUG_LOG:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(name)-15s %(message)s')
        # devlog = logging.getLogger(" ".join([config.name, config.version]))
        devlog = logging.getLogger()
        devlogfile = logging.FileHandler(os.path.join(gamedir, "devlog.txt"))
        devlogfile.setLevel(logging.DEBUG)
        devlog.addHandler(devlogfile)
        devlog.critical("\n--- launch game ---")
        # fm = logging.Formatter('%(levelname)-8s %(name)-15s %(message)s')
        fm = logging.Formatter('%(levelname)-8s %(message)s')
        devlogfile.setFormatter(fm)
        devlog.info("Engine Version: %s" % str(renpy.version()))
        devlog.info("Game Version: %s" % str(config.version))
        del fm
        devlog.info("game directory: %s" % str(gamedir)) # Added str() call to avoid cp850 encoding

    class TimeLog(_object):
        '''
        Uses Devlog to log execution time between the two statements.
        Failed to use RenPy log, switching to dev.
        '''
        def __init__(self):
            # dict of msg: start_time
            self.log = {}

        def start(self, msg, report_start=False):
            if DEBUG_PROFILING:
                if msg not in self.log:
                    self.log[msg] = time.time()
                    if report_start:
                        devlog.info("Starting timer: {}".format(msg))
                else:
                    devlog.warning("!!! Tried to start before finishing a timer: {}!".format(msg))

        def end(self, msg):
            if DEBUG_PROFILING:
                duration = self.log.pop(msg, None)
                if duration is None:
                    devlog.warning("!!! Tried to end before starting a timer: {}!".format(msg))
                    return

                duration = time.time() - duration
                duration = round(duration, 2)
                msg = (" " * len(self.log)) + msg
                devlog.info("%s completes in %ss." % (msg, duration))

    tl = TimeLog()
    tl.start("Ren'Py User Init!")

    # setting the window on center
    # useful if game is launched in the window mode
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Best I can tell, does nothing, but looks kinda nice :)
    sys.setdefaultencoding('utf-8')

    # some debug functions
    #def resolve_lib_file(badf, l=1):
    #    m = re.match(r'^(?:.*[\\/])?(library[\\/].*\.rpy)c?$', badf)
    #    if m:
    #        f = m.group(1).replace('\\','/')
    #        try:
    #            return (renpy.loader.transfn(f), l)
    #        except Exception: pass

    #def get_screen_src(name):
    #    for n, f, l in renpy.dump.screens:
    #        if isinstance(name, basestring) and n == name or n == name+"_screen":
    #            return resolve_lib_file(f, l)

    #def get_label_src(name):
    #    for n, r in renpy.game.script.namemap.iteritems():
    #        if isinstance(name, basestring) and n == name or n == name+"_label":
    #            return resolve_lib_file(r.filename, r.linenumber)

    # Getting rid of Ren'Py's containers since we don't require rollback.
    dict = _dict
    set = _set
    list = _list
    # object = _object # We are not using Ren'Pys object anywhere but it will throw errors if initiated this early because layout cannot be built with Pythons one.
    _rollback = False

    # Object to specify a lack of value when None can be considered valid.
    # Use as "x is undefined".
    undefined = object()

    # Prepping a list to append all events for the registration.
    world_events = list()

    # Prepping a list to append all quests for the registration.
    world_quests = list()

    # Prepping a list to append all gossips for the registration.
    world_gossips = list()

    # Override the default game_menu
    config.game_menu_action = Show("s_menu", s_menu="Settings", main_menu=True)

    # Registration of extra music channels:
    renpy.music.register_channel("events", "sfx", False, file_prefix="content/sfx/sound/")
    renpy.music.register_channel("events2", "sfx", False,  file_prefix="content/sfx/sound/")
    renpy.music.register_channel("world", "music", True, file_prefix="content/sfx/music/world/")
    renpy.music.register_channel("gamemusic", "music", True, file_prefix="content/sfx/music/")

    ######################## Classes/Functions ###################################
    IMAGE_EXTENSIONS = (".png", ".jpg", ".gif", ".jpeg", ".webp")
    MOVIE_EXTENSIONS = (".webm", ".mkv")
    CONTENT_EXTENSIONS = IMAGE_EXTENSIONS + MOVIE_EXTENSIONS
    MUSIC_EXTENSIONS = (".mp3", ".ogg", ".wav")
    IMG_NOT_FOUND_PATH = os.path.join("content", "gfx", "interface", "images", "no_image.png")

    def check_image_extension(fn):
        #return fn.rsplit(".", 1)[-1].lower() in IMAGE_EXTENSIONS
        return fn.lower().endswith(IMAGE_EXTENSIONS)
    def check_movie_extension(fn):
        return fn.lower().endswith(MOVIE_EXTENSIONS)
    def check_content_extension(fn):
        return fn.lower().endswith(CONTENT_EXTENSIONS)
    def check_music_extension(fn):
        return fn.lower().endswith(MUSIC_EXTENSIONS)

    class Flags(_object):
        """Simple class to log all variables into a single namespace

        Now and count...

        PF Flags:
        starts with "jobs": Reset internally in SimPy land! Usually at the end of Env.
        starts with "dnd": Deleted at the very end of next day logic!
        starts with "cnd": Deleted at the very end of next day logic if its value matches the current day!
        """
        def __init__(self):
            self.flags = dict()

        def __iter__(self):
            return iter(self.flags)

        def flag(self, flag):
            return self.flags.get(flag, False)

        #def mod_flag(self, flag, value):
        #    """Can be used as a simple counter for integer based flags.

        #   Simply changes the value of the flag otherwise.
        #    """
        #    if DEBUG_LOG:
        #        if not self.has_flag(flag) and "next" not in last_label:
        #            devlog.warning("{} flag modded before setting it's value!".format(flag))

        #    if isinstance(value, int):
        #        self.flags[flag] = self.flags.get(flag, 0) + value
        #    else:
        #        self.set_flag(flag, value)

        def get_flag(self, flag, default=None):
            # works similar to dicts .get method
            return self.flags.get(flag, default)

        def set_flag(self, flag, value=True):
            self.flags[flag] = value

        def del_flag(self, flag):
            if flag in self.flags:
                del self.flags[flag]

        def has_flag(self, flag):
            """Check if flag exists at all (not just set to False).
            """
            return flag in self.flags

        def up_counter(self, flag, value=1):
            """A more advanced version of a counter than mod_flag.
            """
            self.flags[flag] = self.flags.get(flag, 0) + value

        #def up_counter(self, flag, value=1, max=None, delete=False):
        #    """A more advanced version of a counter than mod_flag.

        #    This can keep track of max and delete a flag upon meeting it.
        #    """
        #    result = self.flags.get(flag, 0) + value
        #    if max is not None and result >= max:
        #        if delete:
        #            self.del_flag(flag)
        #        else:
        #            self.set_flag(flag, max)
        #    else:
        #        self.set_flag(flag, result)

        #def down_counter(self, flag, value=1, min=None, delete=False):
        #    """A more advanced version of a counter than mod_flag.

        #    This can keep track of min and delete a flag upon meeting it.
        #    """
        #    result = self.flags.get(flag, 0) - value

        #    if min is not None and result <= min:
        #        if delete:
        #            self.del_flag(flag)
        #        else:
        #            self.set_flag(flag, min)
        #    else:
        #        self.set_flag(flag, result)

        #def set_union(self, flag, value):
        #    """Can be used to create sets.

        #    If a flag exists, expects it to be a set() and creates a union with it.
        #    """
        #    if DEBUG_LOG:
        #        if not self.has_flag(flag) and "next" not in last_label:
        #            devlog.warning("{} flag modded before setting it's value!".format(flag))

        #    if not isinstance(value, (set, list, tuple)):
        #        value = set([value])

        #    self.flags.setdefault(flag, set()).union(value)

        #def add_to_set(self, flag, value):
        #    """Creates a set with flags"""
        #    self.flags.setdefault(flag, set()).add(value)

        #def remove_from_set(self, flag, value):
        #    """Removes from flag which is a set"""
        #    if value in self.flags[flag]:
        #        self.flags[flag].remove(value)


    # unsafe, but faster random generators
    def randrange(a):
        """ Return a random integer in the range of [0, a) """
        return int(random.random()*a)
    def randint(a, b):
        """ Return a random integer in the range of [a, b] """
        return a + int(random.random() * (b - a + 1))
    def randfloat(value):
        """ Return a random integer in the range of:
             [0, int(value) + (1 if fraction is not zero)]
         or  [int(value) - (1 if fraction is not zero), 0] if value is negative
            the chance to add a 'bonus' depends on the value of the fraction
            e.g 2.6 returns a number in the range of [0, 3], 60% chance of an added 1
        """
        v = int(value)
        result_int, result_frac = random.random(), random.random()
        if value > 0:
            result_int = int(result_int*(v+1))
            if result_frac < value - v:
                result_int += 1
        else:
            result_int = int(result_int*(v-1))
            if result_frac < v - value:
                result_int -= 1

        return result_int

    def dice_int(value):
        """ Return an integer in the range of:
             [int(value), int(value) + (1 if fraction is not zero)]
         or  [int(value) - (1 if fraction is not zero), int(value)] if value is negative
            the chance to add a 'bonus' depends on the value of the fraction
            e.g 2.4 returns a number in the range of [2, 3], 40% chance of an added 1
        """
        v = int(value)
        #if dice(abs(value - v)*100):
        if random.random() < abs(value - v):
            v += (1 if value >= 0 else -1)
        return v

    def dice(percent_chance):
        """ returns randomly True with given % chance, or False """
        return random.random() * 100 < percent_chance

    def locked_dice(percent_chance):
        # Same as above, only using locked seed...
        return locked_random("random") * 100 < percent_chance

    # Locking random seed of internal renpys random
    def locked_random(type, *args, **kwargs):
        #store.stored_random_seed = renpy.random.getstate()
        return getattr(renpy.random, type)(*args, **kwargs)

    # Safe jump, if label doesn't exists, game will notify about it
    def jump(labelname):
        if renpy.has_label(labelname):
            gui_debug("jump %s" % labelname)
            renpy.jump(labelname)
        else:
            gui_debug(u"Label '%s' does not exist." % labelname)

    # Useful methods for path
    def listfiles(dir):
        return (file for file in os.walk(os.path.join(dir, '.')).next()[2])
    def listdirs(dir):
        return (file for file in os.walk(os.path.join(dir, '.')).next()[1])

    #def exist(path):
    #    if isinstance(path, basestring):
    #        return os.path.exists(os.path.join(gamedir, path))
    #    return all(exist(x) for x in path)

    # Analizis of strings and turning them into int, float or bool.
    # Useful for importing data from xml.
    #def parse(string):
    #    try:
    #        value = int(string)
    #    except TypeError:
    #        value = string
    #    except AttributeError:
    #        value = string
    #    except ValueError:
    #        try:
    #            value = float(string)
    #        except ValueError:
    #            if string.lower() in ['true', 'yes', 'on']:
    #                value = True
    #            elif string.lower() in ['false', 'no', 'off', 'none']:
    #                value = False
    #            else:
    #                value = string
    #    return value

    # -------------------------------------------------------------------------------------------------------- Ends here

init -4 python:
    ########################## Images ##########################
    # Colors are defined in colors.rpy to global namespace, prolly was not the best way but file was ready to be used.

    ##################### Autoassociation #####################
    # Backrounds are automatically registered in the game and set to width/height of the default screen
    # displayed by "show bg <filename>" or similar commands
    # file name without the extention
    fname = tag = image = None
    dir = content_path("gfx", "bg")
    for fname in listfiles(dir):
        if check_image_extension(fname):
            tag = 'bg ' + fname.rsplit(".", 1)[0]
            image = os.path.join(dir, fname)
            renpy.image(tag, im.Scale(image, config.screen_width,
                        config.screen_height))

    dir = content_path("gfx", "bg", "locations")
    for fname in listfiles(dir):
        if check_image_extension(fname):
            tag = 'bg ' + fname.rsplit(".", 1)[0]
            image = os.path.join(dir, fname)
            renpy.image(tag, im.Scale(image, config.screen_width,
                        config.screen_height))

    dir = content_path("gfx", "bg", "story")
    for fname in listfiles(dir):
        if check_image_extension(fname):
            tag = 'bg ' + 'story ' + fname.rsplit(".", 1)[0]
            image = os.path.join(dir, fname)
            renpy.image(tag, im.Scale(image, config.screen_width,
                        config.screen_height))

    dir = content_path("gfx", "bg", "be")
    for fname in listfiles(dir):
        if check_image_extension(fname):
            tag = 'bg ' + fname.rsplit(".", 1)[0]
            image = os.path.join(dir, fname)
            renpy.image(tag, im.Scale(image, config.screen_width,
                        config.screen_height))

    dir = content_path("events", "slave_club")
    for fname in listfiles(dir):
        if check_image_extension(fname):
            tag = 'smc ' + fname[:-5]
            image = os.path.join(dir, fname)
            renpy.image(tag, im.Scale(image, config.screen_width,
                        config.screen_height))
    del fname, tag, dir, image

    # Dungeon:
    light = blend = fname = orientations = ori = wall = bgfname = fn_end = bg_img = tag = fg_img = dir = image = None
    for light in ('', '_torch'):
        # 4 sided symmetry (or symmetry ignored)
        for blend in ('bluegrey', 'door', 'barrel', 'mossy', 'pilar', 'more_barrels', 'barrel_crate',
                      'portal', 'portal_turned', 'ladderdownf', 'mossy_alcove', 'dagger', 'ring'):
            dir = content_path("dungeon", "%s%s" % (blend, light))
            for fname in listfiles(dir):
                if check_image_extension(fname):
                    image = os.path.join(dir, fname)
                    renpy.image(fname[:-5], image)

        # 2 sided symmetry and no symmetry
        for blend, orientations in [('portal', ['', '_turned']), ('ladder', "lrfb")]:
            for ori in orientations:
                dir = content_path("dungeon", "%s%s%s" % (blend, ori, light))
                for fname in listfiles(dir):
                    if check_image_extension(fname):
                        image = os.path.join(dir, fname)
                        renpy.image(fname[:-5], image)

        #composite images
        for wall in ('bluegrey', 'mossy'):
            dir = content_path("dungeon", "%s%s" % (wall, light))
            for bgfname in listfiles(dir):
                if check_image_extension(bgfname):
                    bg_img = os.path.join(dir, bgfname)
                    for blend in ('door2','button'):
                        fn_end = bgfname[len('dungeon_'+wall):-5]
                        tag = 'dungeon_%s_%s%s' % (wall, blend, fn_end)
                        fg_img = 'content/dungeon/%s%s/dungeon_%s%s.webp' % (blend, light, blend, fn_end)

                        if os.path.isfile('%s/%s' % (gamedir, fg_img)):
                            renpy.image(tag, im.Composite((1280,720), (0, 0), bg_img, (0, 0), fg_img))
                        else:
                            renpy.image(tag, bgfname[:-5])
    del light, blend, fname, orientations, ori, wall, bgfname, fn_end, bg_img, tag, fg_img, dir, image

    # Auto-Animations are last
    folder = path = dir = split_dir = len_split = folder_path = img_name = delay = loop = None
    for folder in (["gfx", "animations"], ["gfx", "be", "auto-animations"]):
        path = content_path(*folder)
        for dir in listdirs(path):
            split_dir = dir.split(" ")
            len_split = len(split_dir)

            img_name = split_dir[0]
            delay = float(split_dir[1]) if len_split > 1 else .25
            loop = bool(int(split_dir[2])) if len_split > 2 else False

            folder_path = os.path.join(path, dir)
            renpy.image(img_name, animate(folder_path, delay, loop=loop))
    del folder, path, dir, split_dir, len_split, folder_path, img_name, delay, loop

    # Overrides
    colorprev = Color.__new__
    Color.__prev_new__ = classmethod(colorprev)
    def colornew(cls, cls_, color=None, hls=None, hsv=None, rgb=None, alpha=1.0):
        color = _COLORS_.get(color, color)
        return Color.__prev_new__(color, hls, hsv, rgb, alpha)
    Color.__new__ = classmethod(colornew)
    del colornew, colorprev

    # Or we crash due to an engine bug (going to MMS):
    class SetVariable(SetField):
        def __init__(self, name, value):
            super(SetVariable, self).__init__(store, name, value, kind="variable")

        def get_selected(self):
            try:
                return super(SetVariable, self).get_selected()
            except:
                return False

init -1 python: # Constants:
    # for f in renpy.list_files():
        # if check_image_extension(f):
            # renpy.image(f, At(f, slide(so1=(600, 0), t1=.7, eo2=(1300, 0), t2=.7)))
    # BATTLE_STATS = ("health", "mp", "vitality")
    CLIENT_CASTES = ['None', 'Peasant', 'Merchant', 'Nomad', 'Wealthy Merchant', 'Clerk', 'Noble', 'Royal']
    EQUIP_SLOTS = OrderedDict([("body", "Body"),
                               ("head", "Head"),
                               ("feet", "Legs"),
                               ("wrist", "Wrist"),
                               ("amulet", "Neck"),
                               ("cape", "Cape"),
                               ("weapon", "Right Hand"),
                               ("misc", "Misc"),
                               ("ring", "Ring"),
                               ("smallweapon", "Left Hand")])
    ND_IMAGE_SIZE = (820, 705)
    MOVIE_CHANNEL_COUNT = 32

init:
    default NEXT_MOVIE_CHANNEL = 0
    default DAILY_EXP_CORE = 30 # 1 lvl per 10 days give or take. Rebalance experience gain.
    default DAILY_AFF_CORE = 10 # about 20 affection per day, give or take. Rebalance affection gain. 
    default MAX_TIER = 10 # to limit the characters tier
    # a few 'macros' (just to make it easier to search for dependencies)
    #default MAX_MAGIC_TIER = MAX_ITEM_TIER = 4
    #default MAX_STAT_PER_TIER = PP_PER_AP = 100
    #default SKILLS_MAX = 5000
    default block_say = False
    #define PytPix = renpy.display.transition.Pixellate
    default last_label_pure = ""

    default special_save_number = 1

    #$ renpyd = renpy.displayable
    # Or we crash due to an engine bug (going to MMS):
    #default char = None
    #default char_profile_entry = None # Label to access chars profile from weird locations.
    #default hero_profile_entry = None # Label to access hero profile from weird locations.
    #default girls = None
    #default came_to_equip_from = None # Girl equipment screen came from label holder
    #default eqtarget = None # Equipment screen
    #default just_view_next_day = False
    #default bm_mid_frame_mode = None
    #default bm_selected_exp_area = None
    #default bm_exploration_view_mode = None
    #default bm_selected_log_area = None
    #default the_chosen = None
    #default equip_girls = None

init 999 python:
    # ensure that all initialization debug messages have been written to disk
    if DEBUG_LOG:
        devlogfile.flush()
        del devlogfile

    tl.end("Ren'Py User Init!")
