screen building_management_leftframe_exploration_guild_mode:
    if bm_mid_frame_mode.view_mode == "upgrades":
        use building_management_leftframe_businesses_mode
    elif bm_mid_frame_mode.view_mode == "team":
        use building_management_leftframe_teambuilder
    elif bm_mid_frame_mode.view_mode == "explore":
        $ selected_exp_area = bm_mid_frame_mode.selected_exp_area
        fixed: # making sure we can align stuff...
            xysize 320, 665
            frame:
                style_group "content"
                xalign .5 ypos 3
                xysize (200, 50)
                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                label (u"Maps") text_size 23 text_color "ivory" align (.5, .8)

            viewport:
                xysize 224, 600
                xalign .5 ypos 57
                mousewheel True
                has vbox spacing 4
                $ temp = sorted([a for a in fg_areas.values() if a.area is None and a.unlocked], key=attrgetter("stage"))

                for area in temp:
                    $ img = PyTGFX.scale_content(area.img, 220, 124)
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.9), 10, 10)
                        padding 2, 2
                        margin 0, 0
                        button:
                            align .5, .5
                            xysize 220, 124
                            background Transform(img, align=(.5, .5))
                            if selected_exp_area == area:
                                action NullAction()
                                $ name_bg = "content/gfx/frame/frame_bg.png"
                                $ hcolor = "gold"
                            else:
                                hover_background Transform(PyTGFX.bright_content(img, .05), align=(.5, .5))
                                action SetField(bm_mid_frame_mode, "selected_exp_area", area)
                                $ name_bg = "content/gfx/frame/ink_box.png"
                                $ hcolor = "red"
                            frame:
                                align .5, .0
                                padding 20, 2
                                background Frame(im.Alpha(name_bg, alpha=.5), 5, 5)
                                text area.name:
                                    color "gold"
                                    hover_color hcolor
                                    style "interactions_text"
                                    size 18 outlines [(1, "#3a3a3a", 0, 0)]
                                    layout "nobreak"
                                    align .5, .5
    elif bm_mid_frame_mode.view_mode == "area":
        # Left frame with Area controls
        python:
            can_use_horses = False
            guild = bm_mid_frame_mode
            area = guild.selected_exp_area_sub
            teams = guild.teams_to_launch()
            if teams:
                if guild.team_to_launch_index >= len(teams):
                    guild.team_to_launch_index = 0
                focus_team = teams[guild.team_to_launch_index]

                for u in guild.building.businesses:
                    if u.__class__ == StableBusiness:
                        num = len(focus_team)
                        reserved = u.reserved_capacity + num
                        if u.capacity >= reserved:
                            can_use_horses = True
        # The idea is to add special icons for as many features as possible in the future to make Areas cool:
        style_prefix "basic"
        button:
            xalign .5
            xysize 300, 30
            if len(area.camp_queue) != 0:
                action ToggleField(area, "building_camp")
                tooltip "Activate if you want the team to spend its time on building the camp."
            text "Build the camp" xalign .5
        null height 2
        button:
            xalign .5
            xysize 300, 30
            action ToggleField(area, "capture_chars")
            text "Capture Chars" xalign .5
        null height 2
        button:
            xalign .5
            xysize 300, 30
            if can_use_horses:
                action ToggleField(area, "use_horses")
                tooltip "Activate if you want the team to borrow horses from the Stable. Allows to travel twice as fast!"
            text "Use horses" xalign .5
        null height 5
        frame:
            background Frame(im.Alpha("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
            xalign .5
            xysize 300, 30
            margin 0, 0
            padding 3, 2
            style_group "proper_stats"
            $ distance = round_int(area.travel_time / 20.0)
            if distance > 1:
                $ temp = "Travel time is about %d days" % distance
            elif distance == 1:
                $ temp = "Travel time is about a day"
            else:
                $ temp = "Travel time is less than one day"
            text temp xalign .5 # xpos 5
        null height 2
        frame:
            background Frame(im.Alpha("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
            xalign .5
            xysize 300, 40
            margin 0, 0
            padding 3, 2
            style_group "proper_stats"
            hbox:
                xysize 294, 36
                text "Days Exploring:" pos (5, 5)
                vbox:
                    xsize 80
                    xalign 1.0
                    hbox:
                        ysize 30
                        xalign .5
                        textbutton "-":
                            style "basic_button"
                            xysize 21, 21
                            text_hover_color "red"
                            action SetField(area, "days", max(3, area.days-1))
                            selected False
                        fixed:
                            xysize 30, 21
                            yoffset -4
                            text "[area.days]" xalign .5 # # yoffset -1
                        textbutton "+":
                            style "basic_button"
                            xysize 21, 21
                            text_hover_color "red"
                            text_yoffset -1
                            action SetField(area, "days", min(15, area.days+1))
                            selected False
                    bar:
                        ysize 10
                        yoffset -11
                        align .5, .1
                        value FieldValue(area, 'days', area.maxdays-3, max_is_zero=False, style='scrollbar', offset=3, step=1)
                        xmaximum 70
                        thumb 'content/gfx/interface/icons/move15.png'
                        tooltip "Adjust the number of days to spend on site."
        null height 2
        frame:
            background Frame(im.Alpha("content/gfx/frame/Namebox.png", .9), 10, 10)
            xalign .5
            xysize 300, 40
            margin 0, 0
            padding 3, 2
            style_group "proper_stats"
            hbox:
                xysize 294, 36
                text "Risk:" pos (5, 5)
                vbox:
                    xsize 80
                    xalign 1.0
                    hbox:
                        ysize 30
                        xalign .5
                        textbutton "-":
                            style "basic_button"
                            xysize 21, 21
                            text_hover_color "red"
                            action SetField(area, "risk", max(0, area.risk-1))
                            selected False
                        fixed:
                            xysize 30, 21
                            yoffset -4
                            text "[area.risk]" xalign .5 # # yoffset -1
                        textbutton "+":
                            style "basic_button"
                            xysize 21, 21
                            text_hover_color "red"
                            text_yoffset -1
                            action SetField(area, "risk", min(100, area.risk+1))
                            selected False
                    bar:
                        ysize 10
                        yoffset -11
                        align .5, .1
                        value FieldValue(area, 'risk', 100, max_is_zero=False, style='scrollbar', offset=0, step=1)
                        xmaximum 70
                        thumb 'content/gfx/interface/icons/move15.png'
                        tooltip ("Adjust the risk your team takes while exploring. Higher risk gives higher reward, " +
                                 "but your team may not even return if you push this too far!")

        null height 5
        hbox:
            spacing 10
            xalign .5
            button:
                style "paging_green_button_left"
                yalign .5
                action Function(guild.prev_team_to_launch)
                tooltip "Previous Team"
                sensitive len(teams) > 1
            button:
                style "marble_button"
                padding 10, 10
                if teams:
                    action Function(guild.launch_team, focus_team, area), With(fade)
                    tooltip "Send %s on %s days long exploration run!" % (focus_team.name, area.days)
                    vbox:
                        xminimum 150
                        spacing -30
                        text "Launch" style "basic_button_text" xalign .5
                        text "\n[focus_team.name]" style "basic_button_text" xalign .5
                else:
                    action NullAction()
                    text "No Teams Available!" style "basic_button_text" align .5, .5

            button:
                style "paging_green_button_right"
                yalign .5
                action Function(guild.next_team_to_launch)
                tooltip "Next Team"
                sensitive len(teams) > 1

        default objects_mode = "allowed"
        null height 10
        frame:
            align .5, .02
            xsize 330
            background None
            $ builders = any(t.building_camp for t in area.trackers)
            if objects_mode == "allowed":
                button:
                    xalign .5
                    xsize 300
                    text "To build" color "ivory" align (.0, .5) size 17 outlines [(1, "#424242", 0, 0)]
                    background im.Scale("content/gfx/interface/buttons/tablefts.webp", 300, 30)
                    action NullAction()
                    focus_mask True
                button:
                    xalign .5
                    xsize 300
                    text "In queue" color "ivory" align (1.0, .5) size 16
                    background im.Scale("content/gfx/interface/buttons/tabright.webp", 300, 30)
                    action SetScreenVariable("objects_mode", "queue")
                    tooltip "View Objects In Queue"
                    focus_mask True
                vbox:
                    ypos 40
                    xalign .5
                    xsize 330 #, 150
                    $ temp = set([u.type for u in area.camp_queue])
                    for u in area.allowed_objects:
                        if u.type not in temp:
                            $ temp.add(u.type)
                            button:
                                xalign .5
                                xysize 300, 25
                                style "pb_button"
                                text "[u.name]" align (.5, .5) color "ivory"
                                action Function(area.queue, u)
                                sensitive (not builders)
                                tooltip u.desc
            else:
                button:
                    xalign .5
                    xsize 300
                    text "To build" color "ivory" align (.0, .5) size 16
                    background im.Scale("content/gfx/interface/buttons/tableft.webp", 300, 30)
                    action SetScreenVariable("objects_mode", "allowed")
                    tooltip "View Objects To Build"
                    focus_mask True
                button:
                    xalign .5
                    xsize 300
                    text "In queue" color "ivory" align (1.0, .5) size 17 outlines [(1, "#424242", 0, 0)]
                    background im.Scale("content/gfx/interface/buttons/tabrights.webp", 300, 30)
                    action NullAction()
                    focus_mask True

                vbox:
                    ypos 40
                    xalign .5 #, .2
                    xsize 330 #, 150
                    for u in area.camp_queue:
                        button:
                            xalign .5
                            xysize 300, 25
                            style "pb_button"
                            text "[u.name]" align (.5, .5) color "ivory"
                            action Function(area.dequeue, u)
                            sensitive (not builders)
                            tooltip u.desc

    elif bm_mid_frame_mode.view_mode == "log":
        python:
            main_area = bm_mid_frame_mode.selected_log_area
            selected_log_area_sub = bm_mid_frame_mode.selected_log_area_sub
            temp = sorted([a for a in fg_areas.values() if a.area is None and a.unlocked], key=attrgetter("stage"))
            if main_area is None:
                # We assume that there is always at least one area!
                main_area = temp[0]
            focused_area_index = temp.index(main_area)
        vbox:
            xsize 320 spacing 1
            # Maps sign:
            frame:
                style_group "content"
                xalign .5 ypos 3
                xysize 200, 50
                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                label (u"Maps") text_size 23 text_color "ivory" align .5, .8

            null height 5

            # Main Area with paging:
            $ img = PyTGFX.scale_content(main_area.img, 220, 124)
            hbox:
                xalign .5
                spacing 5
                button:
                    style "paging_green_button_left"
                    yalign .5
                    action SetField(bm_mid_frame_mode, "selected_log_area", temp[(focused_area_index - 1) % len(temp)])
                frame:
                    background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.9), 10, 10)
                    padding 2, 2
                    margin 0, 0
                    xalign .5
                    button:
                        align .5, .5
                        xysize 220, 124
                        background Transform(img, align=(.5, .5))
                        action NullAction()
                        frame:
                            align .5, .0
                            padding 20, 2
                            background Frame(im.Alpha("content/gfx/frame/frame_bg.png", alpha=.5), 5, 5)
                            text main_area.name:
                                color "gold"
                                style "interactions_text"
                                size 18 outlines [(1, "#3a3a3a", 0, 0)]
                                layout "nobreak"
                                align .5, .5
                button:
                    style "paging_green_button_right"
                    yalign .5
                    action SetField(bm_mid_frame_mode, "selected_log_area", temp[(focused_area_index + 1) % len(temp)])

            # Sub Areas:
            null height 5
            $ areas = sorted([a for a in fg_areas.values() if a.area == main_area.id], key=attrgetter("stage"))
            fixed:
                xalign .5
                xysize 310, 190
                vbox:
                    xalign .5
                    style_prefix "dropdown_gm2"
                    for area in areas:
                        if area.unlocked:
                            $ tmp = area.name
                        else:
                            $ tmp = "?????????"
                        button:
                            xysize 220, 18
                            if area.unlocked:
                                if selected_log_area_sub == area:
                                    action SetField(bm_mid_frame_mode, "selected_log_area_sub", None)
                                    selected True
                                else:
                                    action SetField(bm_mid_frame_mode, "selected_log_area_sub", area)
                                tooltip area.desc
                            else:
                                action NullAction()
                            text str(area.stage):
                                size 12
                                xalign .02
                                yoffset 1
                            label "[tmp]":
                                text_color "limegreen"
                                text_selected_color "gold"
                                text_size 12
                                align 1.0, .5

            # Total Main Area Stats (Data Does Not Exist Yet):
            frame:
                style_group "content"
                xalign .5
                xysize 200, 50
                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                label (u"Total") text_size 23 text_color "ivory" align .5, .8

            vbox:
                xalign .5
                style_prefix "proper_stats"
                $ total = sum(main_area.found_items.values())
                frame:
                    xoffset 4
                    xysize 270, 27
                    xpadding 7
                    text "Items Found:":
                        color "ivory"
                    text "[total]":
                        style_suffix "value_text"
                        color "ivory"
                frame:
                    xoffset 4
                    xysize 270, 27
                    xpadding 7
                    text "Gold Found:":
                        color "ivory"
                    text "[main_area.cash_earned]":
                        style_suffix "value_text"
                        color "ivory"
                $ total = sum(main_area.mobs_defeated.values())
                frame:
                    xoffset 4
                    xysize 270, 27
                    xpadding 7
                    text "Mobs Crushed:":
                        color "ivory"
                    text "[total]":
                        style_suffix "value_text"
                        color "ivory"
                frame:
                    xoffset 4
                    xysize 270, 27
                    xpadding 7
                    text "Chars Captured:":
                        color "ivory"
                    text "[main_area.chars_captured]":
                        style_suffix "value_text"
                        color "ivory"

screen building_management_midframe_exploration_guild_mode:
    if bm_mid_frame_mode.view_mode == "upgrades":
        use building_management_midframe_businesses_mode
    elif bm_mid_frame_mode.view_mode == "team":
        use building_management_midframe_teambuilder
    elif bm_mid_frame_mode.view_mode == "explore":
        $ selected_area = bm_mid_frame_mode.selected_exp_area 
        vbox:
            xalign .5
            frame: # Image
                xalign .5
                padding 5, 5
                background Frame("content/gfx/frame/MC_bg3.png", 10 ,10)
                add im.Scale("content/gfx/bg/buildings/Exploration.webp", 600, 390)

            hbox:
                box_wrap 1
                spacing 2
                xalign .5
                if selected_area is not None:
                    $ temp = sorted([a for a in fg_areas.values() if a.area == selected_area.id], key=attrgetter("stage"))
                    for area in temp:
                        if area.unlocked:
                            $ temp = area.name
                            $ action = [SetField(bm_mid_frame_mode, "selected_exp_area_sub", area), SetField(bm_mid_frame_mode, "view_mode", "area")]
                        else:
                            $ temp = "?????????"
                            $ action = NullAction()
                        button:
                            background Frame(im.Alpha("content/gfx/frame/mes12.jpg", alpha=.9), 10, 10)
                            hover_background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/mes11.webp", .10), alpha=.9), 10, 10)
                            xysize (150, 90)
                            ymargin 1
                            ypadding 1
                            action action 
                            text temp color "gold" style "interactions_text" size 14 outlines [(1, "#3a3a3a", 0, 0)] align (.5, .3)
                            hbox:
                                align (.5, .9)
                                use stars(area.explored, area.maxexplored)
    elif bm_mid_frame_mode.view_mode == "area":
        $ area = bm_mid_frame_mode.selected_exp_area_sub
        # Area-Name
        frame:
            background Frame(im.Alpha("content/gfx/frame/mes11.webp", alpha=.9), 10, 10)
            xysize (620, 90)
            ymargin 1
            ypadding 1
            text "[area.name]" color "gold" style "interactions_text" size 35 outlines [(1, "#3a3a3a", 0, 0)] align (.5, .3)
            hbox:
                align (.5, .9)
                # Get the correct stars:
                use stars(area.explored, area.maxexplored)

        # Area image
        frame:
            ypos 100 
            align .5, .0
            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.95), 10, 10)
            add PyTGFX.scale_content(area.img, 600, 350)

        # Overlay objects
        frame:
            ypos 100
            xalign .5
            padding 10, 10
            background Null()
            $ objects = area.camp_objects[:]
            $ objects.sort(key=lambda x: getattr(x, "layer", 0))
            viewport:
                xysize (600, 350)
                frame:
                    xysize (600, 350)
                    background Null()
                    padding 0, 0
                    margin 0, 0
                    for o in objects:
                        $ img = PyTGFX.get_content(o.img)
                        button:
                            style 'image_button'
                            pos o.pos
                            idle_background img
                            focus_mask True
                            action NullAction()
                            hover_background PyTGFX.bright_content(img, .25)
                            tooltip o.name

        # Teams
        frame:
            background Null()
            style_group "proper_stats"
            pos 10, 460
            has vbox
            label "Teams Exploring:" xalign .5
            if area.trackers:
                vpgrid:
                    xalign .5
                    cols 2
                    xysize 610, 130
                    yminimum 130
                    scrollbars "vertical"
                    mousewheel True
                    xspacing 10
                    yspacing 3
                    for tracker in area.trackers:
                        frame:
                            background Frame(im.Alpha("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
                            xsize 290
                            padding 3, 2
                            margin 0, 0
                            hbox:
                                xalign .5
                                xsize 280
                                fixed:
                                    align (.02, .5)
                                    xysize 200, 20
                                    text "[tracker.team.name]" yalign .5
                                if tracker.used_horses:
                                    add PyTGFX.scale_img("content/gfx/interface/images/ranch35.png", 20, 20) yalign .5 
                                text "%d (%d)" % (tracker.day-1, tracker.days) align (.98, .5)
            else:
                frame:
                    background Frame(im.Alpha("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
                    xsize 290
                    padding 3, 2
                    margin 0, 0
                    text "No teams on exploration runs." align (.5, .5)

        hbox:
            align .5, .99
            button:
                style_group "basic"
                action SetField(bm_mid_frame_mode, "view_mode", "explore")
                minimum (50, 30)
                text "Back"
                keysym "mousedown_3"

    elif bm_mid_frame_mode.view_mode == "log":
        $ area = bm_mid_frame_mode.selected_log_area_sub
        if area is None:
            frame: # Image
                xalign .5
                padding 5, 5
                background Frame("content/gfx/frame/MC_bg3.png", 10 ,10)
                add im.Scale("content/gfx/bg/buildings/log.webp", 600, 390)
        else:
            default focused_log = None
            frame:
                background Frame(im.Alpha("content/gfx/frame/mes11.webp", alpha=.9), 10, 10)
                xysize (620, 90)
                xalign .5
                ymargin 1
                ypadding 1
                text area.name color "gold" style "interactions_text" size 35 outlines [(1, "#3a3a3a", 0, 0)] align (.5, .3)
                hbox:
                    align (.5, .9)
                    # Get the correct stars:
                    use stars(area.explored, area.maxexplored)

            # Buttons with logs (Events):
            frame:
                background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                style_prefix "dropdown_gm2"
                ypos 100 xalign .0
                ysize 550
                padding 10, 10
                has vbox xsize 230 spacing 1
                frame:
                    style_group "content"
                    xalign .5
                    padding 15, 5
                    background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.6), 10, 10)
                    label "Events" text_size 20 text_color "ivory" align .5, .5

                for l in area.logs:
                    button:
                        xalign .5
                        ysize 18
                        action SetScreenVariable("focused_log", l)
                        text str(l.name) size 12 xalign .02 yoffset 1
                        text str(l.suffix) size 12 align (1.0, .5)

            # Information (Story)
            frame:
                background Frame(im.Alpha(im.Flip("content/gfx/frame/p_frame4.png", vertical=True), alpha=.6), 10, 10)
                ysize 550
                padding 10, 10
                ypos 100 xalign 1.0
                has vbox xsize 350 spacing 1
                frame:
                    style_group "content"
                    xalign .5
                    padding 15, 5
                    background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.6), 10, 10)
                    label "Story" text_size 20 text_color "ivory" align .5, .5

                frame:
                    background Frame("content/gfx/frame/ink_box.png", 10, 10)
                    has viewport draggable 1 mousewheel 1
                    if focused_log:
                        $ obj = focused_log.event_object
                        if isinstance(obj, Item):
                            vbox:
                                spacing 10
                                xfill True
                                text obj.id xalign .5 style "stats_value_text" size 16 color "goldenrod"
                                add PyTGFX.scale_content(obj.icon, 100, 100) xalign .5
                                text obj.desc xalign .5 style "stats_value_text" size 14 color "ivory"
                        elif isinstance(obj, Char):
                            vbox:
                                spacing 10
                                xfill True
                                add obj.show("portrait", resize=(100, 100), cache=True) xalign .5
                                text obj.name xalign .5 style "stats_value_text" size 18 color "ivory"
                        elif isinstance(obj, OrderedDict):
                            # map of item/count pairs
                            vbox:
                                spacing 10
                                xfill True
                                for item, amount in obj.iteritems():
                                    $ temp = item.id
                                    if amount != 1:
                                        $ temp += " x%d" % amount
                                    text temp xalign .5 style "stats_value_text" size 16 color "goldenrod"
                                    add PyTGFX.scale_content(item.icon, 100, 100) xalign .5
                                    text item.desc xalign .5 style "stats_value_text" size 14 color "ivory"
                                    null height 10
                        elif isinstance(obj, list):
                            # battle_log
                            text "\n".join(obj) style "stats_value_text" size 14 color "ivory"

