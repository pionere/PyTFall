init 1000 python:
    class TestSuite(_object):

        @staticmethod
        def testAll():
            TestSuite.testContext()
            TestSuite.testGame()

        @staticmethod
        def testContext():
            TestSuite.testPyp()
            TestSuite.testMobs()
            TestSuite.testTagDB()
            TestSuite.testBE()
            TestSuite.testChars()

        @staticmethod
        def testChars():
            TestSuite.testNPCs()
            TestSuite.testUChars()
            TestSuite.testRChars()
            TestSuite.testFighters()

        @staticmethod
        def testGame():
            TestSuite.gameItems()
            TestSuite.gameTraits()
            TestSuite.gameAreas()
            TestSuite.gameChars()
            TestSuite.gameHero()
            TestSuite.gameBuildings()

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
        def testBE():
            TestSuite.testBEDirect()
            TestSuite.testBEConflictR()

        @staticmethod
        def testBEDirect():
            # Prepear the teams:
            off_team = Team(name="Off Team", max_size=3)
            mob = build_mob(id="Goblin Shaman", level=120)
            mob.controller = BE_AI(mob)
            mob.front_row = 1
            off_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=100)
            mob.controller = BE_AI(mob)
            off_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=100)
            mob.controller = BE_AI(mob)
            off_team.add(mob)

            def_team = Team(name="Def Team", max_size=3)
            mob = build_mob(id="Goblin Shaman", level=60)
            mob.controller = BE_AI(mob)
            mob.front_row = 1
            def_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=60)
            mob.controller = BE_AI(mob)
            def_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=60)
            mob.controller = BE_AI(mob)
            def_team.add(mob)

            max_turns=15*(len(off_team)+len(def_team))

            global battle
            battle = BE_Core(logical=True, max_turns=max_turns)
            battle.teams.append(off_team)
            battle.teams.append(def_team)

            battle.start_battle()

            # Reset Controller:
            off_team.reset_controller()
            def_team.reset_controller()

            rv = battle.combat_status
            if isinstance(rv, basestring):
                raise Exception("Battle result is %s, but it should not be a string." % rv)
            if battle.winner != off_team:
                raise Exception("The weaker team won, but they should not since they are much weaker!")

        @staticmethod
        def testBEConflictR(simple_ai=True):
            off_team = None
            for mob in mobs:
                if off_team is None:
                    off_team = Team(name="Off Team", max_size=3)
                    def_team = Team(name="Def Team", max_size=3)
                mob = build_mob(id=mob, level=100)
                if len(off_team) < 3:
                    off_team.add(mob)
                    continue
                if len(def_team) < 3:
                    def_team.add(mob)
                    continue
                battle = new_style_conflict_resolver(off_team, def_team, simple_ai)
                off_team = None

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
                if e.duration is not None and e.days_active > e.duration:
                    raise Exception("The entity (%s) %s's effect %s run longer (%d) than expected (%d)" % (context, c.fullname, e.name, e.days_active, e.duration))

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
        def testNPCs():
            pass
        @staticmethod
        def testUChars():
            pass
        @staticmethod
        def testFighters():
            pass

        @staticmethod
        def gameHero():
            if hero.front_row is not 0 and hero.front_row is not 1:
                raise Exception("Hero(%s)'s front_row attribute is set to %s, but it should be 0 or 1" % (hero.fullname, hero.front_row))

            for k, v in hero.magic_skills.items.items():
                if v == 0:
                    raise Exception("Hero(%s)'s magic_skills is not properly cleaned (%s:%d)" % (hero.fullname, k, v))
            for k, v in hero.attack_skills.items.items():
                if v == 0:
                    raise Exception("Hero(%s)'s attack_skills is not properly cleaned (%s:%d)" % (hero.fullname, k, v))

            for t in hero.traits:
                if not isinstance(t, Trait):
                    raise Exception("Hero(%s)'s traits contains an invalid entry %s" % (hero.fullname, t))
                if getattr(t, "gender", hero.gender) != hero.gender:
                    raise Exception("Hero(%s)'s traits contains a gender mismatching entry %s (%s vs. %s)" % (hero.fullname, t, t.gender, hero.gender))
                
            for t in hero.traits.blocked_traits:
                if not isinstance(t, Trait):
                    raise Exception("Hero(%s)'s blocked_traits contains an invalid entry %s" % (hero.fullname, t))

            for t in hero.traits.ab_traits:
                if not isinstance(t, Trait):
                    raise Exception("Hero(%s)'s ab_traits contains an invalid entry %s" % (hero.fullname, t))

            for k, e in hero.effects.items():
                if not isinstance(e, CharEffect):
                    raise Exception("The entity (%s) %s has an invalid effect %s with key %s" % (hero.fullname, e, k))
                if e.name != k:
                    raise Exception("The entity (%s) %s's effect %s is registered with wrong key %s" % (hero.fullname, e, k))
                if e.days_active > e.duration:
                    raise Exception("Hero(%s)'s effect %s run longer (%d) than expected (%d)" % (hero.fullname, e.days_active, e.duration))

            for k, v in hero.eqslots.items():
                if v and getattr(v, "gender", hero.gender) != hero.gender:
                    raise Exception("Hero (%s) has a gender mismatching equipment (%s vs %s) in slot %s" % (hero.fullname, v.gender, hero.gender, k))

            # Teams:
            if hero.team not in hero.teams:
                raise Exception("Hero(%s)'s current team %s is not listed in their teams" % (hero.fullname, hero.team.name))

            for team in hero.teams:
                if team.members[0] != hero:
                    raise Exception("Hero(%s)'s team %s does not have hero as its first member." % (hero.fullname, team.name))
                for member in team:
                    if member != hero and member not in hero.chars:
                        raise Exception("Hero(%s)'s team-member %s is not under hero's controll (not listed in hero.chars)." % (hero.fullname, member.name))

            # chars:
            all_chars = chars.values()
            for char in hero.chars:
                if char not in all_chars:
                    raise Exception("Hero(%s)'s char %s is no longer in the global chars." % (hero.fullname, char.name))

        @staticmethod
        def gameChars():
            all_chars = chars.values()
            for c in all_chars:
                TestSuite.checkChar(c, "game-char")
                if isinstance(c, rChar):
                    if not c.has_flag("from_day_in_game"):
                        raise Exception("Rchar %s does not have 'from_day_in_game' flag" % c.fullname)

            # check Slave Market
            for c in pytfall.sm.inhabitants:
                if c not in all_chars:
                    raise Exception("Char %s is not registered, but inhabitant of the slave market" % c.fullname)

            for c in pytfall.sm.chars_list:
                if c not in all_chars:
                    raise Exception("Char %s is not registered, but on sale in the slave market" % c.fullname)

            # TODO blue_slaves ?

            # check Jail
            for c in pytfall.jail.slaves:
                if c not in all_chars:
                    raise Exception("Char %s is not registered, but she/he is in jail as a runaway slave" % c.fullname)
                if c.status != "slave":
                    raise Exception("Non-slave char %s listed as runaway slave" % c.fullname)

            for c in pytfall.jail.captures:
                if c not in all_chars:
                    raise Exception("Char %s is not registered, but listed as captured in the jail" % c.fullname)

            for c in pytfall.jail.cells:
                if c not in all_chars:
                    raise Exception("Char %s is not registered, but she/he is in the jail" % c.fullname)
                if c.status != "free":
                    raise Exception("Non-free char %s listed as civilian prisoner" % c.fullname)

            # check Employment Agency
            for v in employment_agency_chars.itervalues():
                for c in v:
                    if c not in all_chars:
                        raise Exception("Char %s is not registered, but she/he available at the EA" % c.fullname)
                    if c.status != "free":
                        raise Exception("Non-free char %s listed to be hired at EA" % c.fullname)

        @staticmethod
        def gameTraits():
            for key, trait in traits.items():
                if trait.id != key:
                    raise Exception("Bad Trait Entry %s for trait %s" % (key, trait.id))
                if not isinstance(trait, Trait):
                    raise Exception("Invalid entry %s for key %s (not a Trait instance)!" % (str(trait), key))
                if getattr(trait, "gender", "female") not in ["female", "male"]:
                    raise Exception("Invalid gender %s for trait %s (not 'female' or 'male')!" % (trait.gender, key))
                for t in trait.blocks:
                    if not isinstance(t, Trait):
                        raise Exception("Invalid blocked trait %s for trait %s (not a Trait instance)!" % (str(t), key))

        @staticmethod
        def gameItems():
            valid_pref_classes = ["Any", "Casual", "Warrior", "Mage", "Shooter", "Manager", "Bartender", "Whore", "Stripper", "SIW", "Service", "Slave"]
            for key, item in items.items():
                if item.id != key:
                    raise Exception("Bad Item Entry %s for item %s" % (key, item.id))
                if not isinstance(item, Item):
                    raise Exception("Invalid entry %s for key %s (not an Item instance)!" % (str(item), key))
                if getattr(item, "gender", "female") not in ["female", "male"]:
                    raise Exception("Invalid gender %s for item %s (not 'female' or 'male')!" % (item.gender, key))
                for p in item.pref_class:
                    if p not in valid_pref_classes:
                        raise Exception("Invalid pref_class %s for item %s (not in %s)!" % (p, key, ", ".join(valid_pref_classes)))

        @staticmethod
        def gameAreas():
            for key, area in fg_areas.items():
                if area.id != key:
                    raise Exception("Bad Area Entry %s for area %s" % (key, area.id))
                if not isinstance(area, FG_Area):
                    raise Exception("Invalid entry %s for key %s (not an FG_Area instance)!" % (key, str(area)))
                if area.area is None:
                    continue # just a main area -> skip
                if not isinstance(area.maxexplored, (int, float)) or area.maxexplored <= 0:
                    raise Exception("Area %s has an invalid maxexplored setting %s (should be a greater than zero number)!" % (key, str(area.maxexplored)))
                for item in area.items:
                    if item not in items:
                        raise Exception("Area %s has an invalid item to be found: %s!" % (key, item))

        @staticmethod
        def gameBuildings():
            for b in chain(hero.buildings, buildings.itervalues()):
                if b.needs_manager and b not in hero.buildings and any([b.clients, b.all_clients, b.regular_clients]):
                    raise Exception("Building %s has active clients while it is for sale!" % b.name)

                if not hasattr(b, "threat_mod"):
                    locs = ["Flee Bottom", "Midtown", "Richford"]
                    if b.location not in locs:
                        raise Exception("Building %s has an invalid location field! It must be one of the followings : %s.(Or threat_mod must be configured manually)" % (b.name, ", ".join(locs))) # threat_mod setting depends on this

                for a in b.adverts:
                    if "name" not in a:
                        raise Exception("An Advert in Building %s missing its name field." % b.name)
                    if not isinstance(a.get("upkeep", 0), int):
                        raise Exception("Advert %s in Building %s has an invalid 'upkeep' field! It must be an integer." % (a["name"], b.name))
                    if not isinstance(a.get("client", 0), int):
                        raise Exception("Advert %s in Building %s has an invalid 'client' field! It must be an integer." % (a["name"], b.name))
                    if "fame" in a:
                        mod = a["fame"]
                        if not isinstance(mod, list) or len(mod) != 2:
                            raise Exception("Advert %s in Building %s has an invalid 'fame' field! It must be a list(2)." % (a["name"], b.name))
                        if not (isinstance(mod[0], int) and isinstance(mod[1], int)):
                            raise Exception("Advert %s in Building %s has an invalid 'fame' field! The values must be integers." % (a["name"], b.name))
                    if "reputation" in a:
                        mod = a["reputation"]
                        if not isinstance(mod, list) or len(mod) != 2:
                            raise Exception("Advert %s in Building %s has an invalid 'reputation' field! It must be a list(2)." % (a["name"], b.name))
                        if not (isinstance(mod[0], int) and isinstance(mod[1], int)):
                            raise Exception("Advert %s in Building %s has an invalid 'reputation' field! The values must be integers." % (a["name"], b.name))

                for u in b.upgrades:
                    if not isinstance(getattr(u, "materials", None), dict):
                        raise Exception("Upgrade %s in Building %s has an invalid 'materials' field! It must be a dict/map." % (u.name, b.name))
                    for m in u.materials:
                        if m not in items:
                            raise Exception("Upgrade %s in Building %s requires an invalid item: %s!" % (u.name, b.name, m))
                    if u.expands_capacity:
                        raise Exception("Upgrade %s in Building %s is expandable, but it should not be!" % (u.name, b.name))
                    if u.duration is not None:
                        if not isinstance(u.duration, list) or len(u.duration) != 2:
                            raise Exception("Upgrade %s in Building %s has an invalid 'duration' field! It must be a list(2)." % (u.name, b.name))
                        if not (isinstance(u.duration[0], int) and isinstance(u.duration[1], int)):
                            raise Exception("Upgrade %s in Building %s has an invalid 'duration' field! The values must be integers." % (u.name, b.name))

                for bs in b.businesses:
                    if bs.habitable and bs.workable:
                        raise Exception("Business %s in Building %s is both habitable and workable, but these are exclusive settings!" % (bs.name, b.name)) # capacity calculation depends on this

                    if bs.expects_clients and not bs.workable:
                        raise Exception("Business %s in Building %s expects clients, but not workable!" % (bs.name, b.name))

                    for u in b.upgrades:
                        if not isinstance(getattr(u, "materials", None), dict):
                            raise Exception("Business-Upgrade %s of %s in Building %s has an invalid 'materials' field! It must be a dict/map." % (u.name, bs.name, b.name))
                        for m in u.materials:
                            if m not in items:
                                raise Exception("Business-Upgrade %s of %s in Building %s requires an invalid item: %s!" % (u.name, bs.name, b.name, m))
                        if u.expands_capacity:
                            raise Exception("Business-Upgrade %s of %s in Building %s is expandable, but it should not be!" % (u.name, bs.name, b.name))
                        if u.duration is not None:
                            if not isinstance(u.duration, list) or len(u.duration) != 2:
                                raise Exception("Business-Upgrade %s of %s in Building %s has an invalid 'duration' field! It must be a list(2)." % (u.name, bs.name, b.name))
                            if not (isinstance(u.duration[0], int) and isinstance(u.duration[1], int)):
                                raise Exception("Business-Upgrade %s of %s in Building %s has an invalid 'duration' field! The values must be integers." % (u.name, bs.name, b.name))

                    if not isinstance(getattr(bs, "materials", None), dict):
                        raise Exception("Business %s in Building %s has an invalid 'materials' field! It must be a dict/map." % (bs.name, b.name))
                    for m in bs.materials:
                        if m not in items:
                            raise Exception("Business %s in Building %s requires an invalid item: %s!" % (bs.name, b.name, m))
                    if bs.duration is not None:
                        if not isinstance(bs.duration, list) or len(bs.duration) != 2:
                            raise Exception("Business %s in Building %s has an invalid 'duration' field! It must be a list(2)." % (bs.name, b.name))
                        if not (isinstance(bs.duration[0], int) and isinstance(bs.duration[1], int)):
                            raise Exception("Business %s in Building %s has an invalid 'duration' field! The values must be integers." % (bs.name, b.name))
                    ec_fields = ["exp_cap_in_slots", "exp_cap_ex_slots", "exp_cap_cost", "exp_cap_materials", "exp_cap_duration"]
                    if bs.expands_capacity:
                        for f in ec_fields:
                            if not hasattr(bs, f):
                                raise Exception("Business %s in Building %s is expandable, but missing expansion-related field %s!" % (bs.name, b.name, f))

                        if bs.exp_cap_duration is not None:
                            if not isinstance(bs.exp_cap_duration, list) or len(bs.exp_cap_duration) != 2:
                                raise Exception("Business %s in Building %s has an invalid 'exp_cap_duration' field! It must be a list(2)." % (bs.name, b.name))
                            if not (isinstance(bs.exp_cap_duration[0], int) and isinstance(bs.exp_cap_duration[1], int)):
                                raise Exception("Business %s in Building %s has an invalid 'exp_cap_duration' field! The values must be integers." % (bs.name, b.name))

                        if not isinstance(getattr(bs, "exp_cap_materials", None), dict):
                            raise Exception("Business %s in Building %s has an invalid 'exp_cap_materials' field! It must be a dict/map." % (bs.name, b.name))
                        for m in bs.exp_cap_materials:
                            if m not in items:
                                raise Exception("Business %s in Building %s requires an invalid item (%s) to expand its capacity!" % (bs.name, b.name, m))
                    else:
                        for f in ec_fields:
                            if hasattr(bs, f):
                                raise Exception("Business %s in Building %s is not expandable, but has expansion-related field %s!" % (bs.name, b.name, f))

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
            