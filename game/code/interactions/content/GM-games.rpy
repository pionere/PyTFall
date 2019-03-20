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
        archery_min_distance, archery_max_distance = 50, 300
        archery_distance = 100
        archery_min_skill, archery_max_skill = 0, 2000
        archery_hero_skill = hero.get_stat("attack")
        if "Bow Master" in hero.traits:
            archery_hero_skill *= 1.2
        archery_char_skill = char.get_stat("attack")
        if "Bow Master" in char.traits:
            archery_char_skill *= 1.2
        if "Clumsy" in char.traits:
            archery_char_skill *= .8
        if "Bad Eyesight" in char.traits:
            archery_char_skill *= .6
        archery_hero_skill = min(archery_hero_skill, archery_max_skill)
        archery_char_skill = min(archery_char_skill, archery_max_skill)
        
        archery_strain = 800
        
        archery_wind = {"beach": 5, "city": 4, "village": 3, "park": 2, "forest": 1}
        archery_wind = archery_wind[archery_location]
        archery_wind = (uniform(.8, 1.2)*archery_wind, uniform(.8, 1.2)*archery_wind)
        
        archery_prev_mouse_hide = config.mouse_hide_time

label interactions_archery_start:
    # adjust and show wind indicator
    $ archery_wind = (uniform(.9, 1.1)*archery_wind[0], uniform(.9, 1.1)*archery_wind[1])

    $ archery_hero_arrows = []
    $ archery_char_arrows = []

    menu:
        "Select the competition type"
        "Three shoots":
            $ archery_num_arrows = 3
            $ archery_best_of = False
        "Six shoots":
            $ archery_num_arrows = 6
            $ archery_best_of = False
        "Best of three":
            $ archery_num_arrows = 3
            $ archery_best_of = True
        "Best of six":
            $ archery_num_arrows = 6
            $ archery_best_of = True
    
    # adjust target distance
    call screen interactions_archery_range_targeting
    
label interactions_archery_loop:
    show screen interactions_archery_range_shoot

    $ config.mouse_hide_time = 0
    while 1:
        $ result = ui.interact()

        if result == "shoot":
            python hide:
                posx, posy = renpy.get_mouse_pos()
                '''
                 :FIXME: add wind effect
                '''
            
                '''
                 :FIXME: add distance effect
                '''
                
                scale = get_linear_value_of(archery_distance, archery_min_distance, 1.0, archery_max_distance, .25)

                centerx, centery = config.screen_width/2, config.screen_height/2-(56*scale)
                size = 200*scale

                value = math.hypot(posx-centerx, posy-centery)
                if value <= size:
                    # hit
                    value = round_int(5*(1.0-value/size))
                    if value == 5:
                        # Bulls Eye
                        value += 5
                    else:
                        value += 1

                    rotation = randint(0, 360)
                    archery_hero_arrows.append(((posx, posy), rotation, value))
                    
                    renpy.notify(str(value))
                else:
                    # miss
                    archery_hero_arrows.append((None, None, 0))
                    
                    renpy.notify("Miss")
            jump interactions_archery_result
        elif result == "timeout":
            python hide:
                posx, posy = renpy.get_mouse_pos()
                # bit of random shake sideways 
                posx += randint(0, 4) -  2
                # weight of the bow
                posy += randint(2, 5)
                renpy.set_mouse_pos(posx, posy)
                # relaxing muscles
                if store.archery_strain < 2:
                    store.archery_strain = 0
                else:
                    store.archery_strain -= randint(1, 2)
                renpy.restart_interaction()

screen interactions_archery_range_target:
    # FIXME: add wind indicator

    # the target
    $ scale = get_linear_value_of(archery_distance, archery_min_distance, 1.0, archery_max_distance, .25)
    $ sizex, sizey = 200, 312
    add im.Scale("content/gfx/images/archery_target_1.webp", sizex*scale, sizey*scale) align .5, .5

    # the arrows
    $ arrows = [a for h, c in zip(archery_hero_arrows, archery_char_arrows) for a in ((h, True), (c, False))]
    for (pos, rot, value), of_hero in arrows:
        if pos is not None: # skip missed shots
            if not of_hero:
                if hero.gender == "male":
                    $ tint = [.5, 0.5, 1.0]
                else:
                    $ tint = [1.0, .5, .5]
            else:
                if char.gender == "male":
                    $ tint = [.75, .75, 1.0]
                else:
                    $ tint = [1.0, .75, .75]
            $ sx, sy = 30, 30
            $ pos = (pos[0]-sx/2, pos[1]-sy/2)
            add Transform(im.Scale(im.MatrixColor("content/gfx/images/archery_fletching_2.webp", im.matrix.tint(*tint)), sx, sy), rotate=rot) pos pos  

