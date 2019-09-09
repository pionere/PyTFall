label girl_interactions:
    # Run quests and events
    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    scene expression iam.bg_cache

    $ PyTSFX.set_music(False) # TODO pytfall.enter_location("interaction", False, iam.env_cache) ?

    show screen girl_interactions
    with dissolve

    # Show greeting:
    if iam.see_greeting:
        $ iam.see_greeting = False

        if renpy.has_label("%s_greeting" % iam.mode):
            call expression ("%s_greeting" % iam.mode) from _call_expression

label girl_interactions_after_greetings: # when character wants to say something in the start of interactions, we need to skip greetings and go here
    python hide:
        # Show menu
        iam.show_menu = True

        # GM labels can now be of the following formats (where %l is the label and %g is the girl's id):
        # girl_meets_%l_%g
        # girl_meets_%l
        # girl_interactions_%l_%g
        # girl_interactions_%l
        # girl_trainings_%l_%g
        # girl_trainings_%g
        # interaction_%l_%g
        # interaction_%l
        #
        # The GM system will pick the most specific available label. Possible choices can be restricted by setting the follow arguments as False:
        # allow_gm
        # allow_int
        # allow_tr
        # allow_unique
        #
        # Note, the above doesn't work for actions generated through the ST module, although they will use girl-specific labels if available.
        #
        # You can limit what action is available under what mode by setting the mode argument to:
        # girl_meets = When meeting free girls in the city.
        # girl_interactions = When interacting with girls under your employ.
        # girl_training = When training slaves.
        #
        # If you wish to limit an entire menu you need to set condition to either _gm_mode, _gi_mode or _gt_mode for girl_meets, girl_interactions or girl_trainings respectively.
        #

        # Create actions
        pwa = pytfall.world_actions
        if pwa.location("girl_interactions"):
            #_gi_mode = Iff(S((iam, "mode")), "==", "girl_interactions")
            #_gt_mode = Iff(S((iam, "mode")), "==", "girl_trainings")

            # CHAT
            m = 0
            pwa.menu(m, "Chat")
            pwa.gm_choice("Small Talk", index=(m, 0))
            pwa.gm_choice("About Job", condition="char.employer == hero", index=(m, 1))
            pwa.gm_choice("How She Feels", condition="char.gender == 'female' and char.employer == hero", label="how_feels", index=(m, 2))
            pwa.gm_choice("How He Feels", condition="char.gender != 'female' and char.employer == hero", label="how_feels", index=(m, 3))
            pwa.gm_choice("About Her", condition="char.gender == 'female'", label="about_char", index=(m, 4))
            pwa.gm_choice("About Him", condition="char.gender != 'female'", label="about_char", index=(m, 5))
            pwa.gm_choice("About Occupation", condition="char.employer != hero", index=(m, 6))
            pwa.gm_choice("Interests", index=(m, 7))
            pwa.gm_choice("Flirt", index=(m, 8))

            # TRAINING
            #m = 1
            #pwa.menu(m, "Training", mode="girl_trainings")

            # Loop through all courses that don't belong to a school, and return the real dict
            #n = 0
            #for k,c in get_all_courses(no_school=True, real=True).iteritems():

            # Loop through all courses in the training dungeon:
            # for b in hero.buildings:
                # if isinstance(b, TrainingDungeon):
                    # for k,c in schools[TrainingDungeon.NAME].all_courses.iteritems():
                        # # Get the lessons that are one off events
                        # ev = [l for l in c.options if l.is_one_off_event]

                        # if ev:
                            # # Create the menu for the course
                            # pwa.menu((m, n), k, condition=OneOffTrainingAction("menu", c))

                            # for l in range(len(ev)):
                                # # Add the lesson
                                # pwa.add((m, n, l), ev[l].name, OneOffTrainingAction("action", ev[l]), condition=OneOffTrainingAction("condition", ev[l]))

                            # n += 1

            # PRAISE
            m = 2
            pwa.menu(m, "Praise", condition="char.employer != hero")
            pwa.gm_choice("Clever", index=(m, 0))
            pwa.gm_choice("Strong", index=(m, 1))
            pwa.gm_choice("Cute", index=(m, 2))

            # INSULT
            m = 3
            pwa.menu(m, "Insult", condition="char.employer != hero")
            pwa.gm_choice("Stupid", index=(m, 0))
            pwa.gm_choice("Weak", index=(m, 1))
            pwa.gm_choice("Ugly", index=(m, 2))

            # GIVE MONEY
            m = 4
            pwa.menu(m, "Money", condition="char.status == 'free'")
            pwa.gm_choice("Give money", label="giftmoney", index=(m, 0))
            pwa.gm_choice("Ask for money", label="askmoney", index=(m, 1))

            m = 5
            pwa.menu(m, "Money", condition="char.status != 'free'")
            pwa.gm_choice("Give", label="give_money", index=(m, 0))
            pwa.gm_choice("Take", label="take_money", index=(m, 1))

            # GIVE GIFT
            m = 6
            pwa.add(m, "Give Gift", Return(["gift", True]))

            # INVITE
            m = 7
            pwa.menu(m, "Invite", condition="iam.label_cache in ('main_street', 'city_beach_cafe_main', 'academy_town', 'char_profile')")
            pwa.gm_choice("Ice Cream", condition="iam.label_cache in ('city_beach_cafe_main', 'char_profile')", label="invite_ice", index=(m, 0))
            pwa.gm_choice("Cafe", condition="iam.label_cache in ('main_street', 'char_profile')", label="invite_cafe", index=(m, 1))
            pwa.gm_choice("Eat out", condition="iam.label_cache in ('main_street', 'char_profile')", label="invite_eat", index=(m, 2))
            pwa.gm_choice("Study", condition="iam.label_cache in ('academy_town', 'char_profile')", label="invite_study", index=(m, 3))

            # PROPOSITION
            m = 8
            pwa.menu(m, "Propose")
            pwa.gm_choice("Girlfriend", condition="char.gender == 'female' and not check_lovers(char)", label="befriend", index=(m, 0))
            pwa.gm_choice("Boyfriend", condition="char.gender != 'female' and not check_lovers(char)", label="befriend", index=(m, 1))
            pwa.gm_choice("Break Up", condition="check_lovers(char)", index=(m, 2))
            pwa.gm_choice("Move in", condition="char.home != hero.home and char.status == 'free'", index=(m, 3))
            pwa.gm_choice("Move out", condition="char.home == hero.home and char.status == 'free'", index=(m, 4))
            pwa.gm_choice("Hire", condition="char.employer != hero", index=(m, 5))
            pwa.gm_choice("Sparring", condition="char.employer != hero", index=(m, 6))

            # PLAY A GAME
            m = 9
            pwa.menu(m, "Play")
            pwa.gm_choice("Archery", label="play_bow", index=(m, 0))
            pwa.gm_choice("PowerBalls", label="play_power", index=(m, 1))

            # INTIMACY
            m = 10
            pwa.menu(m, "Intimacy")
            pwa.gm_choice("Hug", index=(m, 0))
            pwa.gm_choice("Touch Cheek", index=(m, 1))
            pwa.gm_choice("Grab Butt", index=(m, 2))
            pwa.gm_choice("Grab Breasts", condition="char.gender == 'female'", index=(m, 3))
            pwa.gm_choice("Kiss", index=(m, 4))
            pwa.gm_choice("Sex", index=(m, 5))
            pwa.gm_choice("Hire For Sex", index=(m, 6), condition="not(check_lovers(char)) and char.status == 'free'")
            pwa.gm_choice("Become Fr", index=(m, 10), condition="DEBUG_INTERACTIONS")
            pwa.gm_choice("Become Lv", index=(m, 11), condition="DEBUG_INTERACTIONS")
            pwa.gm_choice("Disp", index=(m, 12), condition="DEBUG_INTERACTIONS")

            # Quests/Events to Interactions Menu:
            """
            Expects a dictionary with the following k/v pairs to be set as a flag that starts with :
            event_to_interactions_  as a flag and {"label": "some_label", "button_name='Some Name'", "condition": "True"}
            """
            m = 11
            n = 0
            for k, v in char.flags.items():
                if k.startswith("event_to_interactions_"):
                    if n == 0:
                        # add the Menu
                        pwa.menu(m, "U-Actions")
                    pwa.gm_choice(v["button_name"], label=v.get("label", None), index=(m, n), condition=v.get("condition", True))
                    n += 1

            # m = 9  --- for the time being we disable negative actions, since they require ST
            # pwa.menu(m, "Harassment", condition="not(char in hero.team) and char.employer == hero") # no fights between team members
            # pwa.gm_choice("Insult", index=(m, 0))
            # pwa.gm_choice("Escalation", index=(m, 1))

            pwa.add("zzz", "Leave", Return(["control", "return"]), keysym="mousedown_3")
            pwa.finish()

    jump interactions_control