screen building_management_rightframe_exploration_guild_mode:
    if bm_mid_frame_mode.view_mode == "area":
        $ area = bm_mid_frame_mode.selected_exp_area_sub
        frame:
            background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            xysize (310, 335)
            xpadding 5
            frame:
                style_group "content"
                align (.5, .015)
                xysize (210, 40)
                background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.6), 10, 10)
                label (u"Enemies") text_size 23 text_color "ivory" align .5, .5
            viewport:
                style_prefix "proper_stats"
                xysize (300, 265)
                mousewheel True
                draggable True
                ypos 50
                xalign .5
                has vbox spacing 3
                for m in area.mobs_defeated:
                    $ m = mobs[m]
                    fixed:
                        xysize 300, 65
                        frame:
                            xpos 6
                            left_padding 2
                            align .01, .5
                            xsize 197
                            text m["name"]
                        frame:
                            yalign .5
                            xanchor 1.0
                            ysize 44
                            xpadding 4
                            xminimum 28
                            xpos 233
                            $ temp = m["min_lvl"]
                            text ("Lvl\n[temp]+") style "TisaOTM" size 17 text_align .5 line_spacing -6
                        frame:
                            background Frame(im.Alpha("content/gfx/interface/buttons/choice_buttons2.png", alpha=.75), 10, 10)
                            padding 3, 3
                            margin 0, 0
                            xysize 60, 60
                            align .99, .5
                            $ img = PyTGFX.scale_content(m["portrait"], 57, 57)
                            imagebutton:
                                align .5, .5
                                idle img
                                hover PyTGFX.bright_content(img, .15)
                                action Show("arena_bestiary", dissolve, m, return_button_action=[Function(SetVariable, "bm_mid_frame_mode", bm_mid_frame_mode)])

        frame:
            background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            xysize (310, 335)
            xpadding 5
            frame:
                style_group "content"
                align (.5, .015)
                xysize (210, 40)
                background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.6), 10, 10)
                label (u"Items") text_size 23 text_color "ivory" align .5, .5
            viewport:
                style_prefix "proper_stats"
                mousewheel True
                draggable True
                xysize (300, 265)
                ypos 50
                xalign .5
                has vbox spacing 3
                for i, n in area.found_items.items():
                    $ i = items[i]
                    fixed:
                        xysize 300, 65
                        frame:
                            xpos 6
                            left_padding 2
                            align .01, .5
                            xsize 197
                            text i.id
                        frame:
                            yalign .5
                            xanchor 1.0
                            ysize 40
                            xsize 35
                            xpadding 4
                            xpos 233
                            if n >= 100:
                                $ n = "99+"
                            text "[n]" align (.5, .5) style "TisaOTM" size 18
                        frame:
                            background Frame(im.Alpha("content/gfx/interface/buttons/choice_buttons2.png", alpha=.75), 10, 10)
                            padding 3, 3
                            xysize 60, 60
                            align .99, .5
                            $ temp = PyTGFX.scale_content(i.icon, 57, 57)
                            imagebutton:
                                align .5, .5
                                idle temp
                                hover PyTGFX.bright_content(temp, .15)
                                action Show("popup_info", content="item_info_content", param=i)
                            $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 16, 16)
                            imagebutton:
                                align 1.0, 0 offset 2, -2
                                idle temp
                                hover PyTGFX.bright_img(temp, .15)
                                action Function(area.found_items.pop, i.id)
                                tooltip "Remove item from the list\n(resets its counter as well)"

    else:
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
                    if False:
                        button:
                            xysize (150, 40)
                            yalign .5
                            action NullAction()
                            tooltip "All the meetings and conversations are held in this Hall. On the noticeboard, you can take job that available for your rank. Sometimes guild members or the master himself and his Council, can offer you a rare job."
                            text "Main Hall" size 15
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
                        action SetField(bm_mid_frame_mode, "view_mode", "explore")
                        tooltip ("On this screen you can organize the expedition. Also, there is a "+
                                 "possibility to see all available information on the various places, enemies and items drop.")
                        text "Exploration" size 15
                    button:
                        xysize (150, 40)
                        yalign .5
                        action SetField(bm_mid_frame_mode, "view_mode", "log")
                        tooltip "Check the latest recorded events for each exploration-area."
                        text "Log" size 15
                    button:
                        xysize 150, 40
                        yalign .5
                        action Return(["bm_mid_frame_mode", None])
                        tooltip ("Back to the main overview of the building.")
                        text "Back" size 15

