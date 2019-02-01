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
            action Function(pyp.close)
            tooltip "Close PyTFallopedia"
            keysym "K_ESCAPE", "mousedown_3"

        $ img = im.Scale("content/gfx/interface/buttons/arrow_button_metal_gold_left.png", 35, 35)
        imagebutton:
            align .035, .5
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            insensitive im.Sepia(img)
            action Function(pyp.back)
            sensitive pyp.root != pyp.focused_page
            tooltip "Back"
            keysym "mousedown_3"

    # Right frame with info (Will prolly be a bunch of separate screens in the future)
    frame:
        background Frame("content/gfx/frame/mes11.webp", 2, 2)
        pos 289, 42
        xysize config.screen_width-287, config.screen_height-41
        style_prefix "proper_stats"

    #$ renpy.show_screen(pyp.focused_page[1])
    # use expression pyp.focused_page[1]

    if pyp.root == pyp.focused_page:
        fixed:
            pos 302, 49
            xysize 971, 664
            style_prefix "pyp"

            add "content/gfx/interface/logos/logo9.png" xalign .5 ypos 30

            vbox:
                align .5, .5
                label "Welcome to PyTFallopedia" xalign .5 text_size 40
                null height 100
                text "An in-game encyclopedia that introduces the player to the core game-world and game-play concepts!" xalign .5

        add "content/gfx/frame/h3.webp"

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
            python:
                curr_page = pyp.focused_page
                menu = curr_page[3]
                if not menu:
                    # the selected page is a leaf -> use the menu of the parent
                    menu = curr_page[2][3]
                curr_page = curr_page[1]

            for entry in menu:
                    button:
                        xsize 270
                        text entry[0]
                        if pyp.focused_page == entry:
                            selected True
                            action NullAction()
                        else:
                            action Function(pyp.open, entry)

        vbar value YScrollValue("vp")


# DEFAULT positioning blueprint that can be used with any screen pyp info in the future.
screen pyp_default():
    zorder 1001

    fixed:
        pos 302, 49
        xysize 971, 664
        style_prefix "pyp"
        fixed:
            xysize 600, 664
            # Title and text bits:
            frame:
                style_suffix "title_frame"
                xalign .5 ypos 10
                text "**Title**" size 30

        fixed:
            xpos 601
            xysize 370, 664
            style_prefix "pyp"
            # Images and maybe details:

    # ForeGround frame (should be a part of every screen with Info):
    add "content/gfx/frame/h3.webp"
