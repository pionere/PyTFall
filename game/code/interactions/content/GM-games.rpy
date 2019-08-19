##################################################################################################
#
#                                ARCHERY
#
##################################################################################################    
label interactions_play_bow:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end

    $ m = iam.flag_count_checker(char, "flag_interactions_archery")
    if m > 1:
        $ del m
        $ iam.refuse_because_tired(char)
        jump girl_interactions
    $ del m

    $ iam.archery_start(char)

    menu:
        "Where would you like to do it?"
        "Beach":
            show bg b_beach_2 with fade
            $ archery_location="beach"
        "Park":
            show bg city_park with fade
            #show bg b_park_1 with fade
            #show bg b_nature_1 with fade
            $ archery_location="park"
        "Village":
            #show bg hiddenvillage_alley with fade
            show bg b_village_1 with fade
            $ archery_location="village"
        "City":
            show bg b_city_1 with fade
            #show bg b_city_4 with fade
            $ archery_location="city"
        "Forest":
            show bg b_forest_5 with fade
            #show bg b_forest_6 with fade
            #show bg b_forest_8 with fade
            $ archery_location="forest"

    hide screen girl_interactions

    show expression hero.get_vnsprite() at left as player with dissolve
    show expression char.get_vnsprite() at right as character with dissolve

    python:
        min_distance = 5        # the minimum distance of the target
        max_distance_perc = .1  # 
        target_scale = 1.0

        archery_min_skill, archery_max_skill = 0, hero.get_max_stat("attack", tier=MAX_TIER)

        dummy = copy_char(hero)
        dummy.equip(items["Long Bow"], remove=False, aeq_mode=True)
        hero_skill = dummy.get_stat("attack")

        dummy = copy_char(char)
        dummy.equip(items["Long Bow"], remove=False, aeq_mode=True)
        char_skill = dummy.get_stat("attack")

        if "Clumsy" in char.traits:
            char_skill *= .8
        if "Bad Eyesight" in char.traits:
            char_skill *= .6
        hero_skill = min(hero_skill, archery_max_skill)
        char_skill = min(char_skill, archery_max_skill)

        max_strain = 1000       # the relative maximum strain
        speed_per_force = 200   # the maximum speed of the arrow when released
        g_force = 5             # half of the standard grav. force to simplify the calculation
        distance_per_speed = 40 # conversion between pixels and world distance

        temp = {"beach": 5, "city": 4, "village": 3, "park": 2, "forest": 1}
        wind = temp[archery_location]
        wind = [uniform(.8, 1.2)*wind, randint(0, 360), None]
        wind_mpl = 5           # default multiplier of the wind effect

        target_size = 200      # the width of the target at min_distance
        target_border = 3      # border of the target where the hit does not count
        crosshair_size = 400   # base size of the crosshair (reduced by skill)
        prev_mouse_hide = config.mouse_hide_time
        arrow = None           # the flying arrow of the hero
        game_result = None  # detailed result of the shot to give feedback

label interactions_archery_start:
    # adjust and show wind indicator
    $ wind = [min(6.4, uniform(.9, 1.1)*wind[0]), round_int(uniform(.9, 1.1)*wind[1]) % 360, None]
    $ temp = ["azure", "lightcyan", "lightblue", "lightsalmon", "lightcoral", "tomato", "orangered"]
    $ wind[2] = temp[round_int(wind[0])]

    $ hero_arrows = []
    $ char_arrows = []

    menu:
        "Select the competition type"
        "Three shoots":
            $ num_arrows = 3
            $ best_of = False
        "Six shoots":
            $ num_arrows = 6
            $ best_of = False
        "Best of three":
            $ num_arrows = 3
            $ best_of = True
        "Best of six":
            $ num_arrows = 6
            $ best_of = True

    # adjust target distance
    call screen interactions_archery_range_targeting

    $ distance = min_distance / target_scale

    jump interactions_archery_char_turn

label interactions_archery_hero_turn:
    if game_result is not None:
        call interaction_archery_char_comment_self from _call_interaction_archery_char_comment_self

    hide screen interactions_archery_range_result

    $ config.mouse_hide_time = 0
    $ archery_strain = 300   # initial strain

    show screen interactions_archery_range_shoot

    while 1:
        $ result = ui.interact()

        if result == "shoot":
            python hide:
                global game_result
                m_posx, m_posy = posx, posy = renpy.get_mouse_pos()
                speed = (archery_strain/float(max_strain)) # strain percentage -> 0.0 <= speed <= 1.0
                speed = 8*(1.0-speed)                      #                   -> 8.0 >= speed >= 0.0
                speed = speed*(math.e**(-speed))           # x * e^(-x)        -> 0.0 <= speed <= 0.36788
                force = get_linear_value_of(hero_skill, archery_min_skill, .5, archery_max_skill, 1.0)
                speed *= force * speed_per_force
                # wind (y) effect
                speed += wind_mpl * wind[0]*math.cos(wind[1]*math.pi/180) * uniform(.9, 1.1)

                if speed <= 0:
                    # miss
                    hero_arrows.append((None, None, 0))

                    game_result = (None, None, None)
                else:
                    # distance effect
                    dt = distance / speed
                    posy += dt * dt * g_force * distance_per_speed * target_scale

                    # wind (x) effect
                    wind_speed = wind_mpl * wind[0]*math.sin(wind[1]*math.pi/180) * uniform(.9, 1.1)
                    posx += dt * wind_speed * distance_per_speed * target_scale

                    rotation = randint(0, 360)
                    store.arrow = [[round_int(m_posx), round_int(m_posy)], [round_int(posx), round_int(posy)], dt, rotation]

                    centerx, centery = config.screen_width/2, config.screen_height/2-(66*target_scale)
                    size = target_scale*((target_size-target_border)/2)

                    value = math.hypot(posx-centerx, posy-centery)
                    if value <= size:
                        # hit
                        value = 5*(1.0-value/size)
                        if value >= 4.75:
                            # Bulls Eye
                            value = 10
                        else:
                            value = int(value)+1

                        hero_arrows.append(((posx, posy), rotation, value))

                        game_result = ((posx, posy), None, value)
                    else:
                        # miss
                        hero_arrows.append((None, None, 0))

                        game_result = ((posx, posy), size, (centerx, centery))

            jump interactions_archery_char_turn
        elif result == "timeout":
            python hide:
                posx, posy = renpy.get_mouse_pos()
                # bit of random shake sideways
                dx = get_linear_value_of(hero_skill, archery_min_skill, 2+2.0*archery_strain/max_strain, archery_max_skill, .5) 
                posx += random.uniform(-dx, dx)
                # breath effect
                posy += 2*dx*math.cos(time.time()*math.pi*2/4)
                # heart-beat effect
                posy += math.cos(time.time()*math.pi*2*2)
                # weight of the bow
                posy += random.uniform(0, dx/2)
                renpy.set_mouse_pos(round_int(posx), round_int(posy))
                # relaxing muscles
                dx = round_int(2*dx)
                if store.archery_strain < dx:
                    store.archery_strain = 0
                else:
                    store.archery_strain -= randint(1, dx)
                renpy.restart_interaction()