screen interactions_archery_range_targeting:
    # Set Distance
    vbox:
        align .5, .2
        spacing 5
        text "Distance" style "pb_button_text" color "black" outlines [(2, "ivory", 1, 1)] size 20
        bar:
            value FieldValue(store, 'archery_distance', archery_max_distance-archery_min_distance, max_is_zero=False, style='scrollbar', offset=archery_min_distance, step=10)
            xmaximum 150
            thumb 'content/gfx/interface/icons/move15.png'
            tooltip "Adjust the distance to the target."

    # the target
    use interactions_archery_range_target

    # Set initial strain
    vbox:
        align .5, .8
        spacing 5
        text "String" style "pb_button_text" color "black" outlines [(2, "ivory", 1, 1)] size 20
        bar:
            value FieldValue(store, 'archery_strain', 1000, max_is_zero=False, style='scrollbar', offset=0, step=100)
            xmaximum 150
            thumb 'content/gfx/interface/icons/move15.png'
            tooltip "Adjust the initial strain of the string."

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
            value max(0, archery_strain-500)
            range 500
            bottom_bar "content/gfx/interface/bars/progress_bar_full1.png"
            top_bar "content/gfx/interface/bars/progress_bar_1.png"
            thumb None
            xysize (22, 175)

        vbar:
            bar_invert True
            top_gutter 12
            bottom_gutter 0
            value max(0, 500-archery_strain)
            range 500
            bottom_bar im.Flip("content/gfx/interface/bars/progress_bar_1.png", vertical=True)
            top_bar "content/gfx/interface/bars/bar_mine.png"
            thumb None
            xysize(22, 175)

    $ scale = get_linear_value_of(archery_hero_skill, archery_min_skill, 1.0, archery_max_skill, .25)
    $ sizex, sizey = 200, 200
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
            action SetVariable("archery_strain", archery_strain - randint(80,120))
            text "A" align .5, .5 size 30 color "black"
            keysym "a"
        button:
            xysize 40, 40
            idle_background img
            hover_background hover_img
            action SetVariable("archery_strain", archery_strain - randint(20,40))
            text "S" align .5, .5 size 30 color "black"
            keysym "s"
        button:
            xysize 40, 40
            idle_background img
            hover_background hover_img
            action SetVariable("archery_strain", archery_strain + randint(20,40))
            text "D" align .5, .5 size 30 color "black"
            keysym "d"
        button:
            xysize 40, 40
            idle_background img
            hover_background hover_img
            action SetVariable("archery_strain", archery_strain + randint(80,120))
            text "F" align .5, .5 size 30 color "black"
            keysym "f"
    hbox:
        align .1, .2
        xysize 150, 40
        $ img = im.Scale("content/gfx/images/button.webp", 150, 40)
        $ hover_img = im.MatrixColor(img, im.matrix.brightness(.10))
        button:
            xysize 150, 40
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
    $ config.mouse_hide_time = archery_prev_mouse_hide
    while 1:
        $ result = ui.interact()

        if result == "char_turn":
            python hide:
                scale = get_linear_value_of(archery_distance, archery_min_distance, 1.0, archery_max_distance, .25)

                centerx, centery = config.screen_width/2, config.screen_height/2-(56*scale)
                size = 200*scale

                value = get_linear_value_of(archery_char_skill, archery_min_skill, 1.0, archery_max_skill, .25)
                '''
                 :FIXME: add wind effect
                '''
            
                '''
                 :FIXME: add distance effect
                '''
                value *= size
                value = int(value)

                posx, posy = centerx - value + random.triangular(0, 2*value), centery - value + random.triangular(0, 2*value)

                value = math.hypot(posx-centerx, posy-centery)
                if value <= size:
                    # hit
                    value = round_int(5*(1.0-value/size))
                    if value == 5:
                        # Bulls Eye
                        value += 5
                    else:
                        value += 1

                    rotation = randint(0, 360)
                    archery_char_arrows.append(((posx, posy), rotation, value))
                    
                    renpy.notify(str(value))
                else:
                    # miss
                    archery_char_arrows.append((None, 0))
                    
                    renpy.notify("Miss")

        elif result == "done":
            python hide:
                hero_points = [a[2] for a in archery_hero_arrows]
                char_points = [a[2] for a in archery_char_arrows]

                if archery_best_of:
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
    if len(archery_hero_arrows) == archery_num_arrows:
        button :
            style_group "pb"
            action Return("done")
            text "Done" style "pb_button_text"
            align .5, .9
    elif len(archery_hero_arrows) == len(archery_char_arrows):
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
        cleanup = ["archery_hero_arrows", "archery_char_arrows",
                   "archery_min_skill", "archery_max_skill", "archery_prev_mouse_hide",
                   "archery_hero_skill", "archery_char_skill",
                   "archery_distance", "archery_min_distance", "archery_max_distance",
                   "archery_wind", "archery_location", "archery_strain",
                   "archery_num_arrows", "archery_best_of"]
        for i in cleanup:
            if hasattr(store, i):
                delattr(store, i)
    jump girl_interactions