screen building_management_leftframe_teambuilder:
    $ workers = bm_mid_frame_mode.workers
    # Filters:
    frame:
        background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
        style_group "proper_stats"
        xsize 316
        xalign .5
        padding 10, 10
        has vbox spacing 1
        label "Filters:" xalign .5
        vbox:
            style_prefix "basic"
            xalign .5
            textbutton "Reset":
                xsize 296
                action Function(workers.clear)
            textbutton "Combatants":
                xsize 296
                action ModFilterSet(workers, "occ_filters", "Combatant")
            textbutton "Servers":
                xsize 296
                action ModFilterSet(workers, "occ_filters", "Server")
            textbutton "SIW":
                xsize 296
                action ModFilterSet(workers, "occ_filters", "SIW")
            textbutton "Idle":
                xsize 296
                action ModFilterSet(workers, "action_filters", None)

    # Sorting:
    frame:
        background Frame(im.Alpha("content/gfx/frame/MC_bg.png", alpha=.55), 10 ,10)
        style_group "proper_stats"
        xysize (316, 50)
        xalign .5
        padding 10, 10
        has hbox spacing 10 align .5, .5
        label "Sort:":
            yalign .5 

        $ options = OrderedDict([("level", "Level"), ("name", "Name"), (None, "-")])
        use dropdown_box(options, max_rows=4, row_size=(160, 30), pos=(89, 200), value=workers.sorting_order, field=(workers, "sorting_order"), action=Function(workers.filter))

        if workers.sorting_desc:
            $ temp = "content/gfx/interface/icons/checkbox_checked.png"
        else:
            $ temp = "content/gfx/interface/icons/checkbox_unchecked.png"
        button:
            xysize (25, 25)
            align 1.0, 0.5 #offset 9, -2
            background Frame(im.Alpha("content/gfx/frame/MC_bg2.png", alpha=.55), 5, 5)
            action ToggleField(workers, "sorting_desc"), Function(workers.filter)
            add (im.Scale(temp, 20, 20)) align .5, .5
            tooltip 'Descending order'

