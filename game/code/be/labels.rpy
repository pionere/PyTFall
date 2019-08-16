label test_be:
    python:
        # Prepare the teams:
        enemy_team = Team(name="Enemy Team")
        for mob in ("Slime", "Blazing Star", "Blazing Star"):
            mob = build_mob(id=mob, level=1)
            mob.front_row = 1
            enemy_team.add(mob)

        h = chars["Hinata"]
        if len(hero.team) != 3 and h not in hero.team:
            initial_levelup(h, 50, True)
            h.front_row = 1
            h.status = "free"
            h.employer = hero
            hero.team.add(h)
        n = chars["Sakura"]
        if len(hero.team) != 3 and n not in hero.team:
            initial_levelup(n, 50, True)
            n.front_row = 1
            n.status = "free"
            n.employer = hero
            hero.team.add(n)

        for i in hero.team:
            restore_battle_stats(i)
            i.restore_ap()

        for i in chain(hero.team, enemy_team):
            if i == hero:
                continue
            for skill in battle_skills.values():
                if skill.delivery in ["melee", "ranged"]:
                    if skill not in i.attack_skills:
                        i.attack_skills.append(skill)
                else:
                    if skill not in i.magic_skills:
                        i.magic_skills.append(skill)

        #enemy_team.reset_controller()

        global battle
        battle = BE_Core(bg="content/gfx/bg/be/b_forest_1.webp", music="random",
                         start_sfx=get_random_image_dissolve(1.5), end_sfx=dissolve,
                         use_items=True, give_up="escape", teams=[hero.team, enemy_team])
        battle.start_battle()

    jump mainscreen

label test_be_logical:
    $ tl.start("Logical BE Scenario with Setup!")
    python:
        # Prepear the teams:
        enemy_team = Team(name="Enemy Team")
        if len(enemy_team) != 3:
            mob = build_mob(id="Goblin Shaman", level=120)
            mob.front_row = 1
            mob.apply_trait(traits["Fire"])
            enemy_team.add(mob)
        if len(enemy_team) != 3:
            mob = build_mob(id="Goblin Archer", level=100)
            mob.front_row = 0
            mob.attack_skills.append(battle_skills["Sword Slash"])
            enemy_team.add(mob)
        if len(enemy_team) != 3:
            mob = build_mob(id="Goblin Archer", level=100)
            mob.front_row = 0
            mob.attack_skills.append(battle_skills["Bow Shot"])
            mob.apply_trait(traits["Air"])
            enemy_team.add(mob)

        h = chars["Hinata"]
        if len(hero.team) != 3 and h not in hero.team:
            h.status = "free"
            initial_levelup(h, 50, True)
            h.front_row = 1
            hero.team.add(h)
        n = chars["Sakura"]
        if len(hero.team) != 3 and n not in hero.team:
            n.status = "free"
            n.apply_trait(traits["Air"])
            initial_levelup(n, 50, True)
            n.front_row = 1
            hero.team.add(n)

        for i in hero.team:
            restore_battle_stats(i)
            i.restore_ap()

        hero.team.setup_controller(True)
        enemy_team.setup_controller(True)

        global battle
        battle = BE_Core(logical=True, teams=[hero.team, enemy_team])

        tl.start("Logical BE Scenario without Setup!")
        battle.start_battle()
        tl.end("Logical BE Scenario without Setup!")

        # Reset Controller:
        hero.team.reset_controller()
        enemy_team.reset_controller()

    $ tl.end("Logical BE Scenario with Setup!")

    scene black
    call screen battle_report

    jump mainscreen

screen battle_report():
    vbox:
        align (.5, .3)
        spacing 10
        frame:
            background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
            style "dropdown_gm_frame"

            has viewport:
                xysize (540, 400)
                scrollbars "vertical"
                has vbox
                for entry in reversed(battle.combat_log):
                    label "%s"%entry style_group "stats_value_text" text_size 14 text_color "ivory"

        textbutton "Exit":
            xalign .5
            action Return()