label girl_interactions_end:
    # End the GM:
    $ iam.end()

label interactions_control:
    while 1:
        $ result = ui.interact()

        # Gifts
        if result[0] == "gift":
            # Show menu:
            if result[1] is True:
                $ iam.show_menu_givegift = True
            # Hide menu:
            elif result[1] is None:
                $ iam.show_menu_givegift = False
            # Give gift:
            else:
                $ iam.show_menu_givegift = False
                python hide:
                    item = result[1]
                    # Prevent repetition of this action (any gift, we do this on per gift basis already):
                    n = 1 + iam.flag_days_checker(char, "interactions_gifts")
                    if not iam.want_gift(char, n):
                        iam.refuse_gift_too_many(char)
                        jump("interactions_control")

                    item.hidden = False # We'll use existing hidden flag to hide items effectiveness.
                    dismod = getattr(item, "dismod", 0)

                    if item.type == "romantic" and not(check_lovers(char)) and char.get_stat("affection") < 700:  # cannot give romantic gifts to anyone
                        dismod = -10
                    else:
                        for t, v in getattr(item, "traits", {}).iteritems():
                            if t in char.traits:
                                dismod += v

                    flag_name = "cnd_item_%s" % item.id
                    flag_value = char.get_flag(flag_name, day) - day
                    cblock = item.cblock

                    # Add the appropriate dismod value:
                    if flag_value == 0:
                        # first time gift
                        char.set_flag(flag_name, cblock+day-1)
                    else:
                        if flag_value < cblock:
                            dismod = round_int(float(dismod)*(cblock-flag_value)/cblock)

                            char.up_counter(flag_name, cblock)
                        else:
                            iam.refuse_gift(char)
                            jump("interactions_control")
                    dismod /= n

                    iam.dispo_reward(char, dismod)
                    hero.inventory.remove(item)
                    if dismod > 0:
                        perfect = dismod > 30
                        if item.type == "romantic":
                            dismod *= 2
                        dismod /= 10.0
                        char.gfx_mod_stat("affection", affection_reward(char, dismod))
                        if perfect:
                            iam.accept_perfectgift(char)
                        else:
                            iam.accept_goodgift(char)
                    else:
                        char.gfx_mod_stat("affection", affection_reward(char, -1))
                        iam.accept_badgift(char)
        # Controls
        elif result == ["control", "return"]:
            jump girl_interactions_end

