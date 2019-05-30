# Tagger
label tagger:
    $ tagr = Tagger()

    $ hs()
    scene black
    show screen new_style_tooltip
    show screen tagger
    with dissolve

    python:
        while 1:
            result = ui.interact()
            if not isinstance(result, list):
                continue

            if result[0] == "select_pic":
                if tagr.tagz == tagr.oldtagz or renpy.call_screen("yesno_prompt", message="Discard your changes?", yes_action=Return(True), no_action=Return(False)):
                    tagr.select_image(result[1])

            elif result[0] == "rename":
                # rename file from input
                n = renpy.call_screen("pyt_input", tagr.pic, "Enter Name", length=100, size=(1200, 150))
                if len(n) and n != tagr.pic:
                    if os.sep in n:
                        renpy.show_screen("message_screen", "Moving to different folder is not supported!")
                    else:
                        tagr.rename_tag_file(tagr.pic, n)

            elif result[0] == "generate_ids":
                if tagr.tagz == tagr.oldtagz or renpy.call_screen("yesno_prompt", message="Discard your changes?", yes_action=Return(True), no_action=Return(False)):
                    if tagr.tagz is not None:
                        tagr.tagz = tagr.oldtagz[:]
                    if renpy.call_screen("yesno_prompt", message="This will prefix all images of the char with a generated ID.\nProceed?", yes_action=Return(True), no_action=Return(False)):
                        repair = renpy.call_screen("yesno_prompt", message="Remove invalid tags?", yes_action=Return(True), no_action=Return(False))
                        tagr.generate_ids(repair)

            elif result[0] == "tagchar":
                if result[1] == "pick":
                    if tagr.tagz == tagr.oldtagz or renpy.call_screen("yesno_prompt", message="Discard your changes?", yes_action=Return(True), no_action=Return(False)):
                        tagr.select_char(result[2])

            elif result[0] == "tags":
                if result[1] == "json_to_fn":
                    if renpy.call_screen("yesno_prompt", message="This will convert any loaded json tags into filenames!\n\n Are you Sure?", yes_action=Return(True), no_action=Return(False)):
                        if renpy.call_screen("yesno_prompt", message="This process can take quite a while!\n\nDo not turn your PC off and be sure to back your old packs up!\n\n Are you Sure?", yes_action=Return(True), no_action=Return(False)):
                            renpy.call("convert_json_to_filenames")
                elif result[1] == "write_to_fn":
                    if renpy.call_screen("yesno_prompt", message="This will write all tags to filenames!\n\n Are you Sure?", yes_action=Return(True), no_action=Return(False)):
                        nums = "".join(list(str(i) for i in range(10)))
                        pool = list("".join([string.ascii_lowercase, nums]))
                        inverted = {v:k for k, v in tagdb.tags_dict.iteritems()}
                        # Carefully! We write a script to rename the image files...
                        alltagz = set(tagdb.tags_dict.values())
                        for img in tagdb.get_imgset_with_tag(tagr.char["id"]):
                            # Normalize the path:
                            f = os.path.join(gamedir, img)
                            # Gets the tags:
                            tags = list(alltagz & tagdb.get_tags_per_path(img))
                            if not tags:
                                devlog.warning("Found no tags for image during renaming: %s" % f)
                                continue
                            tags.sort()
                            tags = list(inverted[tag] for tag in tags)
                            # New filename string:
                            fn = "".join(["-".join(tags), "-", "".join(list(choice(pool) for i in range(4)))])
                            fn += "." + img.split(".")[-1]
                            if img.endswith(".png"):
                                fn = fn + ".png"
                            elif img.endswith(".jpg"):
                                fn = fn + ".jpg"
                            elif img.endswith(".jpeg"):
                                fn = fn + ".jpeg"
                            elif img.endswith(".gif"):
                                fn = fn + ".gif"
                            oldfilename = f.split(os.sep)[-1]
                            if oldfilename.split("-")[:-1] == fn.split("-")[:-1]:
                                continue
                            else:
                                newdir = f.replace(oldfilename, fn)
                                os.rename(f, newdir)
                        del alltagz
                        del nums
                        del inverted
                        renpy.show_screen("message_screen", "Please check devlog.txt for any errors during the process!!")
            elif result[0] == "control":
                if result[1] == "return":
                    break

    hide screen tagger
    with dissolve
    jump mainscreen

