init 100 python:
    pyp = PyTFallopedia()

    tagdb = TagDatabase()
    for tag in tags_dict.values():
        tagdb.tagmap[tag] = set()

    tl.start("Loading: Mobs")
    mobs = load_mobs()
    tl.end("Loading: Mobs")

default defeated_mobs = {}
default gazette = Gazette()

label start:
    $ renpy.block_rollback()
    $ locked_random("random") # Just making sure that we have set the variable...

    if DEBUG:
        $ renpy.show_screen("debug_tools")
    $ renpy.show_screen("new_style_tooltip")
    $ gfx_overlay = GFXOverlay()
    $ renpy.show("pf_gfx_overlay", what=gfx_overlay, layer="pytfall")

    python: # Variable defaults:
        chars_list_last_page_viewed = 0
        char = None # Character global
        came_to_equip_from = None # Girl equipment screen came from label holder
        eqtarget = None # Equipment screen
        gallery = None

    python: # Day/Calendar/Names/Menu Extensions and some other defaults.
        # Global variables and loading content:
        day = 1
        calendar = Calendar(day=28, month=2, year=125)
        global_flags = Flags()

        ilists = ListHandler()
        # difficulty = Difficulties()

        # Load random names selections for rGirls:
        tl.start("Loading: Random Name Files")
        female_first_names = load_female_first_names(200)
        male_first_names = load_male_first_names(200)
        random_last_names = load_random_last_names(200)
        random_team_names = load_team_names(50)
        tl.end("Loading: Random Name Files")

        tl.start("Loading: PyTFallWorld")
        pytfall = PyTFallWorld()
        tl.end("Loading: PyTFallWorld")

        tl.start("Loading: Menu Extensions")
        menu_extensions = MenuExtension()
        menu_extensions["Abby The Witch Main"] = []
        menu_extensions["Xeona Main"] = []
        tl.end("Loading: Menu Extensions")

    python: # Traits:
        # Load all game elements:
        tl.start("Loading/Sorting: Traits")
        traits = load_traits()
        global_flags.set_flag("last_modified_traits", os.path.getmtime(content_path('db/traits')))

    call sort_traits_for_gameplay from _call_sort_traits_for_gameplay

    $ tl.end("Loading/Sorting: Traits")

    python: # Items/Shops:
        tl.start("Loading/Sorting: Items")
        items = load_items()
        global_flags.set_flag("last_modified_items", os.path.getmtime(content_path('db/items')))
        items_upgrades = json.load(renpy.file("content/db/upgrades.json"))

        # Build shops:
        pytfall.init_shops()

    call sort_items_for_gameplay from _call_sort_items_for_gameplay

    $ tl.end("Loading/Sorting: Items")

    python: # Dungeons (Building (Old))
        tl.start("Loading: Dungeons")
        dungeons = load_dungeons()
        tl.end("Loading: Dungeons")

        # Battle Skills:
        tl.start("Loading: Battle Skills")
        battle_skills = load_battle_skills()
        tiered_magic_skills = dict()
        for s in battle_skills.values():
            tiered_magic_skills.setdefault(s.tier, []).append(s)
        tl.end("Loading: Battle Skills")

    $ hero = Player()

    python: # Jobs:
        tl.start("Loading: Jobs")
        # This jobs are usually normal, most common type that we have in PyTFall
        temp = [WhoreJob(), StripJob(), BarJob(), Manager(), CleaningJob(), GuardJob(), Rest(), AutoRest()]
        simple_jobs = {j.id: j for j in temp}
        del temp
        tl.end("Loading: Jobs")

    python: # Ads and Buildings:
        tl.start("Loading: Buildings")
        buildings = load_buildings()
        tl.end("Loading: Buildings")

        # Training/Schools:
        tl.start("Loading: School")
        pytfall.school.add_courses()
        tl.end("Loading: School")

    # python: # Picked Tags and maps (afk atm):
    #     maps = xml_to_dict(content_path('db/map.xml'))
    #
    #     import cPickle as pickle
    #     tl.start("Loading: Binary Tag Database")
    #     # pickle.dump(tagdb.tagmap, open(config.gamedir + "/save.p", "wb"))
    #     tagdb = TagDatabase()
    #     tagdb.tagmap = pickle.load(open(config.gamedir + "/save.p", "rb"))
    #     tagslog.info("loaded %d images from binary files" % tagdb.count_images())
    #     tl.end("Loading: Binary Tag Database")

    python: # Tags/Loading Chars/Mobs/Quests.first_day
        # Loading characters:
        # tagdb = TagDatabase()
        # for tag in tags_dict.values():
        #     tagdb.tagmap[tag] = set()

        tl.start("Loading: All Characters!")
        chars = load_characters("chars", Char)
        #global_flags.set_flag("last_modified_chars", os.path.getmtime(content_path('chars')))
        npcs = load_characters("npc", NPC)
        #global_flags.set_flag("last_modified_npcs", os.path.getmtime(content_path('npc')))
        rchars = load_random_characters()
        #global_flags.set_flag("last_modified_rchars", os.path.getmtime(content_path('rchars')))
        tl.end("Loading: All Characters!")
        if DEBUG_LOG:
            devlog.info("Loaded %d images from filenames!" % tagdb.count_images())

        # Start auto-quests
        pytfall.world_quests.first_day()

        # tl.start("Loading: Mobs")
        # mobs = load_mobs()
        # tl.end("Loading: Mobs")

    python: # SE (Areas)
        tl.start("Loading: Exploration Areas")
        # pytfall.forest_1 = Exploration()
        fg_areas = load_fg_areas()
        tl.end("Loading: Exploration Areas")

    python: # Move to a World AI method:
        tl.start("Loading: Populating World with RChars")
        pytfall.populate_world()
        tl.end("Loading: Populating World with RChars")
        tl.start("Loading: Populating EmploymentAgency")
        populate_ea()
        tl.end("Loading: Populating EmploymentAgency")

    python: # Girlsmeets:
        tl.start("Loading: GirlsMeets")
        gm = GirlsMeets()
        tl.end("Loading: GirlsMeets")

    jump dev_testing_menu_and_load_mc

