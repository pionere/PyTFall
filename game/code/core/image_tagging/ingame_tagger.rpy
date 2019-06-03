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

            if result[0] == "select_image":
                next_image = result[1]
                if tagr.tagz != tagr.oldtagz:
                    choice = renpy.call_screen("tagger_navigation_prompt")
                    if choice == "cancel":
                        continue
                    if choice == "save":
                        tagr.save_image()
                tagr.select_image(next_image)

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
                if tagr.tagz != tagr.oldtagz:
                    choice = renpy.call_screen("tagger_navigation_prompt")
                    if choice == "cancel":
                        continue
                    if choice == "save":
                        tagr.save_image()
                tagr.load_tag_chars(tagr.char_group)
                tagr.select_char(tagr.char)

            elif result[0] == "generate_ids":
                if tagr.tagz != tagr.oldtagz:
                    choice = renpy.call_screen("tagger_navigation_prompt")
                    if choice == "cancel":
                        continue
                    if choice == "save":
                        tagr.save_image()
                    else:
                        tagr.tagz = tagr.oldtagz[:]
                if renpy.call_screen("yesno_prompt", message="This will prefix all images of the char with a generated ID.\n(Existing IDs with matching length are preserved)\nProceed?", yes_action=Return(True), no_action=Return(False)):
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
                    n = renpy.call_screen("pyt_input", tagr.char_edit[field], "Enter Text", length=length, size=(12*length, 150))
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
                        if len(options) == 1:
                            tagr.char_edit[field].append(options[0])
                        else:
                            pos = renpy.get_mouse_pos()
                            max_rows = min(10, len(options)+1)
                            row_size = (160, 30)
                            n = renpy.call_screen("dropdown_content", options, max_rows, row_size, pos, undefined, None, None)
                            if n is not undefined:
                                if isinstance(field, basestring):
                                    tagr.char_edit[field].append([n, None])
                                else:
                                    field.append([n, None])
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
                    elif result[4] == "text":
                        length = result[5]
                        n = renpy.call_screen("pyt_input", field[idx], "Enter Text", length=length, size=(12*length, 150))
                        field[idx] = n
                elif result[1] == "remove":
                    field = result[2]
                    tagr.char_edit[field].remove(result[3])
            elif result[0] == "tagchar":
                if result[1] == "pick":
                    next_char = result[2]
                    if tagr.tagz != tagr.oldtagz:
                        choice = renpy.call_screen("tagger_navigation_prompt")
                        if choice == "cancel":
                            continue
                        if choice == "save":
                            tagr.save_image()
                    tagr.select_char(next_char)
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

screen tagger_navigation_prompt:
    zorder 3
    modal True

    # Get mouse coords:
    python:
        x, y = renpy.get_mouse_pos()
        if y > config.screen_height/2:
            yval = 1.0
        else:
            #y += row_size[1]
            yval = .0

    frame:
        background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
        xmargin 0
        padding 5, 5
        pos (x, y)
        yanchor yval
        style_prefix "basic"
        vbox:
            spacing 10
            text u"The image has been modified. What do you want to do?" color "ivory"
            hbox:
                xalign .5
                xsize 200
                spacing 10
                textbutton "Cancel":
                    text_size 16
                    style "basic_choice2_button"
                    action Return("cancel")
                    keysym "mousedown_3", "K_ESCAPE"
                textbutton "Discard changes":
                    text_layout "nobreak"
                    text_size 16
                    style "basic_choice2_button"
                    action Return("discard")
                textbutton "Save changes":
                    text_layout "nobreak"
                    text_size 16
                    style "basic_choice2_button"
                    action Return("save")