screen interactions_archery_range_target:
    # wind indicator
    fixed:
        align .8, .0
        xysize 200, 200
        add im.Scale("content/gfx/images/vane_back_1.webp", 150, 150) align .5, .5
        add Transform(im.Scale("content/gfx/images/vane_3.webp", 25, 90), rotate=wind[1]) align .5, .5 
        button:
            align .5, 1.0
            style_group "basic_choice2"
            text str(round(wind[0], 1)) size 14 color wind[2]
            action NullAction()
            tooltip "Wind speed and direction."

    # the target
    $ sizex, sizey = target_size, 332
    add im.Scale("content/gfx/images/archery_target_1.webp", sizex*target_scale, sizey*target_scale) align .5, .5

    # the arrows
    python:
        size = 30
        hero_img = [.5, 0.5, 1.0] if hero.gender == "male" else [1.0, .5, .5]
        hero_img = im.Scale(im.MatrixColor("content/gfx/images/archery_fletching_2.webp", im.matrix.tint(*hero_img)), size, size)
        char_img = [.75, .75, 1.0] if char.gender == "male" else [1.0, .75, .75]
        char_img = im.Scale(im.MatrixColor("content/gfx/images/archery_fletching_2.webp", im.matrix.tint(*char_img)), size, size)
        size /= 2
        offset = -((math.sqrt(2)-1.0)*size) # add offset to offset the rotation

        if arrow is not None:
            last_arrow = hero_arrows.pop()
    for h, c in izip_longest(hero_arrows, char_arrows):
        if h is not None:
            $ pos, rot, value = h
            if pos is not None: # skip missed shots
                $ pos = [round_int(pos[0]-size), round_int(pos[1]-size)]
                add Transform(hero_img, rotate=rot) pos pos offset (offset, offset)
        if c is not None: # not shot yet
            $ pos, rot, value = c
            if pos is not None: # skip missed shots
                $ pos = [round_int(pos[0]-size), round_int(pos[1]-size)]
                add Transform(char_img, rotate=rot) pos pos offset (offset, offset)
    # the flying arrow
    if arrow is not None:
        python:
            rot = arrow.pop()
            arrow.append(last_arrow[0] is None)
        add Transform(hero_img, rotate=rot) at move_from_to_pos_with_linear(*arrow) offset (offset-size, offset-size)
        $ hero_arrows.append(last_arrow)
        $ store.arrow = None

screen interactions_archery_range_targeting:
    # Set Distance
    vbox:
        align .5, .2
        spacing 5
        text "Distance" style "pb_button_text" color "black" outlines [(2, "ivory", 1, 1)] size 20
        bar:
            bar_invert True
            value FieldValue(store, 'target_scale', 1.0-max_distance_perc, max_is_zero=False, style='scrollbar', offset=max_distance_perc, step=.05)
            xmaximum 150
            thumb 'content/gfx/interface/icons/move15.png'
            tooltip "Adjust the distance to the target."

    # the target
    use interactions_archery_range_target

    # Confirm:
    button:
        style_group "pb"
        action [Hide("interactions_archery_range_targeting"), Return("done")]
        text "Begin" style "pb_button_text"
        align .5, .9

screen interactions_archery_range_shoot:
    # the target
    use interactions_archery_range_target

    # strain indicator
    vbox:
        align (.95, .31)

        vbar:
            top_gutter 13
            bottom_gutter 0
            value max(0, archery_strain-max_strain/2)
            range max_strain/2
            bottom_bar "content/gfx/interface/bars/progress_bar_full1.png"
            top_bar "content/gfx/interface/bars/progress_bar_1.png"
            thumb None
            xysize (22, 175)

        vbar:
            top_gutter 12
            bottom_gutter 0
            value min(max_strain/2, archery_strain)
            range max_strain/2
            bottom_bar "content/gfx/interface/bars/bar_mine.png"
            top_bar im.Flip("content/gfx/interface/bars/progress_bar_1.png", vertical=True)
            thumb None
            xysize(22, 175)

    $ scale = get_linear_value_of(hero_skill, archery_min_skill, 1.0, archery_max_skill, .25)
    $ sizex, sizey = round_int(crosshair_size*scale), round_int(crosshair_size*scale)
    $ pos = renpy.get_mouse_pos()
    $ pos = (pos[0]-sizex/2, pos[1]-sizey/2)
    add im.Scale("content/gfx/images/crosshair.webp", sizex, sizey) pos pos

    hbox:
        align .1, .1
        xysize 150, 40
        spacing 10
        $ img = im.Scale("content/gfx/images/button.webp", 40, 40)
        $ hover_img = PyTGFX.bright_img(img, .10)
        button:
            xysize 40, 40
            idle_background img
            hover_background hover_img
            action SetVariable("archery_strain", max(0, archery_strain - randint(80,120)))
            text "A" align .5, .5 size 30 color "black"
            keysym "a"
        button:
            xysize 40, 40
            idle_background img
            hover_background hover_img
            action SetVariable("archery_strain", max(0, archery_strain - randint(20,40)))
            text "S" align .5, .5 size 30 color "black"
            keysym "s"
        button:
            xysize 40, 40
            idle_background img
            hover_background hover_img
            action SetVariable("archery_strain", min(max_strain, archery_strain + randint(20,40)))
            text "D" align .5, .5 size 30 color "black"
            keysym "d"
        button:
            xysize 40, 40
            idle_background img
            hover_background hover_img
            action SetVariable("archery_strain", min(max_strain, archery_strain + randint(80,120)))
            text "F" align .5, .5 size 30 color "black"
            keysym "f"
    hbox:
        align .1, .2
        xysize 190, 40
        $ img = im.Scale("content/gfx/images/button.webp", 150, 40)
        button:
            xysize 160, 40
            xalign .5
            idle_background img
            hover_background PyTGFX.bright_img(img, .10)
            action Return("shoot")
            text "Space" align .5, .5 size 30 color "black"
            keysym "K_SPACE", "mousedown_1", "K_ESCAPE"

    timer .1 action Return("timeout") repeat True

