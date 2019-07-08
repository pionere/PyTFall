init -948: # Transforms:
    # Basic transforms:

    # First, More default positions:
    transform mid_right:
        align (.75, 1.0)

    transform mid_left:
        align (.25, 1.0)

    transform center_right:
        align (.95, .5)

    transform center_left:
        align (.05, .5)

    # Other Transforms:
    transform move_from_to_pos_with_linear(start_pos=(0, 0), end_pos=(config.screen_width, config.screen_height), t, hide_when_done):
        # Move by pos with easeOut:
        subpixel True
        pos start_pos
        linear t pos end_pos
        alpha (.0 if hide_when_done else 1.0)

    transform move_from_to_pos_with_ease(start_pos=(0, 0), end_pos=(config.screen_width, config.screen_height), t=1.0, wait=0):
        # Moves the child from start position to end position in t seconds
        subpixel True
        pos start_pos
        pause wait
        ease t pos end_pos

    transform move_from_to_pos_with_easeout(start_pos=(0, 0), end_pos=(config.screen_width, config.screen_height), t):
        # Move by pos with easeOut:
        subpixel True
        pos start_pos
        easeout t pos end_pos

    transform move_from_to_align_with_linear(start_align=(0, 0), end_align=(1.0, 1.0), t=1.0):
        # Move_by_align_with_linear
        subpixel True
        align start_align
        linear t align end_align

    transform move_from_to_align_with_easein(start_align=(0, 0), end_align=(1.0, 1.0), t=1.0):
        # Move_by_align_with_linear
        subpixel True
        align start_align
        easein t align end_align

    transform move_from_to_offset_with_ease(start_offset=(-640, -400), end_offset=(0, 0), t=1.0):
        # move_from_to_offset_with_ease
        subpixel True
        offset start_offset
        ease t offset end_offset

    transform slide(so1=(-1000, 0), eo1=(0, 0), t1=1.0,
                             so2=(0, 0), eo2=(-1000, 0), t2=1.0):
        # Slides in on show
        # Slide out in show
        on show:
            move_from_to_offset_with_ease(so1, eo1, t1)
        on hide:
            move_from_to_offset_with_ease(so2, eo2, t2)

    transform auto_slide(init_pos=(0, -40), show_pos=(0, 0), t1=.25, hide_pos=(0, -40), t2=.25):
        # Auto-Slide, default values are for the top_stripe
        # This is used instead of a normal slide as it doesn't reset in the middle of a motion when switching between show/hide
        pos init_pos
        on show:
            linear t1 pos show_pos
        on hide:
            linear t2 pos hide_pos

    transform fade_from_to(start_val=1.0, end_val=.0, t=1.0, wait=0):
        # Setup as a fade out, reverse the values for the fade in
        # simple_fade (fade is reserved...)
        alpha start_val
        pause wait
        linear t alpha end_val

    transform fade_from_to_with_easeout(start_val=1.0, end_val=.0, t=1.0, wait=0):
        # Setup as a fade out, reverse the values for the fade in
        # simple_fade (fade is reserved...)
        subpixel True
        alpha start_val
        pause wait
        easeout t alpha end_val

    transform fade_in_out(sv1=.0, ev1=1.0, t1=1.0,
                                        sv2=1.0, ev2=.0, t2=1.0):
        on show:
            fade_from_to(sv1, ev1, t1)
        on hide:
            fade_from_to(sv2, ev2, t2)

    transform rotate_by(degrees):
        # When used with x/ycenter in SL, this will (or at leastshould) be positioned correctly!
        rotate degrees
        rotate_pad True
        transform_anchor True
        subpixel True

    transform repeated_rotate(start_val=0, end_val=360, t=1.0):
        rotate start_val
        linear t rotate end_val
        rotate_pad True
        transform_anchor True
        subpixel True
        repeat

    transform simple_zoom_from_to_with_linear(start_val=1.0, end_val=.0, t=1.0):
        # Simple zoom...
        subpixel True
        anchor (.5, .5)
        zoom start_val
        linear t zoom end_val

    transform simple_zoom_from_to_with_easein(start_val=1.0, end_val=.0, t=1.0):
        # Simple zoom...
        subpixel True
        anchor (.5, .5)
        zoom start_val
        easein t zoom end_val

    # Complex transforms(*):
    transform pers_effect():
        subpixel True
        parallel:
            fade_from_to(.98, 1.05, 1.0)
            fade_from_to(1.05, .98, 2.2)
        parallel:
            simple_zoom_from_to_with_linear(.98, 1.05, 1.0)
            simple_zoom_from_to_with_linear(1.05, .98, 2.2)
        repeat

    transform arena_stats_slide:
        move_from_to_offset_with_ease(start_offset=(0, 0), end_offset=(0, -200), t=8.0)

    transform elements:
        subpixel True
        parallel:
            block:
                parallel:
                    fade_from_to(.3, 1.0, 5.0)
                parallel:
                    simple_zoom_from_to_with_linear(1.2, .8, 5.0)
            block:
                parallel:
                    fade_from_to(1.0, .3, 5.0)
                parallel:
                    simple_zoom_from_to_with_linear(.8, 1.2, 5.0)
            repeat
        parallel:
            repeated_rotate(t=30.0)

    transform elements_from_to_with_linear(start_pos, end_pos, t, offset_pos=None, rot=30.0, base_rot=0.0):
        subpixel True
        parallel:
            elements
        parallel:
            pos (start_pos if offset_pos is None else offset_pos)
            linear (t if offset_pos is None else t*(1.0 - (float(offset_pos[0]-start_pos[0])/(end_pos[0]-start_pos[0]) if end_pos[0] != start_pos[0] else float(offset_pos[1]-start_pos[1])/(end_pos[1]-start_pos[1])))) pos end_pos
            block:
                pos start_pos
                linear t pos end_pos
                repeat

    transform arena_textslide:
        # Slider for arena Vicroty/Defeat texts
        on show:
            parallel:
                fade_from_to(.3, 1.0, .5)
            parallel:
                xoffset 500
                ease .5 xoffset -400
                ease .5 xoffset -100
            linear 3.0 zoom 1.3
        on hide:
            fade_from_to(t=.5)

    transform random_fish_movement():
        align(random.random(), random.random())
        block:
            subpixel True
            choice:
                linear randint(16, 22) align(random.random(), random.random())
            choice:
                easein randint(16, 22) align(random.random(), random.random())
            choice:
                easeout randint(16, 22) align(random.random(), random.random())
            choice:
                easein_quad randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_quad randint(16, 22) align(random.random(), random.random())
            choice:
                easein_cubic randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_cubic randint(16, 22) align(random.random(), random.random())
            choice:
                easein_quart randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_quart randint(16, 22) align(random.random(), random.random())
            choice:
                easein_quint randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_quint randint(16, 22) align(random.random(), random.random())
            choice:
                easein_expo randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_expo randint(16, 22) align(random.random(), random.random())
            choice:
                easein_circ randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_circ randint(16, 22) align(random.random(), random.random())
            choice:
                easein_back randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_back randint(16, 22) align(random.random(), random.random())
            choice:
                easein_elastic randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_elastic randint(16, 22) align(random.random(), random.random())
            choice:
                easein_bounce randint(16, 22) align(random.random(), random.random())
            choice:
                easeout_bounce randint(16, 22) align(random.random(), random.random())
            pause randint(1, 3)
            repeat

    # Interactions:
    transform interactions_angry_pulse_tr:
        "angry_pulse"
        pos (150, 566)
        anchor (.5, .5)
        block:
            linear .05 zoom 1.1
            linear .05 zoom .9
            pause .2
            linear .05 zoom 1.1
            linear .05 zoom .9
            pause .8
            repeat

    transform interactions_puzzled_tr:
        "question_mark"
        pos (130, 546)
        alpha .8
        anchor (.0, .0)
        block:
            linear 1 rotate 15 alpha .7 zoom 1.1
            linear 1 rotate -15 alpha .9 zoom .9
            repeat

    transform interactions_note_tr:
        "music_note"
        pos (125, 546)
        alpha .9
        anchor (.0, .0)
        block:
            linear 1 alpha 1.0 zoom 1.1
            linear 1 alpha .8 zoom .9
            repeat

    transform interactions_blush_tr:
        "shy_blush"
        pos (218, 640)
        anchor (.5, .5)
        yzoom 2.0
        block:
            linear 1.0 zoom 1.1
            linear 1.0 zoom .9
            repeat

    transform interactions_surprised_tr:
        "exclamation_mark"
        subpixel True
        pos (157, 650)
        alpha .8
        anchor (.5, 1.0)
        block:
            linear .4 yzoom 1.1 alpha .7
            pause .01
            linear .4 yzoom .9 alpha .9
            repeat

    transform interactions_sweat_drop_tr:
        pos (145, 575) alpha .0
        "sweat_drop"
        easein 1.0 ypos 610 alpha 1.0

    transform interactions_scared_lines_tr:
        "scared_lines"
        pos (160, 577)
        alpha .0
        linear 1.0 alpha 1.0

    transform interactions_zoom(t):
        subpixel True
        anchor (.5, .5)
        block:
            linear t zoom 1.1
            linear t zoom 1

    default interactions_portraits_overlay = DisplayableSwitcher(displayable={"angry": interactions_angry_pulse_tr,
                                                                              "sweat": interactions_sweat_drop_tr,
                                                                              "scared": interactions_scared_lines_tr,
                                                                              "puzzled": interactions_puzzled_tr,
                                                                              "note": interactions_note_tr,
                                                                              "surprised": interactions_surprised_tr,
                                                                              "shy": interactions_blush_tr, # probably should be used only as a replacement for missing shy portraits
                                                                              "love": Transform("hearts_flow", pos=(220, 700)),
                                                                              "like": Transform("hearts_rise", pos=(120, 405), anchor=(.0, .0))
                                                                              })

    # Overlay ATLs:
    transform mc_stats_effect(d, start, pos, yoffset, duration):
        subpixel True
        pause start
        d
        pos pos yoffset 0 anchor (.5, .5)
        alpha 1.0 zoom 1.0
        easein_circ duration*.5 alpha 1.0 zoom 1.0 yoffset yoffset
        pause duration*.1
        zoom .9
        ease duration*.15 zoom 1.1
        zoom .9
        ease duration*.15  zoom 1.2
        # HitlerKaputt(d, 10)
        # linear duration*.1 alpha .0
        easeout_circ duration*.1 alpha .0 zoom .0

    transform char_stats_effect(d, start, pos, yoffset, duration):
        subpixel True
        pause start
        d
        pos pos yoffset 0 anchor (.5, .5)
        alpha 1.0 zoom 1.0
        easein_circ duration*.5 alpha 1.0 zoom 1.0 yoffset yoffset
        pause duration*.1
        zoom .9
        ease duration*.15 zoom 1.1
        zoom .9
        ease duration*.15  zoom 1.2
        easeout_circ duration*.1 alpha .0 zoom .0

    transform affection_effect(d, start, pos, yoffset, duration):
        subpixel True
        pause start
        d
        pos pos yoffset 0 anchor (.5, .5)
        alpha .6 zoom .5
        linear duration alpha 1.0 zoom 1.2 yoffset yoffset

    transform found_effect(d, start, pos, yoffset, duration):
        subpixel True
        pause start
        d
        pos pos yoffset 0 anchor (.5, .5)
        alpha 1.0 zoom .5
        parallel:
            linear duration zoom 1.0 yoffset yoffset
        parallel:
            pause duration*.5
            ease duration*.5 alpha .0


    transform sex_scene_libido_hearth(t):
        anchor (.5, .5)
        subpixel True
        block:
            linear (3.0/(t+1)) zoom (1.1 + t*.05)
            linear (3.0/(t+1)) zoom 1
            repeat

    # BE Transforms:
    transform status_overlay(sv1=.0, ev1=1.0, t1=1.0,
                                        sv2=1.0, ev2=.0, t2=1.0):
        fade_from_to(sv1, ev1, t1)
        fade_from_to(sv2, ev2, t2)
        repeat

    transform damage_color(img): # Note: Testing case, this should become a DD/UDD with moar options at some point.
        im.MatrixColor(img, im.matrix.saturation(1))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.1))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.2))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.3))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.4))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.5))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.6))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.7))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.8))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.7))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.6))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.5))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.4))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.3))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.2))
        .05
        im.MatrixColor(img, im.matrix.saturation(1.1))
        .05
        repeat

    transform damage_shake(t, random_range, delay=0):
        subpixel True
        offset (0, 0)
        pause delay
        choice:
            linear t offset(randint(*random_range), randint(*random_range))
        choice:
            linear t offset(randint(*random_range), randint(*random_range))
        choice:
            linear t offset(randint(*random_range), randint(*random_range))
        choice:
            linear t offset(randint(*random_range), randint(*random_range))
        choice:
            linear t offset(randint(*random_range), randint(*random_range))
        repeat

    transform vertical_damage_shake(t, random_range, delay=0): # earthquake-like vertical shaking for some earth spells
        subpixel True
        offset (0, 0)
        pause delay
        choice:
            linear t offset(0, randint(*random_range))
        choice:
            linear t offset(0, randint(*random_range))
        choice:
            linear t offset(0, randint(*random_range))
        choice:
            linear t offset(0, randint(*random_range))
        choice:
            linear t offset(0, randint(*random_range))
        repeat

    transform battle_bounce(pos):
        alpha 1
        pos pos # Initial position.
        xanchor .5
        easein_circ .3 yoffset -100
        easeout_circ .3 yoffset 0
        easein_circ .3 yoffset -70
        easeout_circ .3 yoffset 0
        linear .3 alpha 0

    transform be_stats_slideout():
        on hover:
            linear .3 xoffset 100
        on idle:
            linear .3 xoffset 300

    transform be_dodge(xoffset, t):
        easein .5 xoffset xoffset
        pause t
        linear .4 xoffset 0

    # GUI ===>>>
    transform circle_around(t=10, around=(config.screen_width/2, config.screen_height/2), angle=0, radius=200):
        subpixel True
        anchor (.5, .5)
        around around
        angle angle
        radius radius
        linear t clockwise circles 1
        repeat

    transform scroll_around(t):
        subpixel True
        #additive 1.0
        xpan -180
        linear t xpan 180
        repeat

    # same as scroll_around, but works in more contexts
    transform mm_clouds(start, end, t):
        subpixel True
        additive 1.0
        xpos start
        linear t xpos end
        repeat

    transform mm_fire(yps, ype, ast, ae, t):
        additive .9
        ypos yps
        alpha ast
        linear t ypos ype alpha ae
        repeat

    transform flashing:
        additive 1.0 alpha .4
        block:
            linear 1.0 alpha .1
            linear 1.0 alpha .4
            repeat

    transform fog:
        linear 1.0 alpha .2
        linear 1.0 alpha .3
        linear 1.0 alpha .4
        linear 1.0 alpha .5
        linear 1.0 alpha .4
        linear 1.0 alpha .3
        repeat

    # UDD ===>>>
    transform vortex_particle(displayable, t=10, around=(config.screen_width/2, config.screen_height/2), angle=0, start_radius=200, end_radius=0, circles=3):
        displayable
        subpixel True
        around around
        angle angle
        radius start_radius
        easeout t radius end_radius clockwise circles circles
        Null()

    transform vortex_particle_2(displayable, t=10, around=(config.screen_width/2, config.screen_height/2), angle=0, start_radius=200, circles=3):
        # This one keeps the radius constant
        displayable
        subpixel True
        around around
        angle angle
        radius start_radius
        linear t clockwise circles 1
        Null()
        repeat circles

    # This bit is required for the Snowing effect:
    transform snowlike_particle(d, delay, startpos, endpos, speed):
        d
        pause delay
        subpixel True
        pos startpos
        linear speed pos endpos

    transform particle(d, delay, speed=1.0, around=(config.screen_width/2, config.screen_height/2), angle=0, radius=200):
        d
        pause delay
        subpixel True
        around around
        radius 0
        linear speed radius radius angle angle

    transform fly_away():
        easeout_bounce 1.5 yoffset -1000
        pause 2.0
        easeout_bounce 1.0 yoffset 0
        parallel:
            easeout_bounce .1 yzoom .95
            easeout_bounce .1 yzoom 1.0
        parallel:
            easeout_bounce .1 yoffset 10
            easeout_bounce .1 yoffset 0

    transform blowing_wind():
        easeout_bounce .1 xzoom -1.0 xanchor .1 xoffset 20
        easeout_bounce .1 xzoom 1.0 xanchor .0 xoffset 0
        repeat

    transform shake(dt=.4, dist=128):
        function renpy.curry(_shake_function)(dt=dt,dist=dist)
