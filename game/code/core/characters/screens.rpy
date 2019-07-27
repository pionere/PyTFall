screen set_action_dropdown(char, pos=()):
    # Trying to create a drop down screen with choices of actions:
    zorder 3
    modal True

    key "mousedown_4" action NullAction()
    key "mousedown_5" action NullAction()

    # Get mouse coords:
    python:
        x, y = pos
        xval = 1.0 if x > config.screen_width/2 else .0
        yval = 1.0 if y > config.screen_height/2 else .0

    frame:
        style_prefix "dropdown_gm"
        pos (x, y)
        anchor (xval, yval)
        has vbox

        if char.action == StudyingTask:
            textbutton "Change Course":
                action [Hide("set_action_dropdown"),
                        If(renpy.get_screen("chars_list"),
                          true=[SetVariable("the_chosen", [char]), Hide("chars_list")],
                          false=[Hide("char_profile")]), 
                        Jump("school_training")]
                tooltip "Change the training course to a different one."
            textbutton "Stop Course":
                action [Function(char.set_task, None),
                        Hide("set_action_dropdown"), With(Dissolve(0.1))]
                tooltip "Call your worker back from the Academy."
        elif char.action in [RestTask, AutoRestTask]:
            $ jobs = char.get_valid_jobs()
            for i in jobs:
                textbutton "[i.id]":
                    action [Function(char.set_job, i),
                            Hide("set_action_dropdown"), With(Dissolve(0.1))]
                    selected char.job == i
                    tooltip "Do [i.id] after rest."
            textbutton "None":
                action [Function(char.set_job, None),
                        Hide("set_action_dropdown"), With(Dissolve(0.1))]
                tooltip "Stop doing anything after rest."
            textbutton "Back To Work":
                action [Function(char.set_task, None),
                        Hide("set_action_dropdown"), With(Dissolve(0.1))]
                tooltip "Call your worker back from resting."
        else:
            $ jobs = char.get_valid_jobs()
            for i in jobs:
                textbutton "[i.id]":
                    action [Function(char.set_job, i),
                            Hide("set_action_dropdown"), With(Dissolve(0.1))]
                    selected char.job == i
                    tooltip i.desc
            if char != hero: # Rest is not really useful for MC, which player controls.
                textbutton "Rest":
                    action [Function(char.set_task, RestTask),
                            Hide("set_action_dropdown"), With(Dissolve(0.1))]
                    tooltip "To prevent overworking..."
            textbutton "None":
                action [Function(char.set_job, None),
                        Hide("set_action_dropdown"), With(Dissolve(0.1))]
                tooltip "In case you are in a great need of a slacker..."

        textbutton "Close":
            action [Hide("set_action_dropdown"), With(Dissolve(0.1))]
            keysym "mousedown_3", "K_ESCAPE"

screen set_workplace_dropdown(char, pos=()):
    # Trying to create a drop down screen with choices of actions:
    zorder 3
    modal True

    key "mousedown_4" action NullAction()
    key "mousedown_5" action NullAction()

    # Get mouse coords:
    python:
        x, y = pos
        xval = 1.0 if x > config.screen_width/2 else .0
        yval = 1.0 if y > config.screen_height/2 else .0

    $ workable_buildings = (b for b in hero.buildings if b.workable)
    frame:
        style_prefix "dropdown_gm"
        pos (x, y)
        anchor (xval, yval)
        has vbox
        for building in workable_buildings:
            textbutton "[building.name]":
                selected char.workplace == building
                action Function(char.mod_workplace, building), Hide("set_workplace_dropdown"), With(Dissolve(0.1))
        textbutton "None":
            selected char.workplace is None
            action [Function(char.mod_workplace, None),
                    Hide("set_workplace_dropdown"), With(Dissolve(0.1))]
        textbutton "Close":
            action Hide("set_workplace_dropdown"), With(Dissolve(0.1))
            keysym "mousedown_3", "K_ESCAPE"

