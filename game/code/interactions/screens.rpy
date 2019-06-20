#init python:
#    # The job for the GT mode
#    gm_job = None

label girl_interactions:
    python:
        if "girl_meets" in pytfall.world_actions.locations:
            del pytfall.world_actions.locations["girl_meets"]
        pytfall.world_actions.clear()

    python:
        # Run quests and events
        pytfall.world_quests.run_quests("auto")
        pytfall.world_events.run_events("auto")

        # Hide menus till greeting
        iam.show_menu = False
        iam.show_menu_givegift = False

    if iam.mode == "girl_interactions":
        scene expression iam.select_char_location(char)
    else:
        scene expression iam.bg_cache

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
        if pytfall.world_actions.location("girl_meets"):
            _gm_mode = Iff(S((iam, "mode")), "==", "girl_meets")
            _gi_mode = Iff(S((iam, "mode")), "==", "girl_interactions")
            _gt_mode = Iff(S((iam, "mode")), "==", "girl_trainings")

            _not_gm_mode = IffOr(_gi_mode, _gt_mode)
            _not_gi_mode = IffOr(_gm_mode, _gt_mode)
            _not_gt_mode = IffOr(_gm_mode, _gi_mode)

            # CHAT
            m = 0
            pytfall.world_actions.menu(m, "Chat")
            pytfall.world_actions.gm_choice("Small Talk", index=(m, 0))
            pytfall.world_actions.gm_choice("About Job", mode="girl_interactions", index=(m, 1))
            pytfall.world_actions.gm_choice("How She Feels", mode="girl_interactions", index=(m, 2))
            pytfall.world_actions.gm_choice("About Her", index=(m, 3))
            pytfall.world_actions.gm_choice("About Occupation", mode="girl_meets", index=(m, 4))
            pytfall.world_actions.gm_choice("Interests", index=(m, 5))
            pytfall.world_actions.gm_choice("Flirt", index=(m, 6))


            # TRAINING
            m = 1
            pytfall.world_actions.menu(m, "Training", condition=_gt_mode)

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
                            # pytfall.world_actions.menu((m, n), k, condition=OneOffTrainingAction("menu", c))

                            # for l in range(len(ev)):
                                # # Add the lesson
                                # pytfall.world_actions.add((m, n, l), ev[l].name, OneOffTrainingAction("action", ev[l]), condition=OneOffTrainingAction("condition", ev[l]))

                            # n += 1

            # PRAISE
            m = 2
            pytfall.world_actions.menu(m, "Praise", condition="not(char in hero.chars)")
            pytfall.world_actions.gm_choice("Clever", mode="girl_meets", index=(m, 0))
            pytfall.world_actions.gm_choice("Strong", mode="girl_meets", index=(m, 1))
            pytfall.world_actions.gm_choice("Cute", mode="girl_meets", index=(m, 2))

            # INSULT
            m = 3
            pytfall.world_actions.menu(m, "Insult", condition="not(char in hero.chars)")
            pytfall.world_actions.gm_choice("Stupid", mode="girl_meets", index=(m, 0))
            pytfall.world_actions.gm_choice("Weak", mode="girl_meets", index=(m, 1))
            pytfall.world_actions.gm_choice("Ugly", mode="girl_meets", index=(m, 2))

            # GIVE MONEY
            m = 4
            pytfall.world_actions.menu(m, "Money", condition="char.status != 'slave'")
            pytfall.world_actions.gm_choice("Propose to give money", label="giftmoney", index=(m, 0))
            pytfall.world_actions.gm_choice("Ask for money", label="askmoney", index=(m, 1))

            m = 5
            pytfall.world_actions.menu(m, "Money", condition="char.status == 'slave'")
            pytfall.world_actions.gm_choice("Give", label="give_money", index=(m, 0))
            pytfall.world_actions.gm_choice("Take", label="take_money", index=(m, 1))

            # GIVE GIFT
            m = 6
            pytfall.world_actions.add(m, "Give Gift", Return(["gift", True]), condition="char.get_flag('cnd_interactions_gift', day)-day < 3")

            # PROPOSITION
            m = 7
            pytfall.world_actions.menu(m, "Propose")
            pytfall.world_actions.gm_choice("Girlfriend", condition="not check_lovers(char)", index=(m, 0))
            pytfall.world_actions.gm_choice("Break Up", condition="check_lovers(char)", index=(m, 1))
            pytfall.world_actions.gm_choice("Move in", condition="char.home != hero.home and char.status == 'free'", index=(m, 2))
            pytfall.world_actions.gm_choice("Move out", condition="char.home == hero.home and char.status == 'free'", index=(m, 3))
            pytfall.world_actions.gm_choice("Hire", condition="not(char in hero.chars)", index=(m, 4))
            pytfall.world_actions.gm_choice("Sparring", condition="'Combatant' in char.gen_occs", index=(m, 5))

            # PLAY A GAME
            m = 8
            pytfall.world_actions.menu(m, "Play")
            pytfall.world_actions.gm_choice("Archery", label="play_bow", index=(m, 0))
            pytfall.world_actions.gm_choice("PowerBalls", label="play_power", index=(m, 1))

            # INTIMACY
            m = 9
            pytfall.world_actions.menu(m, "Intimacy")
            pytfall.world_actions.gm_choice("Hug", index=(m, 0))
            pytfall.world_actions.gm_choice("Grab Butt", index=(m, 1))
            pytfall.world_actions.gm_choice("Grab Breasts", index=(m, 2))
            pytfall.world_actions.gm_choice("Kiss", index=(m, 3))
            pytfall.world_actions.gm_choice("Sex", index=(m, 4))
            pytfall.world_actions.gm_choice("Hire For Sex", index=(m, 5), condition="not(check_lovers(char)) and 'SIW' in char.gen_occs and char.status != 'slave'")
            pytfall.world_actions.gm_choice("Become Fr", index=(m, 6), condition="DEBUG_INTERACTIONS")
            pytfall.world_actions.gm_choice("Become Lv", index=(m, 7), condition="DEBUG_INTERACTIONS")
            pytfall.world_actions.gm_choice("Disp", index=(m, 8), condition="DEBUG_INTERACTIONS")

            # Quests/Events to Interactions Menu:
            """
            Expects a dictionary with the following k/v pairs to be set as a flag that starts with :
            event_to_interactions_  as a flag and {"label": "some_label", "button_name='Some Name'", "condition": "True"}
            """
            m = 10
            n = 0
            for k, v in char.flags.items():
                if k.startswith("event_to_interactions_") and renpy.has_label(v["label"]):
                    if eval(v.get("condition", True)):
                        if n == 0:
                            # add the Menu
                            pytfall.world_actions.menu(m, "U-Actions")
                        pytfall.world_actions.gm_choice(v["button_name"], label=v["label"], index=(m, n))
                        n += 1

            # m = 9  --- for the time being we disable negative actions, since they require ST
            # pytfall.world_actions.menu(m, "Harassment", condition="not(char in hero.team) and char in hero.chars") # no fights between team members
            # pytfall.world_actions.gm_choice("Insult", index=(m, 0))
            # pytfall.world_actions.gm_choice("Escalation", index=(m, 1))

            pytfall.world_actions.add("zzz", "Leave", Return(["control", "back"]), keysym="mousedown_3")

            # Developer mode switches
            if DEBUG_INTERACTIONS:
                pytfall.world_actions.menu("dev", "Developer")
                pytfall.world_actions.add(("dev", "gm"), "GM", Return(["test", "GM"]), condition=_not_gm_mode)
                pytfall.world_actions.add(("dev", "gi"), "GI", Return(["test", "GI"]), condition=_not_gi_mode)
                pytfall.world_actions.add(("dev", "gt"), "GT", Return(["test", "GT"]), condition=_not_gt_mode)

            pytfall.world_actions.finish()

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
                $ iam.show_menu = False
                $ iam.show_menu_givegift = True
            # Hide menu:
            elif result[1] is None:
                $ iam.show_menu = True
                $ iam.show_menu_givegift = False
            # Give gift:
            else:
                python hide:
                    item = result[1]
                    # Prevent repetition of this action (any gift, we do this on per gift basis already):
                    if char.has_flag("cnd_interactions_gifts"):
                        char.up_counter("cnd_interactions_gifts")
                    else:
                        char.set_flag("cnd_interactions_gifts", day)

                    iam.show_menu = True
                    iam.show_menu_givegift = False

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

                    # Add the appropriate dismod value:
                    if flag_value == 0:
                        # first time gift
                        char.set_flag(flag_name, item.cblock+day-1)
                    else:
                        if flag_value < item.cblock:
                            dismod = round_int(float(dismod)*(item.cblock-flag_value)/item.cblock)

                            char.up_counter(flag_name, item.cblock)
                        else:
                            iam.refuse_gift(char)
                            jump("girl_interactions")

                    char.gfx_mod_stat("disposition", dismod)
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
                jump girl_interactions
        # Controls
        elif result[0] == "control":
            # Return / Back
            if result[1] in ("back", "return"):
                jump girl_interactions_end
        # Testing
        elif result[0] == "test":
            python:
                iam.end(safe=True)

                # Girls Meets
                if result[1] == "GM":
                    # Include img as coming from int and tr prevents the "img from last location" from working
                    iam.start_gm(char, img=char.show("profile", exclude=["nude", "bikini", "swimsuit", "beach", "angry", "scared", "ecstatic"]))
                # Interactions
                elif result[1] == "GI":
                    iam.start_int(char)
                # Training
                elif result[1] == "GT":
                    iam.start_tr(char)

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



    # Actions
    if iam.show_menu:
        use location_actions("girl_meets", char, pos=(1180, 315), anchor=(1.0, .5), style="main_screen_3")

    # Give gift interface
    if iam.show_menu_givegift:
        frame:
            style "dropdown_gm_frame"
            xysize (385, 455)
            align (.89, .27)
            viewport:
                xysize (365, 433)
                scrollbars "vertical"
                mousewheel True
                has vbox

                for item in hero.inventory:
                    if item.slot == "gift":
                        python:
                            dismod = getattr(item, "dismod", 0)
                            if item.type == "romantic" and not(check_lovers(char)) and char.get_stat("affection") < 700: # cannot give romantic gifts to anyone
                                dismod = -10
                            else:
                                for t, v in getattr(item, "traits", {}).iteritems():
                                    if t in char.traits:
                                        dismod += v
                            flag_name = "cnd_item_%s" % item.id
                            flag_value = char.get_flag(flag_name, day-1) - day

                        button:
                            style "main_screen_3_button"
                            xysize (350, 100)
                            hbox:
                                fixed:
                                    yoffset 3
                                    xysize (90, 90)
                                    add im.Scale(item.icon, 90, 90)
                                    text str(hero.inventory[item]) color "ivory" style "library_book_header_main" align (0, 0)
                                    if not item.hidden:
                                        if dismod <= 0:
                                            $ img = "content/gfx/interface/icons/gifts_0.png"
                                        elif dismod <= 30:
                                            $ img = "content/gfx/interface/icons/gifts_1.png"
                                        else:
                                            $ img = "content/gfx/interface/icons/gifts_2.png"
                                        $ img = im.Scale(img, 65, 35)
                                        if flag_value >= 0:
                                            $ img = im.Sepia(img)
                                        add img align (.0, .9)
                                null width 10
                                text "[item.id]" yalign .5 style "library_book_header_sub" color "ivory"
                            sensitive (hero.PP >= 25) 
                            action Return(["gift", item])

                null height 10
                textbutton "Back":
                    action Return(["gift", None])
                    minimum(220, 30)
                    xalign .5
                    style "main_screen_3_button"
                    text_style "library_book_header_sub"
                    text_color "ivory"
                    keysym "mousedown_3"

    use top_stripe(False, show_lead_away_buttons=False)
