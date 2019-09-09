init python:
    register_event("fashion_show_adv", locations=["tailor_store"], simple_conditions=["hero.get_stat('reputation') > 500 and hero.get_stat('fame') > 500"], priority=100, start_day=1, max_runs=1, jump=True, trigger_type="auto")

label fashion_show_adv:
    t "Ohh, I almost forgot... I would like to have a word about something."
    t "We used to have a local fashion show to raise funds for the city."
    extend " Since you became a distinguished member of Pytfall, I would like to invite you there."
    t "It takes place every Wednesday. Come by with your partner or even alone, but I'm sure many girls would like to participate in such an event."
    t "You can bring more partners, but there are some conservatives who might frown upon such things..."
    t "This is a party for the elite so please dress accordingly."
    t "But I don't want to steal your precious time any more. So if you excuse me..."
    $ global_flags.set_flag("know_fashion_show")
    jump tailor_menu

label fashion_show:
    if calendar.weekday() != "Wednesday":
        "The place is empty."
        t "Ooh, it is only on Wednesdays, remember?"
        jump tailor_menu

    if hero.has_flag("dnd_fashion_show"):
        t "Sorry, the show is over. Check out next week as well!"
        jump tailor_menu

    if hero.get_stat("reputation") < 200:
        t "I'm sorry, but I can not let you enter here."
        python hide:
            for m in hero.team:
                if m is not hero:
                    iam.dispo_reward(m, -20)
        jump tailor_menu

    scene bg bar_stage
    with dissolve

    $ char = None
    $ partners = [char for char in hero.team if char is not hero]
    if partners:
        $ temp = " and ".join([char.name for char in partners])
        "You enter the place with [temp]."
    else:
        $ temp = None
        "You enter the place."

    $ kayo = npcs["Kayo_Sudou"]
    $ refvalue = kayo.get_relative_max_stat("charisma", 6)
    if any(char.get_stat("charisma") < refvalue/2 for char in hero.team):
        t "I'm really sorry, but your attire does not fit here. I have to ask you to leave."
        $ del t, refvalue, kayo, temp, partners, char
        jump main_street

    t "Welcome to our fashion show!"
    if partners:
        extend " Before you seat yourself, I would like to ask something from [hero.name]."
    menu:
        t "How much do you want to give to our charity?"
        "0":
            $ temp = 0
        "10 000" if hero.gold >= 10000:
            $ temp = 10000
        "20 000" if hero.gold >= 20000:
            $ temp = 20000
        "50 000" if hero.gold >= 50000:
            $ temp = 50000
        "100 000" if hero.gold >= 100000:
            $ temp = 100000
        "Leave":
            $ del t, refvalue, kayo, temp, partners, char
            jump main_street
    if temp != 0:
        $ hero.take_money(temp, "Fashion Show")
        t "Thank you. Please take a seat."
    else:
        t "Well, then please take a seat."
    $ tmp = (temp - 10000) / 1000
    $ iam.dispo_reward(kayo, randint(tmp, tmp+2))
    $ affection_reward(kayo, tmp*.1)

    # Reputation reward:
    python hide:
        # charity
        tmp = (temp - 10000) / (10000 * max(1, len(partners)))
        # partners
        for char in hero.team:
            tmp += 3*min(char.get_stat("charisma") - refvalue, refvalue) / float(refvalue)
        hero.mod_stat("reputation", int(tmp))

    $ hero.set_flag("dnd_fashion_show")

    # FIXME play relevant music
    #$ PyTSFX.play_music("fashion_show")

    # The Party:
    $ style = [("lingerie", "lingeries"),
               ("indoor", "indoor garments"),
               ("formal", "formal dresses"),
               ("everyday", "everyday clothes"),
               ("maid", choice(["maid dresses", "maid costumes"])),
               ("swimsuit", "swimsuits"),
               ("sportswear", "sportswear"),
               ("schoolgirl", choice(["schoolgirl dresses", "schoolgirl costumes"])),
               ("nurse", choice(["nurse dresses", "nurse costumes"]))]
    $ style = renpy.random.choice(style)

    t "Attention please!"
    t "Welcome everybody to our fashion show!"
    $ tmp = choice(["Today I would like to present you the latest %s!",
                     "I would like to present you the best %s!",
                     "Please have a look at the latest %s!",
                     "Today you can check out the latest trends of %s!"])
    $ tmp %= style[1]
    t "[tmp]"
    hide npc
    with dissolve

    python:
        # TODO bind with beach_right
        temp = max(1, temp/10000)
        temp *= hero.get_stat("fame") * max(0, hero.get_stat("reputation"))
        tmp = hero.get_max("fame") * hero.get_max("reputation") * 2
        if temp > tmp:
            temp = tmp
        temp = round_int(get_linear_value_of(temp, 0, 1, tmp, 16))

        party_image = char = None
        tmp = [0, 0]

    show screen fashion_show
    with dissolve

    while temp >= 0:
        $ result = ui.interact()
        
        if result == "check":
            $ char = choice(partners)
            $ party_image = char.show("formal", ("no bg", "indoors", "simple bg"), ("eating", None), exclude=["sex", "nude"], label_cache=True, type="ptls")
            $ tmp[0] += 1
        elif result == "talk":
            $ party_image = kayo.show("formal", ("no bg", "indoors", "simple bg"), ("eating", None), exclude=["sex", "nude"], label_cache=True, type="ptls")
            $ tmp[1] += 1
        elif result == "watch":
            $ temp -= 1
            $ char = build_rc(add_to_gameworld=False)
            $ party_image = char.show(style[0], ("stage", "no bg", "indoors", "simple bg"), ("revealing", None), exclude=["sex", "nude"], type="ptls")
        else:
            $ temp = -1

    # Dispo rewards:
    python hide:
        for char in partners:
            mod = 20 if char.status == "free" else 40
            iam.dispo_reward(char, randint(mod, mod+2))
            affection_reward(char, mod*.5)

    hide screen fashion_show
    with dissolve

    show expression kayo.get_vnsprite() as npc
    with dissolve
        
    t "Thank you for coming!"
    t "Hope to see you soon!"

    if partners:
        if tmp[0] == 0:
            $ char = choice(partners)
            $ temp = ["You did not even look at me during the whole event!", "Why did you even bring me here?", "You were just ogling them, right?", "Hey! I'm also here, you know?"]
            if tmp[1] != 0 and check_lovers(char):
                $ temp += ["Do you want something from Kayo?", "Is Kayo more interesting than me?"]
            $ iam.dispo_reward(char, -40)
            $ iam.say_line(char, temp, "angry")
        elif tmp[1] > tmp[0]:
            $ partners = [char for char in partners if check_lovers(char)]
            if partners:
                $ char = choice(partners)
                $ temp = ["Do you want something from Kayo?", "Is Kayo more interesting than me?", "I guess Kayo is a really interesting woman...", "Kayo was really impressive, right?"]
                $ iam.dispo_reward(char, -20)
                $ iam.say_line(char, temp, "angry")
    $ del t, refvalue, kayo, partners, temp, party_image, char, tmp, style
    jump main_street

screen fashion_show:
    if party_image is not None:
        add party_image align (.5, .5)

    style_prefix "action_btns"
    frame:
        has vbox
        if partners:
            textbutton "Check Your %s" % plural("Partner", len(partners)):
                action Return("check")
                sensitive temp >= 0
        textbutton "Check Kayo":
            action Return("talk") # TODO romance with Kayo?
            sensitive temp >= 0
        textbutton "Watch the show":
            action Return("watch")
            sensitive temp > 0
        textbutton "Leave":
            action Return("leave")
            sensitive temp >= 0
            keysym "mousedown_3"