screen set_home_dropdown(char, pos=()):
    # Trying to create a drop down screen with choices of actions:
    zorder 3
    modal True

    key "mousedown_4" action NullAction()
    key "mousedown_5" action NullAction()

    # Get mouse coords:
    python:
        x, y = pos
        xval = 1.0 if x > config.screen_width/2 else .0
        yval = 1.0 if y > config.screen_height/2 else .0

    default habitable_locations = [b for b in hero.buildings if (b.habitable and b.vacancies)] + [pytfall.streets]

    frame:
        style_prefix "dropdown_gm"
        pos (x, y)
        anchor (xval, yval)
        has vbox

        for loc in habitable_locations:
            textbutton "[loc]":
                selected char.home == loc
                action SetField(char, "home", loc), Hide("set_home_dropdown"), With(Dissolve(0.1))
                tooltip loc.desc
        textbutton "Close":
            action Hide("set_home_dropdown"), With(Dissolve(0.1))
            keysym "mousedown_3", "K_ESCAPE"

screen basic_dropdown_box(options, max_rows, row_size, pos, value=None, field=None, action=None):
    frame:
        style_prefix "dropdown_gm"
        align (.5, .5)
        xysize row_size
        $ tmp = options.get(value, "None")
        $ xsize, ysize = row_size
        textbutton tmp:
            align .5, .5
            xysize row_size
            action Show("basic_dropdown_content", options=options, max_rows=max_rows, row_size=row_size, pos=pos, value=value, field=field, action=action)
            #text tmp idle_color "beige" align .5, .5 hover_color "crimson" size min(ysize-5, int(3*xsize/max(1, 2*len(tmp))))
            text_size min(ysize-5, int(3*xsize/max(1, 2*len(tmp)))) text_layout "nobreak"

screen basic_dropdown_content(options, max_rows, row_size, pos, value=None, field=None, action=None):
    # Trying to create a drop down screen with choices of actions:
    zorder 10
    modal True

    #key "mousedown_4" action NullAction()
    #key "mousedown_5" action NullAction()

    # Get mouse coords:
    python:
        x, y = pos
        if y > config.screen_height/2:
            yval = 1.0
        else:
            y += row_size[1]
            yval = .0
        xsize, ysize = row_size

        max_rows = min(max_rows, len(options)+1)

    frame:
        style_prefix "dropdown_gm"
        xmargin 0
        padding 5, 5
        pos (x, y)
        yanchor yval
        xsize xsize+10
        ymaximum (ysize*max_rows + 10)
        viewport:
            xsize xsize
            ymaximum ysize*max_rows
            mousewheel True
            has vbox
            for key, option in options.items():
                python:
                    btn_action = []
                    if field is None:
                        btn_action.append(Return(key))
                    else:
                        btn_action.append(SetField(field[0], field[1], key))
                        if action is not None:
                            if not isinstance(action, list):
                                action = [action] 
                            btn_action.extend(action)
                    btn_action.extend([Hide("basic_dropdown_content"), With(Dissolve(0.1))])
                textbutton option:
                    xysize (xsize, ysize)
                    selected key == value
                    action btn_action
                    #text option idle_color "beige" hover_color "crimson" selected_color "aqua" align .5, .5 size min(ysize-5, int(3*xsize/max(1, 2*len(option))))
                    text_size min(ysize-5, int(3*xsize/max(1, 2*len(option))))

            python:
                rtn_action = []
                if field is None:
                    rtn_action.append(Return(value))
                rtn_action.extend([Hide("basic_dropdown_content"), With(Dissolve(0.1))])
            textbutton "Close":
                xysize (xsize, ysize)
                action rtn_action
                keysym "mousedown_3", "K_ESCAPE"
                text_size min(ysize-5, int(3*xsize/max(1, 2*len("Close"))))

screen dropdown_box(options, max_rows, row_size, pos, value=None, field=None, action=None):
    frame:
        align (.5, .5)
        xysize row_size
        $ tmp = options.get(value, "None")
        $ xsize, ysize = row_size
        button:
            background Null()
            xysize row_size
            action Show("dropdown_content", options=options, max_rows=max_rows, row_size=row_size, pos=pos, value=value, field=field, action=action)
            text tmp idle_color "beige" align .5, .5 hover_color "crimson" size min(ysize-5, int(3*xsize/max(1, 2*len(tmp)))) layout "nobreak"
            hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