screen building_management_midframe_teambuilder:
    # Backgrounds:
    $ workers = bm_mid_frame_mode.workers
    $ guild_teams = bm_mid_frame_mode.guild_teams
    frame:
        background Frame(im.Alpha("content/gfx/frame/hp_1long.png", alpha=.9), 5, 5)
        xysize 620, 344
        yoffset -5
        xalign .5
        hbox:
            xalign .5
            box_wrap 1
            for i in xrange(workers.page_size):
                frame:
                    xysize 90, 90
                    xmargin 2
                    ymargin 2
                    background Frame("content/gfx/frame/MC_bg.png", 5, 5)
        # Page control buttons:
        hbox:
            style_prefix "paging_green"
            align .5, .97
            hbox:
                spacing 5
                $ temp = workers.page != 0
                button:
                    style_suffix "button_left2x"
                    tooltip "First Page"
                    action Function(workers.first_page)
                    sensitive temp
                button:
                    style_suffix "button_left"
                    tooltip "Previous Page"
                    action Function(workers.prev_page)
                    sensitive temp
            null width 100
            hbox:
                spacing 5
                $ temp = workers.page < workers.max_page()
                button:
                    style_suffix "button_right"
                    tooltip "Next Page"
                    action Function(workers.next_page)
                    sensitive temp
                button:
                    style_suffix "button_right2x"
                    tooltip "Last Page"
                    action Function(workers.last_page)
                    sensitive temp

    # Downframe (for the teams and team paging)
    #frame:
    #    #background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
    #    background Frame(im.Alpha("content/gfx/frame/p_frame_.png", alpha=.9), 5, 5)
    #    xysize 620, 349
    #    ypos 331 xalign .5

    # Paging guild teams!
    hbox:
        style_prefix "paging_green"
        xalign .5 ypos 611
        hbox:
            spacing 5
            $ temp = guild_teams.page != 0
            button:
                style_suffix "button_left2x"
                tooltip "First Page"
                action Function(guild_teams.first_page)
                sensitive temp
            button:
                style_suffix "button_left"
                tooltip "Previous Page"
                action Function(guild_teams.prev_page)
                sensitive temp
        null width 20
        button:
            style_group "pb"
            align (.5, .5)
            xsize 60
            action Return(["fg_team", "create"])
            text "..." style "pb_button_text"
            tooltip "Create new team"
        null width 20
        hbox:
            spacing 5
            $ temp = guild_teams.page < guild_teams.max_page()
            button:
                style_suffix "button_right"
                tooltip "Next Page"
                action Function(guild_teams.next_page)
                sensitive temp
            button:
                style_suffix "button_right2x"
                tooltip "Last Page"
                action Function(guild_teams.last_page)
                sensitive temp

    # We'll prolly have to do two layers, one for backgrounds and other for drags...
    draggroup:
        id "team_builder"
        drag:
            drag_name workers
            xysize (600, 310)
            draggable 0
            droppable True
            pos (0, 0)


        $ init_pos = (0, 344)
        $ boxsizex, boxsizey = 208, 88
        $ curr_pos = list(init_pos)
        for t in guild_teams.page_content():
            $ idle_t = True #t not in bm_mid_frame_mode.exploring_teams()
            for idx, w in enumerate(t):
                $ w_pos = (curr_pos[0]+16+idx*61, curr_pos[1]+12)
                $ w.set_flag("dnd_drag_container", t)
                $ img = w.show("portrait", resize=(46, 46), cache=True)
                if not ExplorationGuild.battle_ready(w):
                    $ img = PyTGFX.sepia_content(img)
                drag:
                    dragged ExplorationGuild.dragged
                    droppable 0
                    draggable idle_t
                    #tooltip "%s\nClick to check equipment\nDrag And Drop to remove from team" % w.fullname
                    tooltip "%s\nDrag And Drop to remove from team" % w.fullname
                    drag_name w
                    pos w_pos
                    if idle_t:
                        #clicked [SetVariable("came_to_equip_from", last_label), SetVariable("char", w),
                        #        SetVariable("eqtarget", w), SetVariable("equip_girls", [w]), Jump("char_equip")]
                        hovered Function(setattr, config, "mouse", mouse_drag)
                        unhovered Function(setattr, config, "mouse", mouse_cursor)

                    add img

            drag:
                drag_name t
                xysize (208, 83)
                draggable 0
                droppable idle_t
                pos curr_pos[:]
                frame:
                    xysize (208, 83)
                    background "content/gfx/frame/team_frame_4.png"
                    button:
                        background Frame("content/gfx/frame/namebox4.png")
                        padding 12, 4
                        margin 0, 0
                        align .5, 1.2
                        action NullAction()
                        text t.name align .5, .5 color "orange" text_align .5
                    # Configure the team:
                    $ img = PyTGFX.scale_img("content/gfx/interface/buttons/preference.png", 20, 20)
                    button:
                        background img
                        hover_background PyTGFX.bright_img(img, .15)
                        insensitive_background PyTGFX.sepia_img(img)
                        padding 0, 0
                        margin 0, 0
                        align 0.0, 0.0 offset -4, -8
                        xysize 20, 20
                        sensitive idle_t
                        action Show("exploration_team", team=t)
                        tooltip "Configure"
                    # Configure the team:
                    $ img = PyTGFX.scale_img("content/gfx/interface/buttons/transfer.png", 20, 20)
                    button:
                        background img
                        hover_background PyTGFX.bright_img(img, .15)
                        insensitive_background PyTGFX.sepia_img(img)
                        padding 0, 0
                        margin 0, 0
                        align 0.0, 1.0 offset -4, -10
                        xysize 20, 20
                        sensitive idle_t
                        action Show("transfer_team", team=t, guild=bm_mid_frame_mode)
                        tooltip "Transfer"
                    # Dissolve the team:
                    $ img = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 20, 20)
                    button:
                        background img
                        hover_background PyTGFX.bright_img(img, .15)
                        insensitive_background PyTGFX.sepia_img(img)
                        padding 0, 0
                        margin 0, 0
                        align 1.0, 0.0 offset 3, -8
                        xysize 20, 20
                        sensitive idle_t
                        action Return(["fg_team", "dissolve", t])
                        tooltip "Dissolve"
                    # Remove all teammembers:
                    $ img = PyTGFX.scale_img("content/gfx/interface/buttons/shape69.png", 20, 20)
                    button:
                        background img
                        hover_background PyTGFX.bright_img(img, .15)
                        insensitive_background PyTGFX.sepia_img(img)
                        padding 0, 0
                        margin 0, 0
                        align 1.0, 1.0 offset 3, -10
                        xysize 20, 20
                        sensitive t and idle_t
                        action Return(["fg_team", "clear", t])
                        tooltip "Remove all members!"
            $ curr_pos[0] += boxsizex
            if curr_pos[0] == (init_pos[0] + boxsizex*3): # columns
                $ curr_pos = [init_pos[0], curr_pos[1]+boxsizey]

        $ init_pos = (46, 9)
        $ boxsize = 90 # with spacing
        $ curr_pos = list(init_pos)
        for w in workers.page_content():
            $ w.set_flag("dnd_drag_container", workers)
            drag:
                dragged ExplorationGuild.dragged
                droppable 0
                #tooltip "%s\nClick to check equipment\nDrag And Drop to build teams" % w.fullname
                tooltip "%s\nDrag And Drop to build teams" % w.fullname
                drag_name w
                pos curr_pos[:]
                #clicked [SetVariable("came_to_equip_from", last_label), SetVariable("char", w),
                #         SetVariable("eqtarget", w), SetVariable("equip_girls", [w]), Jump("char_equip")]
                add w.show("portrait", resize=(74, 74), cache=True)
                hovered Function(setattr, config, "mouse", mouse_drag)
                unhovered Function(setattr, config, "mouse", mouse_cursor)
            $ curr_pos[0] += boxsize
            if curr_pos[0] == (init_pos[0] + boxsize*6): # columns
                $ curr_pos = [init_pos[0], curr_pos[1]+boxsize]