screen girl_interactions():
    # BG
    add "content/gfx/images/bg_gradient.webp" yalign .45

    # Disposition bar
    vbox:
        align (.95, .31)
        $ stats = char.stats
        $ temp = stats._get_stat("disposition")
        vbar:
            top_gutter 13
            bottom_gutter 0
            value AnimatedValue(value=max(temp, 0), range=stats.get_stat_max("disposition"), delay=4.0)
            bottom_bar "content/gfx/interface/bars/progress_bar_full1.png"
            top_bar "content/gfx/interface/bars/progress_bar_1.png"
            thumb None
            xysize (22, 175)

        vbar:
            bar_invert True
            top_gutter 12
            bottom_gutter 0
            value AnimatedValue(value=max(-temp, 0), range=-stats.get_stat_min("disposition"), delay=4.0)
            bottom_bar im.Flip("content/gfx/interface/bars/progress_bar_1.png", vertical=True)
            top_bar "content/gfx/interface/bars/bar_mine.png"
            thumb None
            xysize(22, 175)

    # Affection bar
    vbox:
        align (.97, .31)

        $ temp = stats._get_stat("affection")
        vbar:
            top_gutter 13
            bottom_gutter 0
            value AnimatedValue(value=max(temp, 0), range=stats.get_stat_max("affection"), delay=4.0)
            bottom_bar im.Flip("content/gfx/interface/bars/bar_mine.png", vertical=True)
            top_bar "content/gfx/interface/bars/progress_bar_1.png"
            thumb None
            xysize (22, 175)

        vbar:
            bar_invert True
            top_gutter 12
            bottom_gutter 0
            value AnimatedValue(value=max(-temp, 0), range=-stats.get_stat_min("affection"), delay=4.0)
            bottom_bar im.Flip("content/gfx/interface/bars/progress_bar_1.png", vertical=True)
            top_bar im.Flip("content/gfx/interface/bars/progress_bar_full1.png", vertical=True)
            thumb None
            xysize(22, 175)

    # Girl image
    hbox:
        xanchor 0
        xpos .22
        yalign .22

        frame:
            background Frame("content/gfx/frame/MC_bg.png", 10, 10)
            # basestring assumes that image is coming from cache, so it simply a path.
            if isinstance(iam.img, basestring):
                add PyTGFX.scale_content(iam.img, *iam.IMG_SIZE)
            else:
                add iam.img

        # if DEBUG_INTERACTIONS:
            # null width 15

            # vbox:
                # null height 60
                # text "{color=white}Mode: [iam.mode]"
                # text "{color=white}Label: [iam.jump_cache]"
                # text ("{color=white}Girl.PP: [iam.char.PP] / %s"%iam.char.setPP)
                # text "{color=white}Points: [hero.PP]"

    # Give gift interface
    if iam.show_menu_givegift:
        $ gifts = [(i, n) for i, n in hero.inventory.items.iteritems() if i.slot == "gift"]
        frame:
            style "dropdown_gm_frame"
            xysize (248, 455)
            align (.89, .27)
            xpadding 6
            viewport:
                xysize (242, 433)
                xpos 7
                scrollbars ("vertical" if len(gifts) > 3 else None)
                mousewheel True
                has vbox

                for item, num in gifts:
                    python:
                        if item.hidden:
                            img = None
                        else:
                            dismod = getattr(item, "dismod", 0)
                            if item.type == "romantic" and not(check_lovers(char)) and char.get_stat("affection") < 700: # cannot give romantic gifts to anyone
                                dismod = -10
                            else:
                                for t, v in getattr(item, "traits", {}).iteritems():
                                    if t in char.traits:
                                        dismod += v
                            flag_name = "cnd_item_%s" % item.id
                            flag_value = char.get_flag(flag_name, day-1) - day
                            if dismod <= 0:
                                img = "content/gfx/interface/icons/gifts_0.png"
                            elif dismod <= 30:
                                img = "content/gfx/interface/icons/gifts_1.png"
                            else:
                                img = "content/gfx/interface/icons/gifts_2.png"
                            img = im.Scale(img, 65, 35)
                            if flag_value >= 0:
                                img = im.Sepia(img)
                    button:
                        style "main_screen_3_button"
                        xysize (220, 100)
                        add im.Scale(item.icon, 90, 90) align (.5, .5)
                        text "[item.id]" align (.5, .1) style "library_book_header_sub" color "ivory" outlines [(1, "#424242", 0, 0)]
                        if img is not None:
                            add img align (.0, .9)
                        text str(num) color "ivory" style "library_book_header_main" align (.9, .9)
                        sensitive (hero.PP >= 25) 
                        action Return(["gift", item])

                null height 10
                textbutton "Back":
                    action Return(["gift", None])
                    xsize 220
                    style "main_screen_3_button"
                    keysym "mousedown_3"
    # Actions
    elif iam.show_menu:
        use location_actions("girl_interactions", char, pos=(1180, 315), anchor=(1.0, .5), style="main_screen_3")

    use top_stripe(False, show_lead_away_buttons=False)