label dev_testing_menu_and_load_mc:
    if DEBUG:
        menu:
            "Debug Mode":
                $ hero.traits.basetraits.add(traits["Mage"])
                $ hero.apply_trait(traits["Mage"])
                menu:
                    "Level 1":
                        $ n = 0
                    "Overpowered":
                        $ n = 10
                $ tier_up_to(hero, n, level_bios=(.9, 1.1), skill_bios=(.8, 1.2), stat_bios=(.8, 1.0))
                $ del n
            "Content":
                menu:
                    "Test Intro":
                        call intro from _call_intro
                        call mc_setup from _call_mc_setup
                    "MC Setup":
                        call mc_setup from _call_mc_setup_1
                    "Skip MC Setup":
                        $ pass
                    "Back":
                        jump dev_testing_menu_and_load_mc
            "GFX":
                while 1:
                    menu gfx_testing_menu:
                        "Particle":
                            scene black
                            show expression ParticleBurst([Solid("#%06x"%renpy.random.randint(0, 0xFFFFFF), xysize=(5, 5)) for i in xrange(50)], mouse_sparkle_mode=True) as pb
                            pause
                            hide pb
                        "Back":
                            jump dev_testing_menu_and_load_mc
    else:
        call intro from _call_intro_1
        call mc_setup from _call_mc_setup_2

    python: # We run this in case we skipped MC setup in devmode!
        if not getattr(hero, "_path_to_imgfolder", None):
            renpy.music.stop()
            if not DEBUG:
                # We're fucked if this is the case somehow :(
                raise Exception("Something went horribly wrong with MC setup!")

            male_fighters, female_fighters = load_special_arena_fighters()
            af = choice(male_fighters.values())
            del male_fighters[af.id]

            hero._path_to_imgfolder = af._path_to_imgfolder
            hero.id = af.id
            hero.say = Character(hero.nickname, color=ivory, show_two_window=True, show_side_image=hero.show("portrait", resize=(120, 120)))
            hero.restore_ap()
            hero.log_stats()

            if DEBUG and not hero.home:
                # Find the most expensive building with rooms
                ap = None 
                for b in buildings.values():
                    if b.rooms == 0:
                        continue
                    if ap is None or b.price > ap.price:
                        ap = b
                if ap:
                    hero.buildings.append(ap)
                    hero.home = ap
                del ap

    # Set Human trait for the MC: (We may want to customize this in the future)
    python:
        if not isinstance(hero.race, Trait):
            hero.apply_trait(traits["Human"])
            hero.full_race = "Human"

    jump continue_with_start

