screen building_management_leftframe_workshop_guild_mode:
    if bm_mid_frame_mode.view_mode == "upgrades":
        use building_management_leftframe_businesses_mode
    elif bm_mid_frame_mode.view_mode == "team":
        use building_management_leftframe_teambuilder
    elif bm_mid_frame_mode.view_mode == "work":
        $ selected_team = bm_mid_frame_mode.selected_team
        fixed: # making sure we can align stuff...
            xysize 320, 665
            frame:
                style_group "content"
                xalign .5 ypos 3
                xysize (200, 50)
                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                label (u"Teams") text_size 23 text_color "ivory" align (.5, .8)

            viewport:
                xysize 320, 600
                xalign .5 ypos 57
                mousewheel True
                has vbox xfill True spacing 16
                for team in bm_mid_frame_mode.teams_to_fight():
                    $ tmp = "content/gfx/frame/namebox4.png"
                    if selected_team == team:
                        $ temp = None
                        $ color = "red"
                        $ tmp = im.MatrixColor(tmp, im.matrix.tint(.4, .4, .4))
                        $ back = Frame("content/gfx/frame/h4.webp", 10, 10)
                    else:
                        $ temp = team
                        $ color = "orange"
                        $ back = None
                    fixed:
                        xysize 320, 150
                        frame:
                            background back
                            padding 3, 5
                            margin 0, 0
                            ypos 8
                            xalign .5
                            hbox:
                                xalign .5
                                use team_status(team=team, interactive=False, pos=(0, 0), spacing=1)

                        textbutton team.gui_name:
                            background Frame(tmp)
                            padding 12, 4
                            margin 0, 0
                            xalign .5
                            action SetField(bm_mid_frame_mode, "selected_team", temp)
                            text_color color
                            text_hover_color "red"

