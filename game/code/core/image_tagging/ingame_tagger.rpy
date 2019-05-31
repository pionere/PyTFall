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
                    n = os.path.normpath(n)
                    if os.sep in n:
                        renpy.show_screen("message_screen", "Moving to different folder is not supported!")
                    else:
                        tagr.rename_tag_file(tagr.pic, n)

            elif result[0] == "refresh":
                tagr.load_tag_chars(tagr.char_group)
                tagr.select_char(tagr.char)

            elif result[0] == "generate_ids":
                if tagr.tagz == tagr.oldtagz or renpy.call_screen("yesno_prompt", message="Discard your changes?", yes_action=Return(True), no_action=Return(False)):
                    if tagr.tagz is not None:
                        tagr.tagz = tagr.oldtagz[:]
                    if renpy.call_screen("yesno_prompt", message="This will prefix all images of the char with a generated ID.\nProceed?", yes_action=Return(True), no_action=Return(False)):
                        repair = renpy.call_screen("yesno_prompt", message="Remove invalid tags?", yes_action=Return(True), no_action=Return(False))
                        tagr.generate_ids(repair)

            elif result[0] == "edit_json":
                temp = deepcopy(tagr.char)
                fields = tagr.group_fields()
                for field, type in fields:
                    if field not in temp:
                        if type == "list":
                            temp[field] = []
                        elif type in ["number", "text"]:
                            temp[field] = ""
                        else:
                            temp[field] = type
                tagr.char_edit = temp
                renpy.show_screen("tagger_char_json_config", temp)
            elif result[0] == "json":
                if result[1] == "text":
                    field = result[2]
                    length = result[3]
                    n = renpy.call_screen("pyt_input", tagr.char_edit[field], "Enter Name", length=length, size=(12*length, 150))
                    tagr.char_edit[field] = n
                elif result[1] == "int":
                    field = result[2]
                    length = 20
                    try:
                        value = int(tagr.char_edit[field])
                    except:
                        value = 0
                    n = renpy.call_screen("pyt_input", value, "Enter a Number", length=length, size=(12*length, 150))
                    try:
                        n = int(n)
                    except:
                        n = ""
                    tagr.char_edit[field] = n
                elif result[1] == "float":
                    field = result[2]
                    length = 20
                    try:
                        val = tagr.char_edit[field]
                        value = float(val)
                        if int(val) == value:
                            value = int(val)
                    except:
                        value = 0
                    n = renpy.call_screen("pyt_input", value, "Enter a Value", length=length, size=(12*length, 150))
                    try:
                        n = float(n)
                        if int(n) == n:
                            n = int(n)
                    except:
                        n = ""
                    tagr.char_edit[field] = n
                elif result[1] == "bool":
                    field = result[2]
                    tagr.char_edit[field] = not tagr.char_edit[field]
                elif result[1] == "select":
                    field = result[2]
                    options = result[3]
                    pos = renpy.get_mouse_pos()
                    max_rows = min(10, len(options)+1)
                    row_size = (160, 30)
                    n = renpy.call_screen("dropdown_content", options, max_rows, row_size, pos, tagr.char_edit[field], None, None)
                    tagr.char_edit[field] = n
                elif result[1] == "add":
                    if result[2] == "text":
                        field = result[3]
                        options = result[4]
                        pos = renpy.get_mouse_pos()
                        max_rows = min(10, len(options)+1)
                        row_size = (160, 30)
                        n = renpy.call_screen("dropdown_content", options, max_rows, row_size, pos, undefined, None, None)
                        if n is not undefined:
                            tagr.char_edit[field].append(n)
                    elif result[2] == "pair":
                        field = result[3]
                        options = result[4]
                        pos = renpy.get_mouse_pos()
                        max_rows = min(10, len(options)+1)
                        row_size = (160, 30)
                        n = renpy.call_screen("dropdown_content", options, max_rows, row_size, pos, undefined, None, None)
                        if n is not undefined:
                            tagr.char_edit[field].append([n, None])
                elif result[1] == "edit":
                    field = result[2]
                    idx = result[3]
                    if result[4] == "select":
                        options = result[5]
                        pos = renpy.get_mouse_pos()
                        max_rows = min(10, len(options)+1)
                        row_size = (160, 30)
                        n = renpy.call_screen("dropdown_content", options, max_rows, row_size, pos, field[idx], None, None)
                        field[idx] = n
                    elif result[4] == "int":
                        length = 20
                        try:
                            value = int(field[idx])
                        except:
                            value = 0
                        n = renpy.call_screen("pyt_input", value, "Enter a Number", length=length, size=(12*length, 150))
                        try:
                            n = int(n)
                        except:
                            n = ""
                        field[idx] = n
                elif result[1] == "remove":
                    field = result[2]
                    tagr.char_edit[field].remove(result[3])
            elif result[0] == "tagchar":
                if result[1] == "pick":
                    if tagr.tagz == tagr.oldtagz or renpy.call_screen("yesno_prompt", message="Discard your changes?", yes_action=Return(True), no_action=Return(False)):
                        tagr.select_char(result[2])
                elif result[1] == "new":
                    folder = result[2]
                    n = result[3]
                    if len(n) and len(folder):
                        msg = tagr.create_char(folder, n)
                        if not msg:
                            renpy.hide_screen("tagger_create_tagchar")
                    else:
                        msg = "Both fields are mandatory!"
                    if msg:
                        renpy.show_screen("message_screen", msg)
            elif result[0] == "control":
                if result[1] == "return":
                    break

    hide screen tagger
    with dissolve
    jump mainscreen