screen dropdown_content(options, max_rows, row_size, pos, value=None, field=None, action=None):
    # Trying to create a drop down screen with choices of actions:
    zorder 10
    modal True

    #key "mousedown_4" action NullAction()
    #key "mousedown_5" action NullAction()

    # Get mouse coords:
    python:
        x, y = pos
        if y > config.screen_height/2:
            yval = 1.0
        else:
            y += row_size[1]
            yval = .0
        xsize, ysize = row_size

        max_rows = min(max_rows, len(options)+1)

    frame:
        background Frame(im.Alpha("content/gfx/frame/MC_bg.png", alpha=.55), 10 ,10)
        #style_prefix "content"
        xmargin 0
        padding 5, 5
        pos (x, y)
        yanchor yval
        xsize xsize+10
        ymaximum (ysize*max_rows + 10)
        style_group "proper_stats"
        viewport:
            xsize xsize
            ymaximum ysize*max_rows
            mousewheel True
            has vbox
            for key, option in options.items():
                python:
                    btn_action = []
                    if field is None:
                        btn_action.append(Return(key))
                    else:
                        btn_action.append(SetField(field[0], field[1], key))
                        if action is not None:
                            if not isinstance(action, list):
                                action = [action] 
                            btn_action.extend(action)
                    btn_action.extend([Hide("dropdown_content"), With(Dissolve(0.1))])
                button:
                    background Null()
                    xysize (xsize, ysize)
                    selected key == value
                    action btn_action
                    text option idle_color "beige" hover_color "crimson" selected_color "aqua" align .5, .5 size min(ysize-5, int(3*xsize/max(1, 2*len(option))))
                    hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)
            python:
                rtn_action = []
                if field is None:
                    rtn_action.append(Return(value))
                rtn_action.extend([Hide("dropdown_content"), With(Dissolve(0.1))])
            button:
                background Null()
                xysize (xsize, ysize)
                action rtn_action
                text "Close" idle_color "brown" align .5, .5 hover_color "crimson" size min(ysize-5, int(3*xsize/max(1, 2*len("Close"))))
                hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)
                keysym "mousedown_3", "K_ESCAPE"

screen char_rename(char=None):
    modal True
    zorder 1
    frame:
        if isinstance(char, Player):
            background Frame("content/gfx/frame/post_battle.png", 500, 400)
            xysize(500, 400)
        elif char.status != "slave":
            background Frame("content/gfx/frame/post_battle.png", 500, 300)
            xysize(500, 300)
        else:
            background Frame("content/gfx/frame/post_battle.png", 500, 500)
            xysize(500, 500)
        align (.5, .5)
        vbox:
            style_prefix "wood"
            at fade_in_out()
            align (.5, .5)
            spacing 10
            if isinstance(char, Player) or char.status == "slave":
                text "Name:" size 21 color "goldenrod" outlines [(2, "#3a3a3a", 0, 0)]
                button:
                    xysize (340, 60)
                    xalign 1.0
                    yalign .5
                    text "[char.name]" size 16 color "goldenrod"
                    action Return(["rename", "name"])
                    padding (10, 10)
            if not(isinstance(char, Player)): # it's weird to give a nickname to yourself. should be handled by ingame events
                text "Nickname:" size 21 color "goldenrod" outlines [(2, "#3a3a3a", 0, 0)]
                button:
                    xysize (340, 60)
                    xalign 1.0
                    yalign .5
                    if char.nickname != char.name:
                        text "[char.nickname]" size 16 color "goldenrod"
                    else:
                        text "None" size 16 color "goldenrod"
                    action Return(["rename", "nick"])
                    padding (10, 10)
            if isinstance(char, Player) or char.status == "slave":
                text "Full Name:" size 21 color "goldenrod" outlines [(2, "#3a3a3a", 0, 0)]
                button:
                    xysize (340, 60)
                    xalign 1.0
                    yalign .5
                    text "[char.fullname]" size 16 color "goldenrod"
                    action Return(["rename", "full"])
                    padding (10, 10)

            null height 20
            button:
                xysize (100, 50)
                xalign .5
                yalign .5
                text "Back" size 16 color "goldenrod"
                action Hide("char_rename"), With(dissolve)
                keysym "mousedown_3", "K_ESCAPE"
                padding (10, 10)