label continue_with_start:
    python: # Load Arena
        tl.start("Loading: Arena!")
        pytfall.init_arena()
        tl.end("Loading: Arena!")

    # Call girls starting labels:
    $ all_chars = chars.values()
    while all_chars:
        $ temp = all_chars.pop()
        $ chars_unique_label = "_".join(["start", temp.id])
        if renpy.has_label(chars_unique_label):
            call expression chars_unique_label from _call_expression_1

    python:
        # Clean up globals after loading chars:
        for i in ("chars_unique_label", "char", "girl", "testBrothel", "all_chars", "temp", "utka"):
            del(i)

        tl.start("Loading: Populating SlaveMarket")
        pytfall.sm.populate_chars_list()
        tl.end("Loading: Populating SlaveMarket")

    #  --------------------------------------
    # Put here to facilitate testing:
    if DEBUG and renpy.has_label("testing"):
        call testing from _call_testing

    python in _console:
        if store.DEBUG:
            stdio_lines = []
            stderr_lines = []
            console.history = []

    # last minute checks:
    if not hero.home:
        $ hero.home = pytfall.streets

    jump mainscreen

label sort_items_for_gameplay:
    python:
        # Items sorting for AutoBuy:
        shop_items = [item for item in items.values() if (set(pytfall.shops) & set(item.locations))]
        all_auto_buy_items = [item for item in shop_items if item.usable and not item.jump_to_label]

        trait_selections = {"goodtraits": {}, "badtraits": {}}
        auto_buy_items = {k: [] for k in ("body", "restore", "food", "dress", "rest", "warrior", "scroll")}

        for item in all_auto_buy_items:
            for k in ("goodtraits", "badtraits"):
                if hasattr(item, k):
                    for t in getattr(item, k):
                        # same item may occur multiple times for different traits.
                        trait_selections[k].setdefault(t, []).append(item)

            if item.type != "permanent":
                if item.type == "armor" or item.slot == "weapon":
                    auto_buy_items["warrior"].append(item)
                else:
                    if item.slot == "body":
                        auto_buy_items["body"].append(item)
                    if item.type in ("restore", "food", "scroll", "dress"):
                        auto_buy_items[item.type].append(item)
                    else:
                        auto_buy_items["rest"].append(item)

        for k in trait_selections:
            for v in trait_selections[k].values():
                v = sorted(v, key=lambda i: i.price)

        for k in ("body", "restore", "food", "dress", "rest", "warrior", "scroll"):
            auto_buy_items[k] = [(i.price, i) for i in auto_buy_items[k]]
            auto_buy_items[k].sort()

        # Items sorting per Tier:
        tiered_items = {}
        for i in items.values():
            tiered_items.setdefault(i.tier, []).append(i)
    return

label sort_traits_for_gameplay:
    python:
        # This should be reorganized later:
        tgs = object() # TraitGoups!
        tgs.breasts = [i for i in traits.values() if i.breasts]
        tgs.body = [i for i in traits.values() if i.body]
        tgs.base = [i for i in traits.values() if i.basetrait and not i.mob_only]
        tgs.elemental = [i for i in traits.values() if i.elemental]
        tgs.el_names = set([i.id.lower() for i in tgs.elemental])
        tgs.ct = [i for i in traits.values() if i.character_trait]
        tgs.sexual = [i for i in traits.values() if i.sexual] # This is a subset of character traits!
        tgs.race = [i for i in traits.values() if i.race]
        tgs.client = [i for i in traits.values() if i.client]

        # Base classes such as: {"SIW": [Prostitute, Stripper]}
        gen_occ_basetraits = defaultdict(set)
        for t in tgs.base:
            for occ in t.occupations:
                gen_occ_basetraits[occ].add(t)
        gen_occ_basetraits = dict(gen_occ_basetraits)
    return