screen pick_tagchar:
    zorder 3
    modal True

    #key "mousedown_4" action NullAction()
    #key "mousedown_5" action NullAction()

    frame:
        background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
        align .5, .5
        style_prefix "basic"
        vbox:
            spacing 10
            hbox:
                textbutton "Chars":
                    sensitive tagr.char_group != "chars"
                    action Function(tagr.load_tag_chars, "chars")
                textbutton "RChars":
                    sensitive tagr.char_group != "rchars"
                    action Function(tagr.load_tag_chars, "rchars")
                textbutton "NPCs":
                    sensitive tagr.char_group != "npc"
                    action Function(tagr.load_tag_chars, "npc")
            vbox:
                box_wrap True
                # text "Equip For:" style "black_serpent"
                for g in tagr.all_chars.values():
                    $ ch_id = g["id"]
                    textbutton "{size=10}%s" % ch_id:
                        xalign 0.5
                        xsize 100
                        action [Hide("pick_tagchar"), Return(["tagchar", "pick", g])]
                        tooltip g.get("name", ch_id)
            textbutton "Close":
                xalign 0.5
                action Hide("pick_tagchar")
                keysym "mousedown_3", "K_ESCAPE"

screen tagger():
    default show_tags = 3

    # char + pager:
    fixed:
        xysize (150, 40)
        style_prefix "basic"
        $ temp = "Pick Char" if tagr.char is None else tagr.char["id"]
        button:
            xysize (150, 25)
            xalign .5
            text temp size 16 color "black" hover_color "crimson" align .5, .5:
                if len(temp) > 14:
                    size 12
            action Show("pick_tagchar")
            tooltip "%sClick to select another character" % ("" if tagr.char is None else (temp + "\n"))

        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow_left.png", 30, 14)
        imagebutton:
            xalign 0.1
            ypos 25
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(0.15))
            action Function(tagr.previous_page)
            sensitive len(tagr.images) > tagr.pagesize
            tooltip "Previous Page"
        text ("%d." % tagr.imagespage) style "agrevue" color "cadetblue" xalign 0.5 ypos 35 size 12 #outlines [(1, "ivory", 0, 0)]
        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow_right.png", 30, 14)
        imagebutton:
            xalign .9
            ypos 25
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(0.15))
            action Function(tagr.next_page)
            sensitive len(tagr.images) > tagr.pagesize
            tooltip "Next Page"

    # images:
    viewport:
        ypos 40
        xysize (150, config.screen_height - 40)
        mousewheel True
        style_prefix "basic"
        has vbox xfill True
        if tagr.images:
            $ curr_images = tagr.page_images()
            $ temp = tagr.pic
            for img in curr_images:
                python:
                    fn = img.split(os.sep)[-1]
                    fn_id = fn.split(".")[0].split("-")[0]
                    if not tagr.is_valid(fn):
                        fn_id += "*"
                textbutton fn_id:
                    xysize (145, 22)
                    xalign .5
                    text_size 14
                    text_hover_color "crimson"
                    text_align .5, .5
                    if temp == img:
                        text_color "gray"
                        action Return(["rename"])
                        tooltip fn + "\nClick to rename"
                    else:
                        text_color "black"
                        action Return(["select_pic", img])
                        tooltip fn

    if tagr.pic:
        # Picture:
        fixed:
            xpos 152
            xysize (config.screen_width - 152, config.screen_height)
            #add ProportionalScale(os.path.join(path_to_pic, pic), config.screen_width - 150, config.screen_height) align .5, .5
            #add os.path.join(path_to_pic, pic) align .5, .5
            frame:
                align (.5, .5)
                background Null()
                imagebutton:
                    align (.5, .5)
                    idle os.path.join(tagr.path_to_pic, tagr.pic)
                    maximum (config.screen_width - 152, config.screen_height)

        if show_tags & 1:
            # Selected tagz:
            viewport:
                xpos 152
                xysize (150, config.screen_height)
                draggable True
                mousewheel True
                has vbox xfill True
                label u"Selected Tags:" xalign .5 text_size 14 text_color "ivory" text_outlines [(1, "black", 0, 0)]
                $ temp = tagr.tagz
                for tag in temp:
                    textbutton "[tag]":
                        xysize (150, 20)
                        #style "white_cry_button"
                        action Function(temp.remove, tag)
                        text_color "lime"
                        text_size 12
                        text_outlines [(2, "black", 0, 0)]
                        text_hover_color "crimson"
                        background Null()
                        hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

        # Tagz:
        frame:
            xpos (302 if (show_tags & 1) else 152)
            background Null()
            has vbox
            #ysize config.screen_height
            ymaximum config.screen_height + 30
            box_wrap True
            $ temp = tagr.tagz
            for tag in tagr.tag_options:
                textbutton "[tag]":
                    xysize (150, 20)
                    #style "white_cry_button"
                    if tag in temp:
                        action Function(temp.remove, tag)
                        text_color "lime"
                    else:
                        action Function(temp.append, tag)
                        text_color "ivory"
                    text_size 12
                    text_outlines [(2, "black", 0, 0)]
                    text_hover_color "crimson"
                    background Null()
                    hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

        if show_tags & 2:
            # Tag Groups
            viewport:
                xalign 1.0
                xysize (150, config.screen_height)
                draggable True
                mousewheel True
                has vbox xfill True
                label u"Tag Groups:" xalign .5 text_size 18 text_color "ivory" text_outlines [(1, "black", 0, 0)]
                for tg, v in tagr.tag_groups.iteritems():
                    $ color = v.get("color", "ivory")
                    if isinstance(color, basestring):
                        $ outlines = None
                    else:
                        $ outlines = color[1]
                        $ color = color[0]
                    textbutton tg:
                        xysize (150, 20)
                        #style "white_cry_button"
                        if tg in tagr.selected_groups:
                            action Function(tagr.remove_tag_group, tg)
                        else:
                            action Function(tagr.select_tag_group, tg)
                        text_color color
                        text_size 12
                        if outlines is not None:
                            text_outlines [(2, outlines, 0, 0)]
                        text_hover_color "crimson"
                        background Null()
                        selected tg in tagr.selected_groups
                        selected_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)
                        hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2.png", im.matrix.brightness(.10)), 5, 5)
                null height 5
                textbutton ("Deselect All" if tagr.selected_groups else "Select All"):
                    xysize (150, 30)
                    action Function(tagr.tag_group_all)
                    style "basic_button"
                    xalign .5 
                textbutton "Sort tags":
                    xysize (150, 30)
                    action Function(tagr.sort_tags)
                    style "basic_button"
                    xalign .5

    # Controls:
    vbox:
        align (1.0, 1.0)
        style_prefix "basic"
        python:
            if show_tags == 0:
                temp = "-"
                tmp = "Click to Show Tags"
            elif show_tags == 1:
                temp = "Tags"
                tmp = "Click to Show Groups"
            elif show_tags == 2:
                temp = "Groups"
                tmp = "Click to Show Tags&Groups"
            else:
                temp = "Tags&Groups"
                tmp = "Click to Hide Tags&Groups"
        textbutton temp:
            xysize (150, 30)
            sensitive tagr.pic is not None
            action SetScreenVariable("show_tags", (show_tags+1)%4)
            tooltip tmp
        textbutton "Save image":
            xysize (150, 30)
            sensitive tagr.pic is not None and (tagr.tagz != tagr.oldtagz or not tagr.is_valid(tagr.pic))
            action Function(tagr.save_image)
        textbutton "Generate IDs":
            xysize (150, 30)
            sensitive tagr.images
            action Return(["generate_ids"])

    use exit_button(size=(20, 20), action=Show("s_menu", main_menu=True))
    key "K_ESCAPE" action Show("s_menu", main_menu=True), With(dissolve)