screen building_management_midframe_workshop_guild_mode:
    if bm_mid_frame_mode.view_mode == "upgrades":
        use building_management_midframe_businesses_mode
    elif bm_mid_frame_mode.view_mode == "team":
        use building_management_midframe_teambuilder
    elif bm_mid_frame_mode.view_mode == "work":
        $ guild = bm_mid_frame_mode 
        $ selected_team = guild.selected_team
        $ events = guild.gui_events
        vbox:
            xalign .5
            frame: # Image
                xalign .5
                padding 5, 5
                background Frame("content/gfx/frame/MC_bg3.png", 10 ,10)
                add im.Scale("content/gfx/bg/locations/workshop.webp", 600, 100)

            null height 5
            hbox:
                xfill True
                # Paging I.
                button:
                    style "paging_green_button_left"
                    xalign .1
                    action Function(events.prev_page)
                    sensitive events.page != 0
                    tooltip "Previous Page"

                # filter/fight buttons
                hbox:
                    spacing 2
                    align .5, .5
                    style_group "proper_stats"
                    textbutton "Filter":
                        style "basic_button"
                        action Function(guild.filter)
                        tooltip "Filter the scheduled tasks by the selected type!" 

                    use dropdown_box(guild.gui_options, max_rows=8, row_size=(160, 30), pos=(538, 165), value=guild.event_type, field=(guild, "event_type"))

                    textbutton "Schedule":
                        style "basic_button"
                        action Return(["guild", "schedule", None])
                        sensitive selected_team is not None
                        tooltip "Add new task with the selected type!" 

                # Paging II.
                button:
                    style "paging_green_button_right"
                    xalign .9
                    action Function(events.next_page)
                    sensitive events.page != events.max_page()
                    tooltip "Next Page"

            # scheduled processes
            null height 5
            for e in events.page_content():
                $ ready = e.ready
                frame:
                    #background Frame(im.Alpha("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
                    background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                    xpadding 10 
                    xysize (620, 80)
                    style_group "proper_stats"
                    has hbox
                    # add event + re-schedule
                    vbox:
                        xysize 25, 80
                        fixed:
                            xysize 25, 40
                            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/add.png", 16, 16)
                            imagebutton:
                                align .5, .5
                                idle img
                                hover_background PyTGFX.bright_img(img, .15)
                                action Return(["guild", "schedule", e])
                                sensitive selected_team is not None
                                tooltip "Schedule new task with the selected type before this task!"
                        
                        # Re-schedule the process
                        fixed:
                            xysize 25, 40
                            if ready is None and any(t.task != WorkshopTask for t in e.team):
                                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_l.png", 16, 16)
                                imagebutton:
                                    align .5, .5
                                    idle img
                                    hover_background PyTGFX.bright_img(img, .15)
                                    action Function(guild.reschedule_event, e)
                                    tooltip "Update task of the team members (Re-schedule the task)!"

                    # name + team
                    vbox:
                        xysize 155, 80
                        yalign .5
                        $ temp = e.name
                        $ tmp = PyTGFX.txt_font_size(temp, 150, 24, min_size=10)
                        fixed:
                            xysize 155, 40
                            text temp align .5, .5 size tmp
                        $ temp = e.team.gui_name
                        $ tmp = PyTGFX.txt_font_size(temp, 150, 24, min_size=10)
                        fixed:
                            xysize 155, 40
                            text temp align .5, .5 size tmp

                    # type + difficulty
                    vbox:
                        xysize 80, 80
                        yalign .5
                        $ temp = e.type
                        $ tmp = PyTGFX.txt_font_size(temp, 80, 22, min_size=10)
                        fixed:
                            xysize 80, 40
                            text temp align .5, .5 size tmp
                        $ temp = e.tasks[0]
                        $ temp = "-" if temp == 0 else (roman_num(temp) + ".") 
                        $ tmp = PyTGFX.txt_font_size(temp, 80, 22, min_size=10)
                        fixed:
                            xysize 80, 40
                            text temp align .5, .5 size tmp

                    # occupied capacity
                    vbox:
                        xysize 40, 80
                        yalign .5
                        $ wc = "%g" % e.wait_cap
                        if ready is None:
                            $ temp = str(e.capacity)
                            $ tmp = PyTGFX.txt_font_size(temp, 60, 22, min_size=10)
                            fixed:
                                xysize 40, 40
                                text temp align .5, .5 size tmp
                            $ temp = "(" + wc + ")"
                        else:
                            $ temp = wc
                        $ tmp = PyTGFX.txt_font_size(temp, 60, 22, min_size=10)
                        fixed:
                            xysize 40, 40
                            text temp align .5, .5 size tmp

                    # flags + producct-teams
                    vbox:
                        xysize 155, 80
                        yalign .5
                        hbox:
                            xysize 155, 40
                            xalign .5
                            spacing 20
                            # Repeat:
                            frame:
                                xysize 25, 40
                                yalign .5
                                background None
                                if e.repeat:
                                    $ temp = "content/gfx/interface/icons/checkbox_checked.png"
                                else:
                                    $ temp = "content/gfx/interface/icons/checkbox_unchecked.png"
                                button:
                                    xysize (25, 25)
                                    yalign 0.5
                                    background Frame(im.Alpha("content/gfx/frame/MC_bg2.png", alpha=.55), 5, 5)
                                    action Function(guild.toggle_repeat, e)
                                    add (im.Scale(temp, 20, 20)) align .5, .5
                                    tooltip "Repeat the task"
                            # Sell:
                            frame:
                                xysize 25, 40
                                yalign .5
                                background None
                                if e.sell:
                                    $ temp = "content/gfx/interface/icons/checkbox_checked.png"
                                else:
                                    $ temp = "content/gfx/interface/icons/checkbox_unchecked.png"
                                button:
                                    xysize (25, 25)
                                    yalign 0.5
                                    background Frame(im.Alpha("content/gfx/frame/MC_bg2.png", alpha=.55), 5, 5)
                                    action Function(guild.toggle_sell, e)
                                    add (im.Scale(temp, 20, 20)) align .5, .5
                                    tooltip "Sell the product"
                            # Report:
                            frame:
                                xysize 25, 40
                                yalign .5
                                background None
                                if e.report:
                                    $ temp = "content/gfx/interface/icons/checkbox_checked.png"
                                else:
                                    $ temp = "content/gfx/interface/icons/checkbox_unchecked.png"
                                button:
                                    xysize (25, 25)
                                    yalign 0.5
                                    background Frame(im.Alpha("content/gfx/frame/MC_bg2.png", alpha=.55), 5, 5)
                                    action Function(guild.toggle_report, e)
                                    add (im.Scale(temp, 20, 20)) align .5, .5
                                    tooltip "Report when done"
                            # Warn:
                            frame:
                                xysize 25, 40
                                yalign .5
                                background None
                                if e.warn:
                                    $ temp = "content/gfx/interface/icons/checkbox_checked.png"
                                else:
                                    $ temp = "content/gfx/interface/icons/checkbox_unchecked.png"
                                button:
                                    xysize (25, 25)
                                    yalign 0.5
                                    background Frame(im.Alpha("content/gfx/frame/MC_bg2.png", alpha=.55), 5, 5)
                                    action Function(guild.toggle_warn, e)
                                    add (im.Scale(temp, 20, 20)) align .5, .5
                                    tooltip "Warn when fails"
                        if e.pro_teams:
                            # product teams
                            viewport:
                                xysize 155, 40
                                xalign .5
                                mousewheel True
                                has vbox xfill True
                                for prod, team in e.pro_teams:
                                    if team is None:
                                        $ temp = prod
                                        $ tmp = "Assign a team to the product (%s) of the task" % prod
                                    else:
                                        $ temp = team.name
                                        $ tmp = prod
                                    textbutton temp:
                                        action NullAction() # FIXME
                                        tooltip tmp
                               
                    # Ready:
                    $ temp = e.ready
                    frame:
                        xysize 30, 80
                        yalign .5
                        background None
                        if temp is not None:
                            $ temp = str(temp - day + 1)
                            textbutton temp:
                                align .5, .5
                                action NullAction()
                                tooltip "Remaining days"

                    # Change priority
                    vbox:
                        xysize 25, 80
                        fixed:
                            xysize 25, 40
                            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_up.png", 20, 20)
                            imagebutton:
                                align .5, .5
                                idle img
                                hover_background PyTGFX.bright_img(img, .15)
                                action Function(guild.change_prio, e, -1)
                                sensitive events.pager_content.index(e) != 0
                                tooltip "Raise the priority of the task"

                        fixed:
                            xysize 25, 40
                            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_down.png", 20, 20)
                            imagebutton:
                                align .5, .5
                                idle img
                                hover_background PyTGFX.bright_img(img, .15)
                                action Function(guild.change_prio, e, 1)
                                sensitive events.pager_content[-1] != e
                                tooltip "Lower the priority of the task"

                    # Un-schedule the event
                    frame:
                        xysize 20, 80
                        yalign .5
                        background None
                        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 20, 20)
                        imagebutton:
                            yalign .5
                            idle img
                            hover_background PyTGFX.bright_img(img, .15)
                            action Function(guild.remove_event, e)
                            tooltip "Cancel the task!"

                null height 2