screen tagger_pick_tagchar:
    zorder 3
    modal True

    frame:
        background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
        align .5, .5
        style_prefix "basic"
        vbox:
            spacing 10
            hbox:
                textbutton "Chars":
                    sensitive tagr.list_group != "chars"
                    action Function(tagr.load_tag_chars, "chars")
                textbutton "RChars":
                    sensitive tagr.list_group != "rchars"
                    action Function(tagr.load_tag_chars, "rchars")
                textbutton "NPCs":
                    sensitive tagr.list_group != "npc"
                    action Function(tagr.load_tag_chars, "npc")
            vbox:
                box_wrap True
                # text "Equip For:" style "black_serpent"
                for g in tagr.all_chars.values():
                    $ ch_id = g["id"]
                    textbutton "{size=10}%s" % ch_id:
                        xalign 0.5
                        xsize 100
                        action [Hide("tagger_pick_tagchar"), Return(["tagchar", "pick", g])]
                        tooltip g.get("name", ch_id)
            hbox:
                xminimum 235
                xalign .5
                textbutton "Close":
                    xalign 0.1
                    action Hide("tagger_pick_tagchar")
                    keysym "mousedown_3", "K_ESCAPE"
                textbutton "New":
                    xalign 0.9
                    action [Hide("tagger_pick_tagchar"), Show("tagger_create_tagchar")]
                    tooltip "Create new character in the current group"

screen tagger_create_tagchar:
    zorder 3
    modal True
    default char_id = ""
    default folder = "random" if tagr.list_group == "rchars" else ("Naruto" if tagr.list_group == "chars" else "thugs")
    default mode = "id"

    frame:
        background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
        align .5, .5
        xysize (600, 200)
        style_prefix "basic"
        vbox:
            spacing 10
            hbox:
                xfill True
                vbox:
                    xalign .0
                    label u"ID:" yalign .5
                    label u"Folder:" yalign .5
                vbox:
                    xfill True
                    if mode == "id":
                        input:
                            id "id_input"
                            default char_id
                            length 50
                            xalign .97
                            style "TisaOTM"
                            size 20
                            color "ivory"
                            changed dummy_interaction_restart
                        text folder color "ivory" id "folder_input" xalign .97
                    else:
                        text char_id color "ivory" id "id_input" xalign .97
                        input:
                            id "folder_input"
                            default folder
                            length 50
                            xalign .97
                            style "TisaOTM"
                            size 20
                            color "ivory"
                            changed dummy_interaction_restart
                vbox:
                    xalign 1.0
                    xsize 20
                    xoffset -16
                    $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                    if mode == "folder":
                        imagebutton:
                            idle temp
                            hover im.MatrixColor(temp, im.matrix.brightness(.15))
                            action [SetScreenVariable("folder", renpy.get_widget("tagger_create_tagchar", "folder_input").content), SetScreenVariable("mode", "id")]
                            tooltip "Edit ID"
                    else:
                        null height 30
                        imagebutton:
                            idle temp
                            hover im.MatrixColor(temp, im.matrix.brightness(.15))
                            action [SetScreenVariable("char_id", renpy.get_widget("tagger_create_tagchar", "id_input").content), SetScreenVariable("mode", "folder")]
                            tooltip "Edit Folder"

            hbox:
                xfill True
                textbutton "Cancel":
                    xalign 0.1
                    action [Hide("tagger_create_tagchar"), Show("tagger_pick_tagchar")]
                    keysym "mousedown_3", "K_ESCAPE"
                textbutton "Create":
                    xalign 0.9
                    action Return(["tagchar", "new",
                                   folder if mode == "id" else renpy.get_widget("tagger_create_tagchar", "folder_input").content,
                                   char_id if mode == "folder" else renpy.get_widget("tagger_create_tagchar", "id_input").content])
                    tooltip "Create new character in the current group"