label interactions_archery_char_turn:
    hide screen interactions_archery_range_shoot
    show screen interactions_archery_range_result

    $ config.mouse_hide_time = prev_mouse_hide

    if game_result is not None:
        call interaction_archery_char_comment from _call_interaction_archery_char_comment
    else:
        jump interactions_archery_char_shoot

    while 1:
        $ result = ui.interact()

        if result == "char_turn":
            jump interactions_archery_char_shoot

        elif result == "done":
            python hide:
                global game_result

                hero_points = [a[2] for a in hero_arrows]
                char_points = [a[2] for a in char_arrows]

                if best_of:
                    hero_points = max(hero_points) 
                    char_points = max(char_points)
                else:
                    hero_points = sum(hero_points) 
                    char_points = sum(char_points)

                if hero_points > char_points:
                    game_result = hero
                elif hero_points < char_points:
                    game_result = char
                else:
                    game_result = None
            jump interactions_archery_end

label interactions_archery_char_shoot:
    python hide:
        global game_result

        centerx, centery = config.screen_width/2, config.screen_height/2-(66*target_scale)
        size = target_scale*((target_size-target_border)/2)

        value = get_linear_value_of(char_skill, archery_min_skill, .3, archery_max_skill, .05)

        # independent of the distance -> distance effect...
        value *= target_size
        # wind effect
        value *= get_linear_value_of(wind[0]*math.sin(wind[1]*math.pi/180) , 0, 1.0, 6.4, 1.2) # archery_min_wind = 0, archery_max_wind = 6.4

        posx, posy = centerx + random.gauss(0, 0.6)*value, centery + random.gauss(0, 0.6)*value

        value = math.hypot(posx-centerx, posy-centery)
        if value <= size:
            # hit
            value = 5*(1.0-value/size)
            if value >= 4.75:
                # Bulls Eye
                value = 10
            else:
                value = int(value)+1

            rotation = randint(0, 360)
            char_arrows.append(((posx, posy), rotation, value))

            game_result = ((posx, posy), None, value)
        else:
            # miss
            char_arrows.append((None, None, 0))

            game_result = ((posx, posy), size, (centerx, centery))
    jump interactions_archery_hero_turn

screen interactions_archery_range_result:
    # the target
    use interactions_archery_range_target

    # Confirm:
    if game_result is None:
        if len(hero_arrows) == num_arrows:
            button:
                style_group "pb"
                action Return("done")
                text "Done" style "pb_button_text"
                align .5, .9
        else:
            button:
                style_group "pb"
                action Return("char_turn")
                text "Next Round" style "pb_button_text"
                align .5, .9

label interactions_postgame_lines: # lines and rewards after games
    if game_result == hero:
        "You won."

        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.1))

        if hero_skill > char_skill*2:
            $ iam.dispo_reward(char, randint(3, 4))
        else:
            $ iam.dispo_reward(char, randint(8, 12))
        $ char.gfx_mod_stat("affection", affection_reward(char, .5, stat="attack"))

    elif game_result == char:
        "[char.name] won."

        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.1))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))

        if hero_skill > char_skill*2:
            $ iam.dispo_reward(char, randint(10, 14))
        else:
            $ iam.dispo_reward(char, randint(3, 4))
        $ char.gfx_mod_stat("affection", affection_reward(char, .25, stat="attack"))
        $ char.gfx_mod_stat("affection", affection_reward(char, .25))
    else:
        "Draw."

        $ iam.int_reward_exp(char)

        $ iam.dispo_reward(char, randint(16, 20))
        $ char.gfx_mod_stat("affection", affection_reward(char, .4, stat="attack"))
        $ char.gfx_mod_stat("affection", affection_reward(char, .4))

    $ iam.archery_end(char)
    return

label interaction_archery_char_comment_self: # (game_result)
    call interactions_archery_eval_result from _call_interactions_archery_eval_result_2

    if isinstance(game_result, int):
        # hit
        if game_result == 10:
            # Bulls Eye
            $ temp = choice(["Right in the middle.", "Bullseye!"])
            if target_scale < 0.7:
                $ game_result = choice([" Yeah!", " Lucky shot!"]) 
            else:
                $ game_result = choice([" Not bad.", " Nice one, right?"])
            $ char.gfx_mod_stat("joy", randint(1,2))
            char.say "[temp]" 
            extend "[game_result]"
        elif game_result < 4:
            # weak hit
            $ iam.say_line(char, ("Well, a [game_result]. Maybe the next one...", "Ehh... [game_result]. Could have been better.", "A [game_result]. Not my best one."), "sad")
        else:
            # normal hit
            $ iam.say_line(char, ("A [game_result]. It is fine, I guess.", "A hit of [game_result] is O.K. with me.", "Hm.. [game_result]. That was a nice shot, don't you think?", "A [game_result]. For now that will do.", "Can to beat this [game_result]?"))
    else:
        # miss
        $ iam.say_line(char, ("Hmpf... Can I try again?", "Ouch... that hurts.", "Stop distracting me!", "Eh... Maybe we should not play against the sun.", "Well, here goes nothing..."), "sad")
    $ game_result = None
    return

