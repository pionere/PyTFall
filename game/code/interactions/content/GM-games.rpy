label interactions_play_bow: # additional rounds continue from here
    $ interactions_check_for_bad_stuff(char)
    
    $ m = interactions_flag_count_checker(char, "flag_interactions_archery")
    if m > 1:
        $ del m
        call interactions_refused_because_tired from _call_interactions_refused_because_tired_4
        jump girl_interactions
    $ del m
    
    call interactions_prearchery_lines from _call_interactions_prearchery_lines

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
            show bg hiddenvillage_alley with fade
            #show bg b_village_1 with fade
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

    show expression hero.get_vnsprite() at Transform(align=(.0, 1.0)) as player with dissolve
    show expression char.get_vnsprite() at Transform(align=(1.0, 1.0)) as character with dissolve

    python:
        min_distance, max_distance_perc = 50, .1
        target_scale = 1.0

        archery_min_skill, archery_max_skill = 0, hero.get_relative_max_stat("attack", tier=MAX_TIER)

        dummy = copy_char(hero)
        temp = dummy.eqslots['weapon']
        if temp:
            dummy.unequip(temp, aeq_mode=True)
        dummy.equip(items["Long Bow"], remove=False, aeq_mode=True)
        hero_skill = dummy.get_stat("attack")

        dummy = copy_char(char)
        temp = dummy.eqslots['weapon']
        if temp:
            dummy.unequip(temp, aeq_mode=True)
        dummy.equip(items["Long Bow"], remove=False, aeq_mode=True)
        char_skill = dummy.get_stat("attack")

        if "Clumsy" in char.traits:
            char_skill *= .8
        if "Bad Eyesight" in char.traits:
            char_skill *= .6
        hero_skill = min(hero_skill, archery_max_skill)
        char_skill = min(char_skill, archery_max_skill)

        archery_strain = 300
        max_strain = 1000
        speed_per_force = 40

        wind_speed = {"beach": 5, "city": 4, "village": 3, "park": 2, "forest": 1}
        wind_speed = wind_speed[archery_location]
        wind_speed = (uniform(.8, 1.2)*wind_speed, uniform(.8, 1.2)*wind_speed)

        target_size = 200
        target_border = 3
        crosshair_size = 400
        prev_mouse_hide = config.mouse_hide_time
        archery_result = None

label interactions_archery_start:
    # adjust and show wind indicator
    $ wind_speed = (uniform(.9, 1.1)*wind_speed[0], uniform(.9, 1.1)*wind_speed[1])

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
    if archery_result is not None:
        call interaction_archery_char_comment_self from _call_interaction_archery_char_comment_self

    hide screen interactions_archery_range_result

    show screen interactions_archery_range_shoot

    $ config.mouse_hide_time = 0
    while 1:
        $ result = ui.interact()

        if result == "shoot":
            python hide:
                posx, posy = renpy.get_mouse_pos()
                speed = (archery_strain/float(max_strain)) # strain percentage -> 0.0 <= speed <= 1.0
                speed = 8*(1.0-speed)                      #                   -> 8.0 >= speed >= 0.0
                speed = speed*(math.e**(-speed))           # x * e^(-x)        -> 0.0 <= speed <= 0.36788
                force = get_linear_value_of(hero_skill, archery_min_skill, .5, archery_max_skill, 1.0)
                speed *= force * speed_per_force
                
                if speed == 0:
                    # miss
                    hero_arrows.append((None, None, 0))

                    store.archery_result = (None, None, None)
                else:
                    # distance effect
                    posy += distance / speed

                    '''
                     :FIXME: add wind effect
                    '''

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

                        rotation = randint(0, 360)
                        hero_arrows.append(((posx, posy), rotation, value))

                        store.archery_result = ((posx, posy), None, value)
                    else:
                        # miss
                        hero_arrows.append((None, None, 0))

                        store.archery_result = ((posx, posy), size, (centerx, centery))

            jump interactions_archery_char_turn
        elif result == "timeout":
            python hide:
                posx, posy = renpy.get_mouse_pos()
                # bit of random shake sideways
                dx = get_linear_value_of(hero_skill, archery_min_skill, 2, archery_max_skill, .5) 
                posx += random.uniform(-dx, dx)
                # breath effect
                posy += 2*dx*math.cos(time.time()*math.pi*2/4)
                # heart-beat effect
                posy += math.cos(time.time()*math.pi*2*2)
                # weight of the bow
                posy += random.uniform(0, dx/2)
                renpy.set_mouse_pos(round_int(posx), round_int(posy))
                # relaxing muscles
                if store.archery_strain < 2:
                    store.archery_strain = 0
                else:
                    store.archery_strain -= randint(1, 2)
                renpy.restart_interaction()

