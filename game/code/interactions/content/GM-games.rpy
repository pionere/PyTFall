label interactions_play_bow: # additional rounds continue from here
    $ interactions_check_for_bad_stuff(char)
    
    $ m = interactions_flag_count_checker(char, "flag_interactions_archery")
    if m > 1:
        $ del m
        call interactions_refused_because_tired from _call_interactions_refused_because_tired_4
        jump girl_interactions
    $ del m
    
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

        archery_min_skill, archery_max_skill = 0, 2000
        hero_skill = hero.get_stat("attack")
        if "Bow Master" in hero.traits:
            hero_skill *= 1.2
        char_skill = char.get_stat("attack")
        if "Bow Master" in char.traits:
            char_skill *= 1.2
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

label interactions_archery_loop:
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
                    hero_arrows.append((None, None, 0))

                    renpy.notify("Miss")
                else:
                    # distance effect
                    posy += distance / speed

                    '''
                     :FIXME: add wind effect
                    '''
                    posx, posy = round_int(posx), round_int(posy)

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

                        renpy.notify(str(value))
                    else:
                        # miss
                        hero_arrows.append((None, None, 0))

                        renpy.notify("Miss")
            jump interactions_archery_result
        elif result == "timeout":
            python hide:
                posx, posy = renpy.get_mouse_pos()
                # bit of random shake sideways 
                posx += randint(0, 4) -  2
                # breath effect
                posy += 4*math.cos(time.time()*math.pi*2/4)
                # heart-beat effect
                posy += math.cos(time.time()*math.pi*2)
                # weight of the bow
                posy += randint(0, 2)
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
    for (pos, rot, value), c in izip_longest(hero_arrows, char_arrows):
        if pos is not None: # skip missed shots
            $ pos = [pos[0]-size, pos[1]-size]
            add Transform(hero_img, rotate=rot) pos pos offset (offset, offset)
        if c is not None: # not shot yet
            $ pos, rot, value = c
            if pos is not None: # skip missed shots
                $ pos = [pos[0]-size, pos[1]-size]
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
    $ sizex, sizey = crosshair_size, crosshair_size
    $ pos = renpy.get_mouse_pos()
    $ pos = (pos[0]-sizex/2, pos[1]-sizey/2)
    add im.Scale("content/gfx/images/crosshair.webp", sizex*scale, sizey*scale) pos pos

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

label interactions_archery_result:
    hide screen interactions_archery_range_shoot
    show screen interactions_archery_range_result
    with dissolve

    $ renpy.restart_interaction()
    $ config.mouse_hide_time = prev_mouse_hide
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
                posx, posy = round_int(posx), round_int(posy)

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
                    
                    renpy.notify(str(value))
                else:
                    # miss
                    char_arrows.append((None, None, 0))
                    
                    renpy.notify("Miss")

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
                    narrator("You won.")
                elif hero_points < char_points:
                    narrator("[char.name] won.")
                else:
                    narrator("Draw.")
            jump interactions_archery_end

screen interactions_archery_range_result:
    # the target
    use interactions_archery_range_target

    # Confirm:
    if len(char_arrows) == num_arrows:
        button :
            style_group "pb"
            action Return("done")
            text "Done" style "pb_button_text"
            align .5, .9
    elif len(hero_arrows) == len(char_arrows):
        button:
            style_group "pb"
            action [Hide("interactions_archery_range_result"), Jump("interactions_archery_loop")]
            text "Next Round" style "pb_button_text"
            align .5, .9
    else:
        button:
            style_group "pb"
            action Return("char_turn")
            text "[char.name]'s turn" style "pb_button_text"
            align .5, .9

label interactions_archery_end:
    hide screen interactions_archery_range_result
    with dissolve
    python hide:
        cleanup = ["hero_arrows", "char_arrows",
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