label interaction_archery_char_comment: # (game_result)
    call interactions_archery_eval_result from _call_interactions_archery_eval_result_1

    if isinstance(game_result, int):
        # hit
        if game_result == 10:
            # Bulls Eye
            $ temp = choice(["Right in the middle.", "Bullseye..."])
            if target_scale < 0.7:
                $ game_result = choice([" Impressive!", " Lucky shot!"]) 
            else:
                $ game_result = choice([" Not bad.", " Nice."])
            $ hero.gfx_mod_stat("joy", randint(1, 2))
            char.say "[temp]"
            extend "[game_result]"
        elif game_result < 4:
            # weak hit
            $ iam.say_line(char, ("A [game_result]. Now watch me!", "Anyone can hit a [game_result].", "A [game_result]. Do you even try?"), "confident")
        else:
            # normal hit
            $ iam.say_line(char, ("A [game_result]. You try to challenge me?", "A hit of [game_result] is not bad for a beginner.", "Hm.. [game_result]. Is this your lucky shot?", "A [game_result]. It is O.K., considering the circumstances...", "Are you satisfied with your [game_result]?"))
    else:
        # miss
        if game_result[0] == "_": # "_r", "_R", "_l", "_L"
            # in the box of target
            char.say "That was close."
            extend " A bit more luck and you will hit."
        elif len(game_result) == 1:
            # one-way miss  ("r", "R", "l", "L", "u", "U", "d", "D")
            if game_result == "r":
                $ temp = ("You might want to come a bit closer?", "I guess now you try to blame the wind.")
            elif game_result == "R":
                $ temp = ("That was way too far to the right.", "I would not even try to find that arrow.")
            elif game_result == "l":
                $ temp = ("You might want to come a bit closer?", "I guess now you try to blame the wind.")
            elif game_result == "L":
                $ temp = ("That was way too far to the left.", "I would not even try to find that arrow.")
            elif game_result == "u":
                $ temp = ("I see you have high hopes.", "Optimism helps in many situations.")
            elif game_result == "U":
                $ temp = ("Are you shooting for the stars?", "Watch your back, the arrow might come around the Earth.", "Please, do not hurt the birds!")
            elif game_result == "d":
                $ temp = ("All right, so the trestle is stable.", "You might want to try this on the Moon.", "Well, at least we do not have to pay for this arrow.")
            else: # game_result == "D":
                $ temp = ("Try not to shoot yourself in the foot!", "Are you hunting for gophers?", "You never had to dig a borehole by hand, right?")
            $ iam.say_line(char, temp, "happy")
        else:
            # two-way miss
            if game_result == game_result.lower():
                # ("ru", "rd", "lu", "ld")
                if game_result == "ru":
                    $ game_result = "lower and to the left"
                elif game_result == "rd":
                    $ game_result = "higher and to the left"
                elif game_result == "lu":
                    $ game_result = "lower and to the right"
                else: # game_result == "ld":
                    $ game_result = "higher and to the right"
                char.say "With a bit more practice and aiming [game_result], you might hit the target."
            elif game_result == game_result.upper():
                # ("RU", "RD", "LU", "LD")
                $ temp = choice(["Are you sure this is the right time to play this game?", "You might want to try something else!"]) 
            else:
                # ("rU", "rD", "lU", "lD", "Ru", "Rd", "Lu", "Ld")
                if game_result[0] == game_result[0].upper():
                    $ game_result = game_result[0]
                else:
                    $ game_result = game_result[1]
                if game_result == "R":
                    char.say "That was way too far to the right."
                    extend " Not to mention other issues..."
                elif game_result == "L":
                    char.say "That was way too far to the left."
                    extend " Not to mention other issues..."
                elif game_result == "U":
                    $ temp = ("Are you shooting for the stars?", "Watch your back, the arrow might come around the Earth.", "Please, do not hurt the birds!")
                    $ iam.say_line(char, temp, "happy")
                else: # game_result == "D":
                    $ temp = ("Try not to shoot yourself in the foot!", "Are you hunting for gophers?", "You never had to dig a borehole by hand, right?")
                    $ iam.say_line(char, temp, "happy")
    $ game_result = None
    return

# transform the game_result from the format of [(posx, posy), size, (centerx, centery)] to string  
label interactions_archery_eval_result:
    python hide:
        global game_result
        pos, size, value = game_result
        if pos is None:
            # a complete miss by not shooting the arrow (speed == 0)
            value = "D"
        elif size is None:
            # a hit
            pass
        else:
            # a miss -> convert to string
            posx, posy = pos
            centerx, centery = value

            value = ""
            if posx <= centerx - size:
                if posx < centerx - 2*size:
                    value += "L" # far to the left
                else:
                    value += "l" # a bit to the left
            elif posx >= centerx + size:
                if posx > centerx + 2*size:
                    value += "R" # far to the right
                else:
                    value += "r" # a bit to the right
            if posy <= centery - size:
                if posy < centery - 2*size:
                    value += "U" # far low
                else:
                    value += "u" # a bit low
            elif posy >= centery + size:
                if posy > centery + 2*size:
                    value += "D" # far low
                else:
                    value += "d" # a bit low
            if value == "":
                # in the box of the target, but still a miss
                if posx < centerx:
                    if posy < centery:
                        value = "_l" # bottom-left corner
                    else:
                        value = "_L" # upper-left corner
                else:
                    if posy < centery:
                        value = "_r" # bottom-right corner
                    else:
                        value = "_R" # upper-right corner
        game_result = value 
    return

label interactions_archery_end:
    hide screen interactions_archery_range_result
    with dissolve

    call interactions_postgame_lines from _call_interactions_postgame_lines

    python hide:
        cleanup = ["hero_arrows", "char_arrows", "game_result", "temp", "dummy",
                   "archery_min_skill", "archery_max_skill", "speed_per_force", "g_force",
                   "prev_mouse_hide", "hero_skill", "char_skill",
                   "target_scale", "target size", "target_border", "crosshair_size",
                   "distance", "min_distance", "max_distance_perc",
                   "wind", "archery_location", "archery_strain",
                   "num_arrows", "best_of", "wind_mpl", "arrow"]
        for i in cleanup:
            if hasattr(store, i):
                delattr(store, i)
    jump girl_interactions