screen interactions_archery_range_target:
    # FIXME: add wind indicator

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

screen interactions_archery_range_targeting:
    # Set Distance
    vbox:
        align .5, .2
        spacing 5
        text "Distance" style "pb_button_text" color "black" outlines [(2, "ivory", 1, 1)] size 20
        bar:
            bar_invert True
            value FieldValue(store, 'target_scale', 1.0, max_is_zero=False, style='scrollbar', offset=max_distance_perc, step=.05)
            xmaximum 150
            thumb 'content/gfx/interface/icons/move15.png'
            tooltip "Adjust the distance to the target."

    # the target
    use interactions_archery_range_target

    # Confirm:
    button:
        style_group "pb"
        action [Hide("interactions_archery_range_targeting"), Return("done")]
        text "Done" style "pb_button_text"
        align .5, .8

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
        $ hover_img = im.MatrixColor(img, im.matrix.brightness(.10))
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
        $ hover_img = im.MatrixColor(img, im.matrix.brightness(.10))
        button:
            xysize 160, 40
            xalign .5
            idle_background img
            hover_background hover_img
            action Return("shoot")
            text "Space" align .5, .5 size 30 color "black"
            keysym "K_SPACE", "mousedown_1" 

    timer .1 action Return("timeout") repeat True

label interactions_archery_char_turn:
    hide screen interactions_archery_range_shoot
    show screen interactions_archery_range_result

    $ config.mouse_hide_time = prev_mouse_hide

    if archery_result is not None:
        call interaction_archery_char_comment from _call_interaction_archery_char_comment

    while 1:
        $ result = ui.interact()

        if result == "char_turn":
            python hide:
                centerx, centery = config.screen_width/2, config.screen_height/2-(66*target_scale)
                size = target_scale*((target_size-target_border)/2)

                value = get_linear_value_of(char_skill, archery_min_skill, .3, archery_max_skill, .05)
                '''
                 :FIXME: add wind effect
                '''

                value *= target_size # independent of the distance -> distance effect...

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

                    store.archery_result = ((posx, posy), None, value)
                else:
                    # miss
                    char_arrows.append((None, None, 0))

                    store.archery_result = ((posx, posy), size, (centerx, centery))
            jump interactions_archery_hero_turn

        elif result == "done":
            python hide:
                hero_points = [a[2] for a in hero_arrows]
                char_points = [a[2] for a in char_arrows]

                if best_of:
                    hero_points = max(hero_points) 
                    char_points = max(char_points)
                else:
                    hero_points = sum(hero_points) 
                    char_points = sum(char_points)

                if hero_points > char_points:
                    store.archery_result = hero
                elif hero_points < char_points:
                    store.archery_result = char
                else:
                    store.archery_result = None
            jump interactions_archery_end

screen interactions_archery_range_result:
    # the target
    use interactions_archery_range_target

    # Confirm:
    if archery_result is None:
        if len(hero_arrows) == num_arrows:
            button :
                style_group "pb"
                action Return("done")
                text "Done" style "pb_button_text"
                align .5, .9
        else:
            button:
                style_group "pb"
                action Return("char_turn")
                $ temp = "Next Round" if len(char_arrows) else "Begin"
                text temp style "pb_button_text"
                align .5, .9

label interactions_prearchery_lines: # lines before archery
    if ct("Impersonal"):
        $ rc("Understood. Initialising battle mode.", "Very well. Switching to training mode.")
    elif ct("Imouto"):
        $ rc("Behold of my amazing techniques, [char.mc_ref]!")
    elif ct("Dandere"):
        $ rc("Let's end this quickly, [char.mc_ref]. We have many other things to do.",  "Let's see who's better.")
    elif ct("Kuudere"):
        $ rc("Fine, I accept your challenge.", "Let's fight fair and square.")
    elif ct("Tsundere"):
        $ rc("I won't go easy on you!", "Fine, I'll show you how it's done.")
    elif ct("Bokukko"):
        $ rc("I'm gonna whack you good!", "All right, let's get over with this fast!")
    elif ct("Ane"):
        $ rc("Hehe, let's both do our best.", "Fine, let's find out who is better at this!")
    elif ct("Kamidere"):
        $ rc("Alright, let's see what you can do.", "I suppose, I have a few minutes to spare.")
    elif ct("Yandere"):
        $ rc("Sure, but don't blame me if your ass is gonna be kicked...", "I'll try to be gentle, but no promises.")
    else:
        $ rc("I don't mind. Let's do it.", "Sure, I can use some practice.")
    return

