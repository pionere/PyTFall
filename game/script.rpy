init 100 python:
    load_webms()

    pyp = PyTFallopedia()

    tagdb = TagDatabase()

    tl.start("Loading: Mobs")
    mobs = load_mobs()
    tl.end("Loading: Mobs")

    school_courses = load_db_json("school_courses.json")

    arena_chain_fights = Arena.load_chainfights()

    load_aeq_purposes()

    start_image_prediction()

default defeated_mobs = set()
default gazette = Gazette()

label start:
    $ renpy.block_rollback()
    $ locked_random("random") # Just making sure that we have set the variable...

    if DEBUG:
        $ renpy.show_screen("debug_tools")
    $ renpy.show_screen("new_style_tooltip")
    $ gfx_overlay = GFXOverlay()
    $ renpy.show("pf_gfx_overlay", what=gfx_overlay, layer="pytfall")

    python: # Day/Calendar/Names/Menu Extensions and some other defaults.
        # Global variables and loading content:
        day = 1
        calendar = Calendar(day=28, month=2, year=125)
        global_flags = Flags()

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

        # Dungeons (Building (Old))
        tl.start("Loading: Dungeons")
        dungeons = load_dungeons()
        tl.end("Loading: Dungeons")

        # Battle Skills:
        tl.start("Loading: Battle Skills")
        battle_skills = load_battle_skills()
        # tiered (offensive/support) skills for faster access
        tiered_magic_skills = [[],[],[],[],[]] # MAX_MAGIC_TIER = 4, order is not preserved by the user!
        tiered_healing_skills = [[],[],[],[],[]] # MAX_MAGIC_TIER = 4, order is not preserved by the user!
        for s in battle_skills.values():
            if getattr(s, "mob_only", False) or getattr(s, "item_only", False):
                continue
            if s.kind in ("healing", "buff", "revival"):
                tiered_healing_skills[s.tier or 0].append(s)
            elif s.delivery == "magic":
                tiered_magic_skills[s.tier or 0].append(s)
        del s
        tl.end("Loading: Battle Skills")

        # Traits:
        tl.start("Loading/Sorting: Traits")
        traits = load_traits()
        global_flags.set_flag("last_modified_traits", os.path.getmtime(content_path('db/traits')))
        load_traits_context()
        tl.end("Loading/Sorting: Traits")

    python: # Items/Shops: must be after traits and battle skills
        tl.start("Loading/Sorting: Items")
        items = load_items()
        global_flags.set_flag("last_modified_items", os.path.getmtime(content_path('db/items')))

        # Build shops:
        pytfall.init_shops()

    call sort_items_for_gameplay from _call_sort_items_for_gameplay

    $ tl.end("Loading/Sorting: Items")

    $ hero = Player()

    python hide: # Jobs:
        global simple_jobs, traits
        tl.start("Loading: Jobs")
        # This jobs are usually normal, most common type that we have in PyTFall
        simple_jobs = [WhoreJob, StripJob, BarJob, ManagerJob, CleaningJob, GuardJob, WranglerJob, NurseJob, ExplorationTask, StudyingTask, RestTask, AutoRestTask]
        tl.end("Loading: Jobs")

    python: # Ads and Buildings:
        tl.start("Loading: Buildings")
        buildings = load_buildings()
        tl.end("Loading: Buildings")

        # Training/Schools:
        tl.start("Loading: School")
        pytfall.school.add_courses()
        tl.end("Loading: School")

    python: # Tags/Loading Chars/Mobs/Quests.first_day
        tl.start("Loading: All Characters!")
        chars = load_characters("chars", Char)
        #global_flags.set_flag("last_modified_chars", os.path.getmtime(content_path('chars')))
        npcs = load_characters("npcs", NPC)
        #global_flags.set_flag("last_modified_npcs", os.path.getmtime(content_path('npc')))
        fighters = load_characters("fighters", NPC)
        #global_flags.set_flag("last_modified_fighters", os.path.getmtime(content_path('fighters')))
        rchars = load_characters("rchars")
        #global_flags.set_flag("last_modified_rchars", os.path.getmtime(content_path('rchars')))
        tl.end("Loading: All Characters!")

        # Start auto-quests, initialize world_events-cache
        pytfall.world_quests.first_day()
        pytfall.world_events.next_day()

        # tl.start("Loading: Mobs")
        # mobs = load_mobs()
        # tl.end("Loading: Mobs")

    python: # SE (Areas)
        tl.start("Loading: Exploration Areas")
        # pytfall.forest_1 = Exploration()
        fg_areas = load_fg_areas()
        tl.end("Loading: Exploration Areas")

    python: # Girlsmeets:
        tl.start("Loading: GirlsMeets")
        iam = GirlsMeets(world_gossips)
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
                    "Back":
                        jump dev_testing_menu_and_load_mc
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

            af = choice(fighters.values())
            del fighters[af.id]

            hero._path_to_imgfolder = af._path_to_imgfolder
            hero.id = af.id
            hero.init()

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
                del ap, b
            del af