##################################################################################################
#
#                                POWER BALLS
#
##################################################################################################    
label interactions_play_power:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end

    $ m = iam.flag_count_checker(char, "flag_interactions_power_balls")
    if m > 1:
        $ del m
        $ iam.refuse_because_tired(char)
        jump girl_interactions
    $ del m

    $ iam.archery_start(char)

    hide screen girl_interactions

    show expression hero.get_vnsprite() at left as player with dissolve
    show expression char.get_vnsprite() at right as character with dissolve

    python:
        # off|def    Earth    Water    Fire    Air    Elec    Ice    Dark    Light
        # Earth        1       1.25     .9     .9      .9     .75     .9      .9
        # Water       .75       1      1.25    .9      .9     .9      .9      .9
        # Fire        .9       .75       1    1.25     .9     .9      .9      .9
        # Air         .9       .9       .75     1     1.25    .9      .9      .9
        # Elec        .9       .9       .9     .75      1    1.25     .9      .9
        # Ice        1.25      .9       .9     .9      .75     1      .9      .9
        # Dark       1.05      1.05     .85    .85    .85     1.05     1      .8
        # Light       .85      .85     1.05    1.05   1.05    .85     .8       1
        hero_power_map = {"earth": {"earth" : 1, "water":1.25, "fire":.9, "air":.9, "electricity":.9, "ice":0.75, "darkness":.9, "light":.9}, 
                     "water": {"earth" : 0.75, "water":1, "fire":1.25, "air":.9, "electricity":.9, "ice":.9, "darkness":.9, "light":.9},
                     "fire": {"earth" : .9, "water":0.75, "fire":1, "air":1.25, "electricity":.9, "ice":.9, "darkness":.9, "light":.9},
                     "air": {"earth" : .9, "water":.9, "fire":0.75, "air":1, "electricity":1.25, "ice":.9, "darkness":.9, "light":.9},
                     "electricity": {"earth" : .9, "water":.9, "fire":.9, "air":0.75, "electricity":1, "ice":1.25, "darkness":.9, "light":.9},
                     "ice": {"earth" : 1.25, "water":.9, "fire":.9, "air":.9, "electricity":0.75, "ice":1, "darkness":.9, "light":.9},
                     "darkness": {"earth" : 1.05, "water":1.05, "fire":0.85, "air":0.85, "electricity":0.85, "ice":1.05, "darkness":1, "light":.8},
                     "light": {"earth" : 0.85, "water":0.85, "fire":1.05, "air":1.05, "electricity":1.05, "ice":0.85, "darkness":.8, "light":1}}
        char_power_map = deepcopy(hero_power_map)

        rotation_speed = 20
        source_speed = 10

        hero_magics = ["earth", "water", "fire", "air", "electricity", "ice", "darkness", "light"]
        shuffle(hero_magics)
        char_magics = ["earth", "water", "fire", "air", "electricity", "ice", "darkness", "light"]
        shuffle(char_magics)

        hero_skill = hero.get_stat("magic") + hero.get_stat("intelligence")
        char_skill = char.get_stat("magic") + char.get_stat("intelligence")

        power_min_skill = 0
        power_max_skill = hero.get_max_stat("magic", tier=MAX_TIER) + hero.get_max_stat("intelligence", tier=MAX_TIER)
        if hero_skill > power_max_skill:
            hero_skill = power_max_skill
        if char_skill > power_max_skill:
            hero_skill = power_max_skill

        active_power_lineups = [[None, []], [None, []], [None, []], [None, []], [None, []]]
        live_balls = [[], [], [], [], []]

        hero_life = char_life = max_life = 100

        hero_attack = get_linear_value_of(hero_skill, power_min_skill, 20, power_max_skill, 60)
        char_attack = get_linear_value_of(char_skill, power_min_skill, 20, power_max_skill, 60)

        hero_defence = get_linear_value_of(hero_skill, power_min_skill, 1, power_max_skill, 3)
        char_defence = get_linear_value_of(char_skill, power_min_skill, 1, power_max_skill, 3)

        hero_defence = {s: hero_defence for s in hero_power_map}
        char_defence = {s: char_defence for s in hero_power_map}

        char_action_time = get_linear_value_of(char.tier, 0, 2.0, MAX_TIER, 1.2)

        hero_last_move = hero_last_shot = hero_last_source = char_last_move = char_last_shot = char_last_source = 0
        hero_source_base = char_source_base = 0
        hero_ball_idx = char_ball_idx = 0
        hero_pos = char_pos = 2
        running = False
        redraw_hero_sources = True
        redraw_char_sources = True