screen interactions_meet:
    key "mousedown_3" action ToggleField(iam, "show_girls")
    add "content/gfx/images/bg_gradient.webp" yalign .45
    for entry, pos in zip(iam.display_girls(), iam.coords):
        $ tmp = entry.get_stat("disposition")
        if entry.has_flag("cnd_interactions_blowoff"):
            $ temp = "angry"
        elif tmp >= 500:
            $ temp = "shy"
        elif tmp >= 100:
            $ temp = "happy"
        else:
            $ temp = "indifferent"

        $ p_img = entry.show("portrait", temp, label_cache=True, resize=(90, 90), type="reduce", add_mood=False)

        vbox:
            align pos
            frame:
                padding(2, 2)
                background Frame("content/gfx/frame/MC_bg3.png")
                has fixed fit_first True
                imagebutton:
                    align .5, .5
                    idle p_img
                    hover PyTGFX.bright_content(p_img, .15)
                    action Return(['jump', entry])
                hbox:
                    align 1.0, 1.0
                    if tmp > 0:
                        add "green_dot_gm"
                    if tmp > 100:
                        add "green_dot_gm"
                    if tmp > 250:
                        add "green_dot_gm"

                    if tmp < 0:
                        add "red_dot_gm"
                    if tmp < -100:
                        add "red_dot_gm"
                    if tmp < -250:
                        add "red_dot_gm"

            frame:
                padding(2, 2)
                xsize 94
                background Frame("content/gfx/frame/gm_frame.png")
                label "Tier [entry.tier]" xalign .5 text_color "#DAA520"