label after_load:
    if hasattr(store, "stored_random_seed"):
        $ renpy.random.setstate(stored_random_seed)

    init python:
        def update_object(obj_dest, obj_src, prefix):
            for attr, v in vars(obj_dest).items():
                if hasattr(obj_src, attr):
                    v2 = getattr(obj_src, attr)
                    if v2 != v:
                        devlog.info("{} - Modified Attr {}: {} -> {} in {}".format(prefix, attr, str(v), str(v2), str(obj_dest)))
                        setattr(obj_dest, attr, v2)
                else:
                    devlog.info("{} - Attr Removed: {} from {}".format(prefix, attr, str(obj_dest)))
                    delattr(obj_dest, attr)

            for attr, v2 in vars(obj_src).items():
                if not hasattr(obj_dest, attr):
                    devlog.info("{} - New Attr {} for {} with value {}".format(prefix, attr, str(obj_dest), str(v2)))
                    setattr(obj_dest, attr, v2)

    # Updating Databases:
    # Items:
    python hide:
        last_modified_items = global_flags.get_flag("last_modified_items", 0)
        last_modified = os.path.getmtime(content_path('db/items'))
        if last_modified_items < last_modified: 
            tl.start("Updating items")
            updated_items = load_items()

            for id, item in updated_items.iteritems():
                curr_item = store.items.get(id, None)
                if curr_item is None:
                    # Add new item
                    store.items[id] = item
                    devlog.info("New Item: {}".format(id))
                else:
                    # Update the existing item
                    update_object(curr_item, item, "Item")

            del updated_items
            tl.end("Updating items")
            global_flags.set_flag("last_modified_items", last_modified)
            renpy.call("sort_items_for_gameplay")

    # Traits:
    python hide:
        last_modified_traits = global_flags.get_flag("last_modified_traits", 0)
        last_modified = os.path.getmtime(content_path('db/traits'))
        if last_modified_traits < last_modified:
            tl.start("Updating traits")
            updated_traits = load_traits()
            for id, trait in updated_traits.iteritems():
                curr_trait = store.traits.get(id, None)
                if curr_trait is None:
                    # Add new trait
                    store.traits[id] = trait
                    devlog.info("New Trait: {}".format(id))
                else:
                    # Update the existing trait
                    update_object(curr_trait, trait, "Trait")

            del updated_traits
            tl.end("Updating traits")
            global_flags.set_flag("last_modified_traits", last_modified) 
            renpy.call("sort_traits_for_gameplay")

    # All kinds of chars:
    python hide:
        # uChars:
        # always run till tagdb is not separated from the load_characters
        #last_modified_chars = global_flags.get_flag("last_modified_chars", 0)
        #last_modified = os.path.getmtime(content_path('chars'))
        if True: # last_modified_chars < last_modified:
        #    tl.start("Updating chars")
            updated_chars = load_characters("chars", Char)
            for id, char in updated_chars.items():
                curr_char = store.chars.get(id, None)
                if curr_char is None:
                    # Add new char
                    store.chars[id] = char
        #            devlog.info("New Character: {}".format(id))
        #        else:
        #            # Update the existing char
        #            update_object(curr_char, char, "Char")

        #    del updated_chars
        #    tl.end("Updating chars")
        #    global_flags.set_flag("last_modified_chars", last_modified)

        # NPCs:
        # always run till tagdb is not separated from load_characters
        #last_modified_npcs = global_flags.get_flag("last_modified_npcs", 0)
        #last_modified = os.path.getmtime(content_path('npc'))
        if True: #last_modified_npcs < last_modified:
        #    tl.start("Updating NPCs")
            updated_npcs = load_characters("npc", NPC)
            for id, npc in updated_npcs.items():
                curr_npc = store.npcs.get(id, None)
                if curr_npc is None:
                    # Add new NPC
                    store.npcs[id] = npc
        #            devlog.info("New NPC: {}".format(id))
        #        else:
        #            # Update the existing npc
        #            update_object(curr_npc, npc, "NPC")

        #    del updated_npcs
        #    tl.end("Updating NPCs")
        #    global_flags.set_flag("last_modified_npcs", last_modified)

        # rChars:
        # always run till tagdb is not separated from load_random_characters
        # last_modified_rchars = global_flags.get_flag("last_modified_rchars", 0)
        # last_modified = os.path.getmtime(content_path('rchars'))
        if True: #last_modified_rchars < last_modified:
        #    tl.start("Updating rchars")
            store.rchars = load_random_characters()
        #    tl.end("Updating rchars")
        #    global_flags.set_flag("last_modified_rchars", last_modified)

        # Arena Chars (We need this for databases it would seem...):
        load_special_arena_fighters()

    python:
        if hasattr(store, "dummy"):
            del dummy

    python hide: # Do we need/want this?
        for skill in store.battle_skills.values():
            skill.source = None

    # Save-Load Compatibility TODO Delete when we're willing to break saves (again :D).
    # python hide:
    #     for c in pytfall.sm.inhabitants.copy():
    #         if c not in chars.itervalues():
    #             remove_from_gameworld(c)
    #     aps = pytfall.city
    #     for c in aps.inhabitants.copy():
    #         if c not in chars.itervalues():
    #             remove_from_gameworld(c)
    python hide:
        if isinstance(store.defeated_mobs, dict):
            store.defeated_mobs = set(store.defeated_mobs.keys())

        if hasattr(store, "storyi_treasures") and isinstance(store.storyi_treasures, list):
            hero.del_flag("been_in_old_ruins")

        pytfall.maps = OnScreenMap()

        for s in store.battle_skills.values():
            if "initial_pause" not in s.target_damage_effect.keys():
                s.target_damage_effect["initial_pause"] = s.main_effect["duration"] * .75
            gfx = s.attacker_effects["gfx"]
            if isinstance(gfx, basestring):
                if gfx == "orb":
                    s.attacker_effects["gfx"] = "cast_orb_1"
                    s.attacker_effects["zoom"] = 1.85
                    s.attacker_effects["duration"] = 0.84
                elif gfx == "wolf":
                    s.attacker_effects["gfx"] = "wolf_1_webm"
                    s.attacker_effects["zoom"] = .85
                    s.attacker_effects["duration"] = 1.27
                    s.attacker_effects["cast"] = { "align": (.0, .5) }
                elif gfx == "bear":
                    s.attacker_effects["gfx"] = "bear_1_webm"
                    s.attacker_effects["zoom"] = .85
                    s.attacker_effects["duration"] = 0.97
                    s.attacker_effects["cast"] = { "align": (.0, .5) }
                elif gfx in ["dark_1", "light_1", "water_1", "air_1", "fire_1", "earth_1", "electricity_1", "ice_1"]:
                    s.attacker_effects["gfx"] = "cast_" + gfx
                    s.attacker_effects["zoom"] = 1.5
                    s.attacker_effects["duration"] = 0.84
                    s.attacker_effects["cast"] = { "point": "bc", "yo": -75}
                elif gfx in ["dark_2", "light_2", "water_2", "air_2", "fire_2", "earth_2", "ice_2", "electricity_2"]:
                    s.attacker_effects["gfx"] = "cast_" + gfx
                    s.attacker_effects["zoom"] = .9
                    s.attacker_effects["duration"] = 1.4
                elif gfx == "default_1":
                    s.attacker_effects["gfx"] = "cast_" + gfx
                    s.attacker_effects["zoom"] = 1.6
                    s.attacker_effects["duration"] = 1.12
                    s.attacker_effects["cast"] = { "ontop": False, "point": "bc" }
                elif gfx == "circle_1":
                    s.attacker_effects["gfx"] = "cast_" + gfx
                    s.attacker_effects["zoom"] = 1.9
                    s.attacker_effects["duration"] = 1.05
                    s.attacker_effects["cast"] = { "ontop": False, "point": "bc", "yo": -10 }
                elif gfx == "circle_2":
                    s.attacker_effects["gfx"] = "cast_" + gfx
                    s.attacker_effects["zoom"] = 1.8
                    s.attacker_effects["duration"] = 1.1
                    s.attacker_effects["cast"] = { "point": "bc", "yo": -100 }
                elif gfx == "circle_3":
                    s.attacker_effects["gfx"] = "cast_" + gfx
                    s.attacker_effects["zoom"] = 1.8
                    s.attacker_effects["duration"] = 0.96
                    s.attacker_effects["cast"] = { "yo": -50 }
                elif gfx == "runes_1":
                    s.attacker_effects["gfx"] = "cast_" + gfx
                    s.attacker_effects["zoom"] = 1.1
                    s.attacker_effects["duration"] = 0.75
                    s.attacker_effects["cast"] = { "ontop": False, "point": "bc", "yo": -50}


        hero.clear_img_cache()
        hero.del_flag("train_with_xeona")
        hero.del_flag("train_with_aine")
        hero.del_flag("train_with_witch")
        for c in store.chars.values():
            c.clear_img_cache()
            if hasattr(c, "reservedAP"):
                del c.reservedAP
            if c.has_flag("day_since_shopping"):
                c.set_flag("last_shopping_day", day - c.flag("day_since_shopping"))
                c.del_flag("day_since_shopping")
            c.del_flag("train_with_xeona")
            c.del_flag("train_with_aine")
            c.del_flag("train_with_witch")

        tierless_items = store.tiered_items.get(None)
        if tierless_items:
            for item in tierless_items:
                item.tier = 0
                store.tiered_items[0].append(item)
            del store.tiered_items[None]

        if not hasattr(pytfall.arena, "df_count"):
            pytfall.arena.df_count = 0
            pytfall.arena.hero_match_result = None 

        if hasattr(hero, "STATS"):
            for c in itertools.chain(chars.values(), [hero], hero.chars, npcs.values()):
                if hasattr(c, "STATS"):
                    del c.STATS
                if hasattr(c, "SKILLS"):
                    del c.SKILLS
                if hasattr(c, "FULLSKILLS"):
                    del c.FULLSKILLS
                if hasattr(c, "GEN_OCCS"):
                    del c.GEN_OCCS
                if hasattr(c, "STATUS"):
                    del c.STATUS
                if hasattr(c, "MOOD_TAGS"):
                    del c.MOOD_TAGS
                if hasattr(c, "UNIQUE_SAY_SCREEN_PORTRAIT_OVERLAYS"):
                    del c.UNIQUE_SAY_SCREEN_PORTRAIT_OVERLAYS

        if not hasattr(hero, "teams"):
            hero.teams = [hero.team]
        if not hasattr(hero, "txt"):
            hero.txt = list()

        if hero.controller == "player":
            clearCharacters = True
        if hasattr(hero, "_arena_rep"):
            clearCharacters = True
        if hasattr(hero, "_location"):
            clearCharacters = True
        if hasattr(hero.stats, "delayed_stats"):
            clearCharacters = True

        store.bm_mid_frame_mode = None

        if hasattr(store, "businesses"):
            buildings.update(store.businesses)
            del store.businesses
        if hasattr(store, "adverts"):
            del store.adverts

        if not hasattr(TapBeer, "ID"):
            load_buildings()

        for b in itertools.chain(hero.buildings, buildings.values()):
            if isinstance(b, Building):
                if not hasattr(b, "init_pep_talk"):
                    b.init_pep_talk = True
                    b.cheering_up = True
                    b.asks_clients_to_wait = True
                    b.help_ineffective_workers = True # Bad performance still may get a payout.
                    b.works_other_jobs = False

                    # TODO Before some major release that breaks saves, move manager and effectiveness fields here.
                    b.mlog = None # Manager job log
                if isinstance(b.auto_clean, bool):
                    val = 90 if b.auto_clean else 100
                    del b.auto_clean
                    b.auto_clean = val 
                if hasattr(b, "_adverts"):
                    b.adverts = b._adverts
                    for a in b.adverts:
                        if a['name'] == 'Sign':
                            a['client'] = 2
                        elif a['name'] == 'Celebrity':
                            a['unique'] = True
                    del b._adverts
                if hasattr(b, "logged_clients"):
                    del b.logged_clients
                if hasattr(b, "_daily_modifier"):
                    b.daily_modifier = b._daily_modifier
                    del b._daily_modifier
                if hasattr(b, "_price"):
                    b.price = b._price
                    del b._price
                if not isinstance(b.stats_log, OrderedDict):
                    b.stats_log = OrderedDict(b.stats_log)
                if b.DIRT_STATES != Building.DIRT_STATES:
                    b.DIRT_STATES = Building.DIRT_STATES
                if hasattr(b, "max_stats"):
                    b.maxdirt = b.max_stats["dirt"]
                    b.maxthreat = b.max_stats["threat"]
                    del b.max_stats
                if hasattr(b, "stats"):
                    b.dirt = b.stats["dirt"]
                    b.threat = b.stats["threat"]
                    if not isinstance(b.dirt, int):
                        b.dirt = int(b.dirt)
                    if not isinstance(b.threat, int):
                        b.threat = int(b.threat)
                    del b.stats
                    for s, v in b.stats_log.items():
                        if not isinstance(v, int):
                            b.stats_log[s] = int(v)
                if hasattr(b, "building_jobs"):
                    b.needs_management = True
                    del b.building_jobs
                if isinstance(getattr(b, "all_clients", None), set):
                    b.all_clients = list(b.all_clients)
                    b.clients = list(b.clients)
                    del b.total_clients
                if hasattr(b, "worker_slots_max"):
                    del b.worker_slots_max
                if hasattr(b, "mod"):
                    del b.mod
                if hasattr(b, "blocked_upgrades"):
                    del b.blocked_upgrades
                if not hasattr(b, "rooms"):
                    b.rooms = 0
                if not hasattr(b, "threat_mod"):
                    if b.location == "Flee Bottom":
                        b.threat_mod = 5
                    elif b.location == "Midtown":
                        b.threat_mod = 2
                    elif b.location == "Richford":
                        b.threat_mod = -1
                    else:
                        raise Exception("{} Building with an unknown location detected!".format(str(b)))
                if b._businesses and not b.allowed_businesses:
                    for i in b._businesses:
                        b.allowed_businesses.append(i.__class__)
                if b.allowed_businesses and isclass(b.allowed_businesses[0]):
                    allowed_business_upgrades = getattr(b, "allowed_business_upgrades", {})
                    allowed_businesses = b._businesses[:]
                    for bclass in b.allowed_businesses:
                        for a in allowed_businesses:
                            if a.__class__ == bclass:
                                if hasattr(a, "_exp_cap_cost"):
                                    a.exp_cap_cost = a._exp_cap_cost
                                    del a._exp_cap_cost
                                if not hasattr(a, "exp_cap_materials"):
                                    a.exp_cap_materials = {}
                                if not hasattr(a, "exp_cap_in_slots"):
                                    a.exp_cap_in_slots = 0
                                if not hasattr(a, "exp_cap_ex_slots"):
                                    a.exp_cap_ex_slots = 0
                                break
                        else:
                            a = bclass()
                            a.building = b
                            allowed_businesses.append(a)
                        allowed_upgrades = allowed_business_upgrades.get(bclass.__name__, [])
                        a.allowed_upgrades = []
                        for au in allowed_upgrades:
                            au = getattr(store, au)
                            au = au()
                            au.building = b
                            a.allowed_upgrades.append(au)
                        upgrades = a.upgrades
                        a.upgrades = []
                        for u in upgrades:
                            for au in a.allowed_upgrades:
                                if au.__class__ == u.__class__:
                                    a.upgrades.append(au)
                                    break
                    b.allowed_businesses = allowed_businesses
                    del b.allowed_business_upgrades
                    allowed_upgrades = b.allowed_upgrades
                    b.allowed_upgrades = []
                    for au in allowed_upgrades:
                        au = au()
                        au.building = b
                        b.allowed_upgrades.append(au)
                    upgrades = b._upgrades
                    b._upgrades = []
                    for u in upgrades:
                        for au in b.allowed_upgrades:
                            if au.__class__ == u.__class__:
                                b._upgrades.append(au)
                                break
            else:
                nb = Building()
                nb.init()
                # copy attributes of b to nb
                nb.id = b.id
                nb.name = b.name
                nb.desc = b.desc
                nb.img = b.img
                nb.tier = b.tier
                nb.price = b.price
                nb._habitable = b._habitable
                nb.rooms = b.rooms
                nb.inhabitants = b.inhabitants
                nb.daily_modifier = b._daily_modifier
                nb.location = b.location

                nb.status = b.status
                nb.given_items = b.given_items
                nb.inventory = b.inventory

                # previous defaults
                nb.maxthreat = 0
                nb.maxdirt = 0
                nb.in_slots_max = 0
                nb.out_slots_max = 0

                if b in hero.buildings:
                    hero.buildings[hero.buildings.index(b)] = nb
                    if hero.home == b:
                        hero.home = nb
                    for c in hero.chars:
                        if c.home == b:
                            c.home = nb
                else:
                    buildings[nb.id] = nb

        if "clearCharacters" in locals():
            for char in itertools.chain([hero], chars.values(), hero.chars, npcs.values()):
                if char.controller == "player":
                    char.controller = None
                if hasattr(char, "_arena_rep"):
                    char.arena_rep = char._arena_rep
                if hasattr(char, "_location"):
                    char.location = char._location
                if hasattr(char.stats, "delayed_stats"):
                    del char.stats.delayed_stats
                if hasattr(char, "besprite"):
                    del char.besprite
                if hasattr(char, "beinx"):
                    del char.beinx
                if hasattr(char, "row"):
                    del char.row
                if hasattr(char, "beteampos"):
                    del char.beteampos
                if hasattr(char, "betag"):
                    del char.betag
                if hasattr(char, "dpos"):
                    del char.dpos
                if hasattr(char, "sopos"):
                    del char.sopos
                if hasattr(char, "cpos"):
                    del char.cpos
                if hasattr(char, "besk"):
                    del char.besk
                if hasattr(char, "allegiance"):
                    del char.allegiance
                if hasattr(char, "beeffects"):
                    del char.beeffects
                if hasattr(char, "dmg_font"):
                    del char.dmg_font
                if hasattr(char, "status_overlay"):
                    del char.status_overlay
                if hasattr(char, "besprite_size"):
                    del char.besprite_size

            #for girl in itertools.chain(jail.chars_list, pytfall.ra.girls.keys()):
            #    if girl.controller == "player":
            #        girl.controller = None

            arena = pytfall.arena
            for fighter in itertools.chain(arena.ladder, arena.arena_fighters.values()):
                if fighter.controller == "player":
                    fighter.controller = None
                if hasattr(fighter, "_arena_rep"):
                    fighter.arena_rep = fighter._arena_rep
                if hasattr(fighter, "_location"):
                    fighter.location = fighter._location

            for team in itertools.chain(arena.teams_2v2, arena.teams_3v3,\
                 arena.dogfights_1v1, arena.dogfights_2v2, arena.dogfights_3v3,\
                 arena.lineup_1v1, arena.lineup_2v2, arena.lineup_3v3):

                    for fighter in team:
                        if fighter.controller == "player":
                            fighter.controller = None
                        if hasattr(fighter, "_arena_rep"):
                            fighter.arena_rep = fighter._arena_rep
                        if hasattr(fighter, "_location"):
                            fighter.location = fighter._location

            for setup in itertools.chain(arena.matches_1v1, arena.matches_2v2, arena.matches_3v3):
                for fighter in itertools.chain(setup[0].members, setup[1].members):
                    if fighter.controller == "player":
                        fighter.controller = None
                    if hasattr(fighter, "_arena_rep"):
                        fighter.arena_rep = fighter._arena_rep
                    if hasattr(fighter, "_location"):
                        fighter.location = fighter._location

            for b in hero.buildings:
                if isinstance(b, Building):
                    for client in b.all_clients:
                        if client.controller == "player":
                            client.controller = None
                        if hasattr(client, "_arena_rep"):
                            client.arena_rep = client._arena_rep
                        if hasattr(client, "_location"):
                            client.location = client._location

    python hide:
        if hasattr(store, "json_fighters"):
            hero._path_to_imgfolder = hero._path_to_imgfolder.replace("npc/arena_males", "fighters/males/warriors")
            hero.update_sayer()

            for fighter in store.male_fighters.values():
                fighter._path_to_imgfolder = fighter._path_to_imgfolder.replace("npc/arena_males", "fighters/males/warriors")
            for fighter in store.female_fighters.values():
                fighter._path_to_imgfolder = fighter._path_to_imgfolder.replace("npc/arena_females", "fighters/females")

            for id, fighter in store.json_fighters.iteritems():
                if fighter.gender == "male":
                    store.male_fighters[id] = fighter
                    fighter._path_to_imgfolder = fighter._path_to_imgfolder.replace("npc/arena_json_adjusted", "fighters/males/json_adjusted")
                else:
                    store.female_fighters[id] = fighter
                    fighter._path_to_imgfolder = fighter._path_to_imgfolder.replace("npc/arena_json_adjusted", "fighters/females/json_adjusted")

            del store.json_fighters

        for obj in pytfall.__dict__.values():
            if isinstance(obj, ItemShop) and not hasattr(obj, "total_items_price"):
                obj.total_items_price = 0

        if hasattr(pytfall, "it"):
            del pytfall.it
        if hasattr(store, "jail"):
            pytfall.jail = store.jail

            del pytfall.jail.focused

            del store.jail

        if hasattr(store, "schools"):
            pytfall.school = store.schools.popitem()[1]
            del store.schools

        if not hasattr(pytfall, "city"):
            pytfall.city = store.locations["City Apartments"]
            pytfall.streets = store.locations["Streets"]
            pytfall.afterlife = store.locations["After Life"]

            del pytfall.city.rooms
            del pytfall.streets.rooms
            del pytfall.afterlife.rooms

            del pytfall.city._habitable
            del pytfall.streets._habitable
            del pytfall.afterlife._habitable

            pytfall.city.daily_modifier = pytfall.city._daily_modifier
            del pytfall.city._daily_modifier

            pytfall.streets.daily_modifier = pytfall.streets._daily_modifier
            del pytfall.streets._daily_modifier

            pytfall.afterlife.daily_modifier = pytfall.afterlife._daily_modifier
            del pytfall.afterlife._daily_modifier

            city = store.locations["City"]
            if hero.location == city:
                hero.location = pytfall.city
            for c in chars.values():
                if c.location == city:
                    c.location = pytfall.city
            del store.locations

    python hide:
        for d in pytfall.world_actions.nest:
            if hasattr(d, "values"):
                for obj in d.values():
                    if not hasattr(obj, "keysym"):
                        obj.keysym = None
            else:
                if not hasattr(d, "keysym"):
                    d.keysym = None

        for d in pytfall.world_actions.locations.values():
            if hasattr(d, "values"):
                for obj in d.values():
                    if not hasattr(obj, "keysym"):
                        obj.keysym = None
            else:
                if not hasattr(d, "keysym"):
                    d.keysym = None

    stop music
    return