label interactions_power_balls_start:
    # add board
    python hide:
        # main lanes
        for i in range(5):
            img = Frame("content/gfx/frame/p_frame53.png", xsize=86, ysize=740, xpos=420+44+88*i, ypos=730)
            renpy.show("lane%d"%i, what=img)
        # boxes for the sources
        for i in range(7):
            img = Frame("content/gfx/frame/MC_bg2.png", xsize=86, ysize=86, xpos=420+44+88*(i-1), ypos=94)
            renpy.show("source_box_0_%d"%i, what=img)
            img = Frame("content/gfx/frame/MC_bg2.png", xsize=86, ysize=86, xpos=420+44+88*(i-1), ypos=714)
            renpy.show("source_box_1_%d"%i, what=img)

    # add power sources
    $ start_time = curr_time = time.time()
    call interactions_power_sources from _call_interactions_power_sources_1

    # show the interface
    show screen interactions_power_balls_interface
    
    while 1:
        $ result = ui.interact()
        $ curr_time = time.time()
        if result == "timeout":
            $ pass
        elif result == "shoot":
            if running is True:
                $ interactions_power_shoot(hero, "hero_ball_%d" % hero_ball_idx, hero_pos, (630, 30),
                                           hero_source_base, hero_magics, hero_attack)
                $ hero_last_shot = curr_time
                $ hero_ball_idx += 1
                
        elif result == "move_left":
            $ hero_pos -= 1
            $ hero_last_move = curr_time 
        elif result == "move_right":
            $ hero_pos += 1
            $ hero_last_move = curr_time
        elif result == "source_left":
            $ hero_source_base -= 88
            $ hero_last_source = curr_time
            $ redraw_hero_sources = True
        elif result == "source_right":
            $ hero_source_base += 88
            $ hero_last_source = curr_time
            $ redraw_hero_sources = True
        elif result == "start":
            $ running = True
        
        if running is True:
            python hide:
                # calculate positions of live balls
                global running, char_life, hero_life, char_pos, char_last_shot, char_last_move, char_last_source, char_ball_idx, char_source_base, redraw_char_sources

                pops = []
                for idx, line in enumerate(live_balls):
                    for ball in line:
                        ypos = (curr_time - ball[0]) * (600.0 / 16.0) # DISTANCE / DT
                        if ball[1] == hero:
                            ypos = 630 - ypos   # HERO_Y_POS
                            if ypos < 90:       # CHAR_Y_POS
                                # hit to char
                                char_life -= ball[3]/char_defence[ball[4]]
                                ypos = None
                        else:
                            ypos = ypos + 90    # CHAR_Y_POS
                            if ypos > 630:      # HERO_Y_POS
                                # hit to hero
                                hero_life -= ball[3]/hero_defence[ball[4]]
                                ypos = None
                        ball[5] = ypos
                        if ypos is None:
                            pops.append((ball, line))

                            apl = active_power_lineups[idx]
                            balls = apl[1]
                            for b in balls:
                                if b[2] == ball[2]:
                                    balls.remove(b)
                                    break
                            if not balls:
                                apl[0] = None

                # check collisions/hits
                for idx, line in enumerate(live_balls):
                    for ball in line:
                        ypos = ball[5]
                        if ypos is None:
                            continue # popped
    
                        owner = ball[1]
                        size = ball[3]
                        for ball_ in line:
                            if ball == ball_ or ball_[1] == owner:
                                continue
                            ypos_ = ball_[5]
                            if ypos_ is None:
                                continue # popped
    
                            ypos_ -= ypos
                            if ypos_ < 0:
                                ypos_ = -ypos_
                            size_ = ball_[3]
                            if ypos_ < (size + size_)/2:
                                # collision
                                source = ball[4]
                                source_ = ball_[4]
                                if owner == hero:
                                    pm = hero_power_map
                                    pm_ = char_power_map
                                else:
                                    pm = char_power_map
                                    pm_ = hero_power_map
                                size *= pm[source][source_]
                                size_ *= pm_[source_][source]
                                
                                size -= size_
                                if size > 0:
                                    pops.append((ball_, line))
                                    ball_[5] = None
                                    ball[3] = size

                                    # redraw the ball with reduced size
                                    orig_ypos = (630, 30) if owner == hero else (90, 690) # HERO_Y_POS, - DISTANCE ; CHAR_Y_POS, + DISTANCE
                                    interactions_power_ball_draw(ball, idx, orig_ypos)

                                elif size < 0:
                                    pops.append((ball, line))
                                    ball[5] = None
                                    ball_[3] = -size

                                    # redraw the ball with reduced size
                                    orig_ypos = (90, 690) if owner == hero else (630, 30) # CHAR_Y_POS, + DISTANCE ; HERO_Y_POS, - DISTANCE
                                    interactions_power_ball_draw(ball_, idx, orig_ypos)

                                    break
                                else:
                                    pops.append((ball, line))
                                    pops.append((ball_, line))
                                    ball[5] = None
                                    ball_[5] = None
                                    break
    
                # remove popped balls
                for ball, line in pops:
                    #if ball in line: 
                    line.remove(ball)
                    # FIXME pop effect?
                    renpy.hide(ball[2])

                # AI move
                can_move = (curr_time - 1) > char_last_move
                can_source = (curr_time - 1) > char_last_source
                if (curr_time - char_action_time) > char_last_shot:
                    # AI ready to shoot
                    option = None # (move, source)
                    if can_move:
                        if can_source:
                            # 9 or 6 available options -> always shoot
                            limit = 0
                            for dl in ([0, 1] if char_pos == 0 else ([0, -1] if char_pos == 4 else [0, -1, 1])):
                                for ds in [0, -1, 1]:
                                    lane = char_pos+dl
                                    source = lane+ds
                                    lane = active_power_lineups[lane]
                                    source = interactions_power_source_at(source, char_source_base, char_magics)
                                    if lane[0] is hero:
                                        value = char_power_map[source][lane[1][0][4]]
                                    elif lane[0] is char:
                                        value = .8
                                    else:
                                        value = 1
                                    if value > limit:
                                        limit = value
                                        option = [dl, -ds]
                        else:
                            # 3 or 2 available options -> shoot if there is a gain (1.1)
                            limit = 1.1
                            for dl in ([0, 1] if char_pos == 0 else ([0, -1] if char_pos == 4 else [0, -1, 1])):
                                lane = char_pos+dl
                                source = interactions_power_source_at(lane, char_source_base, char_magics)
                                lane = active_power_lineups[lane]
                                if lane[0] is hero:
                                    value = char_power_map[source][lane[1][0][4]]
                                    if value > limit:
                                        limit = value
                                        option = [dl, 0]
                    else:
                        if can_source:
                            # 3 available options -> shoot if there is a gain (1.1)
                            limit = 1.1
                            for ds in [0, -1, 1]:
                                source = char_pos+ds
                                source = interactions_power_source_at(source, char_source_base, char_magics)
                                lane = active_power_lineups[char_pos]
                                if lane[0] is hero:
                                    value = char_power_map[source][lane[1][0][4]]
                                    if value > limit:
                                        limit = value
                                        option = [0, -ds]
                        else:
                            # 1 available option -> wait if current lane is not lucrative (1.2)
                            source = interactions_power_source_at(char_pos, char_source_base, char_magics)
                            lane = active_power_lineups[char_pos]
                            if lane[0] is hero and char_power_map[source][lane[1][0][4]] >= 1.2:
                                option = [0, 0]

                    if option is not None:
                        if option[0] != 0: # move char
                            char_pos += option[0]
                            char_last_move = curr_time
                        if option[1] != 0: # move source
                            char_source_base += option[1]
                            redraw_char_sources = True
                            char_last_source = curr_time
                        # fire projectile
                        interactions_power_shoot(char, "char_ball_%d" % char_ball_idx, char_pos, (90, 690),
                                                 char_source_base, char_magics, char_attack)
                        char_last_shot = curr_time
                        char_ball_idx += 1
                elif can_move:
                    # can not shoot, but move -> move closer to threat/center
                    if char_pos == 2:
                        if active_power_lineups[0][0] == hero:
                            if active_power_lineups[2][0] != hero and active_power_lineups[3][0] != hero and active_power_lineups[4][0] != hero:
                                char_pos = 1
                                char_last_move = curr_time
                        elif active_power_lineups[4][0] == hero:
                            if active_power_lineups[2][0] != hero and active_power_lineups[1][0] != hero and active_power_lineups[0][0] != hero:
                                char_pos = 3
                                char_last_move = curr_time
                    elif char_pos == 1:
                        if active_power_lineups[0][0] != hero and (active_power_lineups[1][0] != hero or (active_power_lineups[2][0] == hero and active_power_lineups[3][0] == hero)):
                            char_pos = 2
                            char_last_move = curr_time
                    elif char_pos == 3:
                        if active_power_lineups[4][0] != hero and (active_power_lineups[3][0] != hero or (active_power_lineups[2][0] == hero and active_power_lineups[1][0] == hero)):
                            char_pos = 2
                            char_last_move = curr_time
                    elif char_pos == 0:
                        if active_power_lineups[0][0] != hero or (active_power_lineups[1][0] == hero and active_power_lineups[2][0] == hero):
                            char_pos = 1
                            char_last_move = curr_time
                    elif char_pos == 4:
                        if active_power_lineups[4][0] != hero or (active_power_lineups[3][0] == hero and active_power_lineups[2][0] == hero):
                            char_pos = 3
                            char_last_move = curr_time

                # check game state
                if (hero_life < max_life/5 and char_life < max_life/5):
                    running = "Draw"
                elif hero_life < 0:
                    running = char
                elif char_life < 0:
                    running = hero
    
            if redraw_hero_sources or redraw_char_sources:
                call interactions_power_sources from _call_interactions_power_sources_2
            #$ renpy.restart_interaction()