screen building_management_rightframe_workshop_guild_mode:
    if True:
        frame:
            xalign .5
            xysize 260, 40
            background Frame("content/gfx/frame/namebox5.png", 10, 10)
            label str(bm_mid_frame_mode.name) text_size 18 text_color "ivory" align .5, .6

        frame:
            background Null()
            xfill True yfill True
            frame:
                background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                align .5, .95
                padding 10, 10
                vbox:
                    style_group "wood"
                    align .5, .5
                    spacing 10
                    button:
                        xysize (150, 40)
                        yalign .5
                        action SetField(bm_mid_frame_mode, "view_mode", "upgrades")
                        tooltip "Expand your Guild"
                        text "Upgrades" size 15
                    button:
                        xysize (150, 40)
                        yalign .5
                        action SetField(bm_mid_frame_mode, "view_mode", "team")
                        tooltip "You can customize your teams here or hire Guild members."
                        text "Teams" size 15
                    button:
                        xysize (150, 40)
                        yalign .5
                        action SetField(bm_mid_frame_mode, "view_mode", "work")
                        tooltip ("On this screen you can organize the work.")
                        text "Work" size 15
                    button:
                        xysize 150, 40
                        yalign .5
                        action Return(["bm_mid_frame_mode", None])
                        tooltip ("Back to the main overview of the building.")
                        text "Back" size 15