screen character_pick_screen(): # screen to select someone from the MC team
    frame:
        align (.5, .5)
        xsize 450
        ysize 310
        padding(2, 2)
        background Frame("content/gfx/frame/frame_dec_1.png")
        label "Select a character" align (.5, .08) text_color "#DAA520" text_size 18
        hbox:
            spacing 45
            align (.5, .4)
            for l in hero.team:
                $ char_profile_img = l.show('portrait', resize=(101, 101), cache=True)
                $ img = "content/gfx/frame/ink_box.png"
                vbox:
                    spacing 1
                    xsize 102
                    imagebutton:
                        xalign .5
                        background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
                        idle char_profile_img
                        hover PyTGFX.bright_content(char_profile_img, .15)
                        action Return(l)
                        xysize (102, 102)
                    bar:
                        xalign .5
                        right_bar im.Scale("content/gfx/interface/bars/empty_bar2.png", 102, 14)
                        left_bar im.Scale("content/gfx/interface/bars/hp2.png", 102, 14)
                        value l.get_stat("health")
                        range l.get_max("health")
                        thumb None
                        left_gutter 0
                        right_gutter 0
                        xysize (102, 14)
                    bar:
                        xalign .5
                        right_bar im.Scale("content/gfx/interface/bars/empty_bar2.png", 102, 14)
                        left_bar im.Scale("content/gfx/interface/bars/mp2.png", 102, 14)
                        value l.get_stat("mp")
                        range l.get_max("mp")
                        thumb None
                        left_gutter 0
                        right_gutter 0
                        xysize (102, 14)
                    bar:
                        xalign .5
                        right_bar im.Scale("content/gfx/interface/bars/empty_bar2.png", 102, 14)
                        left_bar im.Scale("content/gfx/interface/bars/vitality2.png", 102, 14)
                        value l.get_stat("vitality")
                        range l.get_max("vitality")
                        thumb None
                        left_gutter 0
                        right_gutter 0
                        xysize (102, 14)
                    frame:
                        xalign .5
                        xsize 102
                        ysize 30
                        padding(2, 2)
                        background Frame("content/gfx/frame/gm_frame.png")
                        $ name = l.name[:8]
                        label "[name]" align (.5, .5) text_color "#DAA520" text_size 16

        vbox:
            style_group "wood"
            align (.5, .9)
            button:
                xysize (102, 40)
                yalign .5
                action Return(False)
                text "Cancel" size 15 color "goldenrod"
                keysym "mousedown_3", "K_ESCAPE"

