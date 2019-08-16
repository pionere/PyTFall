label city_beach_right:
    $ iam.enter_location(goodtraits=["Not Human", "Alien"], badtraits=["Shy", "Coward", "Homebody", "Human"],
                        coords=[[.4, .9], [.6, .8], [.9, .7]])
    python:
        # Build the actions
        if pytfall.world_actions.location("city_beach_right"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg city_beach_right
    with dissolve
    show screen city_beach_right
    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            python hide:
                char = result[1]
                iam.start_int(char, img=iam.select_beach_img_tags(char), keep_music=False)

        elif result == ['control', 'return']:
            $ global_flags.set_flag("keep_playing_music")
            hide screen city_beach_right
            jump city_beach


screen city_beach_right():
    use top_stripe(True)
    use location_actions("city_beach_right")

    if iam.show_girls:
        use interactions_meet
    else:
        $ img = im.Scale("content/gfx/interface/icons/beach_competition.png", 80, 80)
        imagebutton:
            pos (870, 400)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_right"), Jump("mc_action_beach_competitions")]
            tooltip "Competitions"

        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "return"])

label mc_action_beach_competitions:
    if not global_flags.flag('beach_competition'):
        $ global_flags.set_flag('beach_competition')
        "Here you can organize various events for the public (2 AP)."
        extend "Each event has a base price, but you can decide to spend more gold on it."
        "The number of competitors is depending on your fame and reputation, "
        extend "as well as the gold you spent on it."
        "Depending on the event type, you might choose the winner yourself."
        extend " In case of the 'Swimsuit contest' always, otherwise if the result is a draw."

    if hero.has_flag("dnd_beach_competition"):
        "You already organized an event today."
        jump city_beach_right

    menu:
        "What kind of event do you want to organize?"

        "Sport (10000+ Gold)":
            $ event_type = "sport"
            $ base_expense = 10000
        "Magic (20000+ Gold)":
            $ event_type = "magic"
            $ base_expense = 20000
        "Swimsuit contest (100000+ Gold)":
            $ event_type = "swimsuit"
            $ base_expense = 100000
        "Forget it":
            jump city_beach_right

    $ expenses = [base_expense, 2*base_expense, 4*base_expense]
    menu:
        "How much gold do you want to spend on the event?"

        "[expenses[0]]" if hero.gold >= expenses[0]:
            $ expense = expenses[0]
        "[expenses[1]]" if hero.gold >= expenses[1]:
            $ expense = expenses[1]
        "[expenses[2]]" if hero.gold >= expenses[2]:
            $ expense = expenses[2]
        "Forget it":
            $ del event_type, base_expense, expenses
            jump city_beach_right

    if not hero.take_ap(2):
        "You don't have enough Action Points left (You need at least 2 AP). Try again tomorrow."
        $ del event_type, base_expense, expenses
        jump city_beach_right

    $ hero.take_money(expense, "Beach Competition")
    $ competitors = []
    python hide:
        mod = expense / float(base_expense)
        mod *= hero.get_stat("fame") * hero.get_stat("reputation")
        stat_max = hero.get_max("fame") * hero.get_max("reputation") * 2
        if mod > stat_max:
            mod = stat_max
        num = round_int(get_linear_value_of(mod, 0, 1, stat_max, 16))

        interactive_chars = set(iam.get_all_girls()) | set(hero.chars) ^ set(iam.display_girls())
        possible_chars = [c for c in chars.itervalues() if c not in interactive_chars]
        choices = [c for c in possible_chars if c.home == pytfall.city and c.location != pytfall.jail]

        num = min(len(choices), num)
        competitors.extend(random.sample(choices, num))

    if not competitors:
        "Unfortunately no one come to the event."
        $ del competitors, base_expense, expense, expenses, event_type
        jump city_beach_right

    call screen beach_competition_event(competitors[:], event_type)
    $ winners = _return

    show screen beach_competition_result(winners, event_type)

    python:
        num = len(competitors) * 8 
        winners[0].add_money(expense/2)
        winners[0].gfx_mod_stat("disposition", randint(num/2, num))
        winners[0].gfx_mod_stat("affection", affection_reward(winners[0], .02 * num))
        winners[0].gfx_mod_stat("joy", randint(num/4, num/2))
        if len(winners) > 1:
            winners[1].add_money(expense/5)
            winners[1].gfx_mod_stat("disposition", randint(num/4, num/2))
            winners[1].gfx_mod_stat("affection", affection_reward(winners[1], .01 * num))
            winners[1].gfx_mod_stat("joy", randint(num/8, num/4))
        if len(winners) > 2:
            winners[2].add_money(expense/10)
            winners[2].gfx_mod_stat("disposition", randint(num/8, num/4))
            winners[2].gfx_mod_stat("affection", affection_reward(winners[2], .005 * num))
            winners[2].gfx_mod_stat("joy", randint(num/16, num/8))

    $ del winners, competitors, base_expense, expense, expenses, event_type, num

    while 1:
        $ result = ui.interact()

        if result == "done":
            hide screen beach_competition_result
            jump city_beach_right

