label gallery:
    python:
        if getattr(getattr(store, "gallery", None), "girl", None) != char:
            tl.start("Loading Gallery")
            gallery = PytGallery(char)
            tl.end("Loading Gallery")

    scene bg gallery
    $ pytfall.enter_location("management", music=True, env=None)

    show screen gallery
    with dissolve # dissolve the whole scene, not just the bg
    python hide:
        while 1:
            result = ui.interact()

            if result[0] == "image":
                index = gallery.pathlist.index(gallery.imagepath)
                if result[1] == "next":
                    index += 1
                elif result[1] == "previous":
                    index -= 1 
                gallery.set_img(gallery.pathlist[index % len(gallery.pathlist)])
            elif result[0] == "tag":
                gallery.load_images(result[1])
            elif result[0] == "view_trans":
                gallery.trans_view()
            elif result == ["control", "return"]:
                break

    hide screen gallery
    $ del gallery
    jump char_profile

screen gallery():
    default black_bg = True

    # Tags + Image:
    style_group "content"
    frame:
        background Frame("content/gfx/frame/p_frame5.png", 20, 20)
        xysize (984, 722)
        $ backimg = "content/gfx/frame/MC_bg3.png"
        if not black_bg:
            $ backimg = im.Twocolor(backimg, "white", "white")
        frame:
            align(.5, .5)
            background Frame(backimg, 10 ,10)
            imagebutton:
                align (.5, .5)
                idle PyTGFX.scale_content(gallery.get_image(), *gallery.imgsize)
                action SetScreenVariable("black_bg", not black_bg)
                tooltip "Tags: %s" % gallery.tags

    # Tags Buttons and controls:
    vbox:
        align (1.0, 0)
        # Tags:
        frame:
            background Frame("content/gfx/frame/p_frame5.png", 10, 10)
            xysize (300, 570)
            has vbox xfill True #xalign .5
            $ img = PyTGFX.scale_img("content/gfx/interface/logos/logo9.png", 280, 60)
            imagebutton:
                xalign .5
                idle img
                action NullAction()
            null height 2
            frame:
                background Frame(im.Alpha("content/gfx/frame/mc_bg.png", alpha=.5), 5, 5)
                xysize (280, 495)
                xalign .5
                # ypos 15
                side "c r":
                    viewport id "g_buttons_vp":
                        xysize (260, 480)
                        style_group "basic"
                        draggable True
                        mousewheel True
                        vbox:
                            for key, amount in gallery.tagsdict.iteritems():
                                button:
                                    xalign .5
                                    xysize (260, 30)
                                    if gallery.tag == key:
                                        selected True
                                        action Return(["tag", gallery.girl.id])
                                    else:
                                        action Return(["tag", key])
                                        selected False 
                                    fixed:
                                        xysize (250, 28)
                                        text key.capitalize() xalign 0
                                        text str(amount) color "blue" xalign .93 yoffset -2
                    vbar value YScrollValue("g_buttons_vp")

        # Buttons:
        frame:
            yoffset -5
            background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
            style_group "basic"
            xysize (300, 157)
            has vbox xalign .5 spacing 5
            $ temp = len(gallery.pathlist) > 1
            textbutton "SlideShow":
                xalign .5
                action Return(["view_trans"])
                sensitive temp
            hbox:
                xalign .5
                spacing 10
                $ img = im.Scale("content/gfx/interface/buttons/blue_arrow_left.png", 60, 60)
                imagebutton:
                    idle img
                    hover im.MatrixColor(img, im.matrix.brightness(.15))
                    insensitive im.Sepia(img)
                    sensitive temp
                    action Return(["image", "previous"])

                use exit_button(size=(45, 45), align=(.5, .5))

                $ img = im.Scale("content/gfx/interface/buttons/blue_arrow_right.png", 60, 60)
                imagebutton:
                    idle img
                    hover im.MatrixColor(img, im.matrix.brightness(.15))
                    insensitive im.Sepia(img)
                    sensitive temp
                    action Return(["image", "next"])

            textbutton "Lets Jig with this girl! :)":
                xalign .5
                sensitive check_image_extension(gallery.get_image())
                action Jump("jigsaw_puzzle_start")

screen gallery_trans():
    timer 3.0 action Return(True)

    button:
        align (.5, .5)
        background None
        xysize (config.screen_width, config.screen_height)
        action Return(False)
        keysym "mousedown_3", "K_ESCAPE"