screen tagger_pick_tagchar:
    zorder 3
    modal True

    default genders = [None, "male", "female"]
    default gender_icons = ["content/gfx/interface/icons/both.png",
                            "content/gfx/interface/icons/male.png",
                            "content/gfx/interface/icons/female.png"]
    $ group = tagr.list_group
    $ gender = tagr.list_gender
    frame:
        background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
        xalign .5
        ypos 20
        style_prefix "basic"
        vbox:
            hbox:
                xalign .5
                textbutton "Chars":
                    sensitive group != "chars"
                    selected group == "chars"
                    action Function(tagr.load_tag_chars, "chars")
                textbutton "RChars":
                    sensitive group != "rchars"
                    selected group == "rchars"
                    action Function(tagr.load_tag_chars, "rchars")
                textbutton "NPCs":
                    sensitive group != "npcs"
                    selected group == "npcs"
                    action Function(tagr.load_tag_chars, "npcs")
                textbutton "Fighters":
                    sensitive group != "fighters"
                    selected group == "fighters"
                    action Function(tagr.load_tag_chars, "fighters")
            null height 5
            hbox:
                xminimum 235
                xalign .5
                # Gender filter
                python:
                    index = genders.index(gender)
                    next_gender = genders[(index + 1) % len(genders)]
                    img = ProportionalScale(gender_icons[index], 30, 30)
                imagebutton:
                    xalign .5
                    action SetField(tagr, "list_gender", next_gender)
                    idle img
                    hover im.MatrixColor(img, im.matrix.brightness(.15))
            null height 10
            $ all_chars = tagr.all_chars.values()
            if gender is not None:
                $ all_chars = [c for c in all_chars if c.get("gender", "female") == gender]
            $ all_chars.sort(key=lambda x: x.get("name", x["id"]))
            vpgrid:
                rows 25
                xalign .5
                mousewheel True
                for char in all_chars:
                    python:
                        temp = str(char["id"])
                        if len(temp) > 16:
                            tmp = temp[0:14] + "..."
                        else:
                            tmp = temp
                    textbutton tmp:
                        xsize 120
                        text_size 12
                        text_layout "nobreak"
                        action [Hide("tagger_pick_tagchar"), Return(["tagchar", "pick", char])]
                        tooltip char.get("name", temp)
            null height 10
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
    default folder = tagr.base_folder()
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

screen tagger_json_dropdown(char, field, options, label=None):
    python:
        value = char[field]
        if value in options:
            if field in ["color", "what_color"] and value:
                color = value
            else:
                color = "ivory"
                value = str(value)
        else:
            color = "red"
            value = "%s*" % value
        if label is None:
            label = u"%s:" % field.capitalize()
    hbox:
        xfill True
        label label align .0, .5
        hbox:
            xalign 1.0
            textbutton value:
                yalign .5
                text_color color
                background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                hover_background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                action Return(["json", "select", field, options])
            $ temp = ProportionalScale("content/gfx/interface/buttons/edit.png", 20, 20)
            imagebutton:
                idle temp
                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                action Return(["json", "text", field, 30])
                tooltip "Edit"

