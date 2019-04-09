init 1000 python:
    class TestSuite(_object):

        @staticmethod
        def testAll():
            testContext()
            testGame()

        @staticmethod
        def testContext():
            testPyp()
            testMobs()
            testTagDB()

        @staticmethod
        def testChars():
            testNPCs()
            testUChars()
            testRChars()
            testFighters()

        @staticmethod
        def testGame():
            gameItems()
            gameTraits()
            gameAreas()
            gameChars()
            gameHero()

        @staticmethod
        def testPyp():
            pass

        @staticmethod
        def testMobs():
            for m in mobs:
                mob = build_mob(id=m, level=10)
                
                if not isinstance(mob, Mob):
                    raise Exception("Creating mob %s does not result a Mob instance" % m)
                if mob.level < 10:
                    raise Exception("Creating mob %s with at least level 10 results a mob level %d" % (m, mob.level))
                if not isinstance(mob.race, Trait):
                    raise Exception("The entity of mob %s does not have a race, or it is not a Trait instance %s" % (m, mob.race))
                if not isinstance(mob.full_race, basestring):
                    raise Exception("The entity of mob %s does not have a full_race, or it is not a basestring instance %s" % (m, mob.full_race))
                if mob.front_row is not 0 and mob.front_row is not 1:
                    raise Exception("The entity of mob %s does not have a valid front_row attribute. It is set to %s, but it should be 0 or 1" % (m, mob.front_row))

        @staticmethod
        def testTagDB():
            pass

        @staticmethod
        def checkChar(c, context):
            if c.gender not in ["female", "male"]:
                raise Exception("The entity (%s) %s does not have a valid gender %s" % (context, c.fullname, c.gender))
            temp = getattr(c, "race", None)
            if not isinstance(temp, Trait):
                raise Exception("The entity (%s) %s does not have a race, or it is not a Trait instance %s" % (context, c.fullname, temp))
            if temp not in c.traits:
                raise Exception("The entity (%s) %s's race traits is not listed in its traits" % (context, c.fullname))
            temp = getattr(c, "personality", None)
            if not isinstance(temp, Trait):
                raise Exception("The entity (%s) %s does not have a personality, or it is not a Trait instance %s" % (context, c.fullname, temp))
            if temp not in c.traits:
                raise Exception("The entity (%s) %s's personality trait is not listed in its traits" % (context, c.fullname))
            temp = getattr(c, "gents", None)
            if not isinstance(temp, Trait):
                raise Exception("The entity (%s) %s does not have a gents-trait, or it is not a Trait instance %s" % (context, c.fullname, temp))
            if temp not in c.traits:
                raise Exception("The entity (%s) %s's gents-trait is not listed in its traits" % (context, c.fullname))
            temp = getattr(c, "body", None)
            if not isinstance(temp, Trait):
                raise Exception("The entity (%s) %s does not have a body-trait, or it is not a Trait instance %s" % (context, c.fullname, temp))
            if temp not in c.traits:
                raise Exception("The entity (%s) %s's body-trait is not listed in its traits" % (context, c.fullname))
            if not c.elements:
                raise Exception("The entity (%s) %s does not have an elemental trait" % (context, c.fullname))
            for item in c.inventory:
                if item.id not in items:
                    raise Exception("The entity (%s) %s's inventory has an unknown item %s" % (context, c.fullname, item.id))

            if c.front_row is not 0 and c.front_row is not 1:
                raise Exception("The entity (%s) %s's front_row attribute is set to %s, but it should be 0 or 1" % (context, c.fullname, c.front_row))

            for k, v in c.magic_skills.items.items():
                if v == 0:
                    raise Exception("The entity (%s) %s's magic_skills is not properly cleaned (%s:%d)" % (context, c.fullname, k, v))
            for k, v in c.attack_skills.items.items():
                if v == 0:
                    raise Exception("The entity (%s) %s's attack_skills is not properly cleaned (%s:%d)" % (context, c.fullname, k, v))

            for t in c.traits:
                if not isinstance(t, Trait):
                    raise Exception("The entity (%s) %s's traits contains an invalid entry %s" % (context, c.fullname, t))
                if getattr(t, "gender", c.gender) != c.gender:
                    raise Exception("The entity (%s) %s's traits contains a gender mismatching entry %s (%s vs. %s)" % (context, c.fullname, t, t.gender, c.gender))
                
            for t in c.traits.blocked_traits:
                if not isinstance(t, Trait):
                    raise Exception("The entity (%s) %s's blocked_traits contains an invalid entry %s" % (context, c.fullname, t))

            for t in c.traits.ab_traits:
                if not isinstance(t, Trait):
                    raise Exception("The entity (%s) %s's ab_traits contains an invalid entry %s" % (context, c.fullname, t))

            for k, e in c.effects.items():
                if not isinstance(e, CharEffect):
                    raise Exception("The entity (%s) %s has an invalid effect %s with key %s" % (context, c.fullname, e, k))
                if e.name != k:
                    raise Exception("The entity (%s) %s's effect %s is registered with wrong key %s" % (context, c.fullname, e, k))
                if e.days_active > e.duration:
                    raise Exception("The entity (%s) %s's effect %s run longer (%d) than expected (%d)" % (context, c.fullname, e.days_active, e.duration))

            for k, v in c.eqslots.items():
                if v and getattr(v, "gender", c.gender) != c.gender:
                    raise Exception("The entity (%s) %s has a gender mismatching equipment (%s vs %s) in slot %s" % (context, c.fullname, v.gender, c.gender, k))

        @staticmethod
        def testRChars():
            for i in range(100):
                c = build_rc(name="alpha", last_name="beta",
                             bt_go_patterns="Specialist",
                             set_status="free", set_locations=True,
                             tier=4, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False,
                             spells_to_tier=True)
                if c.fullname != "alpha beta":
                    raise Exception("Ignored name presets while creating a random char (result: %s)" % c.fullname)
                TestSuite.checkChar(c, "rchar/freeSpecialist")

            for i in range(100):
                c = build_rc(bt_go_base="Server",
                             set_status="free", set_locations=True,
                             tier=7, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False,
                             spells_to_tier=True)

                TestSuite.checkChar(c, "rchar/freeServer")

            for i in range(100):
                c = build_rc(bt_go_patterns="Combatant",
                             set_status="free", set_locations=True,
                             tier=MAX_TIER, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=True,
                             spells_to_tier=True)

                TestSuite.checkChar(c, "rchar/freeCombatant")

            for i in range(100):
                c = build_rc(bt_go_patterns="SIW",
                             set_status="slave", set_locations=True,
                             tier=4, add_to_gameworld=False,
                             give_civilian_items=False, give_bt_items=False,
                             spells_to_tier=True)

                TestSuite.checkChar(c, "rchar/slaveSIW")

            for i in range(100):
                c = build_rc(bt_go_base="Server",
                             set_status="slave", set_locations=True,
                             tier=2, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False,
                             spells_to_tier=True)

                TestSuite.checkChar(c, "rchar/slaveServer")

        @staticmethod
        def gameChars():
            for c in chars.values():
                TestSuite.checkChar(c, "game-char")

        @staticmethod
        def gameTraits():
            for key, trait in traits.items():
                if trait.id != key:
                    raise Exception("Bad Trait Entry %s for trait %s" % (key, trait.id))
                if not isinstance(trait, Trait):
                    raise Exception("Invalid entry %s for key %s (not a Trait instance)!" % (key, str(trait)))
                if getattr(trait, "gender", "female") not in ["female", "male"]:
                    raise Exception("Invalid gender %s for trait %s (not 'female' or 'male')!" % (trait.gender, key))
                for t in trait.blocks:
                    if not isinstance(t, Trait):
                        raise Exception("Invalid blocked trait %s for trait %s (not a Trait instance)!" % (str(t), key))

        @staticmethod
        def gameItems():
            for key, item in items.items():
                if item.id != key:
                    raise Exception("Bad Item Entry %s for item %s" % (key, item.id))
                if not isinstance(item, Item):
                    raise Exception("Invalid entry %s for key %s (not an Item instance)!" % (key, str(item)))
                if getattr(item, "gender", "female") not in ["female", "male"]:
                    raise Exception("Invalid gender %s for item %s (not 'female' or 'male')!" % (item.gender, key))

        @staticmethod
        def performanceTest():
            msg = "Attempt to auto-buy 3 items for {} girls!".format(len(chars))
            tl.start(msg)
            for i in chars.values():
                i.gold = 100000
                i.autobuy = True
                i.auto_buy(amount=3, smart_ownership_limit=False)
                i.equip_for("Combat")
            tl.end(msg)
            tl.start("Create Chars")
            for i in range(1000):
                build_rc(tier=10, give_bt_items=True, give_civilian_items=True)
            tl.end("Create Chars")
            tl.start("Create Chars")
            for i in range(1000):
                build_rc(tier=10, give_bt_items=True, give_civilian_items=False)
            tl.end("Create Chars")
            tl.start("Create Chars")
            for i in range(1000):
                build_rc(tier=10, give_bt_items=False, give_civilian_items=True)
            tl.end("Create Chars")
            tl.start("Create Chars")
            for i in range(1000):
                build_rc(tier=10, give_bt_items=False, give_civilian_items=False)
            tl.end("Create Chars")
            #import cProfile
            #cProfile.runctx('testrun(1)', globals(), locals(), 'results')

        @staticmethod
        def printGlobals():
            # "updater", "stored_random_seed" "style", , "anim" "blank" "build" "pickle", 
            temp = set(["gui", "updater", "icon", "ET", "re", "preferences", "layeredimage", "_predict_set", "_cache_pin_set", "_kwargs", "_quit_slot", "_console", "_window_subtitle", "_test", "_m1_00stylepreferences__alternatives", "nvl_list", "_m1_00gltest__dxwebsetup", "fnmatch", "renpy", "simpy", "pygame", "types", "_ignore_action", "anim", "_text_rect", "_side_image", "_side_image_attributes", "main_menu", "logging", "_window_during_transitions", "_rollback", "_return", "store", "_gamepad", "_config", "random", "__file__", "default_transition", "_game_menu_screen", "scrap", "_m1_00stylepreferences__spdirty", "__doc__", "_last_say_who", "_last_say_args", "block_say", "im", "_history", "_in_replay", "sys", "_skipping", "_last_say_kwargs", "collections", "save_name", "_define", "_last_say_what", "_side_image_raw", "_window", "_month_name_long", "_preferences", "ui", "_last_voice_play", "time", "_weekday_name_short", "_side_image_attributes_reset", "_m1_00stylepreferences__preferences", "last_label", "_version", "_m1_classic_load_save__scratch", "_side_image_old", "_confirm_quit", "_overlay_screens", "_history_list", "_warper", "config", "_voice", "math", "__builtins__", "_predict_screen", "_restart", "_args", "iap", "copy", "_m1_00action_data__FieldNotFound", "_nvl_language", "mouse_visible", "_weekday_name_long", "functools", "bisect", "_windows_hidden", "_widget_properties", "itertools", "json", "_dismiss_pause", "define", "_month_name_short", "__package__", "_errorhandling", "SCRAP_TEXT", "audio", "_widget_by_id", "nvl_variant", "_window_auto", "string", "_default_keymap", "library", "director", "inspect", "__name__", "_defaults_set", "print_function", "_load_prompt", "os", "_last_raw_what", "operator", "_menu", "persistent"])
            temp.update(["NextDayEvents", "tl", "AEQ_PURPOSES", "EQUIP_SLOTS", "hero", "items", "tags_dict", "simple_jobs", "DEBUG_QE", "defeated_mobs", "fg_areas", "DEBUG_PROFILING", "random_team_names", "DEBUG_ND", "pytfall", "FIGHTING_AEQ_PURPOSES", "DEBUG_SIMPY_ND_BUILDING_REPORT", "DEBUG_INTERACTIONS", "main_menu", "tiered_items", "gen_occ_basetraits", "male_first_names", "rchars", "undefined", "gfx_overlay", "DEBUG_LOG", "devlog", "chars", "ND_IMAGE_SIZE", "tgs", "all_auto_buy_items", "DEBUG_AUTO_ITEM", "DSNBR", "result", "global_flags", "female_fighters", "IMAGE_EXTENSIONS", "mobs", "DEBUG_CHARS", "male_fighters", "traits", "CLIENT_CASTES", "random_last_names", "tiered_magic_skills", "tiered_healing_skills", "DEBUG_SE", "char", "gm", "female_first_names", "MUSIC_EXTENSIONS", "last_label", "DEBUG", "chars_list_state", "DEBUG_BE", "menu_extensions", "last_label_pure", "gamedir", "day", "npcs", "dungeons", "tisa_otm_adv", "pyp", "gazette", "DEBUG_SIMPY", "calendar", "base_trait_presets", "sex_action_tags", "base_traits_groups", "tagslog", "MAX_TIER", "coords", "BDP", "tagdb", "SKILLS_MAX", "DAILY_EXP_CORE", "SKILLS_THRESHOLD", "_COLORS_", "battle_skills", "all_chars"])
            temp.update(["index", "last_inv_filter", "equipment_safe_mode", "girls", "school_courses", "interactions_portraits_overlay"])
            devlog.warn("Current Vars: %s" % ", ".join(k for k in store.__dict__.keys() if k not in temp and not isclass(store.__dict__[k]) and not callable(store.__dict__[k])))
            