label interactions_postarchery_lines: # lines and rewards after archery
    if archery_result == hero:
        "You won."

        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.1))

        $ char.gfx_mod_stat("disposition", randint(5, 10))
        $ char.gfx_mod_stat("affection", affection_reward(char, .5, stat="attack"))

    elif archery_result == char:
        "[char.name] won."

        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.1))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.33))

        $ char.gfx_mod_stat("disposition", randint(10, 15))
        $ char.gfx_mod_stat("affection", affection_reward(char, .25, stat="attack"))
        $ char.gfx_mod_stat("affection", affection_reward(char, .25))
    else:
        "Draw."

        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.33))
        
        $ char.gfx_mod_stat("disposition", randint(15, 20))
        $ char.gfx_mod_stat("affection", affection_reward(char, .4, stat="attack"))
        $ char.gfx_mod_stat("affection", affection_reward(char, .4))

    if ct("Impersonal"):
        $ rc("Practice is over. Switching to standby mode.", "All right, let's get back to normal.")
    elif ct("Imouto"):
        $ rc("Woohoo! Getting better every day!", "Haha, it was fun! We should do it again!")
    elif ct("Dandere"):
        $ rc("Guess that does it. Good fight.", "Ok, I suppose we can leave it at this.")
    elif ct("Kuudere"):
        $ rc("You are a worthy opponent.", "We both still have much to learn.")
    elif ct("Tsundere"):
        $ rc("Jeez, now I'm tired after all that.", "Haaa... It was pretty fun.")
    elif ct("Bokukko"):
        $ rc("Oh, we done already?", "Not a bad exercise, was it?")
    elif ct("Ane"):
        $ rc("Oh my, I think I may have overdone it a little. Apologies.")
    elif ct("Kamidere"):
        $ rc("I'm tired. We are done here.", "I suppose it was a valuable experience.")
    elif ct("Yandere"):
        $ rc("Sorry, I got carried away. But you did well nevertheless.", "Goodness, look at this. I got my clothes all wet.")
    else:
        $ rc("You're pretty good.", "Phew... We should do this again sometime.")

    return

label interaction_archery_char_comment_self: # (archery_result)
    call interactions_archery_eval_result from _call_interactions_archery_eval_result_2

    if isinstance(archery_result, int):
        # hit
        if archery_result == 10:
            # Bulls Eye
            $ temp = choice(["Right in the middle.", "Bullseye!"])
            if target_scale < 0.7:
                $ archery_result = choice([" Yeah!", " Lucky shot!"]) 
            else:
                $ archery_result = choice([" Not bad.", " Nice one, right?"])
            $ char.gfx_mod_stat("joy", randint(1,2))
            char.say "[temp]" 
            extend "[archery_result]"
        elif archery_result < 4:
            # weak hit
            $ rc("Well, a [archery_result]. Maybe the next one...", "Ehh... [archery_result]. Could have been better.", "A [archery_result]. Not my best one.")
        else:
            # normal hit
            $ rc("A [archery_result]. It is fine, I guess.", "A hit of [archery_result] is O.K. with me.", "Hm.. [archery_result]. That was a nice shot, don't you think?", "A [archery_result]. For now that will do.", "Can to beat this [archery_result]?")
    else:
        # miss
        $ rc("Hmpf... Can I try again?", "Ouch... that hurts.", "Stop distracting me!", "Eh... Maybe we should not play against the sun.", "Well, here goes nothing...")
    $ archery_result = None
    return

