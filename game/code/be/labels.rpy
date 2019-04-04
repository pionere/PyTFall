label test_be:
    python: # Do this just once, otherwise they get stronger and stronger when reloading.
        h = chars["Hinata"]
        if h.level < 40:
            initial_levelup(h, 50, True)
        h.front_row = 1
        h.status = "free"

        n = chars["Sakura"]
        if n.level < 40:
            initial_levelup(n, 50, True)
        n.front_row = 1
        n.status = "free"

        for skill in battle_skills.values():
            if skill.delivery in ["melee", "ranged"]:
                if skill not in h.attack_skills:
                    h.attack_skills.append(skill)
                if skill not in n.attack_skills:
                    n.attack_skills.append(skill)
            else:
                if skill not in h.magic_skills:
                    h.magic_skills.append(skill)
                if skill not in n.magic_skills:
                    n.magic_skills.append(skill)

    python:
        # Prepare the teams:
        enemy_team = Team(name="Enemy Team", max_size=3)
        mob = build_mob(id="Slime", level=1)
        mob.front_row = 1

        if len(enemy_team) != 3:
            enemy_team.add(mob)

        mob = build_mob(id="Blazing Star", level=1)
        mob.front_row = 1
        if len(enemy_team) != 3:
            enemy_team.add(mob)

        mob = build_mob(id="Blazing Star", level=1)
        mob.front_row = 1
        if len(enemy_team) != 3:
            enemy_team.add(mob)

        if len(hero.team) != 3 and h not in hero.team:
            hero.team.add(h)
        h.AP = 6
        if len(hero.team) != 3 and n not in hero.team:
            hero.team.add(n)
        n.AP = 6

        for i in hero.team:
            i.set_stat("health", i.get_max("health"))
            i.set_stat("mp", i.get_max("mp"))
            i.set_stat("vitality", i.get_max("vitality"))

        for i in enemy_team:
            # i.controller = Complex_BE_AI(i)
            for skill in battle_skills.values():
                if skill.delivery in ["melee", "ranged"]:
                    if skill not in i.attack_skills:
                        i.attack_skills.append(skill)
                    if skill not in i.attack_skills:
                        i.attack_skills.append(skill)
                else:
                    if skill not in i.magic_skills:
                        i.magic_skills.append(skill)
                    if skill not in i.magic_skills:
                        i.magic_skills.append(skill)
        # ImageReference("chainfights")
        enemy_team.reset_controller()

    python:
        battle = BE_Core(Image("content/gfx/bg/be/b_forest_1.webp"), music="random",
                         start_sfx=get_random_image_dissolve(1.5), end_sfx=dissolve,
                         use_items=True, give_up="escape")
        battle.teams.append(hero.team)
        battle.teams.append(enemy_team)
        battle.start_battle()

    jump mainscreen

label test_be_logical:
    $ tl.start("Logical BE Scenario with Setup!")
    python:
        # Prepear the teams:
        enemy_team = Team(name="Enemy Team", max_size=3)
        if len(enemy_team) != 3:
            mob = build_mob(id="Goblin Shaman", level=120)
            mob.controller = BE_AI(mob)
            mob.front_row = 1
            mob.apply_trait("Fire")
            enemy_team.add(mob)
        if len(enemy_team) != 3:
            mob = build_mob(id="Goblin Archer", level=100)
            mob.controller = BE_AI(mob)
            mob.front_row = 0
            mob.attack_skills.append("Sword Slash")
            enemy_team.add(mob)
        if len(enemy_team) != 3:
            mob = build_mob(id="Goblin Archer", level=100)
            mob.controller = BE_AI(mob)
            mob.front_row = 0
            mob.attack_skills.append("Bow Shot")
            mob.apply_trait("Air")
            enemy_team.add(mob)

        hero.controller = BE_AI(hero)
        h = chars["Hinata"]
        h.status = "free"
        h.controller = BE_AI(h)
        initial_levelup(h, 50, True)
        h.front_row = 1
        n = chars["Sakura"]
        n.status = "free"
        n.controller = BE_AI(n)
        n.apply_trait("Air")
        n.front_row = 1
        initial_levelup(n, 50, True)

        if len(hero.team) != 3 and h not in hero.team:
            hero.team.add(h)
        h.AP = 6
        if len(hero.team) != 3 and n not in hero.team:
            hero.team.add(n)
        n.AP = 6
        # ImageReference("chainfights")
        battle = BE_Core(logical=True)
        battle.teams.append(hero.team)
        battle.teams.append(enemy_team)

        tl.start("Logical BE Scenario without Setup!")
        battle.start_battle()
        tl.end("Logical BE Scenario without Setup!")

        # Reset Controller:
        hero.controller = None
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
