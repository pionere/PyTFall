init 1000 python:
    class TestSuite(_object):
        mode = "devlog"

        @staticmethod
        def reportError(msg):
            if TestSuite.mode == "devlog":
                devlog.error(msg)
            else:
                raise Exception(msg)

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
            TestSuite.testAreas()

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
                    TestSuite.reportError("Creating mob %s does not result a Mob instance" % m)
                    continue
                if mob.level < 10:
                    TestSuite.reportError("Creating mob %s with at least level 10 results a mob level %d" % (m, mob.level))
                if not isinstance(mob.race, Trait):
                    TestSuite.reportError("The entity of mob %s does not have a race, or it is not a Trait instance %s" % (m, mob.race))
                if not isinstance(mob.full_race, basestring):
                    TestSuite.reportError("The entity of mob %s does not have a full_race, or it is not a basestring instance %s" % (m, mob.full_race))
                if mob.front_row is not 0 and mob.front_row is not 1:
                    TestSuite.reportError("The entity of mob %s does not have a valid front_row attribute. It is set to %s, but it should be 0 or 1" % (m, mob.front_row))

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
            off_team = Team(name="Off Team")
            mob = build_mob(id="Goblin Shaman", level=120)
            mob.front_row = 1
            off_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=100)
            off_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=100)
            off_team.add(mob)

            def_team = Team(name="Def Team")
            mob = build_mob(id="Goblin Shaman", level=60)
            mob.front_row = 1
            def_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=60)
            def_team.add(mob)
            mob = build_mob(id="Goblin Archer", level=60)
            def_team.add(mob)

            off_team.setup_controller(True)
            def_team.setup_controller(True)

            global battle
            battle = BE_Core(logical=True, max_turns=True, teams=[off_team, def_team])
            battle.start_battle()

            # Reset Controller:
            off_team.reset_controller()
            def_team.reset_controller()

            rv = battle.combat_status
            if isinstance(rv, basestring):
                TestSuite.reportError("Battle result is %s, but it should not be a string." % rv)
            if battle.winner != off_team:
                TestSuite.reportError("The weaker team won, but they should not since they are much weaker!")

        @staticmethod
        def testBEConflictR(simple_ai=True):
            off_team = None
            for mob in mobs:
                if off_team is None:
                    off_team = Team(name="Off Team")
                    def_team = Team(name="Def Team")
                mob = build_mob(id=mob, level=100)
                if len(off_team) < 3:
                    off_team.add(mob)
                    continue
                if len(def_team) < 3:
                    def_team.add(mob)
                    continue
                battle = run_auto_be(off_team, def_team, simple_ai)
                off_team = None

        @staticmethod
        def checkStat(msg, result, expected, stats, expected_stats):
            if result != expected:
                TestSuite.reportError("%s failed! result:%s, expected: %s" % (msg, result, expected))
            if isinstance(stats, Stats):
                stats = [stats.stats["stat"], stats.min["stat"], stats.max["stat"], stats.lvl_max["stat"], stats.imod["stat"], stats.imin["stat"], stats.imax["stat"]]
                idx = 0
                for value, expected_value in zip(stats, expected_stats):
                    if value != expected_value:
                        TestSuite.reportError("%s failed at idx %d! result:%s, expected: %s" % (msg, idx, value, expected_value))
                    idx += 1
            else:
                if stats != expected_stats:
                    TestSuite.reportError("Secondary check of %s failed! result:%s, expected: %s" % (msg, stats, expected_stats))

        @staticmethod
        def testStats():
            # stat entry means [stat, min, max, lvl_max, imod, imin, imax]

            # CHECK STATS WITH MAX, LEVEL_MAX
            # current stat+
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 0, 0, 0] })
            TestSuite.checkStat("Stat+", stats.get_max("stat"), 50, stats._get_stat("stat"), 5)

            # current stat++
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, 0, 0, 0] })
            TestSuite.checkStat("Max limited stat++", stats.get_max("stat"), 50, stats._get_stat("stat"), 50)

            # current stat+ lvl_max limited
            stats = Stats("dummy", {'stat': [5, 0, 70, 60, 0, 0, 0] })
            TestSuite.checkStat("Level-Max limited stat+", stats.get_max("stat"), 60, stats._get_stat("stat"), 5)

            # current stat++ lvl_max limited
            stats = Stats("dummy", {'stat': [65, 0, 70, 60, 0, 0, 0] })
            TestSuite.checkStat("Level-Max limited stat++", stats.get_max("stat"), 60, stats._get_stat("stat"), 60)

            # CHECK STATS WITH MAX, LEVEL_MAX, MIN
            # current stat+
            stats = Stats("dummy", {'stat': [15, 10, 50, 60, 0, 0, 0] })
            TestSuite.checkStat("Stat+ with min", stats.get_max("stat"), 50, stats._get_stat("stat"), 15)

            # current stat-
            stats = Stats("dummy", {'stat': [5, 10, 50, 60, 0, 0, 0] })
            TestSuite.checkStat("Stat- min", stats.get_max("stat"), 50, stats._get_stat("stat"), 10)

            # current stat- max-
            stats = Stats("dummy", {'stat': [5, 55, 50, 60, 0, 0, 0] })
            TestSuite.checkStat("Stat- max- min", stats.get_max("stat"), 55, stats._get_stat("stat"), 55)

            # current stat- max- lvl_max-
            stats = Stats("dummy", {'stat': [5, 65, 50, 60, 0, 0, 0] })
            TestSuite.checkStat("Stat- max- lvl_max- min", stats.get_max("stat"), 65, stats._get_stat("stat"), 65)

            # CHECK STATS WITH MAX, LEVEL_MAX, IMAX
            # current stat+ max limited because of imax+
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 0, 0, 5] })
            TestSuite.checkStat("Level-Max limited stat+ due imax+", stats.get_max("stat"), 55, stats._get_stat("stat"), 5)

            # current stat++ max limited because of imax+
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, 0, 0, 5] })
            TestSuite.checkStat("Level-Max limited stat++ due imax+", stats.get_max("stat"), 55, stats._get_stat("stat"), 55)

            # current stat+ lvl_max limited because of imax+
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 0, 0, 20] })
            TestSuite.checkStat("Level-Max limited stat+ due imax++", stats.get_max("stat"), 60, stats._get_stat("stat"), 5)

            # current stat++ lvl_max limited because of imax+
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, 0, 0, 20] })
            TestSuite.checkStat("Level-Max limited stat++ due imax++", stats.get_max("stat"), 60, stats._get_stat("stat"), 60)

            # current stat+ lvl_max limited because of imax-
            stats = Stats("dummy", {'stat': [5, 0, 70, 60, 0, 0, -5] })
            TestSuite.checkStat("Level-Max limited stat+ due imax-", stats.get_max("stat"), 60, stats._get_stat("stat"), 5)

            # current stat++ max limited because of imax-
            stats = Stats("dummy", {'stat': [75, 0, 70, 60, 0, 0, -5] })
            TestSuite.checkStat("Level-Max limited stat++ due imax-", stats.get_max("stat"), 60, stats._get_stat("stat"), 60)

            # current stat+ max limited because of imax--
            stats = Stats("dummy", {'stat': [5, 0, 70, 60, 0, 0, -20] })
            TestSuite.checkStat("Max limited stat+ due imax--", stats.get_max("stat"), 50, stats._get_stat("stat"), 5)

            # current stat++ lvl_max limited because of imax--
            stats = Stats("dummy", {'stat': [75, 0, 70, 60, 0, 0, -20] })
            TestSuite.checkStat("Max limited stat++ due imax--", stats.get_max("stat"), 50, stats._get_stat("stat"), 50)

            # CHECK STATS WITH MAX, LEVEL_MAX, IMOD
            # current stat+ with imod+
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 15, 0, 0] })
            TestSuite.checkStat("Stat+ with imod+", stats.get_max("stat"), 50, stats._get_stat("stat"), 20)

            # current stat+ with imod+ max limited
            stats = Stats("dummy", {'stat': [15, 0, 50, 60, 40, 0, 0] })
            TestSuite.checkStat("Max limited stat+ with imod+", stats.get_max("stat"), 50, stats._get_stat("stat"), 50)

            # current stat+ with imod+ lvl_max limited
            stats = Stats("dummy", {'stat': [15, 0, 70, 60, 50, 0, 0] })
            TestSuite.checkStat("Level-Max limited stat+ with imod+", stats.get_max("stat"), 60, stats._get_stat("stat"), 60)

            # current stat++ with imod- max limited
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, -10, 0, 0] })
            TestSuite.checkStat("Max limited stat++ with imod-", stats.get_max("stat"), 50, stats._get_stat("stat"), 50)

            # current stat++ with imod--
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, -20, 0, 0] })
            TestSuite.checkStat("Stat++ with imod--", stats.get_max("stat"), 50, stats._get_stat("stat"), 45)

            # current stat++ with imod---
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, -100, 0, 0] })
            TestSuite.checkStat("Stat++ with imod---", stats.get_max("stat"), 50, stats._get_stat("stat"), 0)

            # current stat++ with imod- lvl_max limited
            stats = Stats("dummy", {'stat': [65, 0, 60, 50, -10, 0, 0] })
            TestSuite.checkStat("Level-Max limited stat++ with imod-", stats.get_max("stat"), 50, stats._get_stat("stat"), 50)

            # current stat++ with imod--
            stats = Stats("dummy", {'stat': [65, 0, 60, 50, -20, 0, 0] })
            TestSuite.checkStat("Stat++ with imod-- with lvl_max", stats.get_max("stat"), 50, stats._get_stat("stat"), 45)

            # current stat++ with imod---
            stats = Stats("dummy", {'stat': [65, 0, 60, 50, -100, 0, 0] })
            TestSuite.checkStat("Stat++ with imod--- with lvl_max", stats.get_max("stat"), 50, stats._get_stat("stat"), 0)

            # CHECK STATS WITH MAX, LEVEL_MAX, IMOD, IMAX

            # TODO

            # CHECK STAT INCREMENTS
            # stat raised
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 40)
            TestSuite.checkStat("Stat raised", result, 40, stats, [45, 0, 50, 60, 0, 0, 0])

            # stat raised++ max limited
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Max limited Stat raised++", result, 45, stats, [60, 0, 50, 60, 0, 0, 0])

            # stat raised++ lvl_max limited
            stats = Stats("dummy", {'stat': [5, 0, 70, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Level-Max limited Stat raised++", result, 55, stats, [60, 0, 70, 60, 0, 0, 0])

            # stat+ raised max limited
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 2)
            TestSuite.checkStat("Max limited Stat+ raised", result, 0, stats, [57, 0, 50, 60, 0, 0, 0])

            # stat+ raised++ max limited
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Max limited Stat+ raised++", result, 0, stats, [60, 0, 50, 60, 0, 0, 0])

            # stat++ raised++ max limited
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Max limited Stat++ raised++", result, 0, stats, [65, 0, 50, 60, 0, 0, 0])

            # stat+ raised++ lvl_max limited
            stats = Stats("dummy", {'stat': [65, 0, 70, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Level-Max limited Stat+ raised++", result, 0, stats, [65, 0, 70, 60, 0, 0, 0])

            # Remark: the behaviour of the stat- cases are inconsistent.
            #         the result of the method does not match the apparent change,
            # stat- raised
            stats = Stats("dummy", {'stat': [-10, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 5)
            TestSuite.checkStat("Stat raised", result, 0, stats, [-5, 0, 50, 60, 0, 0, 0])

            # stat- raised++
            stats = Stats("dummy", {'stat': [-10, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 20)
            TestSuite.checkStat("Stat raised", result, 10, stats, [10, 0, 50, 60, 0, 0, 0])

            # stat- raised++ max_limited
            stats = Stats("dummy", {'stat': [-20, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Max limited Stat raised++", result, 50, stats, [60, 0, 50, 60, 0, 0, 0])

            # stat- raised++ lvl_max limited
            stats = Stats("dummy", {'stat': [-10, 0, 80, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Level-Max limited Stat raised++", result, 60, stats, [60, 0, 80, 60, 0, 0, 0])

            # CHECK STAT INCREMENTS WITH IMOD
            # stat raised+ with imod+
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 20, 0, 0] })
            result = stats._mod_base_stat("stat", 10)
            TestSuite.checkStat("Stat raised+ with imod+", result, 10, stats, [15, 0, 50, 60, 20, 0, 0])

            # stat raised++ with imod+
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 20, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Stat raised++", result, 25, stats, [60, 0, 50, 60, 20, 0, 0])

            # stat raised++ imod-
            stats = Stats("dummy", {'stat': [15, 0, 50, 60, -10, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Stat raised++ imod-", result, 45, stats, [70, 0, 50, 60, -10, 0, 0])

            # stat raised++ imod--
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, -20, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Stat raised++ imod--", result, 50, stats, [80, 0, 50, 60, -20, 0, 0])

            # stat++ raised++ imod-
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, -10, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Stat++ raised++ imod-", result, 0, stats, [70, 0, 50, 60, -10, 0, 0])

            # stat+++ raised++ imod-
            stats = Stats("dummy", {'stat': [75, 0, 50, 60, -10, 0, 0] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Stat+++ raised++ imod-", result, 0, stats, [75, 0, 50, 60, -10, 0, 0])

            # CHECK STAT INCREMENTS WITH IMAX
            # stat raised++ imax+
            stats = Stats("dummy", {'stat': [5, 0, 60, 70, 0, 0, 4] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Max limited Stat raised++ imax+", result, 59, stats, [70, 0, 60, 70, 0, 0, 4])

            # stat raised++ lvl_max limited due imax++
            stats = Stats("dummy", {'stat': [5, 0, 50, 60, 0, 0, 40] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Stat raised++ imax++", result, 55, stats, [60, 0, 50, 60, 0, 0, 40])

            # stat raised++ imax-
            stats = Stats("dummy", {'stat': [5, 0, 80, 70, 0, 0, -20] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Level-Max limited Stat raised++ imax-", result, 55, stats, [70, 0, 80, 70, 0, 0, -20])

            # stat raised++ imax--
            stats = Stats("dummy", {'stat': [5, 0, 80, 70, 0, 0, -100] })
            result = stats._mod_base_stat("stat", 100)
            TestSuite.checkStat("Level-Max limited Stat raised++ imax--", result, 0, stats, [70, 0, 80, 70, 0, 0, -100])

            # CHECK STAT INCREMENTS WITH IMAX, IMOD

            # TODO

            # CHECK STAT DECREMENTS
            # stat lowered
            stats = Stats("dummy", {'stat': [45, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", -40)
            TestSuite.checkStat("Stat lowered", result, -40, stats, [5, 0, 50, 60, 0, 0, 0])

            # stat lowered-- min limited
            stats = Stats("dummy", {'stat': [45, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Min limited Stat lowered--", result, -45, stats, [0, 0, 50, 60, 0, 0, 0])

            # stat+ lowered- max limited
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", -2)
            TestSuite.checkStat("Max limited Stat+ lowered-", result, -2, stats, [48, 0, 50, 60, 0, 0, 0])

            # stat+ lowered- lvl_max limited
            stats = Stats("dummy", {'stat': [55, 0, 60, 50, 0, 0, 0] })
            result = stats._mod_base_stat("stat", -2)
            TestSuite.checkStat("Level-Max limited Stat+ lowered-", result, -2, stats, [48, 0, 60, 50, 0, 0, 0])

            # stat+ lowered-- max limited
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Max limited Stat++ lowered--", result, -50, stats, [0, 0, 50, 60, 0, 0, 0])

            # stat+ lowered-- lvl_max limited
            stats = Stats("dummy", {'stat': [65, 0, 70, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Level-Max limited Stat+ lowered--", result, -60, stats, [0, 0, 70, 60, 0, 0, 0])

            # stat- lowered
            stats = Stats("dummy", {'stat': [-5, 0, 50, 60, 0, 0, 0] })
            result = stats._mod_base_stat("stat", -10)
            TestSuite.checkStat("Stat- lowered", result, 0, stats, [-5, 0, 50, 60, 0, 0, 0])

            # CHECK STAT DECREMENTS WITH IMOD
            # stat lowered- with imod
            stats = Stats("dummy", {'stat': [20, 0, 50, 60, 15, 0, 0] })
            result = stats._mod_base_stat("stat", -10)
            TestSuite.checkStat("Stat lowered with imod", result, -10, stats, [10, 0, 50, 60, 15, 0, 0])

            # stat lowered- with imod
            stats = Stats("dummy", {'stat': [20, 0, 50, 60, 15, 0, 0] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Stat lowered- with imod", result, -20, stats, [0, 0, 50, 60, 15, 0, 0])

            # stat+ lowered- with imod
            stats = Stats("dummy", {'stat': [40, 0, 50, 60, 15, 0, 0] })
            result = stats._mod_base_stat("stat", -10)
            TestSuite.checkStat("Stat lowered with imod", result, -10, stats, [25, 0, 50, 60, 15, 0, 0])

            # max limited stat++ lowered- with imod
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, 15, 0, 0] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Max limited Stat++ lowered- with imod", result, -30, stats, [5, 0, 50, 60, 15, 0, 0])

            # lvl_max limited stat++ lowered- with imod
            stats = Stats("dummy", {'stat': [65, 0, 70, 60, 15, 0, 0] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Level-Max limited Stat++ lowered- with imod", result, -30, stats, [15, 0, 70, 60, 15, 0, 0])

            # lvl_max limited stat++ lowered- with imod, imax
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, 15, 0, 20] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Level-Max limited Stat++ lowered- with imod, imax", result, -30, stats, [15, 0, 50, 60, 15, 0, 20])

            # stat lowered- with imod-
            stats = Stats("dummy", {'stat': [20, 0, 50, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -10)
            TestSuite.checkStat("Stat lowered with imod-", result, -5, stats, [10, 0, 50, 60, -15, 0, 0])

            # stat lowered- with imod-
            stats = Stats("dummy", {'stat': [20, 0, 50, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Stat lowered- with imod-", result, -5, stats, [0, 0, 50, 60, -15, 0, 0])

            # (max) limited stat++ lowered- with imod-
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("(Max) limited Stat++ lowered- with imod-", result, -30, stats, [25, 0, 50, 60, -15, 0, 0])

            # (max) limited stat++ lowered-- with imod-
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("(Max) limited Stat++ lowered-- with imod-", result, -40, stats, [0, 0, 50, 60, -15, 0, 0])

            # (lvl_max) limited stat++ lowered-- with imod-
            stats = Stats("dummy", {'stat': [65, 0, 70, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("(Level-Max limited) Stat++ lowered-- with imod-", result, -50, stats, [0, 0, 70, 60, -15, 0, 0])

            # (lvl_max limited) stat++ lowered-- with imod--, imax
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, -15, 0, 20] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("(Level-Max limited) Stat++ lowered-- with imod-, imax", result, -50, stats, [0, 0, 50, 60, -15, 0, 20])

            # max limited stat++ lowered- with imod
            stats = Stats("dummy", {'stat': [75, 0, 50, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Max limited Stat++ lowered- with imod", result, -30, stats, [35, 0, 50, 60, -15, 0, 0])

            # lvl_max limited stat++ lowered- with imod
            stats = Stats("dummy", {'stat': [85, 0, 70, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Level-Max limited Stat++ lowered- with imod", result, -30, stats, [45, 0, 70, 60, -15, 0, 0])
            
            # lvl_max limited stat++ lowered- with imod, imax
            stats = Stats("dummy", {'stat': [85, 0, 50, 60, -15, 0, 20] })
            result = stats._mod_base_stat("stat", -30)
            TestSuite.checkStat("Level-Max limited Stat++ lowered- with imod, imax", result, -30, stats, [45, 0, 50, 60, -15, 0, 20])

            # max limited stat++ lowered-- with imod
            stats = Stats("dummy", {'stat': [75, 0, 50, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Max limited Stat++ lowered-- with imod", result, -50, stats, [0, 0, 50, 60, -15, 0, 0])

            # lvl_max limited stat++ lowered-- with imod
            stats = Stats("dummy", {'stat': [85, 0, 70, 60, -15, 0, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Level-Max limited Stat++ lowered-- with imod", result, -60, stats, [0, 0, 70, 60, -15, 0, 0])
            
            # lvl_max limited stat++ lowered-- with imod, imax
            stats = Stats("dummy", {'stat': [85, 0, 50, 60, -15, 0, 20] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Level-Max limited Stat++ lowered-- with imod, imax", result, -60, stats, [0, 0, 50, 60, -15, 0, 20])

            # CHECK STAT DECREMENTS WITH IMAX
            # CHECK STAT DECREMENTS WITH IMAX, IMOD
            # TODO

            # CHECK STAT DECREMENTS WITH IMIN
            # stat lowered imin limited
            stats = Stats("dummy", {'stat': [45, 0, 50, 60, 0, 10, 0] })
            result = stats._mod_base_stat("stat", -40)
            TestSuite.checkStat("IMin limited Stat lowered-", result, -35, stats, [5, 0, 50, 60, 0, 10, 0])

            # stat lowered-- imin limited
            stats = Stats("dummy", {'stat': [45, 0, 50, 60, 0, 10, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("IMin limited Stat lowered--", result, -35, stats, [0, 0, 50, 60, 0, 10, 0])

            # stat+ lowered- max to imin limited
            stats = Stats("dummy", {'stat': [55, 0, 50, 60, 0, 10, 0] })
            result = stats._mod_base_stat("stat", -48)
            TestSuite.checkStat("Max-IMin limited Stat+ lowered-", result, -40, stats, [2, 0, 50, 60, 0, 10, 0])

            # stat+ lowered- lvl_max to imin limited
            stats = Stats("dummy", {'stat': [55, 0, 60, 50, 0, 10, 0] })
            result = stats._mod_base_stat("stat", -48)
            TestSuite.checkStat("Level-Max-IMin limited Stat+ lowered-", result, -40, stats, [2, 0, 60, 50, 0, 10, 0])

            # stat+ lowered-- max to imin limited
            stats = Stats("dummy", {'stat': [65, 0, 50, 60, 0, 10, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Max-IMin limited Stat++ lowered--", result, -40, stats, [0, 0, 50, 60, 0, 10, 0])

            # stat+ lowered-- lvl_max to imin limited
            stats = Stats("dummy", {'stat': [65, 0, 70, 60, 0, 10, 0] })
            result = stats._mod_base_stat("stat", -100)
            TestSuite.checkStat("Level-Max-IMin limited Stat+ lowered--", result, -50, stats, [0, 0, 70, 60, 0, 10, 0])

        @staticmethod
        def checkChar(c, context):
            if c.gender not in ["female", "male"]:
                TestSuite.reportError("The entity (%s) %s does not have a valid gender %s" % (context, c.fullname, c.gender))
            temp = getattr(c, "race", None)
            if not isinstance(temp, Trait):
                TestSuite.reportError("The entity (%s) %s does not have a race, or it is not a Trait instance %s" % (context, c.fullname, temp))
            elif temp not in c.traits:
                TestSuite.reportError("The entity (%s) %s's race traits is not listed in its traits" % (context, c.fullname))
            temp = getattr(c, "personality", None)
            if not isinstance(temp, Trait):
                TestSuite.reportError("The entity (%s) %s does not have a personality, or it is not a Trait instance %s" % (context, c.fullname, temp))
            elif temp not in c.traits:
                TestSuite.reportError("The entity (%s) %s's personality trait is not listed in its traits" % (context, c.fullname))
            temp = getattr(c, "gents", None)
            if not isinstance(temp, Trait):
                TestSuite.reportError("The entity (%s) %s does not have a gents-trait, or it is not a Trait instance %s" % (context, c.fullname, temp))
            elif temp not in c.traits:
                TestSuite.reportError("The entity (%s) %s's gents-trait is not listed in its traits" % (context, c.fullname))
            temp = getattr(c, "body", None)
            if not isinstance(temp, Trait):
                TestSuite.reportError("The entity (%s) %s does not have a body-trait, or it is not a Trait instance %s" % (context, c.fullname, temp))
            elif temp not in c.traits:
                TestSuite.reportError("The entity (%s) %s's body-trait is not listed in its traits" % (context, c.fullname))
            if not c.elements:
                TestSuite.reportError("The entity (%s) %s does not have an elemental trait" % (context, c.fullname))
            for item in c.inventory:
                if item.id not in items:
                    TestSuite.reportError("The entity (%s) %s's inventory has an unknown item %s" % (context, c.fullname, item.id))

            if c.front_row is not 0 and c.front_row is not 1:
                TestSuite.reportError("The entity (%s) %s's front_row attribute is set to %s, but it should be 0 or 1" % (context, c.fullname, c.front_row))

            for k, v in c.magic_skills.items.items():
                if v == 0:
                    TestSuite.reportError("The entity (%s) %s's magic_skills is not properly cleaned (%s:%d)" % (context, c.fullname, k, v))
            for k, v in c.attack_skills.items.items():
                if v == 0:
                    TestSuite.reportError("The entity (%s) %s's attack_skills is not properly cleaned (%s:%d)" % (context, c.fullname, k, v))

            for t in c.traits:
                if not isinstance(t, Trait):
                    TestSuite.reportError("The entity (%s) %s's traits contains an invalid entry %s" % (context, c.fullname, t))
                if getattr(t, "gender", c.gender) != c.gender:
                    TestSuite.reportError("The entity (%s) %s's traits contains a gender mismatching entry %s (%s vs. %s)" % (context, c.fullname, t, t.gender, c.gender))
                
            for t in c.traits.blocked_traits:
                if not isinstance(t, Trait):
                    TestSuite.reportError("The entity (%s) %s's blocked_traits contains an invalid entry %s" % (context, c.fullname, t))

            for t in c.traits.ab_traits:
                if not isinstance(t, Trait):
                    TestSuite.reportError("The entity (%s) %s's ab_traits contains an invalid entry %s" % (context, c.fullname, t))

            for k, e in c.effects.items():
                if not isinstance(e, CharEffect):
                    TestSuite.reportError("The entity (%s) %s has an invalid effect %s with key %s" % (context, c.fullname, e, k))
                    continue
                if e.name != k:
                    TestSuite.reportError("The entity (%s) %s's effect %s is registered with wrong key %s" % (context, c.fullname, e, k))
                if e.duration is not None and e.days_active > e.duration:
                    TestSuite.reportError("The entity (%s) %s's effect %s run longer (%d) than expected (%d)" % (context, c.fullname, e.name, e.days_active, e.duration))

            for k, v in c.eqslots.items():
                if v and getattr(v, "gender", c.gender) != c.gender:
                    TestSuite.reportError("The entity (%s) %s has a gender mismatching equipment (%s vs %s) in slot %s" % (context, c.fullname, v.gender, c.gender, k))

        @staticmethod
        def testRChars():
            for i in range(10):
                c = build_rc(name="alpha", last_name="beta",
                             bt_group="Specialist",
                             set_status="free", set_locations=True,
                             tier=4, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False)
                if c.fullname != "alpha beta":
                    TestSuite.reportError("Ignored name presets while creating a random char (result: %s)" % c.fullname)
                TestSuite.checkChar(c, "rchar/freeSpecialist")

            for i in range(10):
                c = build_rc(bt_group="Server",
                             set_status="free", set_locations=True,
                             tier=7, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False)

                TestSuite.checkChar(c, "rchar/freeServer")

            for i in range(10):
                c = build_rc(bt_group="Combatant",
                             set_status="free", set_locations=True,
                             tier=MAX_TIER, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=True)

                TestSuite.checkChar(c, "rchar/freeCombatant")

            for i in range(10):
                c = build_rc(bt_group="SIW",
                             set_status="slave", set_locations=True,
                             tier=4, add_to_gameworld=False,
                             give_civilian_items=False, give_bt_items=False)

                TestSuite.checkChar(c, "rchar/slaveSIW")

            for i in range(10):
                c = build_rc(bt_group="Server",
                             set_status="slave", set_locations=True,
                             tier=2, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False)

                TestSuite.checkChar(c, "rchar/slaveServer")

            for i in range(10):
                c = build_rc(name="alpha", last_name="beta",
                             bt_group="Specialist", bt_list="any",
                             set_status="free", set_locations=True,
                             tier=4, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False)
                if c.fullname != "alpha beta":
                    TestSuite.reportError("Ignored name presets while creating a random char (result: %s)" % c.fullname)
                TestSuite.checkChar(c, "rchar/freeSpecialist")

            for i in range(10):
                c = build_rc(bt_group="Server", bt_list="any",
                             set_status="free", set_locations=True,
                             tier=7, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False)

                TestSuite.checkChar(c, "rchar/freeServer")

            for i in range(10):
                c = build_rc(bt_group="Combatant", bt_list="any",
                             set_status="free", set_locations=True,
                             tier=MAX_TIER, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=True)

                TestSuite.checkChar(c, "rchar/freeCombatant")

            for i in range(10):
                c = build_rc(bt_group="SIW", bt_list="any",
                             set_status="slave", set_locations=True,
                             tier=4, add_to_gameworld=False,
                             give_civilian_items=False, give_bt_items=False)

                TestSuite.checkChar(c, "rchar/slaveSIW")

            for i in range(10):
                c = build_rc(bt_group="Server", bt_list="any",
                             set_status="slave", set_locations=True,
                             tier=2, add_to_gameworld=False,
                             give_civilian_items=True, give_bt_items=False)

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
        def get_area_children(key, children, ac):
            cc = children.get(key, None)
            if cc is None:
                return
            for c in cc:
                if c in ac:
                    continue
                ac.add(c)
                TestSuite.get_area_children(c, children, ac)

        @staticmethod
        def testAreas():
            fg_areas = load_fg_areas()

            names = set()
            parents = dict()
            for key, area in fg_areas.iteritems():
                if area.id != key:
                    TestSuite.reportError("Bad Area Entry %s for area %s" % (key, area.id))
                if not isinstance(key, int) or key < 0:
                    TestSuite.reportError("Bad Area Key %s" % key)
                if not isinstance(area, FG_Area):
                    TestSuite.reportError("Invalid entry %s for key %s (not an FG_Area instance)!" % (key, str(area)))
                    continue
                name = getattr(area, "name", None)
                if name is None:
                    TestSuite.reportError("Area %s does not have a 'name' parameter!" % key)
                    name = str(key)
                else:
                    if name in names:
                        TestSuite.reportError("Area %s does not have a unique name!" % name)
                    else:
                        names.add(name)
                    name = "'%s' (%s)" % (name, key)
                if not hasattr(area, "stage"):
                    TestSuite.reportError("Area %s does not have a 'stage' parameter!" % name)
                if not hasattr(area, "img"):
                    TestSuite.reportError("Area %s does not have an 'img' parameter!" % name)
                if area.area is None:
                    continue # main area -> skip the rest
                if not isinstance(area.maxexplored, (int, float)) or area.maxexplored <= 0:
                    TestSuite.reportError("Area %s has an invalid maxexplored setting %s (should be a greater than zero number)!" % (name, str(area.maxexplored)))
                for item in area.items:
                    if item not in items:
                        TestSuite.reportError("Area %s has an invalid item to be found: %s!" % (name, item))
                for mob in area.mobs:
                    if mob not in store.mobs:
                        TestSuite.reportError("Area %s has an invalid mob to encounter: %s!" % (name, mob))
                for id, data in area.chars.items():
                    if id not in store.chars:
                        TestSuite.reportError("Area %s has an invalid char to be captured: %s!" % (name, id))
                for id, data in area.rchars.items():
                    if id not in store.rchars:
                        TestSuite.reportError("Area %s has an invalid rchar to be captured: %s!" % (name, id))
                for k in getattr(area, "unlocks", []):
                    if k == key or k not in fg_areas:
                        TestSuite.reportError("Area %s unlocks an invalid area: %s!" % (name, k))
                        continue
                    entry = parents.get(k, None)
                    if entry is None:
                        parents[k] = key
                    elif isinstance(entry, list):
                        entry.append(key)
                    else:
                        parents[k] = [entry, key]
                    try:
                        uarea = fg_areas[k]
                        parea = area.area
                        uparea = uarea.area
                        if uparea != parea:
                            stage = fg_areas[parea].stage
                            if uparea is None:
                                ustage = uarea.stage
                            else:
                                ustage = fg_areas[uparea].stage
                        else:
                            stage = area.stage
                            ustage = uarea.stage
                        if stage >= ustage:
                            uname = "'%s' (%s)" % (getattr(uarea, "name", ""), k)
                            TestSuite.reportError("Area '%s' unlocks an area '%s' with lower or equal stage (%s vs. %s)!" % (name, uname, stage, ustage))
                    except:
                        pass

            for k, v in parents.iteritems():
                area = fg_areas[k]
                if getattr(area, "unlocked", False):
                    msg = "Unlocked Area %s is also unlocked by %s!"
                    if not isinstance(v, list):
                        v = [v]
                elif not isinstance(v, list):
                    continue
                else:
                    msg = "Area %s is unlocked by multiple areas: %s!"
                name = "'%s' (%s)" % (getattr(area, "name", ""), k)
                uname = ", ".join(["'%s' (%s)" % (getattr(fg_areas[k], "name", ""), k) for k in v])
                TestSuite.reportError(msg % (name, uname))

            base_areas = []
            for key, area in fg_areas.iteritems():
                entry = parents.get(key, None)
                if getattr(area, "unlocked", False):
                    parent = area.area
                    if parent is None:
                        base_areas.append(area)
                        continue
                    if entry is None:
                        parents[key] = parent
                    elif isinstance(entry, list):
                        entry.append(parent)
                    else:
                        parents[key] = [entry, parent]
                    continue
                if entry is None:
                    name = "'%s' (%s)" % (getattr(area, "name", ""), key)
                    TestSuite.reportError("Area %s is inaccessible!" % name)

            children = dict()
            for k, v in parents.iteritems():
                if not isinstance(v, list):
                    v = [v]
                for c in v:
                    entry = children.get(c, None)
                    if entry is None:
                        children[c] = [k]
                    elif isinstance(entry, list):
                        entry.append(k)

            base_areas.sort(key=lambda x: getattr(area, "stage", 0))
            intervals = []
            for area in base_areas:
                key = area.id
                ac = set()
                TestSuite.get_area_children(key, children, ac)
                if not ac:
                    name = "'%s' (%s)" % (getattr(area, "name", ""), key)
                    TestSuite.reportError("Base Area %s does not have a sub-area!" % name)
                k_min = k_max = area.stage
                for a in ac:
                    try:
                        a = fg_areas[a]
                        if a.area is None:
                            a = a.stage
                            if a > k_max:
                                k_max = a
                    except:
                        pass
                intervals.append((k_min, k_max))
            for i0, i1 in intervals:
                #devlog.warn("Interval %s - %s" % (i0, i1))
                for i0_, i1_ in intervals:
                    if i0 < i0_ and i1 > i0_:
                        name0 = "'%s' (%s)" % (getattr(fg_areas[i0], "name", ""), i0)
                        name1 = "'%s' (%s)" % (getattr(fg_areas[i1], "name", ""), i1)
                        TestSuite.reportError("Area %s and area %s have overlapping stage intervals [(%s;%s) - (%s;%s)]!" % (name0, name1, i0, i1, i0_, i1_))

        @staticmethod
        def gameHero():
            if hero.front_row is not 0 and hero.front_row is not 1:
                TestSuite.reportError("Hero(%s)'s front_row attribute is set to %s, but it should be 0 or 1" % (hero.fullname, hero.front_row))

            for k, v in hero.magic_skills.items.items():
                if v == 0:
                    TestSuite.reportError("Hero(%s)'s magic_skills is not properly cleaned (%s:%d)" % (hero.fullname, k, v))
            for k, v in hero.attack_skills.items.items():
                if v == 0:
                    TestSuite.reportError("Hero(%s)'s attack_skills is not properly cleaned (%s:%d)" % (hero.fullname, k, v))

            for t in hero.traits:
                if not isinstance(t, Trait):
                    TestSuite.reportError("Hero(%s)'s traits contains an invalid entry %s" % (hero.fullname, t))
                if getattr(t, "gender", hero.gender) != hero.gender:
                    TestSuite.reportError("Hero(%s)'s traits contains a gender mismatching entry %s (%s vs. %s)" % (hero.fullname, t, t.gender, hero.gender))
                
            for t in hero.traits.blocked_traits:
                if not isinstance(t, Trait):
                    TestSuite.reportError("Hero(%s)'s blocked_traits contains an invalid entry %s" % (hero.fullname, t))

            for t in hero.traits.ab_traits:
                if not isinstance(t, Trait):
                    TestSuite.reportError("Hero(%s)'s ab_traits contains an invalid entry %s" % (hero.fullname, t))

            for k, e in hero.effects.items():
                if not isinstance(e, CharEffect):
                    TestSuite.reportError("The entity (%s) %s has an invalid effect %s with key %s" % (hero.fullname, e, k))
                    continue
                if e.name != k:
                    TestSuite.reportError("The entity (%s) %s's effect %s is registered with wrong key %s" % (hero.fullname, e, k))
                if e.days_active > e.duration:
                    TestSuite.reportError("Hero(%s)'s effect %s run longer (%d) than expected (%d)" % (hero.fullname, e.days_active, e.duration))

            for k, v in hero.eqslots.items():
                if v and getattr(v, "gender", hero.gender) != hero.gender:
                    TestSuite.reportError("Hero (%s) has a gender mismatching equipment (%s vs %s) in slot %s" % (hero.fullname, v.gender, hero.gender, k))

            # Teams:
            if hero.team not in hero.teams:
                TestSuite.reportError("Hero(%s)'s current team %s is not listed in their teams" % (hero.fullname, hero.team.name))

            for team in hero.teams:
                if team.leader is not hero:
                    TestSuite.reportError("Hero(%s)'s team %s does not have hero as its leader." % (hero.fullname, team.name))
                if len(team) != len(team._members):
                    TestSuite.reportError("Hero(%s)'s team %s has an incorrect size (%d vs %d)." % (hero.fullname, team.name, len(team), len(team._members)))
                for member in team:
                    if member == hero:
                        continue
                    if member not in hero.chars:
                        TestSuite.reportError("Hero(%s)'s team-member %s is not under hero's controll (not listed in hero.chars)." % (hero.fullname, member.name))

            # chars:
            all_chars = chars.values()
            for char in hero.chars:
                if char not in all_chars:
                    TestSuite.reportError("Hero(%s)'s char %s is no longer in the global chars." % (hero.fullname, char.name))
                if char.employer != hero:
                    TestSuite.reportError("Hero(%s)'s char %s does not have hero registered as an employer." % (hero.fullname, char.name))

            for cf in hero.friends:
                if cf not in all_chars:
                    TestSuite.reportError("Friend of Hero, named %s is not registered." % cf.fullname)
            for cl in hero.lovers:
                if cl not in all_chars:
                    TestSuite.reportError("Lover of Hero, named %s is not registered." % cl.fullname)

        @staticmethod
        def gameChars():
            all_chars = chars.values()
            for c in all_chars:
                TestSuite.checkChar(c, "game-char")
                for cf in c.friends:
                    if cf != hero and cf not in chars:
                        TestSuite.reportError("Friend of Char %s, named %s is not registered." % (c.fullname, cf.fullname))
                for cl in c.lovers:
                    if cl != hero and cl not in chars:
                        TestSuite.reportError("Lover of Char %s, named %s is not registered." % (c.fullname, cl.fullname))
                if isinstance(c, rChar):
                    if not c.has_flag("from_day_in_game"):
                        TestSuite.reportError("Rchar %s does not have 'from_day_in_game' flag" % c.fullname)
                if c.employer == hero:
                    if c not in hero.chars:
                        TestSuite.reportError("Char %s has the hero as registered employer, but it is not in hero.chars." % (char.name))
                else:
                    if c in hero.chars:
                        TestSuite.reportError("Hero(%s)'s char %s employer is '%s', not the hero '%s'." % (hero.fullname, char.name, char.employer, hero))

            # check Slave Market
            for c in pytfall.sm.inhabitants:
                if c not in all_chars:
                    TestSuite.reportError("Char %s is not registered, but inhabitant of the slave market" % c.fullname)

            for c in pytfall.sm.chars_list:
                if c not in all_chars:
                    TestSuite.reportError("Char %s is not registered, but on sale in the slave market" % c.fullname)

            # TODO blue_slaves ?

            # check Jail
            for c in pytfall.jail.slaves:
                if c not in all_chars:
                    TestSuite.reportError("Char %s is not registered, but she/he is in jail as a runaway slave" % c.fullname)
                if c.status != "slave":
                    TestSuite.reportError("Non-slave char %s listed as runaway slave" % c.fullname)

            for c in pytfall.jail.captures:
                if c not in all_chars:
                    TestSuite.reportError("Char %s is not registered, but listed as captured in the jail" % c.fullname)

            for c in pytfall.jail.cells:
                if c not in all_chars:
                    TestSuite.reportError("Char %s is not registered, but she/he is in the jail" % c.fullname)
                if c.status != "free":
                    TestSuite.reportError("Non-free char %s listed as civilian prisoner" % c.fullname)

            # check Employment Agency
            for v in pytfall.ea.chars.itervalues():
                for c in v:
                    if c not in all_chars:
                        TestSuite.reportError("Char %s is not registered, but she/he available at the EA" % c.fullname)
                    if c.status != "free":
                        TestSuite.reportError("Non-free char %s listed to be hired at EA" % c.fullname)

        @staticmethod
        def gameTraits():
            for key, trait in traits.items():
                if trait.id != key:
                    TestSuite.reportError("Bad Trait Entry %s for trait %s" % (key, trait.id))
                if not isinstance(trait, Trait):
                    TestSuite.reportError("Invalid entry %s for key %s (not a Trait instance)!" % (str(trait), key))
                    continue
                if getattr(trait, "gender", "female") not in ["female", "male"]:
                    TestSuite.reportError("Invalid gender %s for trait %s (not 'female' or 'male')!" % (trait.gender, key))
                for t in trait.blocks:
                    if not isinstance(t, Trait):
                        TestSuite.reportError("Invalid blocked trait %s for trait %s (not a Trait instance)!" % (str(t), key))

        @staticmethod
        def gameItems():
            valid_pref_classes = ["Any", "Casual", "Warrior", "Mage", "Shooter", "Manager", "Whore", "Stripper", "SIW", "Cleaning", "Bartender", "Service", "Slave"]
            for key, item in items.items():
                if item.id != key:
                    TestSuite.reportError("Bad Item Entry %s for item %s" % (key, item.id))
                if not isinstance(item, Item):
                    TestSuite.reportError("Invalid entry %s for key %s (not an Item instance)!" % (str(item), key))
                    continue
                if getattr(item, "gender", "female") not in ["female", "male"]:
                    TestSuite.reportError("Invalid gender %s for item %s (not 'female' or 'male')!" % (item.gender, key))
                if item.pref_class:
                    for p in item.pref_class:
                        if p not in valid_pref_classes:
                            TestSuite.reportError("Invalid pref_class %s for item %s (not in %s)!" % (p, key, ", ".join(valid_pref_classes)))
                    if item.type == "permanent":
                        TestSuite.reportError("Invalid pref_class %s for item %s (permanent items are not permitted to have a pref_class)!" % (p, key))
                    if item.jump_to_label:
                        TestSuite.reportError("Invalid pref_class %s for item %s (jump_to_label items are not permitted to have a pref_class)!" % (p, key))
                    if item.badness >= 100:
                        TestSuite.reportError("Invalid pref_class %s for item %s (items with higher than 100 badness are not permitted to have a pref_class)!" % (p, key))
                    if not item.usable:
                        TestSuite.reportError("Invalid pref_class %s for item %s (non-usable items are not permitted to have a pref_class)!" % (p, key))
                    if not item.eqchance:
                        TestSuite.reportError("Invalid pref_class %s for item %s (items with no eqchance are not permitted to have a pref_class)!" % (p, key))
                if not isinstance(item.goodtraits, set):
                    TestSuite.reportError("Invalid goodtraits for item %s (not a set)!" % key)
                if not isinstance(item.badtraits, set):
                    TestSuite.reportError("Invalid badtraits for item %s (not a set)!" % key)
                #if item.slot != "misc" and (item.slot != "consumable" or item.ctemp):
                #    for stat, value in item.mod.items():
                #        if stat in ["health", "vitality", "mp", "joy"]:
                #            TestSuite.reportError("Item %s has a permanent modifier to %s stat!" % (key, stat))

        @staticmethod
        def gameAreas():
            for key, area in fg_areas.items():
                if area.id != key:
                    TestSuite.reportError("Bad Area Entry %s for area %s" % (key, area.id))
                if not isinstance(area, FG_Area):
                    TestSuite.reportError("Invalid entry %s for key %s (not an FG_Area instance)!" % (key, str(area)))
                    continue
                if area.area is None:
                    continue # just a main area -> skip
                if not isinstance(area.maxexplored, (int, float)) or area.maxexplored <= 0:
                    TestSuite.reportError("Area %s has an invalid maxexplored setting %s (should be a greater than zero number)!" % (key, str(area.maxexplored)))
                for item in area.items:
                    if item not in items:
                        TestSuite.reportError("Area %s has an invalid item to be found: %s!" % (key, item))

        @staticmethod
        def gameBuildings():
            for b in chain(hero.buildings, buildings.itervalues()):
                if b.needs_manager and b not in hero.buildings and any([b.clients, b.all_clients, b.regular_clients]):
                    TestSuite.reportError("Building %s has active clients while it is for sale!" % b.name)

                if not hasattr(b, "threat_mod"):
                    locs = ["Flee Bottom", "Midtown", "Richford"]
                    if b.location not in locs:
                        TestSuite.reportError("Building %s has an invalid location field! It must be one of the followings : %s.(Or threat_mod must be configured manually)" % (b.name, ", ".join(locs))) # threat_mod setting depends on this

                for a in b.adverts:
                    if "name" not in a:
                        TestSuite.reportError("An Advert in Building %s missing its name field." % b.name)
                    if not isinstance(a.get("upkeep", 0), int):
                        TestSuite.reportError("Advert %s in Building %s has an invalid 'upkeep' field! It must be an integer." % (a["name"], b.name))
                    if not isinstance(a.get("client", 0), int):
                        TestSuite.reportError("Advert %s in Building %s has an invalid 'client' field! It must be an integer." % (a["name"], b.name))
                    if "fame" in a:
                        mod = a["fame"]
                        if not isinstance(mod, list) or len(mod) != 2:
                            TestSuite.reportError("Advert %s in Building %s has an invalid 'fame' field! It must be a list(2)." % (a["name"], b.name))
                        elif not (isinstance(mod[0], int) and isinstance(mod[1], int)):
                            TestSuite.reportError("Advert %s in Building %s has an invalid 'fame' field! The values must be integers." % (a["name"], b.name))
                    if "reputation" in a:
                        mod = a["reputation"]
                        if not isinstance(mod, list) or len(mod) != 2:
                            TestSuite.reportError("Advert %s in Building %s has an invalid 'reputation' field! It must be a list(2)." % (a["name"], b.name))
                        elif not (isinstance(mod[0], int) and isinstance(mod[1], int)):
                            TestSuite.reportError("Advert %s in Building %s has an invalid 'reputation' field! The values must be integers." % (a["name"], b.name))

                for u in b.upgrades:
                    if u not in b.allowed_upgrades:
                        TestSuite.reportError("Built-Upgrade %s in Building %s is not allowed!" % (u.name, b.name))
                    temp = getattr(u, "materials", None)
                    if not isinstance(temp, dict):
                        TestSuite.reportError("Upgrade %s in Building %s has an invalid 'materials' field! It must be a dict/map." % (u.name, b.name))
                    else:
                        for m in temp:
                            if m not in items:
                                TestSuite.reportError("Upgrade %s in Building %s requires an invalid item: %s!" % (u.name, b.name, m))
                    if u.expands_capacity:
                        TestSuite.reportError("Upgrade %s in Building %s is expandable, but it should not be!" % (u.name, b.name))
                    if u.duration is not None:
                        if not isinstance(u.duration, list) or len(u.duration) != 2:
                            TestSuite.reportError("Upgrade %s in Building %s has an invalid 'duration' field! It must be a list(2)." % (u.name, b.name))
                        elif not (isinstance(u.duration[0], int) and isinstance(u.duration[1], int)):
                            TestSuite.reportError("Upgrade %s in Building %s has an invalid 'duration' field! The values must be integers." % (u.name, b.name))

                for bs in b.businesses:
                    if bs not in b.allowed_businesses:
                        TestSuite.reportError("Built-Business %s in Building %s is not allowed!" % (bs.name, b.name))

                    if bs.habitable and bs.workable:
                        TestSuite.reportError("Business %s in Building %s is both habitable and workable, but these are exclusive settings!" % (bs.name, b.name)) # capacity calculation depends on this

                    if bs.expects_clients and not bs.workable:
                        TestSuite.reportError("Business %s in Building %s expects clients, but not workable!" % (bs.name, b.name))

                    for u in b.upgrades:
                        if u not in bs.allowed_upgrades:
                            TestSuite.reportError("Business-Upgrade %s of %s in Building %s is not allowed!" % (u.name, bs.name, b.name))
                        
                        temp = getattr(u, "materials", None)
                        if not isinstance(temp, dict):
                            TestSuite.reportError("Business-Upgrade %s of %s in Building %s has an invalid 'materials' field! It must be a dict/map." % (u.name, bs.name, b.name))
                        else:
                            for m in temp:
                                if m not in items:
                                    TestSuite.reportError("Business-Upgrade %s of %s in Building %s requires an invalid item: %s!" % (u.name, bs.name, b.name, m))
                        if u.expands_capacity:
                            TestSuite.reportError("Business-Upgrade %s of %s in Building %s is expandable, but it should not be!" % (u.name, bs.name, b.name))
                        if u.duration is not None:
                            if not isinstance(u.duration, list) or len(u.duration) != 2:
                                TestSuite.reportError("Business-Upgrade %s of %s in Building %s has an invalid 'duration' field! It must be a list(2)." % (u.name, bs.name, b.name))
                            elif not (isinstance(u.duration[0], int) and isinstance(u.duration[1], int)):
                                TestSuite.reportError("Business-Upgrade %s of %s in Building %s has an invalid 'duration' field! The values must be integers." % (u.name, bs.name, b.name))

                    if not isinstance(getattr(bs, "materials", None), dict):
                        TestSuite.reportError("Business %s in Building %s has an invalid 'materials' field! It must be a dict/map." % (bs.name, b.name))
                        continue
                    for m in bs.materials:
                        if m not in items:
                            TestSuite.reportError("Business %s in Building %s requires an invalid item: %s!" % (bs.name, b.name, m))
                    if bs.duration is not None:
                        if not isinstance(bs.duration, list) or len(bs.duration) != 2:
                            TestSuite.reportError("Business %s in Building %s has an invalid 'duration' field! It must be a list(2)." % (bs.name, b.name))
                        elif not (isinstance(bs.duration[0], int) and isinstance(bs.duration[1], int)):
                            TestSuite.reportError("Business %s in Building %s has an invalid 'duration' field! The values must be integers." % (bs.name, b.name))
                    ec_fields = ["exp_cap_in_slots", "exp_cap_ex_slots", "exp_cap_cost", "exp_cap_materials", "exp_cap_duration"]
                    if bs.expands_capacity:
                        for f in ec_fields:
                            if not hasattr(bs, f):
                                TestSuite.reportError("Business %s in Building %s is expandable, but missing expansion-related field %s!" % (bs.name, b.name, f))

                        temp = getattr(bs, "exp_cap_duration", None)
                        if temp is not None:
                            if not isinstance(temp, list) or len(temp) != 2:
                                TestSuite.reportError("Business %s in Building %s has an invalid 'exp_cap_duration' field! It must be a list(2)." % (bs.name, b.name))
                            elif not (isinstance(bs.exp_cap_duration[0], int) and isinstance(bs.exp_cap_duration[1], int)):
                                TestSuite.reportError("Business %s in Building %s has an invalid 'exp_cap_duration' field! The values must be integers." % (bs.name, b.name))

                        temp = getattr(bs, "exp_cap_materials", dict())
                        if not isinstance(temp, dict):
                            TestSuite.reportError("Business %s in Building %s has an invalid 'exp_cap_materials' field! It must be a dict/map." % (bs.name, b.name))
                            continue
                        for m in temp:
                            if m not in items:
                                TestSuite.reportError("Business %s in Building %s requires an invalid item (%s) to expand its capacity!" % (bs.name, b.name, m))
                    else:
                        for f in ec_fields:
                            if hasattr(bs, f):
                                TestSuite.reportError("Business %s in Building %s is not expandable, but has expansion-related field %s!" % (bs.name, b.name, f))

        @staticmethod
        def build_super_char(bt_list, tier=10):
            c = build_rc(bt_list=bt_list, tier=10)
            for i in items.values():
                c.inventory.append(i)
            initial_levelup(c, c.level, True)
            restore_battle_stats(c)
            c.auto_equip(c.last_known_aeq_purpose)
            return c

        @staticmethod
        def gameArenaChain():
            #global day, DEBUG_BE
            #DEBUG_BE = False

            a = pytfall.arena
            acf = a.all_chain_fights
            teams = []
            """
            t = Team(name="test")
            for i in xrange(3):
                c = build_rc(bt_group="Combatant", tier=10, give_bt_items=True)
                t.add(c)
            teams.append(t)
            t = Team(name="testAWAWAS")
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Assassin", "Shooter"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)

            t = Team(name="testAWAWAM")
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Assassin", "Mage"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)

            t = Team(name="testAWAWM")
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Mage"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)

            t = Team(name="testAW")
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)
            t = Team(name="testAM")
            c = build_rc(bt_list=["Assassin", "Mage"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)

            t = Team(name="testAWMM")
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Mage"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Mage"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)

            t = Team(name="testAWHMM")
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Healer", "Mage"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Mage"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)

            t = Team(name="testAWASM")
            c = build_rc(bt_list=["Assassin", "Warrior"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Assassin", "Shooter"], tier=10, give_bt_items=True)
            t.add(c)
            c = build_rc(bt_list=["Mage"], tier=10, give_bt_items=True)
            t.add(c)
            teams.append(t)

            t = Team(name="testAW")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            teams.append(t)
            t = Team(name="testAM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Mage"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWMM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            teams.append(t)
            t = Team(name="testAWHMM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer", "Mage"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWASM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Assassin", "Shooter"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWASH")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Assassin", "Shooter"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer"])
            t.add(c)
            teams.append(t)
            """
            t = Team(name="testAWHMHM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer", "Mage"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer", "Mage"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWHM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWHH")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWMM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWHMM")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer", "Mage"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Mage"])
            t.add(c)
            teams.append(t)

            t = Team(name="testAWHMH")
            c = TestSuite.build_super_char(bt_list=["Assassin", "Warrior"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer", "Mage"])
            t.add(c)
            c = TestSuite.build_super_char(bt_list=["Healer"])
            t.add(c)
            teams.append(t)

            for t in teams:
                temp = len(t)
                flag_name = "arena_cf_%d" % temp
                fail_flag_name = "arena_cf_bad_%d" % temp
                success_name = "arena_cf_good_%d" % temp
                
                for i in xrange(120):
                    a.nd_run_chainfight(t)
                    flagval = t.leader.flag(flag_name)
                    lvl = flagval/5
                    name = acf[lvl]["id"]
                    devlog.warn("%s Round %d: level: %s (flag:%s id: %s), success: %s, fails: (%s)." % (t.name, i, lvl, flagval, name,
                                    t.leader.get_flag(success_name, None),
                                    ", ".join(["%d: %d"% (l, f) for l, f in t.leader.get_flag(fail_flag_name, {}).iteritems()])))
                    for f in t:
                        restore_battle_stats(f)

        @staticmethod
        def gameArena(num, debug=False):
            global day, DEBUG, DEBUG_LOG, DEBUG_PROFILING
            if debug:
                DEBUG = DEBUG_LOG = DEBUG_PROFILING = False

            a = pytfall.arena
            all_chars = chars.values() + fighters.values()
            for i in xrange(num):
                td = [t for t in chain(a.dogteams_2v2, a.dogteams_3v3)]
                tm = [t for t in chain(a.matchteams_2v2, a.matchteams_3v3)]
                a.next_day()
                if debug:
                    for t in td:
                        if t not in a.dogteams_2v2 and t not in a.dogteams_3v3:
                            devlog.warn("Team %s dropped from the dogs." % t.name)

                    for t in tm:
                        if t not in a.matchteams_2v2 and t not in a.matchteams_3v3:
                            devlog.warn("Team %s dropped from the matches." % t.name)

                for c in all_chars:
                    t = c.arena_permit
                    c.next_day()
                    if debug and c.arena_permit != t:
                        if t:
                            TestSuite.reportError("%s lost the arena permit. %s" % (c.fullname, c.arena_rep))
                        else:
                            TestSuite.reportError("%s bought an arena permit. %s" % (c.fullname, c.arena_rep))

                for c in all_chars:
                    for d in c.fighting_days:
                        if d < day:
                            TestSuite.reportError("%s has an obsolete entry in fighting_days: %s" % (c.fullname, d))

                    if not c.arena_active:
                        continue

                    if not c.arena_willing:
                        TestSuite.reportError("%s is arena active, but not willing!" % c.fullname)

                    if c.arena_permit and c.arena_rep < Arena.PERMIT_REP/2:
                        TestSuite.reportError("%s still has an arena permit, but lacks arena_rep: %d" % (c.fullname, c.arena_rep))

                    for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                        if c.get_stat(stat) != c.get_max(stat):
                            TestSuite.reportError("%s - while arena active - does not have maxed out stats(%s: %s vs %s)." % (c.fullname, stat, c.get_stat(stat), c.get_max(stat)))

                for t in chain(a.dogteams_2v2, a.dogteams_3v3):
                    if len(t) != len(t._members):
                        TestSuite.reportError("Arena Dog Team(%s)'s size is incorrect (%d vs %d)." % (t.name, len(t), len(t._members)))
                    mems = set()
                    for c in t:
                        if c not in all_chars:
                            TestSuite.reportError("%s is registered in the arena dog team %s, but not a known char." % (c.fullname, t.name))
                        if c in mems:
                            TestSuite.reportError("%s is twice in arena dog team %s!" % (c.fullname, t.name))
                        mems.add(c)

                for t in chain(a.matchteams_2v2, a.matchteams_3v3):
                    if len(t) != len(t._members):
                        TestSuite.reportError("Arena Match Team(%s)'s size is incorrect (%d vs %d)." % (t.name, len(t), len(t._members)))
                    mems = set()
                    for c in t:
                        if c not in all_chars:
                            TestSuite.reportError("%s is registered in the arena match team %s, but not a known char." % (c.fullname, t.name))
                        if not c.arena_permit:
                            TestSuite.reportError("%s is registered in the arena match team %s, but does not have a permit!" % (c.fullname, t.name))
                        if c in mems:
                            TestSuite.reportError("%s is twice in arena match team %s!" % (c.fullname, t.name))
                        mems.add(c)

                temp = defaultdict(set)
                for t in chain(a.dogteams_2v2, a.dogteams_3v3, a.matchteams_2v2, a.matchteams_3v3):
                    for c in t:
                        teams = temp[c]
                        for x in teams:
                            if len(x) == len(t) and x is not t:
                                TestSuite.reportError("%s is registered in two %s sized arena teams (%s and %s)!" % (c.fullname, len(t), t.name, x.name))
                        teams.add(t)

                for setup in (a.matches_1v1, a.matches_2v2, a.matches_3v3):
                    t = setup[0]
                    if t is setup[1]:
                        TestSuite.reportError("Team %s (%s) is fighting against self!" % (t.gui_name, len(t)))
    
                singles = dict()
                for setup in a.matches_1v1:
                    for t in (setup[0], setup[1]):
                        if t:
                            c = t.leader
                            team = singles.get(c, None)
                            if team is not None and team is not t:
                                TestSuite.reportError("%s is registered with two 'team's in matches 1v1!" % c.fullname)
                            singles[c] = team
                temp = set()
                for t in a.ladder_1v1:
                    c = t.leader
                    if c in temp:
                        TestSuite.reportError("%s is twice on the ladder 1v1!" % c.fullname)
                    team = singles.get(c, None)
                    if team is not None and team is not t:
                        TestSuite.reportError("%s is in the ladder in a different team as registered in matches 1v1!" % c.fullname)
                    temp.add(c)
                temp = set()
                for t in a.ladder_2v2:
                    if t in temp:
                        TestSuite.reportError("%s is twice on the ladder 2v2!" % t.name)
                    temp.add(t)
                temp = set()
                for t in a.ladder_3v3:
                    if t in temp:
                        TestSuite.reportError("%s is twice on the ladder 3v3!" % t.name)
                    temp.add(t)

                for size, ladder in enumerate(((a.ladder_1v1, a.ladder_1v1_members), (a.ladder_2v2, a.ladder_2v2_members), (a.ladder_3v3, a.ladder_3v3_members)), 1):
                    for t, m in zip(*ladder):
                        if len(t) != len(m):
                            if t.leader.employer != hero:
                                TestSuite.reportError("Mismatching team-size (%s) and members count (%s) of %s in the ladder and they are not employed by the hero!" % (len(t), len(m), t.name))
                        if len(m) != size:
                            TestSuite.reportError("Mismatching ladder-size (%s) and members count (%s) of %s!" % (size, len(m), t.name))

                for idx, m in enumerate([a.matches_1v1, a.matches_2v2, a.matches_3v3], 1):
                    for s in m:
                        if not s[1]:
                            TestSuite.reportError("Missing candidate for match %d of matches_%d." % (m.index(s), idx))

                if debug:
                    devlog.warn("Daily Statistics of the Arena (%s)" % day)
                    devlog.warn(" - Chains - Max5: %s, %s, %s - Max: %s, %s, %s - Fails - VMax: %s, %s, %s - Max: %s, %s, %s" %
                               (max(f for f in (c.get_flag("arena_chain_fight_level_1", 0) for c in all_chars) if f == 0 or f%5 != 0), max(f for f in (c.get_flag("arena_chain_fight_level_2", 0) for c in all_chars) if f == 0 or f%5 != 0), max(f for f in (c.get_flag("arena_chain_fight_level_3", 0) for c in all_chars) if f == 0 or f%5 != 0),
                                max(c.get_flag("arena_chain_fight_level_1", 0) for c in all_chars), max(c.get_flag("arena_chain_fight_level_2", 0) for c in all_chars), max(c.get_flag("arena_chain_fight_level_3", 0) for c in all_chars),
                                max(max(c.get_flag("arena_chain_fight_level_failed_1", {0: 0}).values()) for c in all_chars), max(max(c.get_flag("arena_chain_fight_level_failed_2", {0:0}).values()) for c in all_chars), max(max(c.get_flag("arena_chain_fight_level_failed_3", {0:0}).values()) for c in all_chars),
                                max(max(c.get_flag("arena_chain_fight_level_failed_1", [0])) for c in all_chars), max(max(c.get_flag("arena_chain_fight_level_failed_2", [0])) for c in all_chars), max(max(c.get_flag("arena_chain_fight_level_failed_3", [0])) for c in all_chars)))
                    devlog.warn(" - Matches: %s/%s, %s/%s, %s/%s - Dogs: %s, %s, %s - DT: %s, %s - MT: %s, %s" % (
                            len([s for s in a.matches_1v1 if s[1]]), len([s for s in a.matches_1v1 if s[2] == day+1 and s[1]]),
                            len([s for s in a.matches_2v2 if s[1]]), len([s for s in a.matches_2v2 if s[2] == day+1 and s[1]]),
                            len([s for s in a.matches_3v3 if s[1]]), len([s for s in a.matches_3v3 if s[2] == day+1 and s[1]]),
                            len(a.dogfights_1v1), len(a.dogfights_2v2), len(a.dogfights_3v3),
                            len(a.dogteams_2v2), len(a.dogteams_3v3), len(a.matchteams_2v2), len(a.matchteams_3v3)))
                    devlog.warn(" - Ladder: %s - Tops: %s, %s, %s, %s - Bottoms: %s, %s, %s, %s - Min: %s, %s, %s - Max: %s, %s, %s" % (len(a.ladder),
                            a.ladder[0].arena_rep, a.ladder_1v1[0].get_rep(), a.ladder_2v2[0].get_rep(), a.ladder_3v3[0].get_rep(),
                            a.ladder[-1].arena_rep, a.ladder_1v1[-1].get_rep(), a.ladder_2v2[-1].get_rep(), a.ladder_3v3[-1].get_rep(),
                            min(c.arena_rep for c in all_chars if c.arena_active), min(t.get_rep() for t in chain(a.matchteams_2v2, a.dogteams_2v2)),
                            min(t.get_rep() for t in chain(a.dogteams_3v3, a.matchteams_3v3)),
                            max(c.arena_rep for c in all_chars if c.arena_active), max(t.get_rep() for t in chain(a.matchteams_2v2, a.dogteams_2v2)),
                            max(t.get_rep() for t in chain(a.dogteams_3v3, a.matchteams_3v3))))
                    devlog.warn(" - King: %s (Rep: %s, Exp: %s) - Leaders: %s, %s, %s, %s" % (a.king.fullname, a.king.arena_rep, a.king.exp, a.ladder[0].fullname, a.ladder_1v1[0].gui_name, a.ladder_2v2[0].name, a.ladder_3v3[0].name))
                    devlog.warn(" TOTAL Rep: %s, Exp: %s - %s" % (sum(c.arena_rep for c in all_chars if c.arena_active), sum(c.exp for c in all_chars if c.arena_active), sum(c.exp for c in fighters.values()))) 

                day += 1

        @staticmethod
        def loadBuilding(tier=2, op=False, adverts=[], auto_clean=100, auto_guard=0, business=None, businesses={}, workers=[], stats=[]):
            # building
            b = [b for b in buildings.values() if b.tier == tier][0]

            hero.add_building(b)

            b.modrep(b.maxrep)
            b.modfame(b.maxfame)

            b.auto_clean=auto_clean
            b.auto_guard=auto_guard

            # businesses + upgrades
            for bu in b.allowed_businesses:
                ups = businesses.get(bu.name, None)
                if ups is None:
                    if bu in b.businesses:
                        cost, materials, in_slots, ex_slots = bu.get_cost()
                        hero.gold += cost
                        b.close_business(bu)
                else:
                    # business
                    if bu not in b.businesses:
                        cost, materials, in_slots, ex_slots = bu.get_cost()
                        b.in_slots += in_slots
                        b.ex_slots += ex_slots
                        b.add_business(bu, in_game=True)
                    # capacity of the businesses (except the big one)
                    if bu.name != business and bu.expands_capacity:
                        while bu.capacity > 1:
                            cost, materials, in_slots, ex_slots = bu.get_expansion_cost()
                            bu.in_slots -= in_slots
                            b.in_slots -= in_slots
                            bu.ex_slots -= ex_slots
                            b.ex_slots -= ex_slots
                            bu.capacity -= 1
                    # upgrades
                    for up in bu.allowed_upgrades:
                        if up.name in ups:
                            cost, materials, in_slots, ex_slots = up.get_cost()

                            bu.in_slots += in_slots
                            b.in_slots += in_slots
                            bu.ex_slots += ex_slots
                            b.ex_slots += ex_slots
                            
                            bu.add_upgrade(up)
            # capacity of THE business
            for bu in b.businesses:
                if bu.name == business:
                    cost, materials, in_slots, ex_slots = bu.get_expansion_cost()

                    num = min(b.in_slots_max - b.in_slots / in_slots if in_slots != 0 else float("inf"),
                              b.ex_slots_max - b.ex_slots / ex_slots if ex_slots != 0 else float("inf"))

                    in_slots *= num
                    ex_slots *= num

                    bu.capacity += num
                    bu.in_slots += in_slots
                    b.in_slots += in_slots
                    bu.ex_slots += ex_slots
                    b.ex_slots += ex_slots

            # adverts
            for a in b.adverts:
                if a["name"] in adverts:
                    a["active"] = True
            # clients

            # workers
            wtier = tier
            if op is True:
                wtier += 2
            elif op is not False:
                wtier += op
            for bt_list, num, job in workers:
                for i in xrange(num):
                    worker = build_rc(bt_list=bt_list, give_bt_items=True, give_civilian_items=True, tier=wtier)
                    hero.add_char(worker)
                    worker.mod_workplace(b)
                    worker.set_job(job)
                    for ss in stats:
                        if is_stat(ss):
                            mod_by_max(worker, ss, 1.0)
                        else:
                            worker.stats.mod_full_skill(ss, worker.get_max_skill(ss))
                    worker.autocontrol["Tips"] = True
                    worker.wagemod = 200

        # Bar
        @staticmethod
        def loadBarT2_0(op=False):
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=40, auto_guard=1200,
                                   business="Bar", businesses={"Bar": []}, workers=[("Manager", 1, ManagerJob), ("Maid", 4, BarJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBarT2_1(op=False): # 3400
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=1200,
                                   business="Bar", businesses={"Cleaning Block": [], "Bar": []}, workers=[("Manager", 1, ManagerJob), ("Maid", 4, BarJob), ("Maid", 2, CleaningJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBarT2_2(op=False): # 3000
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=1200,
                                   business="Bar", businesses={"Cleaning Block": [], "Bar": ["Tap Beer"]}, workers=[("Manager", 1, ManagerJob), ("Maid", 4, BarJob), ("Maid", 2, CleaningJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBarT2_3(op=False): # 3500
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Bar", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Bar": []}, workers=[("Manager", 1, ManagerJob), ("Maid", 4, BarJob), ("Maid", 2, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBarT2_4(op=False):
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Bar", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Bar": ["Tap Beer"]}, workers=[("Manager", 1, ManagerJob), ("Maid", 4, BarJob), ("Maid", 2, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBarT6_1(op=False): # ... 5.1 - 3
            TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=5400,
                                   business="Bar", businesses={"Cleaning Block": [], "Bar": []}, workers=[("Manager", 1, ManagerJob), ("Maid", 16, BarJob), ("Maid", 4, CleaningJob)],
                                   stats=["charisma", "joy", "disposition"])

        # Brothel
        @staticmethod
        def loadBrothelT2_0(op=False):
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=40, auto_guard=1200,
                                   business="Brothel", businesses={"Brothel": []}, workers=[("Manager", 1, ManagerJob), ("Prostitute", 24, WhoreJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBrothelT2_1(op=False): # 6800
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=1200,
                                   business="Brothel", businesses={"Cleaning Block": [], "Brothel": []}, workers=[("Manager", 1, ManagerJob), ("Prostitute", 24, WhoreJob), ("Maid", 2, CleaningJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBrothelT2_2(op=False): # 5800
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=1200,
                                   business="Brothel", businesses={"Cleaning Block": [], "Brothel": ["Statue"]}, workers=[("Manager", 1, ManagerJob), ("Prostitute", 24, WhoreJob), ("Maid", 2, CleaningJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBrothelT2_3(op=False): # 6000
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Brothel", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Brothel": []}, workers=[("Manager", 1, ManagerJob), ("Prostitute", 24, WhoreJob), ("Maid", 2, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBrothelT2_4(op=False):
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Brothel", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Brothel": ["Statue"]}, workers=[("Manager", 1, ManagerJob), ("Prostitute", 24, WhoreJob), ("Maid", 2, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["charisma", "joy", "disposition"])

        @staticmethod
        def loadBrothelT6_1(op=False): # ... 7.8 - 5.1
            TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=7200,
                                   business="Brothel", businesses={"Cleaning Block": [], "Brothel": []}, workers=[("Manager", 1, ManagerJob), ("Prostitute", 80, WhoreJob), ("Maid", 4, CleaningJob)],
                                   stats=["charisma", "joy", "disposition"])

        # Strip Club
        @staticmethod
        def loadStripT4_0(op=False):
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=40, auto_guard=1200,
                                   business="Strip Club", businesses={"Strip Club": []}, workers=[("Manager", 1, ManagerJob), ("Stripper", 16, StripJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadStripT4_1(op=False): # ... 2.8 - 1.65
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=3000,
                                   business="Strip Club", businesses={"Cleaning Block": [], "Strip Club": []}, workers=[("Manager", 1, ManagerJob), ("Stripper", 16, StripJob), ("Maid", 3, CleaningJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadStripT4_2(op=False): # 23000
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=3000,
                                   business="Strip Club", businesses={"Cleaning Block": [], "Strip Club": ["Catwalk"]}, workers=[("Manager", 1, ManagerJob), ("Stripper", 16, StripJob), ("Maid", 3, CleaningJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadStripT4_3(op=False): # 22000
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Strip Club", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Strip Club": []}, workers=[("Manager", 1, ManagerJob), ("Stripper", 16, StripJob), ("Maid", 3, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadStripT4_4(op=False): # 20000
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Strip Club", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Strip Club": ["Catwalk"]}, workers=[("Manager", 1, ManagerJob), ("Stripper", 16, StripJob), ("Maid", 3, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadStripT6_1(op=False): # ... 6.85 - 3.85
            TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=6400,
                                   business="Strip Club", businesses={"Cleaning Block": [], "Strip Club": []}, workers=[("Manager", 1, ManagerJob), ("Stripper", 24, StripJob), ("Maid", 4, CleaningJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        # Clinic
        @staticmethod
        def loadClinicT4_0(op=False):
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=20, auto_guard=1800,
                                   business="Clinic", businesses={"Clinic": []}, workers=[("Manager", 1, ManagerJob), (["Healer", "Maid"], 4, NurseJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadClinicT4_1(op=False): # ... 2.7 - 1.1 
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=1800,
                                   business="Clinic", businesses={"Cleaning Block": [], "Clinic": []}, workers=[("Manager", 1, ManagerJob), (["Healer", "Maid"], 4, NurseJob), ("Maid", 3, CleaningJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        #@staticmethod
        #def loadClinicT4_2(op=False): # 23000
        #    TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=3000,
        #                           business="Clinic", businesses={"Cleaning Block": [], "Clinic": ["Catwalk"]}, workers=[("Manager", 1, ManagerJob), (["Healer", "Maid"], 16, NurseJob), ("Maid", 3, CleaningJob)],
        #                           stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadClinicT4_3(op=False): # 22000
            TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Clinic", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Clinic": []}, workers=[("Manager", 1, ManagerJob), (["Healer", "Maid"], 4, NurseJob), ("Maid", 3, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        #@staticmethod
        #def loadClinicT4_4(op=False): # 20000
        #    TestSuite.loadBuilding(tier=4, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
        #                           business="Clinic", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Clinic": ["Catwalk"]}, workers=[("Manager", 1, ManagerJob), (["Healer", "Maid"], 16, NurseJob), ("Maid", 3, CleaningJob), ("Warrior", 2, GuardJob)],
        #                           stats=["charisma", "agility", "joy", "disposition"])

        @staticmethod
        def loadClinicT6_1(op=False): # ... 6.75 - 3.1 
            TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=3600,
                                   business="Clinic", businesses={"Cleaning Block": [], "Clinic": []}, workers=[("Manager", 1, ManagerJob), (["Healer", "Maid"], 6, NurseJob), ("Maid", 4, CleaningJob)],
                                   stats=["charisma", "agility", "joy", "disposition"])

        # Stable
        @staticmethod
        def loadStableT6_0(op=False):
            TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=40, auto_guard=1200,
                                   business="Stable", businesses={"Stable": []}, workers=[("Manager", 1, ManagerJob), ("Maid", 16, WranglerJob)],
                                   stats=["agility", "joy", "disposition", "riding"])

        @staticmethod
        def loadStableT6_1(op=False): # ... 2.0 - 1.1
            TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=2400,
                                   business="Stable", businesses={"Cleaning Block": [], "Stable": []}, workers=[("Manager", 1, ManagerJob), ("Maid", 6, WranglerJob), ("Maid", 3, CleaningJob)],
                                   stats=["agility", "joy", "disposition", "riding"])

        #@staticmethod
        #def loadStableT6_2(op=False): # 23000
        #    TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=3000,
        #                           business="Stable", businesses={"Cleaning Block": [], "Stable": ["Catwalk"]}, workers=[("Manager", 1, ManagerJob), ("Maid", 16, WranglerJob), ("Maid", 3, CleaningJob)],
        #                           stats=["agility", "joy", "disposition", "riding"])

        @staticmethod
        def loadStableT6_3(op=False): # 22000
            TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Stable", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Stable": []}, workers=[("Manager", 1, ManagerJob), ("Maid", 16, WranglerJob), ("Maid", 3, CleaningJob), ("Warrior", 2, GuardJob)],
                                   stats=["agility", "joy", "disposition", "riding"])

        #@staticmethod
        #def loadStableT6_4(op=False): # 20000
        #    TestSuite.loadBuilding(tier=6, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
        #                           business="Stable", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Stable": ["Catwalk"]}, workers=[("Manager", 1, ManagerJob), ("Maid", 16, WranglerJob), ("Maid", 3, CleaningJob), ("Warrior", 2, GuardJob)],
        #                           stats=["agility", "joy", "disposition", "riding"])

        # GG
        @staticmethod
        def loadGladiatorsT2_4(op=False): # 22000
            TestSuite.loadBuilding(tier=2, op=op, adverts=["Sign"], auto_clean=100, auto_guard=0,
                                   business="Gladiators Guild", businesses={"Cleaning Block": [], "Warrior Quarters": [], "Gladiators Guild": ["Healing Springs"]}, workers=[("Maid", 1, CleaningJob), ("Warrior", 9, GuardJob)],
                                   stats=["joy", "disposition"])

        # EG

        @staticmethod
        def testMiniJobs(debug=False):
            # Fishing:
            loots, base_loots, good_loots, magic_loots = [], [], [], []
            for item in items.values():
                if "Fishing" in item.locations:
                    temp = item.price
                    if temp > 5000: # SKILLS_MAX
                        TestSuite.reportError("%s is more expensive (%s) than the maximum Skill (%s) required to fish!" % (item.id, temp, 5000)) # SKILLS_MAX
                        continue

                    tmp = (item, item.chance*2 if item.type == "fish" else item.chance)
                    loots.append(tmp)
                    if temp < 10:
                        continue
                    base_loots.append(tmp)
                    if temp < 50:
                        continue
                    good_loots.append(tmp)
                    if temp >= 100:
                        magic_loots.append(tmp)

            if not loots:
                TestSuite.reportError("There is nothing to fish without bait!")
            if not base_loots:
                TestSuite.reportError("There is nothing to fish with normal bait!")
            if not good_loots:
                TestSuite.reportError("There is nothing to fish with good bait!")
            if not magic_loots:
                TestSuite.reportError("There is nothing to fish with magic bait!")

            if debug:                   #      260                    480                        1030                        1590
                for loot, num, type in ((loots, 3, "out"), (base_loots, 4, " normal"), (good_loots, 5, " good"), (magic_loots, 6, " magic")):
                    sum = value = 0
                    for item, chance in loot:
                        sum += chance
                        value += item.price * chance
                    devlog.warn("Expected loot value of fishing with%s bait: %s" % (type, num * value / float(sum)))

            # Diving:
            loots = []
            for item in items.values():
                if "Diving" in item.locations:
                    temp = item.price
                    if temp > 5000: # SKILLS_MAX
                        TestSuite.reportError("%s is more expensive (%s) than the maximum Skill (%s) required to dive!" % (item.id, temp, 5000)) # SKILLS_MAX
                        continue
                    tmp = (item, item.chance)
                    loots.append(tmp)

            if debug:
                sum = value = 0
                for item, chance in loots:
                    sum += chance
                    value += item.price * chance
                num = 250 / 25
                devlog.warn("Expected loot value of diving: %s" % (num * value / float(sum))) # 1860

            # PoolJob:
            if debug:
                hero_skill, char_skill, char_tier = 1000, 1000, 1
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@1000 - 1000 - 1: %s" % result)

                hero_skill, char_skill, char_tier = 3000, 3000, 1
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@3000 - 3000 - 1: %s" % result)

                hero_skill, char_skill, char_tier = 5000, 5000, 1
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@5000 - 5000 - 1: %s" % result)

                hero_skill, char_skill, char_tier = 5000, 1000, 5
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@5000 - 1000 - 5: %s" % result)

                hero_skill, char_skill, char_tier = 5000, 3000, 5
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@5000 - 3000 - 5: %s" % result)

                hero_skill, char_skill, char_tier = 5000, 5000, 5
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@5000 - 5000 - 5: %s" % result)

                hero_skill, char_skill, char_tier = 5000, 1000, 8
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@5000 - 1000 - 8: %s" % result)

                hero_skill, char_skill, char_tier = 5000, 3000, 8
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@5000 - 3000 - 8: %s" % result)

                hero_skill, char_skill, char_tier = 5000, 5000, 8
                result = (hero_skill/10 + 5)/2
                if result > 200:
                    result = 205
                char = build_rc(tier=char_tier)
                tmp = .5 + char_skill / float(char.get_max_skill("swimming"))
                result += 6 * int(char.expected_wage * tmp)

                devlog.warn("Expected Income@5000 - 5000 - 8: %s" % result)

        @staticmethod
        def swingTest():
            hero.mod_stat("reputation", -1000)
            hero.mod_stat("fame", 1000)
            hero.gold = 1000000
            c = chars["Hinata"]
            c.preferences["anal"] = c.preferences["bdsm"] = c.preferences["group"] = 80
            c.mod_stat("affection", 1000)
            c.mod_stat("disposition", 1000)
            set_lovers(c)
            hero.team.add(c)
            c = chars["Sakura"]
            c.preferences["anal"] = c.preferences["bdsm"] = c.preferences["group"] = 80
            c.mod_stat("affection", 1000)
            c.mod_stat("disposition", 1000)
            set_lovers(c)
            hero.team.add(c)

        @staticmethod
        def fashionTest():
            hero.mod_stat("reputation", 1000)
            hero.mod_stat("fame", 1000)
            hero.gold = 1000000
            tier_up_to(hero, 6)
            hero.mod_stat("charisma", hero.get_max("charisma"))
            c = chars["Hinata"]
            c.mod_stat("affection", 1000)
            c.mod_stat("disposition", 1000)
            tier_up_to(c, 6)
            c.mod_stat("charisma", c.get_max("charisma"))
            set_lovers(c)
            hero.team.add(c)
            c = chars["Sakura"]
            c.mod_stat("affection", 1000)
            c.mod_stat("disposition", 1000)
            tier_up_to(c, 6)
            c.mod_stat("charisma", c.get_max("charisma"))
            hero.team.add(c)

        @staticmethod
        def aeqTest():
            base_traits, other_traits, purpose = ["Mage"], ["Impersonal", "Fire"], "Mage"
            #base_traits, other_traits, purpose = ["Shooter"], ["Yandere"], "Shooter"
            #base_traits, other_traits, purpose = ["Knight"], ["Kuudere"], "Barbarian"
            #base_traits, other_traits, purpose = ["Assassin"], ["Kuudere"], "Barbarian"

            tier = 10
            stats_perc = .9

            char = rChar()
            char.name = "dummy"

            # Status next:
            char.status = "free"

            # BASE TRAITS:
            basetraits = set()
            for t in base_traits:
                other_traits.insert(0, t)
                t = traits[t]
                basetraits.add(t)
            char.traits.basetraits = basetraits

            for t in other_traits:
                char.apply_trait(traits[t])

            # Normalizing new character:
            char.init()

            # And at last, leveling up and stats/skills applications:
            tier_up_to(char, tier, level_bios=(1, 1), skill_bios=(1, 1), stat_bios=(1, 1))

            for stat in char.stats:
                #char.set_stat(stat, char.get_max(stat)*stats_perc)
                value = char.stats.lvl_max[stat]
                if stat not in STATIC_CHAR.FIXED_MAX:
                    value *= stats_perc
                    value = int(value)
                char.stats.stats[stat] = value
                char.stats.max[stat] = value

            #char.apply_item_effects(store.items["Cataclysm Scroll"])
            #char.apply_item_effects(store.items["Fist of Bethel Scroll"])
            #char.apply_item_effects(store.items["Transmutation Scroll"])
            #for item in ("Cataclysm Scroll", "Assassin Dagger", "Rune Staff", "Fiery Charm", "Ring of Recklessness", "Mantle of the Keeper", "Ring of Recklessness"):
            for item in ("Cataclysm Scroll", "Mysterious Gray Ring"):
            #for item in ("Demonic Blade", "Mysterious Gray Ring", "Ring of Recklessness", "Ring of Recklessness", "Spray with Acid", "Devil Arms", "Elven Boots"):
                char.equip(store.items[item], remove=False, aeq_mode=True) # Equips the item

            items = []
            limit_tier = min(((char.tier/2)+1), 5)
            for i in range(limit_tier):
                items.extend(store.tiered_items[i]) # MAX_ITEM_TIER

            base_purpose = STATIC_ITEM.AEQ_PURPOSES[purpose]
            fighting = base_purpose.get("fighting")
            target_stats = base_purpose.get("target_stats")
            target_skills = base_purpose.get("target_skills")
            base_purpose = base_purpose.get("base_purpose")

            slots = store.EQUIP_SLOTS.keys()
            slots.append("consumable")

            picks = eval_inventory(char, items, slots, base_purpose, False)

            #picks = [p for p in picks if p.id == "Manual of Health"]
            result = char.stats.weight_items(picks, target_stats, target_skills, fighting, upto_skill_limit=False)

            result.sort(key=lambda x: (x[1].slot, x[0]))

            temp = "A-Eq=> %s: stats@%s" % (char.name, stats_perc)
            for _weight, item in result:
                temp += "\n Slot: %s Item: %s ==> Weight: %s" % (item.slot, item.id, _weight)
            temp += "\n----------------------------------------------------------------------------------------"
            TestSuite.reportError(temp)

        @staticmethod
        def performanceTest():
            msg = "Attempt to auto-buy 3 items for {} girls!".format(len(chars))
            tl.start(msg)
            for i in chars.values():
                i.gold = 100000
                i.autobuy = True
                i.auto_buy(amount=3) #, smart_ownership_limit=False)
                i.auto_equip("Combat")
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
            # "updater", "stored_random_seed" "style", , "anim" "build" "last_inv_filter", 
            temp = set(["gui", "updater", "icon", "ET", "re", "build", "preferences", "style", "layeredimage", "suppress_overlay", "_predict_set", "_cache_pin_set", "_kwargs", "_quit_slot", "_console", "_window_subtitle", "_test", "_m1_classic_load_save__scratch", "_m1_00accessibility__opendyslexic", "_m1_00gltest__dxwebsetup", "_m1_00stylepreferences__spdirty", "_m1_00stylepreferences__preferences", "_m1_00action_data__FieldNotFound", "_m1_00stylepreferences__alternatives", "nvl_list", "fnmatch", "renpy", "simpy", "pygame", "types", "_ignore_action", "anim", "_text_rect", "_side_image", "_side_image_attributes", "main_menu", "logging", "_window_during_transitions", "_rollback", "_begin_rollback", "_return", "store", "_gamepad", "_config", "random", "__file__", "default_transition", "_game_menu_screen", "scrap", "__doc__", "_last_say_who", "_last_say_args", "block_say", "im", "_history", "_in_replay", "sys", "_skipping", "_last_say_kwargs", "collections", "save_name", "_define", "_last_say_what", "_side_image_raw", "_window", "_month_name_long", "_preferences", "ui", "_last_voice_play", "time", "_weekday_name_short", "_side_image_attributes_reset", "last_label", "_version", "_side_image_old", "_confirm_quit", "_overlay_screens", "_history_list", "_warper", "config", "_voice", "math", "__builtins__", "_predict_screen", "_restart", "_args", "iap", "copy", "_nvl_language", "mouse_visible", "_weekday_name_long", "functools", "bisect", "_windows_hidden", "_widget_properties", "itertools", "json", "_dismiss_pause", "define", "_month_name_short", "__package__", "_errorhandling", "SCRAP_TEXT", "audio", "_widget_by_id", "nvl_variant", "_window_auto", "string", "_default_keymap", "library", "director", "inspect", "__name__", "_defaults_set", "print_function", "_load_prompt", "os", "_last_raw_what", "operator", "_menu", "persistent"])
            temp.update(["NextDayEvents", "tl", "EQUIP_SLOTS", "hero", "items", "simple_jobs", "random_team_names", "pytfall", "main_menu", "tiered_items", "gen_occ_basetraits", "male_first_names", "rchars", "undefined", "gfx_overlay", "DEBUG", "DEBUG_SE", "DEBUG_CHARS", "DEBUG_AUTO_ITEM", "DSNBR", "DEBUG_BE", "DEBUG_SIMPY", "DEBUG_QE", "DEBUG_GUI", "DEBUG_PROFILING", "DEBUG_ND", "DEBUG_SIMPY_ND_BUILDING_REPORT", "DEBUG_INTERACTIONS", "DEBUG_LOG", "devlog", "chars", "ND_IMAGE_SIZE", "MOVIE_CHANNEL_COUNT", "tgs", "all_auto_buy_items", "result", "global_flags", "fighters", "mobs", "defeated_mobs", "fg_areas", "traits", "CLIENT_CASTES", "random_last_names", "tiered_magic_skills", "tiered_healing_skills", "iam", "female_first_names", "IMAGE_EXTENSIONS", "MOVIE_EXTENSIONS", "CONTENT_EXTENSIONS", "MUSIC_EXTENSIONS", "IMG_NOT_FOUND_PATH", "last_label", "chars_list_state", "menu_extensions", "last_label_pure", "gamedir", "day", "npcs", "dungeons", "tisa_otm_adv", "pyp", "gazette", "calendar", "tagslog", "tagdb", "DAILY_EXP_CORE", "DAILY_AFF_CORE", "NEXT_MOVIE_CHANNEL", "MAX_TIER", "_COLORS_", "battle_skills"])
            temp.update(["index", "equipment_safe_mode", "girls", "interactions_portraits_overlay", "char", "special_save_number", "world_events", "world_quests", "world_gossips", "battle", "effect_descs"])
            devlog.warn("Current Vars: %s" % ", ".join(k for k in store.__dict__.keys() if k not in temp and not isclass(store.__dict__[k]) and not callable(store.__dict__[k])))

            devlog.warn("Obsolete Vars: %s" % ", ".join(k for k in temp if k not in store.__dict__))
