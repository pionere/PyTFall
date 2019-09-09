init python:
    register_event("swinger_club_adv", locations=["main_street"], simple_conditions=["hero.get_stat('reputation') < -250 and calendar.weekday() == 'Thursday'"], priority=100, start_day=1, max_runs=1, trigger_type="auto")

label swinger_club_adv(event):
    $ a = Character("???", color="orangered", show_two_window=True)
    a "Hey, psst!"
    extend " ... Yes, you!"
    a "You seem like someone who would be interested in our little meetings."
    a "Why don't you come by this address today or any Thursday?!"
    a "Uhh.. sorry, gotta go! Bye."
    $ del a
    $ global_flags.set_flag("know_swinger_club", 1)
    return

label swinger_club:
    hide screen main_street
    if calendar.weekday() != "Thursday":
        "There is nothing here."
        jump main_street

    $ a = Character("???", color="orangered", show_two_window=True)
    if global_flags.get_flag("know_swinger_club") <= 1:
        a "Yes? What do you want?"
        a "Ohh, it seems we have a new guest!"
        a "Well, well. Let me explain the rules."
        a "This is our little SC, or SwingerClub for the uninitiated. Everyone has to bring a partner and {color=gold}10 000 Gold{/color} entry fee for the drinks."
        a "A partner has to be a lover or a just a slave girl, but in the latter case you better say good bye to her, because our members are not really careful with them."
        a "As you probably guessed by now, the lover might not take this encounter well. So take the right one with you."
        extend " Or even two. You know, the more the merrier, haha."
        a "Ohh, and obviously the more distinguished members can spend more time in our fine estabilishment."
        a "Come back when you feel ready!"
        $ global_flags.set_flag("know_swinger_club", 2)
        $ del a
        jump main_street
    elif global_flags.get_flag("know_swinger_club") == 2:
        a "Soo, here you are!"
        a "You know the rules, right? A lover or a slave girl."
        menu:
            "Do you want to enter?"
            "Yes":
                $ global_flags.set_flag("know_swinger_club", 3)
            "No":
                $ del a
                jump main_street
    elif hero.has_flag("dnd_swinger_club"):
        a "Sorry, the party is over."
        $ del a
        jump main_street
    else:
        a "It is nice to see you again!"

    $ partners = [m for m in hero.team if m is not hero and (check_lovers(m) or (m.status == "slave" and m.gender == "female"))]
    if not partners:
        if len(hero.team) == 1:
            a "Sorry, but you can not enter alone."
        else:
            python hide:
                for m in hero.team:
                    if m.status != "slave":
                        iam.dispo_reward(m, -100)
            "Your team members are disgusted that you brought them to such place and force you to leave."
        $ del a, partners
        jump main_street

    if not hero.take_money(10000, "Swinger Club"):
        a "I think you forgot about the entry fee."
        $ del a, partners
        jump main_street

    $ temp = " and ".join([m.name for m in partners]) 
    "You enter the place with [temp]."

    # FIXME better bg?
    scene bg slave_market_club
    with dissolve

    # FIXME play relevant music
    #$ PyTSFX.play_music("club")

    $ hero.set_flag("dnd_swinger_club")
    $ hero.mod_stat("reputation", -randint(0, 1))

    $ skillz = ("anal", "group", "bdsm")
    python hide:
        for m in partners[:]:
            if m.status == "free":
                for s in skillz:
                    if m.preferences[s] > 70:
                        continue
                    if m.get_skill(s) > 4000: # SKILLS_MAX *.8
                        continue
                    iam.refuse_swing(m)
                    iam.dispo_reward(m, -50)
                    narrator("%s is neither interested in %s nor skilled enough to participate and leaves the party." % (m.name, s))
                    partners.remove(m)
                    break

    if not partners:
        a "I'm sorry, but apparently all your partners left, so you must leave as well."
        $ del a, partners, skillz, temp
        jump main_street

    # The Party:
    python:
        # TODO bind with beach_right
        temp = len(partners)
        temp *= hero.get_stat("fame") * -min(0, hero.get_stat("reputation"))
        tmp = hero.get_max("fame") * hero.get_max("reputation") * 2
        if temp > tmp:
            temp = tmp
        temp = round_int(get_linear_value_of(temp, 0, 1, tmp, 16))

        hero.mod_stat("reputation", -randint(1, 2))

        party_image = char = tmp = None
        skilltagz = ["2c anal", "group", "bdsm"]

    show screen swinger_club
    with dissolve

    while temp >= 0:
        $ result = ui.interact()
        
        if result == "check":
            $ temp -= 1
            $ char = choice(partners)
            $ shuffle(skilltagz)
            $ party_image = char.show(skilltagz + ["after sex", "lingerie", "nude"], ("indoors", "no bg", "simple bg"), ("sexwithmc", None), type="ptls")
            if temp > 0 and dice(30):
                menu:
                    char.say "Do you want to join?"
                    "Yes":
                        $ temp -= 1
                        $ party_image = char.show(("group", "after sex", "lingerie", "nude"), ("indoors", "no bg", "simple bg"), ("sexwithmc", None), type="ptls")
                    "No":
                        $ pass
        elif result == "find":
            $ temp -= 1
            if temp > 0 and dice(50):
                # invite to join
                $ char = build_rc(add_to_gameworld=False)
                $ shuffle(skilltagz)
                $ party_image = char.show(skilltagz + ["after sex", "lingerie", "nude"], ("indoors", "no bg", "simple bg"), ("sexwithmc", None), type="ptls")
                menu:
                    char.say "Do you want to join?"
                    "Yes":
                        $ temp -= 1
                        $ party_image = char.show(("group", "after sex", "lingerie", "nude"), ("indoors", "no bg", "simple bg"), ("sexwithmc", None), type="ptls")
                    "No":
                        $ pass
            else:
                # alone
                $ char = build_rc(add_to_gameworld=False)
                $ party_image = char.show(("lingerie", "nude"), ("indoors", "no bg", "simple bg"), excluded=("sex", "after sex"), type="ptls")
                menu:
                    char.say "Hey there, what are you looking for?"
                    "Anal":
                        $ tmp = "2c %s" % ("analtoy" if hero.gender == "female" else "anal")
                    "Bdsm":
                        $ tmp = "bdsm"
                    "Oral":
                        $ tmp = "bc %s" % ("lickpussy" if hero.gender == "female" else "blowjob")
                    "Vaginal" if char.gender == "female":
                        $ tmp = "2c %s" % ("vaginaltoy" if hero.gender == "female" else "vaginal")
                    "Just hanging around":
                        $ tmp = None
                if tmp is not None:
                    $ party_image = char.show((tmp, "after sex", "lingerie", "nude"), ("indoors", "no bg", "simple bg"), ("sexwithmc", None), exclude=["straight" if char.gender == hero.gender else "gay"], type="ptls")
        else:
            $ temp = -1

    # Penalty:
    #  kill slaves
    #  'damage' others
    python hide:
        for m in partners:                                                                          # SKILLS_MAX *.8
            if m.status == "free" or (check_lovers(m) and all((m.preferences[s] > 75 or m.get_skill(s) > 4000) for s in skillz)):
                # char is willing
                mod = 0
                for s in skillz:
                    if m.get_skill(s) < 3000: # SKILLS_MAX *.6
                        # not skilled enough
                        mod += 2
                    elif m.prefences[s] <= 80 and m.get_skill(s) < 4000: # SKILLS_MAX *.8
                        # is not a real 'fan' of the skill
                        mod += 1
                if mod:
                    m.gfx_mod_stat("health", -20*mod)
                    m.gfx_mod_stat("charisma", -randint(4*mod, 8*mod))
                    m.gfx_mod_stat("character", -randint(0, mod))
                    iam.dispo_reward(m, -randint(4*mod, 5*mod))
            else:
                # forced slave -> dead
                kill_char(m)

                hero.mod_stat("reputation", -randint(4, 8))

    a "It was a pleasure for us."
    a "Looking forward to see you again!"

    hide screen swinger_club
    with dissolve

    $ del a, partners, skillz, temp, party_image, skilltagz, char, tmp
    jump main_street

screen swinger_club:
    if party_image is not None:
        add party_image align (.5, .5)

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Check Your %s" % plural("Partner", len(partners)):
            action Return("check")
            sensitive temp > 0
        textbutton "Find Partner":
            action Return("find")
            sensitive temp > 0
        textbutton "Leave":
            action Return("leave")
            sensitive temp >= 0
            keysym "mousedown_3"