screen crafting_tasks(team, type):
    python:
        guild = bm_mid_frame_mode
        recipes = [r for r in guild.gui_recipes if len(r["tasks"]) == len(team)]
        if type is not None:
            recipes = [r for r in recipes if r["type"] == type]

        inv = guild.building.inventory
    modal True
    frame:
        background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
        at slide(so1=(0, 1200), t1=.7, eo2=(0, 1200), t2=.7)
        style_group "content"
        pos (280, 154)
        xysize (721, 580)
        has vbox
        viewport:
            scrollbars "vertical"
            maximum (710, 515)
            draggable True
            mousewheel True
            child_size (700, 5000)
            has vbox spacing 5
            for setup in recipes:
                frame:
                    #xysize (695, 55)
                    xsize 695
                    background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                    style_prefix "proper_stats"
                    padding 10, 10
                    has vbox
                    # Name
                    $ temp = setup["id"]
                    $ font_size = PyTGFX.txt_font_size(temp, 600, 28, min_size=10)
                    button:
                        xysize 600, 34
                        background Frame("content/gfx/interface/buttons/choice_buttons2.png", 1, 1)
                        action Return(setup)
                        xalign .5
                        text temp align .5, .5 size font_size layout "nobreak" color "gold" hover_color "tomato"

                    #  type
                    text setup["type"] xalign .5 size 16 layout "nobreak" color "ivory" italic True

                    # Workers:
                    hbox:
                        spacing 2
                        hbox:
                            xsize 90
                            text "Task:"
                        $ temp = setup["ap_cost"]
                        frame:
                            xysize (97, 27)
                            has hbox xysize (97, 27)
                            button:
                                background Frame("content/gfx/interface/buttons/preference.png")
                                xysize 20, 20
                                align 0.2, .5
                                action NullAction()
                                tooltip "Base duration (AP)"
                            text ("%g" % temp) xalign .9 style_suffix "value_text"

                        $ temp = setup.get("capacity", 0)
                        if temp:
                            frame:
                                xysize (97, 27)
                                has hbox xysize (97, 27)
                                button:
                                    background Frame("content/gfx/interface/images/layout.png")
                                    xysize 20, 20
                                    align 0.2, .5
                                    action NullAction()
                                    tooltip "Required space (capacity)"
                                text ("%g" % temp) xalign .9 style_suffix "value_text"

                        $ temp = setup.get("dirt_mod", 0)
                        frame:
                            xysize (97, 27)
                            has hbox xysize (97, 27)
                            button:
                                background Frame("content/gfx/interface/buttons/discard.png")
                                xysize 20, 20
                                align 0.2, .5
                                action NullAction()
                                tooltip "Dirt"
                            text ("%g" % temp) xalign .9 style_suffix "value_text"

                        $ temp = setup["tasks"]
                        $ tmp = "%s: %s" % (plural("Tier", len(temp)), itemize(["-" if i == 0 else roman_num(i) for i in temp]))
                        frame:
                            xysize (97, 27)
                            has hbox xysize (97, 27)
                            button:
                                background Frame("content/gfx/interface/buttons/Group_full.png")
                                xysize 20, 20
                                align 0.2, .5
                                action NullAction()
                                tooltip "Required workers"
                            textbutton str(len(temp)):
                                #background None
                                margin 0, 0
                                padding 0, 0
                                #align .9, .5
                                xalign .9
                                action NullAction()
                                text_style "proper_stats_value_text"
                                #style_suffix "value_text"
                                tooltip tmp

                    # Upgrades
                    $ temp = setup.get("upgrades", None)
                    if temp:
                        hbox:
                            spacing 2
                            hbox:
                                xsize 90
                                text "Upgrades:"
                            vpgrid:
                                cols 6
                                xsize 600
                                spacing 2
                                for u in temp:
                                    $ img = u.img
                                    if not guild.has_extension(u):
                                        $ img = PyTGFX.sepia_content(img)
                                    frame:
                                        xysize (27, 27)
                                        button:
                                            background Frame(img)
                                            xysize 20, 20
                                            align .5, .5
                                            action NullAction()
                                            tooltip u.name

                    # Tools
                    $ temp = setup.get("tools", None)
                    if temp:
                        hbox:
                            spacing 2
                            hbox:
                                xsize 90
                                text "Tools:"
                            vpgrid:
                                cols 6
                                xsize 600
                                spacing 2
                                for item, amount in temp.iteritems():
                                    $ icon = items[item].icon
                                    frame:
                                        xysize (97, 27)
                                        has hbox xysize (97, 27)
                                        button:
                                            background Frame(icon)  # TODO scale_content ?
                                            xysize 20, 20
                                            align 0.2, .5
                                            action NullAction()
                                            tooltip item
                                        $ color = "ivory" if inv[item] >= amount else "grey"
                                        text str(amount) xalign .9 color color style_suffix "value_text"

                    # Materials
                    $ temp = setup.get("materials", None)
                    if temp:
                        hbox:
                            spacing 2
                            hbox:
                                xsize 90
                                text "Resources:"
                            vpgrid:
                                cols 6
                                xsize 600
                                spacing 2
                                for item, amount in temp.iteritems():
                                    $ icon = items[item].icon
                                    frame:
                                        xysize (97, 27)
                                        has hbox xysize (97, 27)
                                        button:
                                            background Frame(icon)  # TODO scale_content ?
                                            xysize 20, 20
                                            align 0.2, .5
                                            action NullAction()
                                            tooltip item
                                        $ color = "ivory" if inv[item] >= amount else "grey"
                                        text str(amount) xalign .9 color color style_suffix "value_text"

                    # Waiting period:
                    $ temp = setup.get("wait_days", None)
                    if temp:
                        hbox:
                            spacing 2
                            hbox:
                                xsize 90
                                text "Wait:"
                            frame:
                                background None
                                has hbox
                                text ("%d days" % temp) style_suffix "value_text"
                                $ temp = setup.get("wait_cap", 0)
                                if temp:
                                    text (" using %g capacity" % temp) style_suffix "value_text"

                    # Products
                    hbox:
                        spacing 2
                        hbox:
                            xsize 90
                            text "Products:"
                        vpgrid:
                            cols 6
                            xsize 600
                            spacing 2
                            for item, amount in setup["products"].items():
                                $ icon = items.get(item, None)
                                if icon is None:
                                    # a new process
                                    $ icon = "content/gfx/images/under_construction.webp"
                                else:
                                    # an item
                                    $ icon = icon.icon
                                frame:
                                    xysize (97, 27)
                                    has hbox xysize (97, 27)
                                    button:
                                        background Frame(icon)  # TODO scale_content ?
                                        xysize 20, 20
                                        align 0.2, .5
                                        action NullAction()
                                        tooltip item
                                    text str(amount) xalign .9 style_suffix "value_text"

        null height 5
        button:
            style_group "basic"
            action Return(False)
            minimum(50, 30)
            align (.5, .9995)
            text  "Close"
            keysym "mousedown_3"
