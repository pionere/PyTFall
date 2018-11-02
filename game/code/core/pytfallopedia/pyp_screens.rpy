screen pytfallopedia():
    zorder 1000
    modal True

    # Top Stripe Frame:
    fixed:
        xysize config.screen_width, 40
        add "content/gfx/frame/top_stripe.png"
        # Buttons:
        $ img = im.Scale("content/gfx/interface/buttons/close.png", 35, 35)
        imagebutton:
            align .996, .5
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            insensitive_background img
            action Hide("pytfallopedia")
            tooltip "Close PyTFallopedia"
            keysym "mousedown_3"

        $ img = im.Scale("content/gfx/interface/buttons/arrow_button_metal_gold_left.png", 35, 35)
        imagebutton:
            align .035, .5
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            insensitive_background img
            action NullAction()
            tooltip "Back"
            keysym "mousedown_2"

    # Right frame with info (Will prolly be a bunch of separate screens in the future)
    frame:
        background Frame("content/gfx/frame/mes11.webp", 2, 2)
        pos 289, 42
        xysize config.screen_width-287, config.screen_height-41
        style_prefix "proper_stats"

        if not pyp.main_focused and not pyp.sub_focused:
            add "content/gfx/interface/logos/logo9.png" align .5, .05

            vbox:
                align .5, .5
                label "Welcome to PyTFallopea" xalign .5 text_size 40
                null height 100
                text "An ingame encyclopedia that introduces the player to the core game world and game play concepts!" xalign .5

    # Left frame with buttons:
    frame:
        pos 4, 42
        background Frame("content/gfx/frame/mes11.webp", 2, 2)
        padding 2, 12
        has side "c l"
        vpgrid:
            id "vp"
            style_prefix "basic"
            xysize 279, config.screen_height-53
            mousewheel 1
            draggable 1
            cols 1
            # if pyp.sub_focused:
            #     for name, screen in pyp.sub[pyp.main_focused]:
            #         button:
            #             xsize 270
            #             text name
            #             action Show(screen)
            # if pyp.sub_focused:
            #     for name, screen in pyp.sub[pyp.main_focused]:
            #         button:
            #             xsize 270
            #             text name
            #             action Show(screen)

        vbar value YScrollValue("vp")

    if not pyp.main_focused and not pyp.sub_focused:
        add "content/gfx/frame/h3.png"