#    jump continue_with_start
#label continue_with_start:
    # Call girls starting labels:
    $ all_chars = chars.values()
    while all_chars:
        $ temp = all_chars.pop()
        $ chars_unique_label = "_".join(["start", temp.id])
        if renpy.has_label(chars_unique_label):
            call expression chars_unique_label from _call_expression_1

    python hide:
        # Clean up globals after loading chars:
        for i in ("chars_unique_label", "char", "girl", "testBrothel", "all_chars", "temp", "utka"):
            if hasattr(store, i):
                delattr(store, i)

    python: # Move to a World AI method:
        tl.start("Loading: Populating Arena")
        pytfall.arena.setup_arena()
        tl.end("Loading: Populating Arena")
        tl.start("Loading: Populating World with RChars")
        pytfall.populate_world()
        tl.end("Loading: Populating World with RChars")
        tl.start("Loading: Populating EmploymentAgency")
        pytfall.ea.populate_chars_list()
        tl.end("Loading: Populating EmploymentAgency")
        tl.start("Loading: Populating SlaveMarket And Jail")
        pytfall.sm.populate_chars_list()
        pytfall.jail.populate_chars_list()
        tl.end("Loading: Populating SlaveMarket And Jail")

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
        # AutoBuy + Items sorting per Tier:
        auto_shops = set(pytfall.shops)
        all_auto_buy_items = []
        tiered_items = [[],[],[],[],[]] # MAX_ITEM_TIER = 4
        for i in items.values():
            if i.pref_class: # i.usable and not i.jump_to_label and i.type != "permanent"
                tiered_items[i.tier or 0].append(i)
                if not auto_shops.isdisjoint(i.locations):
                    all_auto_buy_items.append(i)
        del auto_shops, i
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
                        if DEBUG_LOG:
                            devlog.info("{} - Modified Attr {}: {} -> {} in {}".format(prefix, attr, str(v), str(v2), str(obj_dest)))
                        setattr(obj_dest, attr, v2)
                else:
                    if DEBUG_LOG:
                        devlog.info("{} - Attr Removed: {} from {}".format(prefix, attr, str(obj_dest)))
                    delattr(obj_dest, attr)

            for attr, v2 in vars(obj_src).items():
                if not hasattr(obj_dest, attr):
                    if DEBUG_LOG:
                        devlog.info("{} - New Attr {} for {} with value {}".format(prefix, attr, str(obj_dest), str(v2)))
                    setattr(obj_dest, attr, v2)

    # Updating Databases:
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
                    if DEBUG_LOG:
                        devlog.info("New Trait: {}".format(id))
                else:
                    # Update the existing trait
                    update_object(curr_trait, trait, "Trait")

            del updated_traits
            load_traits_context() 
            tl.end("Updating traits")
            global_flags.set_flag("last_modified_traits", last_modified)

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
                    if DEBUG_LOG:
                        devlog.info("New Item: {}".format(id))
                else:
                    # Update the existing item
                    update_object(curr_item, item, "Item")

            del updated_items
            tl.end("Updating items")
            global_flags.set_flag("last_modified_items", last_modified)
            renpy.call("sort_items_for_gameplay")

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
            updated_npcs = load_characters("npcs", NPC)
            current_npcs = store.npcs
            for id, npc in updated_npcs.items():
                curr_npc = current_npcs.get(id, None)
                if curr_npc is None:
                    # Add new NPC
                    current_npcs[id] = npc
        #            devlog.info("New NPC: {}".format(id))
        #        else:
        #            # Update the existing npc
        #            update_object(curr_npc, npc, "NPC")

        #    tl.end("Updating NPCs")
        #    global_flags.set_flag("last_modified_npcs", last_modified)

        # rChars:
        # always run till tagdb is not separated from load_characters
        # last_modified_rchars = global_flags.get_flag("last_modified_rchars", 0)
        # last_modified = os.path.getmtime(content_path('rchars'))
        if True: #last_modified_rchars < last_modified:
        #    tl.start("Updating rchars")
            store.rchars = load_characters("rchars")
        #    tl.end("Updating rchars")
        #    global_flags.set_flag("last_modified_rchars", last_modified)

        # Arena Chars:
        # always run till tagdb is not separated from load_characters
        # last_modified_fighters = global_flags.get_flag("last_modified_fighters", 0)
        # last_modified = os.path.getmtime(content_path('fighters'))
        if True: #last_modified_rchars < last_modified:
        #    tl.start("Updating Fighters")
            current_fighters = getattr(store, "fighters", None)
            if current_fighters is None:
                # FIXME Save-Load Compatibility -> remove this part!
                for pre_folder, new_folder in [("npc/shopkeepers", "npcs/shopkeepers"), ("npc/animals", "npcs/animals"), ("npc/thugs", "npcs/thugs"), ("npc/guards", "npcs/guards")]: 
                    pre_folder = os.path.normpath(pre_folder)
                    new_folder = os.path.normpath(new_folder)
                    for npc in store.npcs.itervalues():
                        npc._path_to_imgfolder = os.path.normpath(npc._path_to_imgfolder).replace(pre_folder, new_folder)

                for npc in store.npcs.itervalues():
                    npc.clear_img_cache()

                current_fighters = dict()
                if hasattr(store, "json_fighters"):
                    folders = [("npc/arena_males", "fighters/males"), ("npc/arena_females", "fighters"), ("npc/arena_json_adjusted", "fighters/json_adjusted")]
                    for id, fighter in store.json_fighters.iteritems():
                        current_fighters[id] = fighter
                    del store.json_fighters
                else:
                    folders = [("fighters/males/warriors", "fighters/males"), ("fighters/females", "fighters")]
                    for id, fighter in store.female_fighters.iteritems():
                        current_fighters[id] = fighter
                    for id, fighter in store.male_fighters.iteritems():
                        current_fighters[id] = fighter
                    del store.male_fighters
                    del store.female_fighters

                arena = pytfall.arena
                for pre_folder, new_folder in folders:
                    pre_folder = os.path.normpath(pre_folder)
                    new_folder = os.path.normpath(new_folder)
                    hero._path_to_imgfolder = os.path.normpath(hero._path_to_imgfolder).replace(pre_folder, new_folder)

                    for fighter in current_fighters.itervalues():
                        fighter._path_to_imgfolder = os.path.normpath(fighter._path_to_imgfolder).replace(pre_folder, new_folder)

                    for fighter in itertools.chain(arena.ladder, arena.arena_fighters.itervalues()):
                        if fighter.__class__ == rChar:
                            continue
                        fighter._path_to_imgfolder = os.path.normpath(fighter._path_to_imgfolder).replace(pre_folder, new_folder)

                    for team in itertools.chain(arena.teams_2v2, arena.teams_3v3,\
                         arena.dogfights_1v1, arena.dogfights_2v2, arena.dogfights_3v3,\
                         arena.lineup_1v1, arena.lineup_2v2, arena.lineup_3v3):

                            for fighter in team:
                                if fighter.__class__ == rChar:
                                    continue
                                fighter._path_to_imgfolder = os.path.normpath(fighter._path_to_imgfolder).replace(pre_folder, new_folder)

                hero.clear_img_cache()
                hero.update_sayer()
                store.fighters = current_fighters

            updated_fighters = load_characters("fighters", NPC)
            updated_fighters.pop(hero.id, None)
            for id, fighter in updated_fighters.items():
                curr_fighter = current_fighters.get(id, None)
                if curr_fighter is None:
                    # Add new fighter
                    current_fighters[id] = fighter
        #    tl.end("Updating Fighters")
        #    global_flags.set_flag("last_modified_fighters", last_modified)

        # lazy init BE_Core (might not be the best solution...)
        if not BE_Core.BDP:
            BE_Core.init()

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

        if hasattr(store, "employment_agency_chars"):
            eachars = store.employment_agency_chars
            if "Caster" not in eachars:
                temp = [c for cl in eachars.values() for c in cl]
                del eachars["Healer"]
                for v in eachars.itervalues():
                    v[:] = []
                eachars["Caster"] = []
                for c in temp:
                    for occ in c.gen_occs:
                        eachars[occ].append(c)
                store.pytfall.rc_free_pop_distr["Caster"] = store.pytfall.rc_free_pop_distr["Healer"]
                del store.pytfall.rc_free_pop_distr["Healer"]
            ea = EmploymentAgency()
            ea.chars = eachars
            ea.restock_day = store.employment_agency_reroll_day
            pytfall.ea = ea
            del store.employment_agency_reroll_day, store.employment_agency_chars

        for d in store.dungeons.values():
            event = getattr(d, "event", {})
            for e in event.values():
                temp = None
                for a in e:
                    func = a.get("function", "")
                    if func == "dungeon.__delattr__":
                        temp = a
                    elif func == "renpy.jump":
                        a["function"] = "exit" 
                    elif "dungeon." in func:
                        a["function"] = func.replace("dungeon.", "")
                if temp is not None:
                    e.remove(temp)
            hs = getattr(d, "spawn_hotspots", {})
            for s in hs.values():
                actions = s.get("actions", {})
                for a in actions:
                    func = a.get("function", "")
                    if func == "dungeon_combat":
                        a["function"] = "combat"
            hs = getattr(d, "item_hotspots", {})
            for s in hs.values():
                actions = s.get("actions", {})
                for a in actions:
                    func = a.get("function", "")
                    if func == "dungeon_grab_item":
                        a["function"] = "grab_item"

        if hasattr(store, "storyi_treasures") and isinstance(store.storyi_treasures, list):
            hero.del_flag("been_in_old_ruins")
        if global_flags.has_flag("time_healing_day"):
            hero.set_flag("dnd_time_healing_day")
            global_flags.del_flag("time_healing_day")
        if global_flags.has_flag("waitress_chosen_today"):
            global_flags.set_flag("waitress_cafe", [global_flags.flag("waitress_chosen_today"), store.cafe_waitress_who])
            global_flags.del_flag("waitress_chosen_today")
            del store.cafe_waitress_who

        pytfall.maps = OnScreenMap()

        for s in store.battle_skills.values():
            if isinstance(s, DefenceBuffSpell):
                if not hasattr(s, "event_duration"):
                    s.event_duration = (5, 8)
            elif isinstance(getattr(s, "event_duration", None), int):
                s.event_duration = (s.event_duration-1, s.event_duration+1)
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

        if isinstance(store.tiered_items, dict):
            store.tiered_items = [[],[],[],[],[]] # MAX_ITEM_TIER = 4
            for i in store.items.values():
                store.tiered_items[i.tier or 0].append(i)

        if isinstance(store.tiered_magic_skills, dict):
            store.tiered_magic_skills = [[],[],[],[],[]] # MAX_MAGIC_TIER = 4, order is not preserved by the user!
            store.tiered_healing_skills = [[],[],[],[],[]] # MAX_MAGIC_TIER = 4, order is not preserved by the user!
            for s in store.battle_skills.values():
                if getattr(s, "mob_only", False) or getattr(s, "item_only", False):
                    continue
                if s.kind in ("healing", "buff", "revival"):
                    store.tiered_healing_skills[s.tier or 0].append(s)
                elif s.delivery == "magic":
                    store.tiered_magic_skills[s.tier or 0].append(s)

        if not hasattr(pytfall.arena, "df_count"):
            pytfall.arena.df_count = 0
            pytfall.arena.hero_match_result = None 
        if hasattr(pytfall.arena, "setup"):
            del pytfall.arena.setup
        if hasattr(pytfall.arena, "seen_report"):
            del pytfall.arena.seen_report
        if hasattr(pytfall.arena, "chain_fights"):
            del pytfall.arena.chain_fights
            del pytfall.arena.chain_fights_order
            del pytfall.arena.chain_fights_order_portraits
        if hasattr(pytfall.arena, "arena_fighters"):
            del pytfall.arena.arena_fighters

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
        if hero.eqsave and not hasattr(hero.eqsave[0], "name"):
            clearCharacters = True
        if hasattr(hero.fin, "stored_upkeep"):
            clearCharacters = True
        if hasattr(hero, "autocontrol"):
            del hero.autocontrol
            clearCharacters = True
        if "riding" not in hero.stats.skills:
            clearCharacters = True
        if not hasattr(hero.stats, "imin"):
            clearCharacters = True
        if hero.front_row.__class__ != int:
            clearCharacters = True
        if hasattr(hero, "baseAP"):
            clearCharacters = True
        if not hasattr(hero, "PP"):
            hero.PP = store.gm.gm_points * 25
            del store.gm.gm_points
            clearCharacters = True
        if hero.get_max("fame") != 1000:
            clearCharacters = True
        if isinstance(simple_jobs, dict):
            if isinstance(simple_jobs["Manager"], Manager):
                pmj = simple_jobs["Manager"]
                mj = ManagerJob()
                simple_jobs[mj.id] = mj
                for b in hero.buildings:
                    if hasattr(b, "jobs") and pmj in b.jobs:
                        b.jobs.remove(pmj)
                        b.jobs.add(mj)
                ej = ExplorationJob()
                simple_jobs[ej.id] = ej
                clearCharacters = True
            if "Study" not in simple_jobs:
                simple_jobs["Study"] = StudyingTask
            if "Wrangler" not in simple_jobs:
                simple_jobs["Wrangler"] = WranglerJob
            for k, v in simple_jobs.items():
                if hasattr(v, "jp_cost"):
                    del v.jp_cost
                if isinstance(v, Job):
                    clearCharacters = True
                    v = v.__class__
                    if v == ExplorationJob:
                        v = ExplorationTask
                    elif v == StudyingJob:
                        v = StudyingTask
                    elif v == Rest:
                        v = RestTask
                    elif v == AutoRest:
                        v = AutoRestTask
                    if hasattr(v, "occupation_traits"):
                        del v.occupation_traits
                    if hasattr(v, "occupations"):
                        del v.occupations
                    if hasattr(v, "allowed_status"):
                        del v.allowed_status
                    simple_jobs[k] = v

        store.bm_mid_frame_mode = None

        if hasattr(store, "businesses"):
            buildings.update(store.businesses)
            del store.businesses
        if hasattr(store, "adverts"):
            del store.adverts

        if hasattr(store, "gm") and not hasattr(store.gm, "coords"):
            store.gm.coords = store.coords
            del store.coords

        if not hasattr(TapBeer, "ID"):
            load_buildings()

        for b in itertools.chain(hero.buildings, buildings.values()):
            if isinstance(b, Building):
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
                if hasattr(b, "_businesses"):
                    b.businesses = b._businesses
                    del b._businesses
                if hasattr(b, "_upgrades"):
                    b.upgrades = b._upgrades
                    del b._upgrades
                if not isinstance(b.stats_log, OrderedDict):
                    b.stats_log = OrderedDict(b.stats_log)
                if hasattr(b, "DIRT_STATES"):
                    del b.DIRT_STATES
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
                if hasattr(b, "threat_mod"):
                    del b.threat_mod
                if not hasattr(b, "auto_guard"):
                    b.auto_guard = 0
                if b.businesses and not b.allowed_businesses:
                    for i in b.businesses:
                        b.allowed_businesses.append(i.__class__)
                if b.allowed_businesses and isclass(b.allowed_businesses[0]):
                    allowed_business_upgrades = getattr(b, "allowed_business_upgrades", {})
                    allowed_businesses = b.businesses[:]
                    for bclass in b.allowed_businesses:
                        for a in allowed_businesses:
                            if a.__class__ == bclass:
                                if hasattr(a, "_exp_cap_cost"):
                                    a.exp_cap_cost = a._exp_cap_cost
                                    del a._exp_cap_cost
                                if a.expands_capacity:
                                    if not hasattr(a, "exp_cap_materials"):
                                        a.exp_cap_materials = {}
                                    if not hasattr(a, "exp_cap_in_slots"):
                                        a.exp_cap_in_slots = 0
                                    if not hasattr(a, "exp_cap_ex_slots"):
                                        a.exp_cap_ex_slots = 0
                                if isinstance(getattr(a, "jobs", None), set):
                                    a.jobs = list(a.jobs)
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
                    upgrades = b.upgrades
                    b.upgrades = []
                    for u in upgrades:
                        for au in b.allowed_upgrades:
                            if au.__class__ == u.__class__:
                                b.upgrades.append(au)
                                break
                if hasattr(b, "mlog"):
                    del b.mlog
                if hasattr(b, "manager"):
                    del b.manager
                if b.needs_manager and not hasattr(b, "init_pep_talk"):
                    b.init_pep_talk = True
                    b.cheering_up = True
                    b.asks_clients_to_wait = True
                    b.help_ineffective_workers = True # Bad performance still may get a payout.
                    b.works_other_jobs = False
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
            if hero.has_flag("mor_fish_dice"):
                q = pytfall.world_quests.quest_instance("Fishery")
                if q.stage != 0:
                    if q.stage == 1:
                        q.set_flag("fish", store.mor_fish)
                        q.set_flag("num_fish", store.mor_quantity)
                    q.prompts[0] = q.prompts[0].replace("[mor_fish.id]", "%s" % store.mor_fish.id).replace("[mor_quantity]", "%d" % store.mor_quantity)
                if hero.flag("mor_fish_dice") == day:
                    hero.set_flag("dnd_mor_fish_quest", (store.mor_fish, store.mor_quantity))

                hero.del_flag("mor_fish_dice")
                hero.del_flag("mor_fish_quest")

                del store.mor_fish
                del store.mor_quantity

            if hero.has_flag("dark_forest_rested_today"):
                if hero.flag("dark_forest_rested_today") == day:
                    hero.set_flag("dnd_dark_forest_rested")
                hero.del_flag("dark_forest_rested_today")

            if hero.has_flag("dark_forest_met_bandits"):
                if hero.flag("dark_forest_met_bandits") == day:
                    hero.set_flag("dnd_dark_forest_bandits")
                hero.del_flag("dark_forest_met_bandits")

            if hero.has_flag("dark_forest_met_girl"):
                if hero.flag("dark_forest_met_girl") == day:
                    hero.set_flag("dnd_dark_forest_girl")
                hero.del_flag("dark_forest_met_girl")

            if hero.has_flag("dark_forest_found_river"):
                if hero.flag("dark_forest_found_river") == day:
                    hero.set_flag("dnd_dark_forest_river")
                hero.del_flag("dark_forest_found_river")

            if hero.has_flag("ate_in_cafe"):
                if hero.flag("ate_in_cafe") == day:
                    hero.set_flag("dnd_ate_in_cafe")
                hero.del_flag("ate_in_cafe")

            if hero.has_flag("rest_in_tavern"):
                if hero.flag("rest_in_tavern") == day:
                    hero.set_flag("dnd_rest_in_tavern")
                hero.del_flag("rest_in_tavern")

            if hero.has_flag("fought_in_tavern"):
                if hero.flag("fought_in_tavern") == day:
                    hero.set_flag("dnd_fought_in_tavern")
                hero.del_flag("fought_in_tavern")

            if hero.has_flag("storyi_rest"):
                if hero.flag("storyi_rest") == day:
                    hero.set_flag("dnd_storyi_rest")
                hero.del_flag("storyi_rest")

            if hero.has_flag("storyi_heal"):
                if hero.flag("storyi_heal") == day:
                    hero.set_flag("dnd_storyi_heal")
                hero.del_flag("storyi_heal")

            if hero.has_flag("rest_at_beach"):
                if hero.flag("rest_at_beach") == day:
                    hero.set_flag("dnd_rest_at_beach")
                hero.del_flag("rest_at_beach")
            
            if hero.has_flag("constitution_bonus_from_swimming_at_beach"):
                global_flags.set_flag("constitution_bonus_from_swimming_at_beach", hero.flag("constitution_bonus_from_swimming_at_beach"))
                hero.del_flag("constitution_bonus_from_swimming_at_beach")

            if hero.has_flag("vitality_bonus_from_diving_at_beach"):
                global_flags.set_flag("vitality_bonus_from_diving_at_beach", hero.flag("vitality_bonus_from_diving_at_beach"))
                hero.del_flag("vitality_bonus_from_diving_at_beach")
            global_flags.del_flag("swam_city_beach")

            if hero.has_flag("visited_deep_forest"):
                global_flags.set_flag("visited_deep_forest")
                hero.del_flag("visited_deep_forest")

            if hero.has_flag("found_old_ruins"):
                global_flags.set_flag("found_old_ruins")
                hero.del_flag("found_old_ruins")

            if hero.has_flag("defeated_boss_1"):
                global_flags.set_flag("defeated_boss_1")
                hero.del_flag("defeated_boss_1")

            if hero.has_flag("been_in_old_ruins"):
                global_flags.set_flag("been_in_old_ruins")
                hero.del_flag("been_in_old_ruins")

            arena = pytfall.arena
            all_live_chars = set([hero] + chars.values() + hero.chars + npcs.values())
            for fighter in itertools.chain(arena.ladder, store.fighters.values()):
                all_live_chars.add(fighter)
            for team in itertools.chain(arena.teams_2v2, arena.teams_3v3,\
                 arena.dogfights_1v1, arena.dogfights_2v2, arena.dogfights_3v3,\
                 arena.lineup_1v1, arena.lineup_2v2, arena.lineup_3v3):

                    for fighter in team:
                        all_live_chars.add(fighter)
            for setup in itertools.chain(arena.matches_1v1, arena.matches_2v2, arena.matches_3v3):
                for fighter in itertools.chain(setup[0].members, setup[1].members):
                    all_live_chars.add(fighter)

            for c in hero.friends.copy():
                if c not in all_live_chars:
                    hero.friends.discard(c)
            for c in hero.lovers.copy():
                if c not in all_live_chars:
                    hero.lovers.discard(c)
            for char in all_live_chars:
                if hasattr(char, "inventory"):
                    outfits = char.eqsave
                    char.eqsave = []
                    for o in outfits:
                        if any(o.values()):
                            if not "name" in o:
                                o["name"] = "Outfit %d" % (len(char.eqsave)+1)
                            char.eqsave.append(o)
                        for k, i in o.iteritems():
                            if i is False:
                                o[k] = None
                    for k, i in char.eqslots.iteritems():
                        if i is False:
                            char.eqslots[k] = None
                    if char.last_known_aeq_purpose == "":
                        char.last_known_aeq_purpose = None
                if not hasattr(char, "PP"):
                    char.PP = char.jobpoints
                    del char.jobpoints
                    if char not in hero.chars:
                        char.baseAP += 1 

                if hasattr(char, "baseAP"):
                    char.basePP = char.baseAP*100 # PP_PER_AP
                    del char.baseAP
                    char.setPP = char.setAP*100 # PP_PER_AP
                    del char.setAP
                    char.PP += char.AP*100 # PP_PER_AP
                    del char.AP

                if char.has_flag("drunk_counter"):
                    char.set_flag("dnd_drunk_counter", char.get_flag("drunk_counter"))
                    char.del_flag("drunk_counter")
                if char.has_flag("food_poison_counter"):
                    char.set_flag("dnd_food_poison_counter", char.get_flag("food_poison_counter"))
                    char.del_flag("food_poison_counter")
                if char.has_flag("exp_extractor"):
                    if char.flag("exp_extractor") == day:
                        char.set_flag("dnd_exp_extractor")
                    char.del_flag("exp_extractor")
                if char.has_flag("gm_praise_day"):
                    if char.flag("gm_praise_day") == day:
                        char.set_flag("dnd_flag_interactions_praise", 1)
                    char.del_flag("gm_praise_day")
                if char.has_flag("gm_char_proposed_sex"):
                    char.del_flag("gm_char_proposed_sex")

                for flag in ("flag_interactions_general","flag_girl_interactions_aboutjob","flag_interactions_howshefeels","flag_interactions_abouther",
                             "flag_interactions_greeting", "flag_interactions_kiss_lesbian_refuses", "flag_interactions_kiss", "harrasment_after_battle",
                             "flag_interactions_insult","flag_interactions_girlfriend","flag_interactions_hireforsex", "flag_interactions_sex",
                             "flag_interactions_hug", "flag_interactions_slapbutt", "flag_interactions_grabbreasts", "flag_interactions_general",
                             "flag_interactions_aboutoccupation", "flag_interactions_interests","flag_interactions_flirt"):
                    if char.has_flag(flag):
                        if char.flag(flag)["day"] == day:
                            char.set_flag("dnd_" + flag, char.flag(flag)["times"])
                        char.del_flag(flag)

                if char.has_flag("dnd_flag_girl_interactions_aboutjob"):
                    char.set_flag("dnd_flag_interactions_aboutjob", char.get_flag("dnd_flag_girl_interactions_aboutjob"))
                    char.del_flag("dnd_flag_girl_interactions_aboutjob")

                if char.has_flag("flag_interactions_giftmoney"):
                    if char.flag("flag_interactions_giftmoney")+3 >= day:
                        char.set_flag("cnd_flag_interactions_giftmoney", char.flag("flag_interactions_giftmoney")+3)
                    char.del_flag("flag_interactions_giftmoney")

                if char.has_flag("flag_interactions_askmoney"):
                    if char.flag("flag_interactions_askmoney")+7 >= day:
                        char.set_flag("cnd_flag_interactions_askmoney", char.flag("flag_interactions_askmoney")+7)
                    char.del_flag("flag_interactions_askmoney")

                if char.has_flag("last_shopping_day"):
                    if char.flag("last_shopping_day")+5 >= day:
                        char.set_flag("cnd_shopping_day", char.flag("last_shopping_day")+5)
                    char.del_flag("last_shopping_day")

                if char.has_flag("_day_countdown_interactions_gifts"):
                    char.set_flag("cnd_interactions_gifts", day+char.flag("_day_countdown_interactions_gifts")-1)
                    char.del_flag("_day_countdown_interactions_gifts")

                if char.has_flag("_day_countdown_interactions_blowoff"):
                    char.set_flag("cnd_interactions_blowoff", day+char.flag("_day_countdown_interactions_blowoff")-1)
                    char.del_flag("_day_countdown_interactions_blowoff")

                for flag in char.flags.keys():
                    if flag.startswith("_day_countdown"):
                        v = char.flag(flag)
                        char.flags.del_flag(flag)
                        flag = flag.replace("_day_countdown", "cnd_item")
                        char.flags.set_flag(flag, day+v-1)

                if isinstance(char.workplace, Building) and char not in char.workplace.all_workers:
                    char.workplace.all_workers.append(char)
                if char.controller == "player":
                    char.controller = None
                if hasattr(char, "_arena_rep"):
                    char.arena_rep = char._arena_rep
                    del char._arena_rep
                if hasattr(char, "_location"):
                    char.location = char._location
                    del char._location
                if hasattr(char, "_action"):
                    action = char._action
                    if action == "Arena Combat":
                        action = None
                    elif getattr(action, "id", None) == "Manager":
                        action = simple_jobs["Manager"]
                    prev_action = char.previousaction
                    if not prev_action:
                        prev_action = None
                    elif getattr(prev_action, "id", None) == "Manager":
                        prev_action = simple_jobs["Manager"]
                    if action.__class__ in [AutoRest, Rest, ExplorationJob, SchoolCourse]:
                        char._job = prev_action
                        char._task = action
                    else:
                        char._job = action
                        char._task = None
                    del char._action
                    del char.previousaction
                if char.location == pytfall.arena:
                    char.location = None
                    char.arena_active = True
                if hasattr(char, "breasts"):
                    char.gents = char.breasts
                    del char.breasts
                if hasattr(char, "likes"):
                    del char.likes
                if hasattr(char, "dislikes"):
                    del char.dislikes
                if hasattr(char, "init_traits"):
                    del char.init_traits
                if char.__class__ in [Char, rChar] and not hasattr(char, "preferences"):
                    char.preferences = dict([(p, randint(0, 100)/100.0) for p in STATIC_CHAR.PREFS])
                if not "affection" in char.stats:
                    char.stats.stats["affection"] = 0
                    char.stats.imod["affection"] = 0
                    char.stats.min["affection"] = -1000
                    char.stats.max["affection"] = 1000
                    char.stats.lvl_max["affection"] = 1000
                if "riding" not in char.stats.skills:
                    char.stats.skills["riding"] = [0, 0]
                    char.stats.skills_multipliers["riding"] = [1, 1, 1]
                if not hasattr(char.stats, "imin"):
                    char.stats.imin = dict()
                    char.stats.imax = dict()
                    for stat in char.stats:
                        char.stats.imin[stat] = 0
                        char.stats.imax[stat] = 0
                    curr_equipped_items = char.eqslots.copy()
                    # Go over all slots and unequip items:
                    for s in store.EQUIP_SLOTS:
                        if s == "ring":
                            for r in ["ring", "ring1", "ring2"]:
                                char.unequip(slot=r, aeq_mode=True)
                        elif s != "consumable":
                            char.unequip(slot=s, aeq_mode=True)
                    for stat, value in char.stats.imin.iteritems():
                        if value != 0:
                            char.stats.min[stat] += value
                            char.stats.imin[stat] = 0
                    for stat, value in char.stats.imax.iteritems():
                        if value != 0:
                            char.stats.max[stat] += value
                            char.stats.imax[stat] = 0
                    for stat, value in char.stats.imod.iteritems():
                        if value != 0:
                            char.stats.stats[stat] += value
                            char.stats.imod[stat] = 0
                    # Re-equip the original items:
                    char.eqslots = curr_equipped_items
                    for slot, item in curr_equipped_items.iteritems():
                        if not item:
                            continue
                        if slot != "misc":
                            char.apply_item_effects(item) # Apply item effects
                        char.inventory.remove(item) # Remove item from the inventory
                if char.get_max("fame") != 1000:
                    char.stats.max["fame"] = char.stats.lvl_max["fame"] = 1000
                    char.stats.max["reputation"] = char.stats.lvl_max["reputation"] = 1000
                if hasattr(char, "price"):
                    del char.price
                if hasattr(char, "days_depressed"):
                    del char.days_depressed
                if hasattr(char, "exp_bar"):
                    del char.exp_bar
                if char.front_row.__class__ != int:
                    char.front_row = 1 if char.front_row else 0
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
                if hasattr(char, "_available"):
                    del char._available
                if hasattr(char, "alive"):
                    del char.alive
                if hasattr(char, "combat_stats"):
                    del char.combat_stats
                if hasattr(char, "arena_stats"):
                    del char.arena_stats
                if hasattr(char.fin, "stored_upkeep"):
                    char.calc_upkeep()
                    del char.fin.stored_upkeep
                if getattr(char, "runaway_look_event", None) == "escaped_girl_recapture":
                    del char.runaway_look_event

                if char.has_flag("days_in_game"):
                    if isinstance(char, rChar):
                        char.set_flag("from_day_in_game", day - char.flag("days_in_game"))
                    char.del_flag("days_in_game")

                char.magic_skills.items = {k: v for k, v in char.magic_skills.items.items() if v != 0}
                char.attack_skills.items = {k: v for k, v in char.attack_skills.items.items() if v != 0}

                char.traits.blocked_traits = set([traits[t] if isinstance(t, basestring) else t for t in char.traits.blocked_traits])

                if isinstance(char._task, Job):
                    char._task = simple_jobs[char._task.id]
                if isinstance(char._job, Job):
                    char._job = simple_jobs[char._job.id]
                for e in char.effects.values():
                    if e.duration is not None and e.name not in ["Poisoned", "Unstable", "Down with Cold", "Food Poisoning", "Injured"]:
                        e.duration = None
            #for girl in itertools.chain(jail.chars_list, pytfall.ra.girls.keys()):
            #    if girl.controller == "player":
            #        girl.controller = None

            for b in hero.buildings:
                if hasattr(b, "all_clients"):
                    for client in b.all_clients:
                        if client.controller == "player":
                            client.controller = None
                        if hasattr(client, "_arena_rep"):
                            client.arena_rep = client._arena_rep
                            del client._arena_rep
                        if hasattr(client, "_location"):
                            client.location = client._location
                            del client._location
                        if not "affection" in fighter.stats:
                            fighter.stats.stats["affection"] = 0
                            fighter.stats.imod["affection"] = 0
                            fighter.stats.min["affection"] = -1000
                            fighter.stats.max["affection"] = 1000
                            fighter.stats.lvl_max["affection"] = 1000

    python hide:
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
            if not hasattr(pytfall.school, "students"):
                pytfall.school.students = {}
            del store.schools
        if not hasattr(pytfall.school, "tier_filter"):
            pytfall.school.tier_filter = hero.tier
            pytfall.school.type_filter = {"xxx", "combat", None}
        if isinstance(pytfall.school.img, im.Image):
            pytfall.school.img = pytfall.school.img.filename

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

            pytfall.jail.daily_modifier = pytfall.jail._daily_modifier
            del pytfall.jail._daily_modifier

            pytfall.sm.daily_modifier = pytfall.sm._daily_modifier
            del pytfall.sm._daily_modifier

            cities = (store.locations["City"], pytfall.city)
            for c in itertools.chain([hero], chars.values(), hero.chars, npcs.values()):
                if c.location in cities:
                    c.location = None
                if c.location == pytfall.sm:
                    c.location = None
                if c.location == RunawayManager.LOCATION:
                    c.location = pytfall.ra
                if c.workplace == pytfall.school:
                    c._workplace = None
                    course = c.action
                    c._task = simple_jobs["Study"]
                    course.remove_student(c)
                    pytfall.school.add_student(c, course)

            if hasattr(pytfall.sm, "type"):
                del pytfall.sm.type
            if hasattr(pytfall.sm, "girl"):
                del pytfall.sm.girl
                pytfall.sm.index = 0
                del pytfall.sm.blue_girls
                pytfall.sm.blue_slaves = list()

                pytfall.jail.index = None
                pytfall.jail.slaves = list()            # caught runaway slaves currently for sale
                pytfall.jail.slave_index = [0,]         # the selected slave
                pytfall.jail.slave_restock_day = day

                pytfall.jail.captures = list()          # captured characters from SE
                pytfall.jail.capt_index = [0,]          # the selected captured char

                pytfall.jail.cells = list()             # civilian prisoners
                pytfall.jail.cell_index = [0,]          # the selected prisoner
                pytfall.jail.cell_restock_day = day

            del store.locations

        if not hasattr(pytfall.ra, "chars"):
            del pytfall.ra.girls
            pytfall.ra.chars = dict()

        if not isinstance(pytfall.afterlife, AfterLife):
            afterlife = pytfall.afterlife
            pytfall.afterlife = AfterLife()
            for char in afterlife.inhabitants:
                pytfall.afterlife.add_inhabitant(char)

    python hide:
        if getattr(store, "chars_list_state", None):
            cls = store.chars_list_state
            if not hasattr(cls.source, "sorting_desc"):
                cls.source.sorting_desc = True

        if hasattr(store, "NextDayEvents") and not isinstance(store.NextDayEvents, NextDayStats):
            nds = NextDayStats()
            nds.event_list = store.NextDayEvents
            nds.unassigned_chars = 0
            nds.prepare_summary()
            store.NextDayEvents = nds

            for i in ("aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "black", "blanchedalmond",
                      "blue", "blueviolet", "brown, burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue",
                      "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey",
                      "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen",
                      "darkslateblue", "darkslategray", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deepskyblue",
                      "dimgray", "dimgrey", "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite",
                      "gold", "goldenrod", "gray", "green", "greenyellow", "grey", "honeydew", "hotpink", "indianred", "indigo", "ivory",
                      "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan",
                      "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen",
                      "lightskyblue", "lightslategray", "lightslategrey", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen",
                      "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen",
                      "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream",
                      "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid",
                      "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum",
                      "powderblue", "purple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen",
                      "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "snow", "springgreen",
                      "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke",
                      "yellow", "yellowgreen"):

                for event in NextDayEvents.event_list:
                    if isinstance(event.txt, list):
                        for idx, t in enumerate(event.txt):
                            event.txt[idx] = t.replace("[%s]" % i, i)
                    elif isinstance(event.txt, basestring):
                        event.txt = event.txt.replace("[%s]" % i, i)
                    else:
                        raise Exception("What? %s" % event.txt.__class__)

                if hasattr(store, i):
                    delattr(store, i)

        for b in chain(hero.buildings, buildings.itervalues()):
            if not hasattr(b, "in_construction_upgrades"):
                b.in_construction_upgrades = []
            for c in getattr(b, "all_clients", []):
                if not hasattr(c, "modthreat"):
                    c.dirtmod = get_linear_value_of(c.rank, 1, 1.0, 7, .5) # MAX_RANK = 7, MIN_RANK = 1
                    c.threatmod = get_linear_value_of(c.rank, 1, 1.0, 7, .5) # MAX_RANK = 7, MIN_RANK = 1
                    if "Aggressive" in c.traits:
                        c.threatmod *= 4
            jobs_changed = False
            for u in b.allowed_businesses:
                if hasattr(u, "intro_string"):
                    u.intro_string = u.__class__.intro_string
                if hasattr(u, "log_intro_string"):
                    del u.log_intro_string
                if hasattr(u, "clients"):
                    del u.clients
                if hasattr(u, "is_running"):
                    del u.is_running
                if hasattr(u, "action"):
                    del u.action
                if hasattr(u, "interrupt"):
                    del u.interrupt
                if hasattr(u, "active_workers") and isinstance(u, OnDemandBusiness):
                    del u.active_workers
                if not hasattr(u, "job_effectiveness_mod"):
                    jem = 0
                    for up in u.upgrades:
                        jem += getattr(up, "job_effectiveness_mod", 0)
                    u.job_effectiveness_mod = jem
                if hasattr(u, "allowed_business_upgrades"):
                    del u.allowed_business_upgrades
                if u.expands_capacity:
                    if not hasattr(u, "exp_cap_duration"):
                        u.exp_cap_duration = None
                    if not hasattr(u, "base_capacity"):
                        cap = u.capacity
                        u.in_slots += cap*u.exp_cap_in_slots
                        u.ex_slots += cap*u.exp_cap_ex_slots
                        u.base_capacity = cap

                for up in u.upgrades:
                    if not hasattr(up, "duration"):
                        up.duration = None
                for idx, ub in enumerate(u.jobs):
                    if isinstance(ub, Job):
                        u.jobs[idx] = simple_jobs[ub.id]
                        jobs_changed = True
            if jobs_changed:
                b.normalize_jobs()

        for b in hero.get_guild_businesses():
            for t in b.explorers:
                for l in t.logs:
                    if hasattr(l, "item"):
                        item = l.item
                        if item is not None:
                            l.event_object = item
                            l.suffix = item.type
                        del l.item
                    if hasattr(l, "battle_log"):
                        log = l.battle_log
                        if log is not None:
                            l.event_object = log
                        del l.battle_log
                    if not hasattr(l, "event_object"):
                        l.event_object = None
                    if hasattr(l, "found_items"):
                        del l.found_items
        for a in fg_areas.values():
            if not hasattr(a, "logs"):
                continue
            for l in a.logs:
                if hasattr(l, "battle_log"):
                    log = l.battle_log
                    if log is not None:
                        l.event_object = log
                    del l.battle_log
                if hasattr(l, "item"):
                    item = l.item
                    if item is not None:
                        l.event_object = item
                        l.suffix = item.type
                    del l.item
                if not hasattr(l, "event_object"):
                    l.event_object = None
                if hasattr(l, "found_items"):
                    del l.found_items

        for e in pytfall.world_events.events:
            for i, c in enumerate(e.simple_conditions):
                if ".magic" in c:
                    e.simple_conditions[i] = c.replace(".magic", ".get_stat('magic')")
            for i, c in enumerate(e.run_conditions):
                if "world_quests.get" in c:
                    e.run_conditions[i] = c.replace("world_quests.get", "world_quests.quest_instance")
            if hasattr(e, "enable_on"):
                del e.enable_on
            if hasattr(e, "disabled"):
                del e.disabled
            if hasattr(e, "quest"):
                del e.quest
            if hasattr(e, "label_cache"):
                del e.label_cache
            if hasattr(e, "last_executed"):
                del e.last_executed

        for q in pytfall.world_quests.quests:
            if isinstance(q.flags, list):
                q.flags = dict([(p, True) for p in q.flags])

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

        if isinstance(store.simple_jobs, dict):
            store.simple_jobs = [v for v in store.simple_jobs.values()]
        if hasattr(pytfall.world_events, "garbage"):
            temp = pytfall.world_events.garbage
            pytfall.world_events.events[:] = [e for e in pytfall.world_events.events if e not in temp]
            del pytfall.world_events.garbage
        if hasattr(pytfall, "desc"):
            del pytfall.desc
        if hasattr(pytfall, "map_pattern"):
            del pytfall.map_pattern
        if hasattr(pytfall, "hp"):
            del pytfall.hp
        if hasattr(store, "equipSlotsPositions"):
            del store.equipSlotsPositions
        if hasattr(store, "SLOTALIASES"):
            del store.SLOTALIASES
        if hasattr(store, "ilists"):
            del store.ilists
        if hasattr(store, "gfxpath"):
            del store.gfxpath
        if hasattr(store, "gfxframes"):
            del store.gfxframes
        if hasattr(store, "gfximages"):
            del store.gfximages
        if hasattr(store, "interfaceimages"):
            del store.interfaceimages
        if hasattr(store, "interfacebuttons"):
            del store.interfacebuttons
        if hasattr(store, "ndresting"):
            del store.ndresting
        if hasattr(store, "nd_buildings"):
            del store.nd_buildings
        if hasattr(store, "ndactive"):
            del store.ndactive
        if hasattr(store, "ndevents"):
            del store.ndevents
        if hasattr(store, "hidden_village_shop"):
            del store.hidden_village_shop
        if hasattr(store, "witches_hut"):
            del store.witches_hut
        if hasattr(store, "witch_spells_shop"):
            del store.witch_spells_shop
        if hasattr(store, "angelica_shop"):
            del store.angelica_shop
        if hasattr(store, "aine_shop"):
            del store.aine_shop
        if hasattr(store, "peevish_shop"):
            del store.peevish_shop
        if hasattr(store, "items_upgrades"):
            del store.items_upgrades
        if hasattr(store, "filter"):
            del store.filter
        if hasattr(store, "background_number_list"):
            del store.background_number_list
        if hasattr(store, "gm_dice"):
            del store.gm_dice
        if hasattr(store, "gm_last_success"):
            del store.gm_last_success
        if hasattr(store, "gm_disp_mult"):
            del store.gm_disp_mult
        if hasattr(store, "gm_fight_bg"):
            del store.gm_fight_bg
        if hasattr(store, "stored_random_seed"):
            del store.stored_random_seed
        if hasattr(store, "sex_action_tags"):
            del store.sex_action_tags
        if hasattr(store, "loc_tags"):
            del store.loc_tags
        if hasattr(store, "tags_dict"):
            del store.tags_dict
        if hasattr(store, "heard_about_arena"):
            if store.heard_about_arena:
                global_flags.set_flag("heard_about_arena")
            del store.heard_about_arena
        if hasattr(store, "city_tavern_dice_bet"):
            global_flags.set_flag("city_tavern_dice_bet", store.city_tavern_dice_bet)
            del store.city_tavern_dice_bet
        if hasattr(store, "clone_id"):
            cid = store.clone_id
            if cid != 0:
                global_flags.up_counter("clone_id", cid)
            del store.clone_id
        if hasattr(gazette, "first_view"):
            del gazette.first_view

        if "Garem Charm" in store.items:
            del store.items["Harem Charm"]
            hc = store.items["Garem Charm"]
            del store.items["Garem Charm"]
            hc.id = "Harem Charm"
            store.items["Harem Charm"] = hc

        if not hasattr(store, "iam"):
            store.iam = store.gm
            del store.gm
        if not hasattr(store.iam, "world_gossips"):
            store.iam.world_gossips = WorldGossipsManager(world_gossips)
        if "girl_meets" in pytfall.world_actions.locations:
            del pytfall.world_actions.locations["girl_meets"]

        if hasattr(pytfall.general_store, "locations"):
            for i in pytfall.__dict__.values():
                if isinstance(i, ItemShop):
                    if hasattr(i, "locations"):
                        i.location = i.locations.pop()
                        del i.locations

        if not hasattr(store.chars_list_state, "all_status_filters"):
            store.chars_list_state = None

    stop music
    return