screen beach_competition_event(competitors, event_type):
    default winners = []
    default char0 = None
    if len(competitors) == 1:
        if char0 is None:
            $ char0 = competitors[0]
            $ char0_img = char0.show(event_type, "beach", exclude=["nude", "sex"], type="reduce", resize=(800, 600))
            $ winners.insert(0, char0)

        add char0_img at truecenter
        text "Winner" align (0.5, 0.9) size 30 color "lime" outlines [(1, "#3a3a3a", 0, 0)]
        timer 1.0 action Return(winners)
    else:
        $ rng_winners = random.sample(competitors, min(len(competitors), 3-len(winners))) + winners
        vbox:
            style_group "wood"
            xalign .5
            button:
                xysize (250, 40)
                action Return(rng_winners)
                text "Finish" size 15
                keysym "mousedown_3"

        default runners = []
        default char1 = None
        python:
            if char0 is None:
                if len(runners) < 2:
                    runners = competitors[:]
                char0 = runners.pop()
                char1 = runners.pop()
                char0_img = char0.show(event_type, "beach", exclude=["nude", "sex"], type="reduce", resize=(600, 515))
                char1_img = char1.show(event_type, "beach", exclude=["nude", "sex"], type="reduce", resize=(600, 515))

        add char0_img at center_left
        add char1_img at center_right

        $ winner = None
        if event_type == "sport":
            $ value0 = max(1, char0.get_stat("agility"))
            $ value1 = max(1, char1.get_stat("agility"))
            if not (.8 < abs(value0/float(value1)) < 1.25) or dice(80):
                $ winner = weighted_choice([(char0, value0), (char1, value1)])
        elif event_type == "magic":
            $ value0 = max(1, char0.get_stat("magic"))
            $ value1 = max(1, char1.get_stat("magic")) 
            if not (.8 < abs(value0/float(value1)) < 1.25) or dice(40):
                $ winner = weighted_choice([(char0, value0), (char1, value1)])
        if winner is None:
            if event_type != "swimsuit":
                text "Draw" align (0.5, 0.9) size 20 color "tomato" outlines [(1, "#3a3a3a", 0, 0)]

            $ actions = [Function(competitors.remove, char1), SetScreenVariable("char0", None)]
            if len(competitors) <= 3:
                $ actions.append(Function(winners.insert, 0, char1))
            textbutton "Winner is %s" % char0.name:
                align .2, .95
                style "basic_choice_button"
                text_color "black"
                action actions

            $ actions = [Function(competitors.remove, char0), SetScreenVariable("char0", None)]
            if len(competitors) <= 3:
                $ actions.append(Function(winners.insert, 0, char0))
            textbutton "Winner is %s" % char1.name:
                align .8, .95
                style "basic_choice_button"
                text_color "black"
                action actions
        else:
            if winner == char0:
                $ loser = char1
                text "Winner" align (0.2, 0.9) size 20 color "lime" outlines [(1, "#3a3a3a", 0, 0)]
            else:
                $ loser = char0
                text "Winner" align (0.8, 0.9) size 20 color "lime" outlines [(1, "#3a3a3a", 0, 0)]

            $ actions = [Function(competitors.remove, loser), SetScreenVariable("char0", None)]
            if len(competitors) <= 3:
                $ actions.append(Function(winners.insert, 0, loser))
            textbutton "Next":
                align .5, .95
                xysize (250, 40)
                style "basic_choice_button"
                text_color "black"
                action actions

screen beach_competition_result(winners, event_type):
    # podium
    add im.Scale("content/gfx/images/podium.webp", 815, 120) align .5, .8

    # winners
    default char0 = None
    default char1 = None
    default char2 = None
    if len(winners) > 2:
        if char2 is None:
            $ char2 = winners[2].show(event_type, "no bg", exclude=["nude", "sex"], type="reduce", resize=(240, 400))
        add char2 align .77, .42

    if len(winners) > 1:
        if char1 is None:
            $ char1 = winners[1].show(event_type, "no bg", exclude=["nude", "sex"], type="reduce", resize=(240, 400))
        add char1 align .23, .38

    if char0 is None:
        $ char0 = winners[0].show(event_type, "no bg", exclude=["nude", "sex"], type="reduce", resize=(240, 400))
    add char0 align .5, .28

    textbutton "Done":
        align .5, .95
        xysize (250, 40)
        style "basic_choice_button"
        text_color "black"
        action Return("done")
        keysym "mousedown_3"