screen finances(obj, mode="logical"):
    modal True
    zorder 1

    default fin_mode = mode
    default focused = obj

    add im.Alpha("content/gfx/images/bg_gradient2.webp", alpha=.3)
    frame:
        at slide(so1=(0, 700), t1=.7, so2=(0, 0), t2=.3, eo2=(0, -config.screen_height))
        background Frame(im.Alpha("content/gfx/frame/frame_gp.webp", alpha=.9), 10, 10)
        style_prefix "proper_stats"
        xysize 1000, 600
        padding 20, 20
        align .5, .5

        $ days, all_income_data, all_expense_data = focused.fin.get_data_for_fin_screen(fin_mode)

        # Days:
        default fin_day = days[-1] if days else None
        # Special check, took some time to track down:
        # Problem here is that we can CTD when switching from Private to Performance...
        # Kind of a hack but it's difficult to do this differently without recoding the screen.
        if fin_day in days:
            pass
        elif days:
            $ fin_day = days[-1]
        else:
            $ fin_day = None

        if fin_day not in all_income_data:
            text "There are no Finances to display for {}!".format(focused.name) align .5, .5
        else:
            hbox:
                style_prefix "basic"
                for d in days:
                    if d == store.day:
                        $ temp = "Today"
                    elif isinstance(d, int):
                        $ temp = "Day " + str(d)
                    else:
                        $ temp = d # All variant...
                    textbutton temp action SetScreenVariable("fin_day", d)

            python:
                income = all_income_data[fin_day]
                len_income = len(income)
                if len_income != 0:
                    len_income = (len_income + 1) * 28 + 14
                    total_income = sum(income.values())
                    income = sorted(income.items(), key=itemgetter(1), reverse=True)
                else:
                    len_income = 27 + 4
                    total_income = 0
            vbox:
                ypos 40
                text "Income:" size 40 color "goldenrod"
                viewport:
                    xysize (398, 350)
                    child_size 398, len_income
                    draggable True
                    mousewheel True
                    add Transform(Solid("grey"), alpha=.3)
                    vbox:
                        ypos 2
                        if income:
                            for reason, value in income:
                                frame:
                                    xoffset 4
                                    xysize (390, 27)
                                    xpadding 7
                                    text reason color "#79CDCD"
                                    text str(value) xalign 1.0 style_suffix "value_text" color "goldenrod"

                            null height 10
                        frame:
                            xoffset 4
                            xysize (390, 27)
                            xpadding 7
                            text "Total" color "#79CDCD"
                            text str(total_income) xalign 1.0 style_suffix "value_text" color "lawngreen"

            python:
                expense = all_expense_data[fin_day]
                len_expense = len(expense)
                if len_expense != 0:
                    len_expense = (len_expense + 1) * 28 + 14
                    total_expense = sum(expense.values())
                    expense = sorted(expense.items(), key=itemgetter(1), reverse=True)
                else:
                    len_expense = 27 + 4
                    total_expense = 0
            vbox:
                ypos 40 xalign 1.0
                text "Expenses:" size 40 color "goldenrod"
                viewport:
                    xysize (398, 350)
                    child_size 398, len_expense
                    draggable True
                    mousewheel True
                    add Transform(Solid("grey"), alpha=.3)
                    vbox:
                        ypos 2
                        if expense:
                            for reason, value in expense:
                                frame:
                                    xoffset 4
                                    xysize (390, 27)
                                    xpadding 7
                                    text reason color "#79CDCD"
                                    text str(value) xalign 1.0 style_suffix "value_text" color "goldenrod"

                            null height 10
                        frame:
                            xoffset 4
                            xysize (390, 27)
                            xpadding 7
                            text "Total" color "#79CDCD"
                            text str(total_expense) xalign 1.0 style_suffix "value_text" color "red"

            frame:
                align .5, .9
                xysize 400, 50
                xpadding 7
                background Frame("content/gfx/frame/rank_frame.png", 3, 3)
                text "Total" size 35 color "goldenrod" yoffset 1
                $ total = total_income - total_expense
                $ temp = "red" if total < 0 else "lawngreen"
                text str(total) xalign 1.0 style_suffix "value_text" color temp size 35 yoffset 1#offset -1, 1

        # Debt
        if focused.fin.income_tax_debt or focused.fin.property_tax_debt:
            $ total_debt = focused.fin.income_tax_debt + focused.fin.property_tax_debt
            frame:
                background Frame(im.Alpha("content/gfx/frame/MC_bg2.png", alpha=.9), 10, 10)
                style_prefix "proper_stats"
                align 1.0, 1.0
                padding 5, 10
                has vbox
                frame:
                    xysize (200, 20)
                    xpadding 7
                    text "Income Tax Debt:" size 15
                    text "[focused.fin.income_tax_debt]" style_suffix "value_text" xalign 1.0 color "red" yoffset -1
                frame:
                    xysize (200, 20)
                    xpadding 7
                    text "Property Tax Debt:" size 15
                    text "[focused.fin.property_tax_debt]" style_suffix "value_text" xalign 1.0 color "red" yoffset -1
                null height 3
                frame:
                    xysize (200, 20)
                    xpadding 7
                    text "Total:" size 15
                    text "[total_debt]" style_suffix "value_text" xalign 1.0 color "red" yoffset -1

        hbox:
            style_prefix "basic"
            align .5, 1.0
            button:
                minimum (100, 30)
                action Hide('finances'), With(dissolve)
                text "OK"
                keysym ("K_RETURN", "K_ESCAPE", "mousedown_3")
            if isinstance(focused, Char):
                button:
                    minimum (100, 30)
                    if fin_mode == "logical":
                        sensitive focused.allowed_to_view_personal_finances
                        action SetScreenVariable('fin_mode', "main")
                        text "Personal"
                    elif fin_mode == "main":
                        action SetScreenVariable('fin_mode', "logical")
                        text "Performance"

    if isinstance(focused, Char):
        key "mousedown_4" action SetScreenVariableC("focused", Function(change_char_in_profile, dir="next"))
        key "mousedown_5" action SetScreenVariableC("focused", Function(change_char_in_profile, dir="prev"))