label interactions_power_sources:
    python hide:
        global redraw_hero_sources, redraw_char_sources
        dt = curr_time-start_time
        dx = 992 - 288
        size = 70
        if redraw_hero_sources:
            ypos = 670
            for idx, source in enumerate(hero_magics):
                img = PyTGFX.scale_content(traits[source.capitalize()].icon, size, size)
                img = ImageButton(idle_image=img, hover_image=PyTGFX.bright_content(img, .25), action=NullAction(), tooltip=source.capitalize())
                offset = 288 + (hero_source_base+88*idx + dx*dt/16) % dx
                renpy.show("hero_magic%d" % idx, what=img, at_list=[elements_from_to_with_linear((288, ypos), (992, ypos), t=16, offset_pos=(offset, ypos), rot=randint(15, 45), base_rot=randint(0, 360))])
    
        if redraw_char_sources:
            ypos = 50
            for idx, source in enumerate(char_magics):
                img = PyTGFX.scale_content(traits[source.capitalize()].icon, size, size)
                img = ImageButton(idle_image=img, hover_image=PyTGFX.bright_content(img, .25), action=NullAction(), tooltip=source.capitalize())
                offset = 288 + (char_source_base+88*idx + dx*dt/16) % dx
                renpy.show("char_magic%d" % idx, what=img, at_list=[elements_from_to_with_linear((288, ypos), (992, ypos), t=16, offset_pos=(offset, ypos), rot=randint(15, 45), base_rot=randint(0, 360))])
    
        redraw_char_sources = redraw_hero_sources = False
    return

init python:
    def interactions_power_source_at(pos, source_base, magics):
        dt = curr_time-start_time
        offset = 420 + pos * 88 + 44 - 288
        dx = (992 - 288)
        dx = (dx*dt/16+source_base) % dx
        return magics[round_int((offset-dx)/88.0)]

    def interactions_power_shoot(shooter, name, pos, ypos, source_base, magics, attack):
        source = interactions_power_source_at(pos, source_base, magics)
    
        size = attack
        size *= random.uniform(.9, 1.1)
        
        img = PyTGFX.scale_content(traits[source.capitalize()].icon, size, size)
        img = ImageButton(idle_image=img, hover_image=PyTGFX.bright_content(img, .25), action=NullAction(), tooltip=source.capitalize())
        offset = 420 + pos * 88 + 44
        renpy.show(name, what=img, at_list=[elements_from_to_with_linear((offset, ypos[0]), (offset, ypos[1]), t=16, offset_pos=None, rot=randint(15, 45), base_rot=randint(0, 360))])
    
        # append to live_balls
        ball = [curr_time, shooter, name, size, source, None]
        live_balls[pos].append(ball)
    
        # add to active_power_lineups
        temp = active_power_lineups[pos]
        if temp[0] is None:
            temp[0] = shooter
        if temp[0] == shooter:
            temp[1].append(ball[:])
        else:
            # apply to the list
            pops = []
            for b in temp[1]:
                size_ = b[3]
                source_ = b[4]
                if shooter == hero:
                    pm = hero_power_map
                    pm_ = char_power_map
                else:
                    pm = char_power_map
                    pm_ = hero_power_map
                size *= pm[source][source_]
                size_ *= pm_[source_][source]
                
                size -= size_
                if size > 0:
                    pops.append(b)
                elif size < 0:
                    b[3] = -size
                    break
                else:
                    pops.append(b)
                    break
            else:
                ball = ball[:]
                ball[3] = size
                temp[0] = shooter
                temp[1] = [ball]

            if temp[0] != shooter:
                lane = temp[1]
                for b in pops:
                    lane.remove(b)
                if not lane:
                    temp[0] = None

    def interactions_power_ball_draw(ball, pos, ypos):
        # ball = [curr_time, shooter, name, size, source, None]
        curr_time = time.time()

        name = ball[2]
        size = ball[3]
        source = ball[4]

        yoffset = ypos[0] + (curr_time-ball[0]) * (ypos[1]-ypos[0]) / 16.0 # DISTANCE / DT

        img = PyTGFX.scale_content(traits[source.capitalize()].icon, size, size)
        img = ImageButton(idle_image=img, hover_image=PyTGFX.bright_content(img, .25), action=NullAction(), tooltip=source.capitalize())
        offset = 420 + pos * 88 + 44
        renpy.show(name, what=img, at_list=[elements_from_to_with_linear((offset, ypos[0]), (offset, ypos[1]), t=16, offset_pos=(offset, yoffset), rot=randint(15, 45), base_rot=randint(0, 360))])