screen exploration_team(team):
    zorder 1
    modal True

    add im.Alpha("content/gfx/images/bg_gradient2.webp", alpha=.3)

    # Hero team ====================================>
    frame:
        style_prefix "proper_stats"
        align .58, .4
        background Frame(im.Alpha(im.Twocolor("content/gfx/frame/ink_box.png", "white", "black"), alpha=.7), 5, 5)
        padding 10, 5
        has vbox spacing 10

        # Name of the Team / Close
        hbox:
            xminimum (300*len(team))
            hbox:
                spacing 2
                xalign .5
                label "[team.name]" align .5, .5 text_color "#CDAD00" text_size 30
                $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/edit.png", 24, 24)
                imagebutton:
                    align .6, .05
                    idle temp
                    hover PyTGFX.bright_img(temp, .15)
                    action Return(["fg_team", "rename", team])
                    tooltip "Rename the team"

            imagebutton:
                align (1.0, .0)
                idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
                hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
                action Hide("exploration_team"), With(dissolve)
                keysym "mousedown_3"
                tooltip "Close team screen"

        # Members
        hbox:
            spacing 10
            xalign .5
            for member in team:
                #spacing 7
                # Portrait/Button:
                fixed:
                    align .5, .5
                    xysize 120, 120
                    $ img = member.show("portrait", resize=(120, 120), cache=True)
                    imagebutton:
                        padding 1, 1
                        align .5, .5
                        style "basic_choice2_button"
                        idle img
                        action None

                    $ img = im.Scale("content/gfx/interface/buttons/row_switch_s.png", 40, 20)
                    if not member.front_row:
                        $ img = im.Flip(img, horizontal=True)

                    imagebutton:
                        align (0, 1.0)
                        idle im.Alpha(img, alpha=.8)
                        hover img
                        action ToggleField(member, "front_row", true_value=1, false_value=0)
                        tooltip "Toggle between rows in battle, currently character fights from the %s row" % ("front" if member.front_row else "back")

                    if member != hero:
                        $ img = "content/gfx/interface/buttons/Profile.png"
                        imagebutton:
                            align (1.0, 1.0)
                            idle im.Alpha(img, alpha=.9)
                            hover img
                            action [Hide("exploration_team"), SetVariable("came_to_equip_from", last_label), SetVariable("char", member),
                                    SetVariable("eqtarget", member), SetVariable("equip_girls", team._members), Jump("char_equip")]
                            tooltip "Check equipment"

                # Name/Status:
                frame:
                    xsize 162
                    padding 10, 5
                    background Frame(im.Alpha("content/gfx/frame/p_frame2.png", alpha=.6), 5, 5)
                    has vbox spacing 4 xfill True
                    fixed:
                        xysize 158, 25
                        xalign .5
                        text "{=TisaOTMolxm}[member.name]" xalign .06
                        $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 20, 20)
                        imagebutton:
                            xalign .92
                            idle temp
                            hover PyTGFX.bright_img(temp, .15)
                            action Return(["fg_team", "remove", team, member])
                            tooltip "Remove %s from %s" % (member.nickname, team.name)

                    # HP:
                    fixed:
                        ysize 25
                        $ temp, tmp = member.get_stat("health"), member.get_max("health")
                        bar:
                            left_bar PyTGFX.scale_img("content/gfx/interface/bars/hp1.png", 150, 20)
                            right_bar PyTGFX.scale_img("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                            value temp
                            range tmp
                            thumb None
                            xysize (150, 20)
                        text "HP" size 14 color "#F5F5DC" bold True xpos 8
                        $ tmb = "red" if temp <= tmp*.3 else "#F5F5DC"
                        text "[temp]" size 14 color tmb bold True style_suffix "value_text" xpos 125 yoffset -8

                    # MP:
                    fixed:
                        ysize 25
                        $ temp, tmp = member.get_stat("mp"), member.get_max("mp")
                        bar:
                            left_bar PyTGFX.scale_img("content/gfx/interface/bars/mp1.png", 150, 20)
                            right_bar PyTGFX.scale_img("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                            value temp
                            range tmp
                            thumb None
                            xysize (150, 20)
                        text "MP" size 14 color "#F5F5DC" bold True xpos 8
                        $ tmb = "red" if temp <= tmp*.3 else "#F5F5DC"
                        text "[temp]" size 14 color tmb bold True style_suffix "value_text" xpos 125 yoffset -8

                    # VP
                    fixed:
                        ysize 25
                        $ temp, tmp = member.get_stat("vitality"), member.get_max("vitality")
                        bar:
                            left_bar PyTGFX.scale_img("content/gfx/interface/bars/vitality1.png", 150, 20)
                            right_bar PyTGFX.scale_img("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                            value temp
                            range tmp
                            thumb None
                            xysize (150, 20)
                        text "VP" size 14 color "#F5F5DC" bold True xpos 8
                        $ tmb = "red" if temp <= tmp*.3 else "#F5F5DC"
                        text "[temp]" size 14 color tmb bold True style_suffix "value_text" xpos 125 yoffset -8

        null height 5

screen transfer_team(team, guild):
    zorder 1
    modal True

    default buildings = OrderedDict([(b, guilds) for b, guilds in [(b, [u for u in b.businesses if u.__class__ in [ExplorationGuild, GladiatorsGuild, WorkshopGuild]]) for b in hero.buildings] if guilds])
    default result = None
    python:
        if result is None:
            result = object()
            result.building = guild.building
            result.guild = guild

        building_options = OrderedDict([(b, b.name) for b in buildings.keys()])
        guild_options = OrderedDict([(g, g.name) for g in buildings[result.building]])

        if result.guild not in guild_options:
            result.guild = guild_options.keys()[0]

    add im.Alpha("content/gfx/images/bg_gradient2.webp", alpha=.3)

    # Guild team ====================================>
    frame:
        style_prefix "proper_stats"
        align .58, .4
        background Frame(im.Alpha(im.Twocolor("content/gfx/frame/ink_box.png", "white", "black"), alpha=.7), 5, 5)
        padding 10, 5
        has vbox spacing 10

        # Name of the Team / Close
        hbox:
            xsize 300
            label "[team.name]" xalign .5 text_color "#CDAD00" text_size 30

            imagebutton:
                align (1.0, .0)
                idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
                hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
                action Hide("transfer_team"), With(dissolve)
                keysym "mousedown_3"
                tooltip "Close transfer screen"

        # Building
        use basic_dropdown_box(building_options, max_rows=6, row_size=(160, 30), pos=(630, 270), value=result.building, field=(result, "building"))
        
        # Guild
        use basic_dropdown_box(guild_options, max_rows=6, row_size=(160, 30), pos=(630, 310), value=result.guild, field=(result, "guild"))

        style_prefix "basic"
        textbutton "Transfer":
            xalign .5
            action [Hide("transfer_team"), With(dissolve), Return(["fg_team", "transfer", team, result.guild])]
            sensitive result.guild != guild
            tooltip "Transfer the team"

screen se_debugger():
    zorder 200
    # Useful SE info cause we're not getting anywhere otherwise :(
    viewport:
        xysize (1280, 720)
        scrollbars "vertical"
        mousewheel True
        has vbox

        for area in fg_areas.values():
            $ trackers = getattr(area, "trackers", None)
            if trackers:
                text area.name
                for t in trackers:
                    hbox:
                        xsize 500
                        spacing 5
                        text t.team.name xalign .0
                        text "[t.state]" xalign 1.0
                    hbox:
                        xsize 500
                        spacing 5
                        text "Days:" xalign .0
                        text "[t.day]/[t.days]" xalign 1.0
                    null height 3
                add Solid("F00", xysize=(1280, 5))

    textbutton "Exit":
        align 1.0, 1.0
        action Hide("se_debugger")