screen race_and_elements(align=(.5, .99), char=None):
    hbox:
        align align
        spacing 20
        # Race:
        frame:
            xysize (100, 100)
            background Frame(im.Alpha("content/gfx/frame/frame_it1.png", alpha=.6), 0, 0)
            $ trait = char.race
            $ img = PyTGFX.scale_content(trait.icon, 95, 95)
            button:
                align (.5, .5)
                xysize (95, 95)
                background img
                action Show("popup_info", content="trait_info_content", param=trait)
                hover_background PyTGFX.bright_content(img, .10)
                tooltip "Race:\n   {}".format(char.full_race)

        # Elements icon:
        $ elements = char.elements
        $ img = build_multi_elemental_icon(elements, size=90)
        $ img_h = build_multi_elemental_icon(elements, size=90, mc=im.matrix.brightness(.10))
        $ ele = ", ".join([e.id for e in elements])
        frame:
            xysize (100, 100)
            background Frame(im.Alpha("content/gfx/frame/frame_it1.png", alpha=.6), 0, 0)
            add im.Scale("content/gfx/interface/images/elements/hover.png", 98, 98) align (.5, .5)
            button:
                xysize 90, 90
                align .5, .5 offset -1, -1
                action Show("popup_info", content="trait_info_content", param=[char, elements])
                background img
                hover_background img_h
                tooltip "Elements:\n   %s" % ele

screen effect_info(effect, xsize, ysize, idle_color="ivory", strikethrough=False):
    python:
        font_size = ysize-5
        while font_size > 10 and Text(effect.name, size=font_size).size()[0] >= xsize:
            font_size -= 1
    frame:
        align (.5, .5)
        xysize (xsize, ysize)
        button:
            background Null()
            xysize (xsize, ysize)
            action NullAction()
            text "[effect.name]" idle_color idle_color align .5, .5 hover_color "crimson" size font_size layout "nobreak" strikethrough strikethrough
            tooltip "%s" % effect.desc
            hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

screen skill_info(skill, xsize, ysize, idle_color="ivory", strikethrough=False):
    python:
        font_size = ysize-5
        while font_size > 10 and Text(skill.name, size=font_size).size()[0] >= xsize:
            font_size -= 1
    frame:
        align (.5, .5)
        xysize (xsize, ysize)
        button:
            background Null()
            xysize (xsize, ysize)
            action NullAction()
            text "[skill.name]" idle_color idle_color align .5, .5 hover_color "crimson" size font_size layout "nobreak" strikethrough strikethrough
            tooltip ["be", skill]
            hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

screen trait_info(trait, xsize, ysize, idle_color="ivory", strikethrough=False):
    python:
        font_size = ysize-5
        while font_size > 10 and Text(trait.id, size=font_size).size()[0] >= xsize:
            font_size -= 1
    frame:
        align (.5, .5)
        xysize (xsize, ysize)
        button:
            background Null()
            xysize (xsize, ysize)
            action Show("popup_info", content="trait_info_content", param=trait)
            text trait.id idle_color idle_color align .5, .5 hover_color "crimson" text_align .5 size font_size layout "nobreak" strikethrough strikethrough
            tooltip "%s" % trait.desc
            hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

screen popup_info(content=None, param=None):
    modal True
    python:
        pos = renpy.get_mouse_pos()
        x, y = pos
        if x > config.screen_width/2:
            x -= 20
            xval = 1.0
        else:
            x += 20
            xval = .0
        temp = config.screen_height/3
        if y < temp:
            yval = .0
        elif y > config.screen_height-temp:
            yval = 1.0
        else:
            yval = .5
    mousearea:
        area(pos[0], pos[1], 1, 1)
        hovered Show(content, transition=None, param=param, pos=(x, y), anchor=(xval, yval))
        unhovered Hide(content), Hide("popup_info")