screen tagger_char_json_config(char):
    zorder 2
    modal True

    $ gender = char.get("gender", "female")
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
                    # "Da Name",
                    hbox:
                        xfill True
                        $ temp = char["name"]
                        label u"Name:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if isinstance(temp, basestring) and len(temp) <= 20:
                                    color = "ivory"
                                else:
                                    color = "red"
                                    temp = "%s*" % temp
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
                    # "von Name",
                    hbox:
                        xfill True
                        $ temp = char["nickname"]
                        label u"Nickname:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if isinstance(temp, basestring) and len(temp) <= 20:
                                    color = "ivory"
                                else:
                                    color = "red"
                                    temp = "%s*" % temp
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
                    # "of Name",
                    hbox:
                        xfill True
                        $ temp = char["fullname"]
                        label u"Fullname:" align .0, .5
                        hbox:
                            xalign 1.0
                            python:
                                if isinstance(temp, basestring) and len(temp) <= 20:
                                    color = "ivory"
                                else:
                                    color = "red"
                                    temp = "%s*" % temp
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
                    python:
                        tmp = OrderedDict()
                        tmp[""] = "None"
                        for k, v in traits.iteritems():
                            if getattr(v, "race", False):
                                tmp[k] = k
                    use tagger_json_dropdown(char, "race", tmp)
                if "status" in char:
                    # "free",
                    $ tmp = OrderedDict([(k, k) for k in STATIC_CHAR.STATUS])
                    use tagger_json_dropdown(char, "status", tmp)
                if "gender" in char:
                    # "female",
                    $ tmp = OrderedDict([("male", "male"), ("female", "female")])
                    use tagger_json_dropdown(char, "gender", tmp)
                if "height" in char:
                    # "average",
                    $ tmp = OrderedDict([("short", "short"), ("average", "average"), ("tall", "tall")])
                    use tagger_json_dropdown(char, "height", tmp)
                $ colors = None
                if "color" in char:
                    # "seagreen",
                    python:
                        colors = _COLORS_.keys()
                        colors.sort()
                        tmp = OrderedDict()
                        tmp[""] = "None"
                        for k in colors:
                            tmp[k] = k
                    use tagger_json_dropdown(char, "color", tmp)
                if "what_color" in char:
                    # "seagreen",
                    python:
                        if colors is None:
                            colors = _COLORS_.keys()
                            colors.sort()
                            tmp = OrderedDict()
                            tmp[""] = "None"
                            for k in colors:
                                tmp[k] = k
                    use tagger_json_dropdown(char, "what_color", tmp)
                if "location" in char:
                    # "city"
                    python:
                        locs = [k["id"] for k in OnScreenMap()("pytfall")]
                        locs.sort()
                        tmp = OrderedDict()
                        tmp[""] = "None"
                        for k in locs:
                            tmp[k] = k
                    use tagger_json_dropdown(char, "location", tmp)
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
                    # boolean,
                    $ tmp = OrderedDict([(True, "True"), (False, "False"), ("", "None")])
                    use tagger_json_dropdown(char, "item_up", tmp, "Initial Items:")
                if "arena_willing" in char:
                    # boolean
                    $ tmp = OrderedDict([(True, "True"), (False, "False"), ("", "None")])
                    use tagger_json_dropdown(char, "arena_willing", tmp)
                if "front_row" in char:
                    # boolean
                    $ tmp = OrderedDict([(1, "True"), (0, "False"), ("", "None")])
                    use tagger_json_dropdown(char, "front_row", tmp)
                if "body" in char:
                    # "Athletic"
                    python:
                        temp = []
                        for k, v in traits.iteritems():
                            if getattr(v, "body", False):
                                temp.append(k)
                        temp.sort()
                        tmp = OrderedDict()
                        tmp[""] = "None"
                        for k in temp:
                            tmp[k] = k
                    use tagger_json_dropdown(char, "body", tmp)
                if "breasts" in char and gender == "female":
                    # "Average Boobs"
                    python:
                        temp = []
                        for k, v in traits.iteritems():
                            if getattr(v, "gents", False) and getattr(v, "gender", "female") == "female":
                                temp.append(k)
                        temp.sort()
                        tmp = OrderedDict([(k, k) for k in temp])
                    use tagger_json_dropdown(char, "breasts", tmp)
                if "penis" in char and gender == "male":
                    # "Average Dick"
                    python:
                        temp = []
                        for k, v in traits.iteritems():
                            if getattr(v, "gents", False) and getattr(v, "gender", "male") == "male":
                                temp.append(k)
                        temp.sort()
                        tmp = OrderedDict([(k, k) for k in temp])
                    use tagger_json_dropdown(char, "penis", tmp)
                if "personality" in char:
                    # "Yandere"
                    python:
                        temp = []
                        for k, v in traits.iteritems():
                            if getattr(v, "personality", False):
                                temp.append(k)
                        temp.sort()
                        tmp = OrderedDict()
                        tmp[""] = "None"
                        for k in temp:
                            tmp[k] = k
                    use tagger_json_dropdown(char, "personality", tmp)
                if "basetraits" in char:
                    # "Healer"
                    hbox:
                        label u"Base-traits:" align .0, .0
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
                        label u"Elements:" align .0, .0
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
                        label u"Traits:" align .0, .0
                        vbox:
                            xfill True
                            python:
                                std_traits = []
                                for k, v in traits.iteritems():
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
                                    if getattr(v, "MC_trait", False):
                                        continue
                                    if getattr(v, "gender", gender) != gender:
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
                if "random_trait_groups" in char:
                    # [[[1, 5], ["Water", "Light", "Air"]], ...]
                    hbox:
                        label u"Random trait groups:" align .0, .0
                        vbox:
                            xfill True
                            spacing 2
                            python:
                                rnd_traits = []
                                for k, v in traits.iteritems():
                                    if getattr(v, "gents", False):
                                        continue
                                    if getattr(v, "body", False):
                                        continue
                                    if getattr(v, "race", False):
                                        continue
                                    if getattr(v, "mob_only", False):
                                        continue
                                    if getattr(v, "MC_trait", False):
                                        continue
                                    if getattr(v, "gender", gender) != gender:
                                        continue
                                    if getattr(v, "basetrait", False):
                                        type = 0
                                    elif getattr(v, "personality", False):
                                        type = 1
                                    elif getattr(v, "elemental", False):
                                        type = 2
                                    elif getattr(v, "character_trait", False):
                                        type = 3
                                    else:
                                        type = 4
                                    rnd_traits.append((k, type))
                                rnd_traits.sort(key=lambda x: (x[1], x[0]))
                                tmp = OrderedDict([(k, k) for k, t in rnd_traits])
                            for rtg in char["random_trait_groups"]:
                                python:
                                    interval, random_traits = rtg
                                    interval_from, interval_to = interval
                                    if isinstance(interval_from, int) and 0 <= interval_from <= len(random_traits):
                                        interval_from_color = "ivory"
                                    else:
                                        interval_from_color = "red"
                                        interval_from = "%s*" % interval_from
                                    if isinstance(interval_to, int):
                                        if interval_from > interval_to:
                                            interval_from_color = "red"
                                            interval_from = "%s*" % interval_from
                                        if interval_to <= len(random_traits):
                                            interval_to_color = "ivory"
                                        else:
                                            interval_to_color = "red"
                                            interval_to = "%s*" % interval_to
                                    else:
                                        interval_to_color = "red"
                                        interval_to = "%s*" % interval_to
                                hbox:
                                    xalign 1.0
                                    textbutton str(interval_from):
                                        yalign .0
                                        text_color interval_from_color
                                        background Null()
                                        hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                                        action Return(["json", "edit", interval, 0, "int"])
                                    text "-" color "ivory" yalign .0
                                    textbutton str(interval_to):
                                        yalign .0
                                        text_color interval_to_color
                                        background Null()
                                        hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                                        action Return(["json", "edit", interval, 1, "int"])
                                    $ temp = ProportionalScale("content/gfx/interface/buttons/discard.png", 20, 20)
                                    imagebutton:
                                        idle temp
                                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                        action Return(["json", "remove", "random_trait_groups", rtg])
                                        tooltip "Remove"
                                    vbox:
                                        for t in random_traits:
                                            $ trait, chance = t
                                            $ trait_color = "ivory" if trait in tmp else "red"
                                            $ chance_color = "ivory" if isinstance(chance, int) else "red"
                                            hbox:
                                                xalign 1.0
                                                textbutton trait:
                                                    #yalign .5
                                                    text_color trait_color
                                                    background Null()
                                                    hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                                                    action Return(["json", "edit", t, 0, "select", tmp])
                                                text ":" color "ivory" yalign .5
                                                textbutton str(chance):
                                                    #yalign .5
                                                    xminimum 40
                                                    #margin 0, 0
                                                    #padding 0, 0
                                                    text_color chance_color
                                                    text_align 1.0, .5
                                                    background Null()
                                                    hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                                                    action Return(["json", "edit", t, 1, "int"])
                                                $ temp = ProportionalScale("content/gfx/interface/buttons/discard.png", 20, 20)
                                                imagebutton:
                                                    idle temp
                                                    hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                                    action Function(random_traits.remove, t)
                                                    tooltip "Remove"
                                        $ temp = ProportionalScale("content/gfx/interface/buttons/add.png", 20, 20)
                                        imagebutton:
                                            xalign 1.0
                                            idle temp
                                            hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                            action Return(["json", "add", "pair", random_traits, tmp])
                                            tooltip "Add"
                            $ temp = ProportionalScale("content/gfx/interface/buttons/add.png", 20, 20)
                            imagebutton:
                                xalign .5
                                idle temp
                                hover im.MatrixColor(temp, im.matrix.brightness(.15))
                                action Return(["json", "add", "pair", "random_trait_groups", [[[0, 0], []]]])
                                tooltip "Add"

                if "random_traits" in char:
                    # ["Long Legs", 20], ...
                    hbox:
                        label u"Random traits:" align .0, .0
                        vbox:
                            xfill True
                            python:
                                rnd_traits = []
                                for k, v in traits.iteritems():
                                    if getattr(v, "basetrait", False):
                                        continue
                                    if getattr(v, "gents", False):
                                        continue
                                    if getattr(v, "body", False):
                                        continue
                                    if getattr(v, "race", False):
                                        continue
                                    if getattr(v, "mob_only", False):
                                        continue
                                    if getattr(v, "MC_trait", False):
                                        continue
                                    if getattr(v, "gender", gender) != gender:
                                        continue
                                    if getattr(v, "personality", False):
                                        type = 0
                                    elif getattr(v, "elemental", False):
                                        type = 1
                                    elif getattr(v, "character_trait", False):
                                        type = 2
                                    else:
                                        type = 3
                                    rnd_traits.append((k, type))
                                rnd_traits.sort(key=lambda x: (x[1], x[0]))
                                tmp = OrderedDict([(k, k) for k, t in rnd_traits])
                            for t in char["random_traits"]:
                                $ trait, chance = t
                                $ trait_color = "ivory" if trait in tmp else "red"
                                $ chance_color = "ivory" if isinstance(chance, int) else "red"
                                hbox:
                                    xalign 1.0
                                    textbutton trait:
                                        yalign .5
                                        text_color trait_color
                                        background Null()
                                        hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                                        action Return(["json", "edit", t, 0, "select", tmp])
                                    text ":" color "ivory" yalign .5
                                    textbutton str(chance):
                                        yalign .5
                                        xminimum 40
                                        margin 0, 0
                                        padding 0, 0
                                        text_color chance_color
                                        text_align 1.0, .5
                                        background Null()
                                        hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                                        action Return(["json", "edit", t, 1, "int"])
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
                    python:
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
                        tmp = OrderedDict()
                        tmp[""] = "None"
                        for k in attacks:
                            tmp[k] = k
                    use tagger_json_dropdown(char, "default_attack_skill", tmp, "Default Attack:")
                if "magic_skills" in char:
                    # "city"
                    hbox:
                        label u"Magic skills:" align .0, .0
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
        xysize (150, 50)
        python:
            tmp = "{i}Click to select another character{/i}"
            if tagr.char is None:
                temp = "Pick Char"
            else:
                temp = tagr.char["id"]
                tmp = "{b}%s{/b}\nImage folder: {a}%s{/a}\n%s" % (temp, tagr.char["_path_to_imgfolder"], tmp)
                if len(temp) > 12:
                    temp = temp[0:10] + "..."
        textbutton temp:
            xysize (150, 30)
            xalign .5
            text_size 18
            text_align .5, .5
            text_layout "nobreak"
            action Show("tagger_pick_tagchar")
            style "main_screen_3_button"
            tooltip tmp

        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow_left.png", 30, 18)
        imagebutton:
            xalign 0.1
            ypos 35
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(0.15))
            action Function(tagr.previous_page)
            sensitive len(tagr.images) > tagr.pagesize
            tooltip "Previous Page"
        textbutton str(tagr.imagespage):
            xysize 32, 22
            background Frame("content/gfx/frame/mes11.webp", 1, 1)
            hover_background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
            text_color "cadetblue"
            xalign .5
            ypos 33
            text_size 16
            text_offset 0, 2
            action Return(["refresh"])
            tooltip "{i}Click to refresh the list{/i}"
        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow_right.png", 30, 18)
        imagebutton:
            xalign .9
            ypos 35
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(0.15))
            action Function(tagr.next_page)
            sensitive len(tagr.images) > tagr.pagesize
            tooltip "Next Page"

    # images:
    viewport:
        ypos 60
        xysize (150, config.screen_height - 85)
        mousewheel True
        style_prefix "basic"
        has vbox xfill True spacing 1
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
                    xysize (145, 20)
                    xalign .5
                    text_size 14
                    text_hover_color "crimson"
                    hover_background Frame("content/gfx/frame/frame_gp.webp", 1, 1)
                    if temp == img:
                        background Frame("content/gfx/frame/mes12.jpg", 1, 1)
                        text_color "orange"
                        action Return(["rename"])
                        tooltip fn + "\n{i}Click to rename{/i}"
                    else:
                        background Frame("content/gfx/frame/mes11.webp", 1, 1)
                        text_color "ivory"
                        action Return(["select_image", img])
                        tooltip fn

    # generate ids
    fixed:
        ypos (config.screen_height - 25)
        textbutton "Generate IDs":
            xysize (150, 25)
            text_size 16
            sensitive tagr.images
            background Null()
            hover_background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
            text_color "tomato"
            action Return(["generate_ids"])
            tooltip "Generate IDs for the images of the character"

    if tagr.pic:
        # Picture:
        fixed:
            xpos 152
            xysize (config.screen_width - 152, config.screen_height)
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
                        hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)

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
                    hover_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)

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
                        selected_background Frame("content/gfx/interface/buttons/choice_buttons2h.png", 5, 5)
                        hover_background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
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
                tmp = "{i}Click to Show Tags{/i}"
            elif show_tags == 1:
                temp = "Tags"
                tmp = "{i}Click to Show Groups{/i}"
            elif show_tags == 2:
                temp = "Groups"
                tmp = "{i}Click to Show Tags&Groups{/i}"
            else:
                temp = "Tags&Groups"
                tmp = "{i}Click to Hide Tags&Groups{/i}"
        textbutton temp:
            xysize (150, 30)
            sensitive tagr.pic is not None
            action SetScreenVariable("show_tags", (show_tags+1)%4)
            tooltip tmp
        textbutton "Save image":
            xysize (150, 30)
            sensitive tagr.pic is not None and (tagr.tagz != tagr.oldtagz or not tagr.is_valid(tagr.pic))
            action Function(tagr.save_image)
        textbutton "JSON":
            xysize (150, 30)
            action Return(["edit_json"])
            tooltip "Show JSON config of the character"

    use exit_button(size=(24, 24), action=tagr.return_action)
    key "K_ESCAPE" action tagr.return_action