screen tagger_char_json_config(char):
    zorder 2
    modal True

    viewport:
        ypos 30
        xalign .5
        xysize (600, config.screen_height - 60)
        mousewheel True
        frame:
            background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
            xsize 600
            align .5, .5
            style_prefix "basic"
            vbox:
                spacing 10
                hbox:
                    xfill True
                    label u"ID:" align .0, .5
                    text char["id"] align 1.0, .5
                if "name" in char:
                    # "An ordinary local girl.",
                    hbox:
                        xfill True
                        $ temp = char["name"]
                        label u"Name:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if len(temp) <= 20:
                                    color = "ivory"
                                else:
                                    color = "red"
                                    temp += "*"
                            text temp yalign .5 color color:
                                if len(temp) > 50:
                                    size 12
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "text", "name", 100])
                                tooltip "Edit"
                if "nickname" in char:
                    # "An ordinary local girl.",
                    hbox:
                        xfill True
                        $ temp = char["nickname"]
                        label u"Nickname:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if len(temp) <= 20:
                                    color = "ivory"
                                else:
                                    color = "red"
                                    temp += "*"
                            text temp yalign .5 color color:
                                if len(temp) > 50:
                                    size 12
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "text", "nickname", 100])
                                tooltip "Edit"
                if "fullname" in char:
                    # "An ordinary local girl.",
                    hbox:
                        xfill True
                        $ temp = char["fullname"]
                        label u"Fullname:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if len(temp) <= 20:
                                    color = "ivory"
                                else:
                                    color = "red"
                                    temp += "*"
                            text temp yalign .5 color color:
                                if len(temp) > 50:
                                    size 12
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "text", "fullname", 100])
                                tooltip "Edit"
                if "desc" in char:
                    # "An ordinary local girl.",
                    hbox:
                        xfill True
                        $ temp = char["desc"]
                        label u"Desc:" align .0, .5
                        hbox:
                            xalign 1.0
                            text temp yalign .5:
                                if len(temp) > 50:
                                    size 12
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "text", "desc", 100])
                                tooltip "Edit"
                if "origin" in char:
                    # "Overwatch"
                    hbox:
                        xfill True
                        label u"Origin:" align .0, .5
                        hbox:
                            xalign 1.0
                            text char["origin"] yalign .5
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "text", "origin", 30])
                                tooltip "Edit"
                if "full_race" in char:
                    # "Human",
                    hbox:
                        xfill True
                        label u"Full race:" align .0, .5
                        hbox:
                            xalign 1.0
                            text char["full_race"] yalign .5
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "text", "full_race", 30])
                                tooltip "Edit"
                if "race" in char:
                    # "Human"
                    hbox:
                        xfill True
                        label u"Race:" align .0, .5
                        python:
                            temp = char["race"]
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            for k, v in traits.iteritems():
                                if getattr(v, "race", False):
                                    tmp[k] = k
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "race", tmp])
                                tooltip "Edit"
                if "status" in char:
                    # "average",
                    hbox:
                        xfill True
                        label u"Status:" align .0, .5
                        python:
                            temp = char["status"]
                            tmp = OrderedDict([(k, k) for k in STATIC_CHAR.STATUS])
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "status", tmp])
                                tooltip "Edit"
                if "gender" in char:
                    # "average",
                    hbox:
                        xfill True
                        label u"Gender:" align .0, .5
                        python:
                            temp = char["gender"]
                            tmp = OrderedDict([("male", "male"), ("female", "female")])
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "gender", tmp])
                                tooltip "Edit"
                if "height" in char:
                    # "average",
                    hbox:
                        xfill True
                        label u"Height:" align .0, .5
                        python:
                            temp = char["height"]
                            tmp = OrderedDict([("short", "short"), ("average", "average"), ("tall", "tall")])
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "height", tmp])
                                tooltip "Edit"
                if "color" in char:
                    # "seagreen",
                    hbox:
                        xfill True
                        label u"Color:" align .0, .5
                        python:
                            colors = _COLORS_.keys()
                            colors.sort()
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            for k in colors:
                                tmp[k] = k
                            temp = char["color"]
                            if temp in tmp:
                                color = temp or "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "color", tmp])
                                tooltip "Edit"
                if "what_color" in char:
                    # "seagreen",
                    hbox:
                        xfill True
                        label u"What color:" align .0, .5
                        python:
                            colors = _COLORS_.keys()
                            colors.sort()
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            for k in colors:
                                tmp[k] = k
                            temp = char["what_color"]
                            if temp in tmp:
                                color = temp or "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "what_color", tmp])
                                tooltip "Edit"
                if "location" in char:
                    # "city"
                    hbox:
                        xfill True
                        label u"Location:" align .0, .5
                        python:
                            temp = char["location"]
                            locs = [k["id"] for k in OnScreenMap()("pytfall")]
                            locs.sort()
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            for k in locs:
                                tmp[k] = k
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "location", tmp])
                                tooltip "Edit"
                if "tier" in char:
                    # 2.5
                    hbox:
                        xfill True
                        $ temp = char["tier"]
                        label u"Tier:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if not temp or (isinstance(temp, (int, float)) and 0 <= temp <= MAX_TIER):
                                    color = "ivory"
                                    temp = str(temp)
                                else:
                                    color = "red"
                                    temp = "%s*" % temp
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "float", "tier"])
                                tooltip "Edit"
                if "gold" in char:
                    # 111
                    hbox:
                        xfill True
                        $ temp = char["gold"]
                        label u"Gold:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if not temp or (isinstance(temp, int) and temp >= 0):
                                    color = "ivory"
                                    temp = str(temp)
                                else:
                                    color = "red"
                                    temp = "%s*" % temp
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "int", "gold"])
                                tooltip "Edit"
                if "item_up" in char:
                    # "average",
                    hbox:
                        xfill True
                        label u"Initial Items:" align .0, .5
                        python:
                            temp = char["item_up"]
                            tmp = OrderedDict([(True, "True"), (False, "False"), ("auto", "auto")])
                            if temp in tmp:
                                color = "ivory"
                                temp = str(temp)
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "item_up", tmp])
                                tooltip "Edit"
                if "arena_willing" in char:
                    # boolean
                    hbox:
                        xfill True
                        label u"Arena willing:" align .0, .5
                        hbox:
                            xalign 1.0
                            textbutton str(char["arena_willing"]):
                                yalign .5
                                action Return(["json", "bool", "arena_willing"])
                if "body" in char:
                    # "Athletic"
                    hbox:
                        xfill True
                        label u"Body:" align .0, .5
                        python:
                            temp = char["body"]
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            for k, v in traits.iteritems():
                                if getattr(v, "body", False):
                                    tmp[k] = k
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "body", tmp])
                                tooltip "Edit"
                if "breasts" in char and char.get("gender", "female") == "female":
                    # "Average Boobs"
                    hbox:
                        xfill True
                        label u"Breasts:" align .0, .5
                        python:
                            temp = char["breasts"]
                            tmp = OrderedDict()
                            for k, v in traits.iteritems():
                                if getattr(v, "gents", False) and getattr(v, "gender", "female") == "female":
                                    tmp[k] = k
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "breasts", tmp])
                                tooltip "Edit"
                if "penis" in char and char.get("gender", "male") == "male":
                    # "Average Dick"
                    hbox:
                        xfill True
                        label u"Penis:" align .0, .5
                        python:
                            temp = char["penis"]
                            tmp = OrderedDict()
                            for k, v in traits.iteritems():
                                if getattr(v, "gents", False) and getattr(v, "gender", "male") == "male":
                                    tmp[k] = k
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "penis", tmp])
                                tooltip "Edit"
                if "personality" in char:
                    # "Yandere"
                    hbox:
                        xfill True
                        label u"Personality:" align .0, .5
                        python:
                            temp = char["personality"]
                            personalities = []
                            for k, v in traits.iteritems():
                                if getattr(v, "personality", False):
                                    personalities.append(k)
                            personalities.sort()
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            for k in personalities:
                                tmp[k] = k
                            if temp in tmp:
                                color = "ivory"
                            else:
                                color = "red"
                                temp += "*"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "personality", tmp])
                                tooltip "Edit"
                if "basetraits" in char:
                    # "Healer"
                    hbox:
                        label u"Base-traits:" align .0, .5
                        vbox:
                            xfill True
                            python:
                                basetraits = []
                                for k, v in traits.iteritems():
                                    if getattr(v, "basetrait", False) and not getattr(v, "mob_only", False):
                                        basetraits.append(k)
                                basetraits.sort()
                                tmp = OrderedDict([(k, k) for k in basetraits])
                            for t in char["basetraits"]:
                                $ color = "ivory" if t in basetraits else "red"
                                hbox:
                                    xalign 1.0
                                    text t yalign .5 color color
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/discard.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "remove", "basetraits", t])
                                        tooltip "Remove"
                            $ temp = ProportionalScale("content/gfx/interface/buttons/add.png", 20, 20)
                            imagebutton:
                                xalign 1.0
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "add", "text", "basetraits", tmp])
                                tooltip "Add"
                if "elements" in char:
                    # "Fire"
                    hbox:
                        label u"Elements:" align .0, .5
                        vbox:
                            xfill True
                            python:
                                elements = []
                                for k, v in traits.iteritems():
                                    if getattr(v, "elemental", False):
                                        elements.append(k)
                                elements.sort()
                                tmp = OrderedDict([(k, k) for k in elements])
                            for t in char["elements"]:
                                $ color = "ivory" if t in elements else "red"
                                hbox:
                                    xalign 1.0
                                    text t yalign .5 color color
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/discard.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "remove", "elements", t])
                                        tooltip "Remove"
                            $ temp = ProportionalScale("content/gfx/interface/buttons/add.png", 20, 20)
                            imagebutton:
                                xalign 1.0
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "add", "text", "elements", tmp])
                                tooltip "Add"
                if "traits" in char:
                    # "Fire"
                    hbox:
                        label u"Traits:" align .0, .5
                        vbox:
                            xfill True
                            python:
                                std_traits = []
                                for k, v in traits.iteritems():
                                    if getattr(v, "elemental", False):
                                        continue
                                    if getattr(v, "basetrait", False):
                                        continue
                                    if getattr(v, "personality", False):
                                        continue
                                    if getattr(v, "gents", False):
                                        continue
                                    if getattr(v, "body", False):
                                        continue
                                    if getattr(v, "race", False):
                                        continue
                                    if getattr(v, "mob_only", False):
                                        continue
                                    if getattr(v, "MC_only_trait", False):
                                        continue
                                    std_traits.append(k)
                                std_traits.sort()
                                tmp = OrderedDict([(k, k) for k in std_traits])
                            for t in char["traits"]:
                                $ color = "ivory" if t in std_traits else "red"
                                hbox:
                                    xalign 1.0
                                    text t yalign .5 color color
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/discard.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "remove", "traits", t])
                                        tooltip "Remove"
                            $ temp = ProportionalScale("content/gfx/interface/buttons/add.png", 20, 20)
                            imagebutton:
                                xalign 1.0
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "add", "text", "traits", tmp])
                                tooltip "Add"
                if "random_traits" in char:
                    # ["Long Legs", 20], ...
                    hbox:
                        label u"Random traits:" align .0, .5
                        vbox:
                            xfill True
                            python:
                                rnd_traits = []
                                gender = char.get("gender", "female")
                                for k, v in traits.iteritems():
                                    if getattr(v, "basetrait", False):
                                        continue
                                    if getattr(v, "gents", False):
                                        continue
                                    if getattr(v, "race", False):
                                        continue
                                    if getattr(v, "mob_only", False):
                                        continue
                                    if getattr(v, "MC_only_trait", False):
                                        continue
                                    if getattr(v, "gender", gender) != gender:
                                        continue
                                    if getattr(v, "personality", False):
                                        type = 0
                                    elif getattr(v, "elemental", False):
                                        type = 1
                                    elif getattr(v, "body", False):
                                        type = 2
                                    elif getattr(v, "character_trait", False):
                                        type = 3
                                    else:
                                        type = 4
                                    rnd_traits.append((k, type))
                                rnd_traits.sort(key=itemgetter(1))
                                tmp = OrderedDict([(k, k) for k, t in rnd_traits])
                            for t in char["random_traits"]:
                                $ trait, chance = t
                                $ color = "ivory" if (trait in tmp and (not chance or isinstance(chance, int))) else "red"
                                hbox:
                                    xalign 1.0
                                    text ("%s:" % trait) yalign .5 color color
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "edit", t, 0, "select", tmp])
                                        tooltip "Edit"
                                    text str(chance) yalign .5 color color
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "edit", t, 1, "int"])
                                        tooltip "Edit"
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/discard.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "remove", "random_traits", t])
                                        tooltip "Remove"
                            $ temp = ProportionalScale("content/gfx/interface/buttons/add.png", 20, 20)
                            imagebutton:
                                xalign 1.0
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "add", "pair", "random_traits", tmp])
                                tooltip "Add"

                if "default_attack_skill" in char:
                    # "Fist Attack"
                    hbox:
                        xfill True
                        label u"Default Attack:" align .0, .5
                        python:
                            temp = char["default_attack_skill"]
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            attacks = []
                            for k, s in battle_skills.iteritems():
                                if getattr(s, "mob_only", False):
                                    continue
                                if s.delivery == "status" or "healing" in s.attributes or s.kind == "revival":
                                    continue
                                elif s.delivery == "magic":
                                    continue
                                attacks.append(k)
                            attacks.sort()
                            for k in attacks:
                                tmp[k] = k
                            color = "ivory" if temp in tmp else "red"
                        hbox:
                            xalign 1.0
                            text temp yalign .5 color color
                            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
                            imagebutton:
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "select", "default_attack_skill", tmp])
                                tooltip "Edit"
                if "magic_skills" in char:
                    # "city"
                    hbox:
                        label u"Magic skills:" align .0, .5
                        vbox:
                            xfill True
                            python:
                                magics = []
                                for k, s in battle_skills.iteritems():
                                    if getattr(s, "mob_only", False) or getattr(s, "item_only", False):
                                        continue
                                    if s.delivery == "status" or "healing" in s.attributes or s.kind == "revival":
                                        pass
                                    elif s.delivery == "magic":
                                        pass
                                    else:
                                        continue
                                    magics.append(k)
                                magics.sort()
                                tmp = OrderedDict([(k, k) for k in magics])
                            for t in char["magic_skills"]:
                                $ color = "ivory" if t in magics else "red"
                                hbox:
                                    xalign 1.0
                                    text t yalign .5 color color
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/discard.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "remove", "magic_skills", t])
                                        tooltip "Remove"
                            $ temp = ProportionalScale("content/gfx/interface/buttons/add.png", 20, 20)
                            imagebutton:
                                xalign 1.0
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "add", "text", "magic_skills", tmp])
                                tooltip "Add"

                hbox:
                    xfill True
                    textbutton "Cancel":
                        xalign .2
                        action Hide("tagger_char_json_config")
                        keysym "mousedown_3", "K_ESCAPE"

                    textbutton "Save":
                        xalign .8
                        action [Hide("tagger_char_json_config"), Function(tagr.save_json)]

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
            action Show("tagger_pick_tagchar")
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
        textbutton ("%d." % tagr.imagespage):
            xysize 32, 16
            background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
            text_color "cadetblue"
            xalign .5
            ypos 25
            text_size 12
            text_align .5, .5
            action Return(["refresh"])
            tooltip "Click to refresh the list"
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
                $ tmp = tagr.tagsmap
                for tag in temp:
                    python:
                        color = tmp[tag][1]
                        if isinstance(color, basestring):
                            outlines = None
                        else:
                            outlines = color[1]
                            color = color[0]
                    textbutton tag:
                        xysize (150, 18)
                        #style "white_cry_button"
                        action Function(temp.remove, tag)
                        text_color color #"lime"
                        text_size 14
                        text_layout "nobreak"
                        if outlines is not None:
                            text_outlines [(2, outlines, 0, 0)]
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
            $ tmp = tagr.tagsmap
            for tag in tagr.tag_options:
                python:
                    color = tmp[tag][1]
                    if isinstance(color, basestring):
                        outlines = None
                    else:
                        outlines = color[1]
                        color = color[0]
                textbutton tag:
                    xysize (150, 18)
                    #style "white_cry_button"
                    if tag in temp:
                        action Function(temp.remove, tag)
                        text_color "lime"
                        text_outlines [(2, "black", 0, 0)]
                    else:
                        action Function(temp.append, tag)
                        text_color color
                        if outlines is not None:
                            text_outlines [(2, outlines, 0, 0)]
                    text_size 14
                    text_layout "nobreak"
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
                        xysize (150, 18)
                        #style "white_cry_button"
                        if tg in tagr.selected_groups:
                            action Function(tagr.remove_tag_group, tg)
                        else:
                            action Function(tagr.select_tag_group, tg)
                        text_color color
                        text_size 14
                        text_layout "nobreak"
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
        textbutton "JSON":
            xysize (150, 30)
            action Return(["edit_json"])
            tooltip "Show JSON config of the character"

    use exit_button(size=(20, 20), action=tagr.return_action)
    key "K_ESCAPE" action tagr.return_action