label interaction_archery_char_comment: # (archery_result)
    call interactions_archery_eval_result from _call_interactions_archery_eval_result_1

    if isinstance(archery_result, int):
        # hit
        if archery_result == 10:
            # Bulls Eye
            $ temp = choice(["Right in the middle.", "Bullseye..."])
            if target_scale < 0.7:
                $ archery_result = choice([" Impressive!", " Lucky shot!"]) 
            else:
                $ archery_result = choice([" Not bad.", " Nice."])
            char.say "[temp]" 
            extend "[archery_result]"
        elif archery_result < 4:
            # weak hit
            $ rc("A [archery_result]. Now watch me!", "Anyone can hit a [archery_result].", "A [archery_result]. Do you even try?")
        else:
            # normal hit
            $ rc("A [archery_result]. You try to challenge me?", "A hit of [archery_result] is not bad for a beginner.", "Hm.. [archery_result]. Is this your lucky shot?", "A [archery_result]. It is O.K., considering the circumstances...", "Are you satisfied with your [archery_result]?")
    else:
        # miss
        if archery_result[0] == "_": # "_r", "_R", "_l", "_L"
            # in the box of target
            $ archery_result = archery_result[1]
            if archery_result == "r":
                $ archery_result = "up and left"
            elif archery_result == "R":
                $ archery_result = "down and left"
            elif archery_result == "l":
                $ archery_result = "up and right"
            else: # "L"
                $ archery_result = "down and right"
            char.say "That was close."
            extend " A bit more to [archery_result] and you will hit."
        elif len(archery_result) == 1:
            # one-way miss  ("r", "R", "l", "L", "u", "U", "d", "D")
            if archery_result == "r":
                char.say "You need to aim more to the left."
            elif archery_result == "R":
                char.say "That was way too far to the right."
            elif archery_result == "l":
                char.say "You need to aim more to the right."
            elif archery_result == "L":
                char.say "That was way too far to the left."
            elif archery_result == "u":
                char.say "You need to lower your aim."
            elif archery_result == "U":
                $ rc("Are you shooting for the stars?", "Watch your back, the arrow might come around the Earth.", "Please, do not hurt the birds!")
            elif archery_result == "d":
                char.say "You need to raise your aim."
            else: # archery_result == "D":
                $ rc("Try not to shoot yourself in the foot!", "Are you hunting for gophers?", "You never had to dig a borehole by hand, right?")
        else:
            # two-way miss
            if archery_result == archery_result.lower():
                # ("ru", "rd", "lu", "ld")
                if archery_result == "ru":
                    $ archery_result = "lower and to the left"
                elif archery_result == "rd":
                    $ archery_result = "higher and to the left"
                elif archery_result == "lu":
                    $ archery_result = "lower and to the right"
                else: # archery_result == "ld":
                    $ archery_result = "higher and to the right"
                char.say "With a bit more practice and aiming [archery_result], you might hit the target."
            elif archery_result == archery_result.upper():
                # ("RU", "RD", "LU", "LD")
                if archery_result == "RU":
                    $ archery_result = "high and to the right."
                elif archery_result == "RD":
                    $ archery_result = "low and to the right."
                elif archery_result == "LU":
                    $ archery_result = "high and to the left."
                else: # archery_result == "LD":
                    $ archery_result = "low and to the left."
                $ temp = choice(["You need some glasses?", "It was hopeless from the beginning!"]) 
                char.say "[temp]"
                extend " That was way too [archery_result]"
            else:
                # ("rU", "rD", "lU", "lD", "Ru", "Rd", "Lu", "Ld")
                if archery_result[0] == archery_result[0].upper():
                    $ archery_result = archery_result[0]
                else:
                    $ archery_result = archery_result[1]
                if archery_result == "R":
                    char.say "That was way too far to the right."
                    extend " Not to mention other issues..."
                elif archery_result == "L":
                    char.say "That was way too far to the left."
                    extend " Not to mention other issues..."
                elif archery_result == "U":
                    $ rc("Are you shooting for the stars?", "Watch your back, the arrow might come around the Earth.", "Please, do not hurt the birds!")
                else: # archery_result == "D":
                    $ rc("Try not to shoot yourself in the foot!", "Are you hunting for gophers?", "You never had to dig a borehole by hand, right?")
    $ archery_result = None
    return

# transform the archery_result from the format of [(posx, posy), size, (centerx, centery)] to string  
label interactions_archery_eval_result:
    python hide:
        pos, size, value = store.archery_result
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
        store.archery_result = value 
    return

label interactions_archery_end:
    hide screen interactions_archery_range_result
    with dissolve

    call interactions_postarchery_lines from _call_interactions_postarchery_lines

    python hide:
        cleanup = ["hero_arrows", "char_arrows", "archery_result", "temp", "dummy",
                   "archery_min_skill", "archery_max_skill", "speed_per_force",
                   "prev_mouse_hide", "hero_skill", "char_skill",
                   "target_scale", "target size", "target_border", "crosshair_size",
                   "distance", "min_distance", "max_distance_perc",
                   "wind_speed", "archery_location", "archery_strain",
                   "num_arrows", "best_of"]
        for i in cleanup:
            if hasattr(store, i):
                delattr(store, i)
    jump girl_interactions
