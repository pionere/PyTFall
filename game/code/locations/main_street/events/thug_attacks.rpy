init python:
    register_event("city_events_thugs_robbery", locations=["main_street"], run_type="jump", priority=50, start_day=1, times_per_days=(1,7))

label city_events_thugs_robbery:
    scene
    $ renpy.scene(layer="screens")
    show bg street_alley with dissolve
    "As you walking down the alley, a shady man approaches you."
    show expression npcs["street_thug"].get_vnsprite() as npc with dissolve
    $ t = npcs["street_thug"].say
    t "A word, my friend!"
    t "These streets are unsafe if you know what I mean. But I can ensure your safety. 200 Gold per week. The price is pretty reasonable, right?"
    if hero.gold < 200:
        "Unfortunately, you don't have enough money."
        t "Hard times, eh... Well, there you go then."
        "He tosses you a few coins."
        t "My mother always told me to help those in need, heh. See ya."
        $ hero.add_money(randint(2, 5), reason="Charity")
        hide npc with dissolve
    else:
        menu:
            "Give him 200 Gold?"
            "Yes":
                t "Thank you kindly. Worry not, no one will bother you. For now."
                $ kill_event("city_events_thugs_robbery_attack")
                $ register_event("city_events_thugs_robbery", locations=["main_street"], run_type="jump", priority=50, start_day=day+7, times_per_days=(1,3))
                $ hero.take_money(200, reason="Robbery")
                if hero.get_stat("joy") > 70:
                    $ hero.gfx_mod_stat("joy", -randint(0, 2))
            "No":
                t "It's your choice. Don't blame me if something will happen."
                $ register_event("city_events_thugs_robbery_attack", locations=["main_street", "city_parkgates", "graveyard_town", "village_town"], run_type="jump", priority=1000, start_day=day+1, times_per_days=(1,2))
            "Attack him":
                t "Oho, you have guts, I like it. Let's see what you can do against my boys!"
                python hide:
                    back = iam.select_background_for_fight("city")
                    enemy_team = Team(name="Enemy Team")
                    min_lvl = max(mobs["Thug"]["min_lvl"], 45)
                    for i in xrange(3):
                        mob = build_mob("Thug", level=randint(min_lvl, min_lvl+20))
                        enemy_team.add(mob)
                    result = run_default_be(enemy_team, background=back, end_background="street_alley", prebattle=True)
                    if result is True:
                        renpy.jump("city_events_thugs_robbery_win")
                    else:
                        renpy.jump("city_events_thugs_robbery_lost")
    $ del t
    jump main_street

label city_events_thugs_robbery_win:
    show expression npcs["street_thug"].get_vnsprite() as npc with dissolve
    t "Nice moves! Fair enough, [hero.name]. My guys won't bother you any longer. See ya."
    $ kill_event("city_events_thugs_robbery_attack")
    $ kill_event("city_events_thugs_robbery")
    "He walks away."
    $ del t
    jump main_street

label city_events_thugs_robbery_lost:
    show expression npcs["street_thug"].get_vnsprite() as npc with dissolve
    t "Huuh? That's it?!"
    if hero.gold > 0:
        t "I'm taking your gold to give you a lesson: don't start a battle you can't win, idiot."
    $ g = min(hero.gold, randint(500, 800))
    $ hero.take_money(g, reason="Robbery")
    $ hero.gfx_mod_stat("joy", -randint(1, 3))
    "He walks away."
    $ del t, g
    jump main_street

label city_events_thugs_robbery_attack:
    "A group of men suddenly surrounds you!"
    python hide:
        hs() # hide everything

        scr = pytfall.world_events.event_instance("city_events_thugs_robbery_attack").label_cache
        back = iam.select_background_for_fight(scr)
        enemy_team = Team(name="Enemy Team")
        min_lvl = max(mobs["Thug"]["min_lvl"], 25)
        for i in xrange(3):
            mob = build_mob("Thug", level=randint(min_lvl, min_lvl+10))
            enemy_team.add(mob)
        result = run_default_be(enemy_team, background=back, end_background=scr, prebattle=True)

        if result is True:
            # win
            g = randint(10, 40)
            hero.add_money(g, reason="Events")
            gfx_overlay.random_find(g, 'gold')
            narrator("You found some gold in their pockets before handing them over to the City Guards.")
        else:
            # lost
            g = min(hero.gold, randint(200, 400))
            hero.take_money(g, reason="Robbery")
            hero.gfx_mod_stat("joy", -randint(0, 2))
            narrator("After beating you, they took some gold and disappeared before City Guards arrived.")

        renpy.jump(scr)