screen interactions_power_balls_interface:
    $ curr_time = time.time()

    # life indicators
    #  heros
    vbox:
        align (.05, .31)

        vbar:
            top_gutter 13
            bottom_gutter 0
            value max(0, hero_life-max_life/2)
            range max_life/2
            bottom_bar "content/gfx/interface/bars/progress_bar_full1.png"
            top_bar "content/gfx/interface/bars/progress_bar_1.png"
            thumb None
            xysize (22, 175)

        vbar:
            top_gutter 12
            bottom_gutter 0
            value min(max_life/2, hero_life)
            range max_life/2
            bottom_bar "content/gfx/interface/bars/bar_mine.png"
            top_bar im.Flip("content/gfx/interface/bars/progress_bar_1.png", vertical=True)
            thumb None
            xysize(22, 175)
    #  chars
    vbox:
        align (.95, .31)

        vbar:
            top_gutter 13
            bottom_gutter 0
            value max(0, char_life-max_life/2)
            range max_life/2
            bottom_bar "content/gfx/interface/bars/progress_bar_full1.png"
            top_bar "content/gfx/interface/bars/progress_bar_1.png"
            thumb None
            xysize (22, 175)

        vbar:
            top_gutter 12
            bottom_gutter 0
            value min(max_life/2, char_life)
            range max_life/2
            bottom_bar "content/gfx/interface/bars/bar_mine.png"
            top_bar im.Flip("content/gfx/interface/bars/progress_bar_1.png", vertical=True)
            thumb None
            xysize(22, 175)
    
    # buttons
    add im.Flip(im.Scale("content/gfx/images/cloud.webp", 330, 220), horizontal=True) pos 90, 560
    add im.Scale("content/gfx/images/cloud.webp", 330, 220) pos 860, 560
    
    $ img = im.Scale("content/gfx/images/button.webp", 40, 40)
    $ hover_img = PyTGFX.bright_content(img, .10)
    $ ins_img = im.Sepia(img)
    button:
        pos (340-2, 670)
        xysize 40, 40
        if (curr_time - 1) > hero_last_source:
            idle_background img
            hover_background hover_img
            action Return("source_left")
        else:
            idle_background ins_img
            hover_background ins_img
            action NullAction()
        text "A" align .5, .5 size 30 color "black" offset (2, 4)
        keysym "a"
    button:
        pos (380-2, 630)
        xysize 40, 40
        if (curr_time - 1) > hero_last_move and hero_pos != 0:
            idle_background img
            hover_background hover_img
            action Return("move_left")
        else:
            idle_background ins_img
            hover_background ins_img
            action NullAction()
        text "S" align .5, .5 size 30 color "black" offset (2, 4)
        keysym "s"
    button:
        pos (860+2, 630)
        xysize 40, 40
        if (curr_time - 1) > hero_last_move and hero_pos != 4:
            idle_background img
            hover_background hover_img
            action Return("move_right")
        else:
            idle_background ins_img
            hover_background ins_img
            action NullAction()
        text "D" align .5, .5 size 30 color "black" offset (2, 4)
        keysym "d"
    button:
        pos (900+2, 670)
        xysize 40, 40
        if (curr_time - 1) > hero_last_source:
            idle_background img
            hover_background hover_img
            action Return("source_right")
        else:
            idle_background ins_img
            hover_background ins_img
            action NullAction()
        text "F" align .5, .5 size 30 color "black" offset (2, 4)
        keysym "f"

    add im.Flip(im.Scale("content/gfx/images/cloud.webp", 330, 220), horizontal=True, vertical=True) pos 90, -50
    add im.Flip(im.Scale("content/gfx/images/cloud.webp", 330, 220), vertical=True) pos 860, -50
    
    $ img = im.Scale("content/gfx/images/button.webp", 80, 30)
    $ hover_img = PyTGFX.bright_content(img, .10)
    $ ins_img = im.Sepia(img)
    button:
        pos (420 + 3 + hero_pos * 88, 600-2)
        xysize 80, 30
        if (curr_time - 1) > hero_last_shot:
            idle_background img
            hover_background hover_img
            action Return("shoot")
        else:
            idle_background ins_img
            hover_background ins_img
            action NullAction()
        text "Space" align .5, .5 size 15 color "black"
        keysym "K_SPACE"
    # char buttons
    $ img = im.Scale("content/gfx/images/button.webp", 40, 40)
    button:
        pos (340-2, 10)
        xysize 40, 40
        idle_background img
        hover_background img
        action NullAction()
    button:
        pos (380-2, 50)
        xysize 40, 40
        idle_background img
        hover_background img
        action NullAction()
    button:
        pos (860+2, 50)
        xysize 40, 40
        idle_background img
        hover_background img
        action NullAction()
    button:
        pos (900+2, 10)
        xysize 40, 40
        idle_background img
        hover_background img
        action NullAction()
    $ img = im.Scale("content/gfx/images/button.webp", 80, 30)
    button:
        pos (420 + 3 + char_pos * 88, 90+2)
        xysize 80, 30
        idle_background img
        hover_background img
        action NullAction()

    if running is False:
        # Not started
        button:
            style_group "pb"
            action Return("start")
            text "Start" style "pb_button_text" size 20
            align .5, .5
            keysym "K_SPACE"
    elif running is not True:
        # Game Over
        $ temp = "You win!" if running == hero else ("You lose!" if running == char else running)
        button:
            style_group "pb"
            action SetVariable("game_result", running), Jump("interactions_power_balls_end")
            text "[temp]" style "pb_button_text" size 20
            align .5, .5

    timer 0.1 action Return("timeout") repeat True

label interactions_power_balls_end:
    hide screen interactions_power_balls_interface
    with dissolve

    python hide:
        # remove remaining balls
        for lane in live_balls:
            for ball in lane:
                # TODO pop effect?
                renpy.hide(ball[2])

    call interactions_postgame_lines from _call_interactions_postgame_lines_2

    python hide:
        # sources
        for i in range(len(hero_magics)):
            renpy.hide("hero_magic%d" % i)

        for i in range(len(char_magics)):
            renpy.hide("char_magic%d" % i)
        # main lanes
        for i in range(5):
            renpy.hide("lane%d"%i)
        # boxes for the sources
        for i in range(7):
            renpy.hide("source_box_0_%d"%i)
            renpy.hide("source_box_1_%d"%i)

    python hide:
        cleanup = ["hero_power_map", "char_power_map", "start_time", "curr_time", "running",
                   "rotation_speed", "source_speed", "active_power_lineups", "live_balls",
                   "hero_magics", "char_magics", "char_attack", "hero_attack", "char_defence", "hero_defence",
                   "power_min_skill", "power_max_skill", "char_skill", "hero_skill",
                   "char_life", "hero_life", "max_life", "char_pos", "hero_pos", "char_action_time",
                   "hero_last_shot", "hero_last_move", "hero_last_source", "hero_ball_idx", "hero_source_base",
                   "char_last_shot", "char_last_move", "char_last_source", "char_ball_idx", "char_source_base",
                   "redraw_char_sources", "redraw_hero_sources", "result"]
        for i in cleanup:
            if hasattr(store, i):
                delattr(store, i)
    jump girl_interactions