# TODO this screen is used to display the modifiers of a trait, 
#      a combined info of a char and the merged info of the elemental traits
#      it could be split to three different screens later...
screen trait_info_content(param, pos, anchor):
    python:
        if isinstance(param, Trait):
            trait_info = param
        else:
            trait_info = Trait() 
    fixed:
        pos pos
        anchor anchor
        fit_first True
        frame:
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            padding 10, 10
            has vbox style_prefix "proper_stats" spacing 1

            $ any_mod = False
            if trait_info.mod_stats:
                $ any_mod = True
                label (u"Stats:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for stat, mod in trait_info.mod_stats.iteritems():
                    frame:
                        xysize 200, 20
                        text stat.title() size 15 color "#79CDCD" align .0, .5 outlines [(1, "black", 0, 0)]
                        $ value = mod[0]
                        if stat == "disposition":
                            $ txt_color = "red" if value < 0 else "lime"
                            label "%+g" % value text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]
                        elif stat == "upkeep":
                            $ txt_color = "lime" if value < 0 else "red"
                            label "%+g" % value text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]
                        else:
                            $ txt_color = "red" if value < 0 else "lime"
                            text "%+g every %d lvl" % (value, mod[1]) align 1.0, .5 size 15 color txt_color outlines [(1, "black", 0, 0)]
            if trait_info.max:
                $ any_mod = True
                label (u"Max:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for stat, value in trait_info.max.iteritems():
                    frame:
                        xysize 200, 20
                        $ txt_color = "red" if value < 0 else "lime"
                        text stat.title() size 15 color "#79CDCD" align .0, .5 outlines [(1, "black", 0, 0)]
                        label "%+g" % value text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]
            if trait_info.min:
                $ any_mod = True
                label (u"Min:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for stat, value in trait_info.min.iteritems():
                    frame:
                        xysize 200, 20
                        $ txt_color = "red" if value < 0 else "lime"
                        text stat.title() size 15 color "#79CDCD" align .0, .5 outlines [(1, "black", 0, 0)]
                        label "%+g" % value text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]

            if trait_info.effects:
                $ any_mod = True
                label (u"Effects:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for effect in trait_info.effects:
                    frame:
                        xysize 200, 20
                        text effect.title() size 15 color "yellow" align .5, .5 text_align .5 outlines [(1, "black", 0, 0)]

            if trait_info.mod_skills:
                $ any_mod = True
                label (u"Skills:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for skill, data in trait_info.mod_skills.iteritems():
                    frame:
                        xysize 200, 20
                        text skill.title() size 15 color "yellowgreen" align .0, .5 outlines [(1, "black", 0, 0)]

                        $ img_path = "content/gfx/interface/icons/skills_icons/"
                        default PS = PyTGFX.scale_img
                        button:
                            style "default"
                            xysize 20, 18
                            action NullAction()
                            align .99, .5
                            if data[0] > 0:
                                add PS(img_path + "left_green.png", 20, 20)
                            elif data[0] < 0:
                                add PS(img_path + "left_red.png", 20, 20)
                            if data[1] > 0:
                                add PS(img_path + "right_green.png", 20, 20)
                            elif data[1] < 0:
                                add PS(img_path + "right_red.png", 20, 20)
                            if data[2] > 0:
                                add PS(img_path + "top_green.png", 20, 20)
                            elif data[2] < 0:
                                add PS(img_path + "top_red.png", 20, 20)

            $ bem = modifiers_calculator(param)
            if any((bem.elemental_modifier, bem.defence_modifier, bem.evasion_bonus, bem.delivery_modifier, bem.damage_multiplier, bem.ch_multiplier)):
                $ any_mod = True
                use list_be_modifiers(bem)

            if trait_info.mod_ap:
                $ any_mod = True
                label (u"Other:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                frame:
                    xysize 200, 20
                    $ output = "AP %+d" % trait_info.mod_ap
                    text (output) align .5, .5 size 15 color "lime" text_align .5 outlines [(1, "black", 0, 0)]

            if not any_mod:
                label ("- no direct effects -") text_size 15 text_color "goldenrod" text_bold True xalign .45 text_outlines [(1, "black", 0, 0)]

screen list_be_modifiers(bem):
    if bem.elemental_modifier:
        #$ any_mod = True
        label (u"Elemental:") text_size 20 text_color "goldenrod" text_bold True xalign .45
        hbox:
            frame:
                xysize 80, 20
                # "element"
            frame:
                xysize 60, 20
                text "damage" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]
            frame:
                xysize 60, 20
                text "defence" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]
        for elem, values in bem.elemental_modifier.iteritems():
            hbox:
                frame:
                    xysize 80, 20
                    text elem size 15 color "goldenrod" align .5, .5 outlines [(1, "black", 0, 0)]
                frame:
                    xysize 60, 20
                    $ val = values["damage"]*100
                    text "%d %%" % val size 15 color ("lime" if val >= 0 else "red") align 1.0, .5 outlines [(1, "black", 0, 0)]
                if "absorbs" in values:
                    frame:
                        xysize 60, 20
                        $ val = values["absorbs"]*100
                        text "%+d %%" % val size 15 color "white" align 1.0, .5 outlines [(1, "black", 0, 0)]
                elif "resist" in values:
                    frame:
                        xysize 60, 20
                        text "res." size 15 color "lime" align 1.0, .5 outlines [(1, "black", 0, 0)]
                else:
                    frame:
                        xysize 60, 20
                        $ val = values["defence"]*100
                        text "%d %%" % val size 15 color ("lime" if val >= 0 else "red") align 1.0, .5 outlines [(1, "black", 0, 0)]

    if bem.defence_modifier or bem.evasion_bonus:
        #$ any_mod = True
        label (u"Defensive:") text_size 20 text_color "goldenrod" text_bold True xalign .45

        if bem.defence_modifier:
            hbox:
                frame:
                    xysize 50, 20
                    # "type"
                frame:
                    xysize 80, 20
                    text "bonus" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]
                frame:
                    xysize 70, 20
                    text "multiplier" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]
            for type, value in bem.defence_modifier.iteritems():
                hbox:
                    frame:
                        xysize 50, 20
                        text type size 15 color "goldenrod" align .5, .5 outlines [(1, "black", 0, 0)]
                    frame:
                        xysize 80, 20
                        $ val = value[0]
                        if val:
                            if isinstance(val, (list, tuple)):
                                $ min, max, lvl = val
                            else:
                                $ min = max = val
                            $ txt_color = "red" if max < 0 else "lime"
                            if min == max:
                                text "%d" % max size 15 color txt_color align .5, .5 outlines [(1, "black", 0, 0)]
                            else:
                                text "%d..%d" % (min, max) size 15 color txt_color align .5, .5 outlines [(1, "black", 0, 0)]
                    frame:
                        xysize 70, 20
                        $ val = value[1]*100
                        if val:
                            text "%d %%" % val size 15 color ("lime" if val > 0 else "red") align 1.0, .5 outlines [(1, "black", 0, 0)]

        $ val = bem.evasion_bonus
        if val:
            if isinstance(val, (list, tuple)):
                $ min, max, lvl = val
            else:
                $ min = max = val
            frame:
                xysize 200, 20
                $ txt_color = "red" if max < 0 else "lime"
                text "Evasion" size 15 color "yellowgreen" align .0, .5 outlines [(1, "black", 0, 0)]
                if min == max:
                    label "%+d" % max text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]
                else:
                    text "%d .. %d at lvl %d" % (min, max, lvl) align 1.0, .5 size 15 color txt_color outlines [(1, "black", 0, 0)]

    if bem.delivery_modifier or bem.damage_multiplier or bem.ch_multiplier:
        #$ any_mod = True
        label (u"Offensive:") text_size 20 text_color "goldenrod" text_bold True xalign .45

        if bem.delivery_modifier:
            hbox:
                frame:
                    xysize 50, 20
                    # "type"
                frame:
                    xysize 80, 20
                    text "bonus" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]
                frame:
                    xysize 70, 20
                    text "multiplier" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]
            for type, value in bem.delivery_modifier.iteritems():
                hbox:
                    frame:
                        xysize 50, 20
                        text type size 15 color "goldenrod" align .5, .5 outlines [(1, "black", 0, 0)]
                    frame:
                        xysize 80, 20
                        $ val = value[0]
                        if val:
                            if isinstance(val, (list, tuple)):
                                $ min, max, lvl = val
                            else:
                                $ min = max = val
                            $ txt_color = "red" if max < 0 else "lime"
                            if min == max:
                                text "%d" % max size 15 color txt_color align .5, .5 outlines [(1, "black", 0, 0)]
                            else:
                                text "%d..%d" % (min, max) size 15 color txt_color align .5, .5 outlines [(1, "black", 0, 0)]
                    frame:
                        xysize 70, 20
                        $ val = value[1]*100
                        if val:
                            text "%+d %%" % val size 15 color ("lime" if val > 0 else "red") align 1.0, .5 outlines [(1, "black", 0, 0)]

        if bem.damage_multiplier:
            frame:
                xysize 200, 20
                $ value = bem.damage_multiplier*100
                $ txt_color = "red" if value < 0 else "lime"
                text "Damage multiplier %+d %%" % value size 15 color txt_color align .5, .5 text_align .5 outlines [(1, "black", 0, 0)]

        if bem.ch_multiplier:
            frame:
                xysize 200, 20
                $ value = bem.ch_multiplier*100
                $ txt_color = "red" if value < 0 else "lime"
                text "Critical hit %+d %%" % value size 15 color txt_color align .5, .5 text_align .5 outlines [(1, "black", 0, 0)]

