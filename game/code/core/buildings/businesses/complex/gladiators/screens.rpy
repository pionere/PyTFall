screen building_management_leftframe_gladiators_guild_mode:
    if bm_mid_frame_mode.view_mode == "upgrades":
        use building_management_leftframe_businesses_mode
    elif bm_mid_frame_mode.view_mode == "team":
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
                    action [Function(workers.occ_filters.add, "Combatant"), Function(workers.action_filters.discard, None), Function(workers.filter)]
                textbutton "Warriors":
                    xsize 296
                    action ModFilterSet(workers, "occ_filters", "Combatant")
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
    elif bm_mid_frame_mode.view_mode == "arena":
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
                xysize 312, 600
                xalign .5 ypos 57
                mousewheel True
                has vbox xfill True spacing 16
                for team in bm_mid_frame_mode.teams_to_fight():
                    $ tmp = "content/gfx/frame/namebox4.png"
                    if selected_team == team:
                        $ temp = None
                        $ color = "red"
                        $ tmp = im.MatrixColor(tmp, im.matrix.tint(.4, .4, .4))
                    else:
                        $ temp = team
                        $ color = "orange"
                    fixed:
                        xysize 306, 150
                        frame:
                            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.9), 10, 10)
                            padding 2, 2
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

                        textbutton str(team.leader.arena_rep):
                            background None
                            xalign .5
                            ypos 30
                            action NullAction()
                            text_color "red"
                            text_size 16
                            text_outlines [(1, "#3a3a3a", 0, 0)]
                            tooltip "Arena Reputation"

    elif bm_mid_frame_mode.view_mode == "log":
        python:
            guild = bm_mid_frame_mode
            match_logs = guild.match_logs
            selected_log_type = guild.selected_log_type
            temp = match_logs.keys()
            if selected_log_type is None:
                # Select the first entry
                selected_log_type = temp[0]
            focused_type_index = temp.index(selected_log_type)

            log_entries = match_logs[selected_log_type]
            days = sorted(list(set(l.day for l in log_entries)), reverse=True)
            log_entry = guild.selected_log_entry
            if log_entry is not None:
                log_entry = log_entries[log_entry[1]].day if log_entry[0] == selected_log_type else None
        vbox:
            xsize 320 spacing 1
            # Maps sign:
            frame:
                style_group "content"
                xalign .5 ypos 3
                xysize 200, 50
                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                label (u"Events") text_size 23 text_color "ivory" align .5, .8

            null height 5

            # Combat types:
            hbox:
                xalign .5
                spacing 5
                button:
                    style "paging_green_button_left"
                    yalign .5
                    action SetField(guild, "selected_log_type", temp[(focused_type_index - 1) % len(temp)])
                frame:
                    background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.9), 10, 10)
                    padding 2, 2
                    margin 0, 0
                    align .5, .5
                    textbutton selected_log_type.capitalize():
                        background Frame(im.Alpha("content/gfx/frame/frame_bg.png", alpha=.5), 5, 5)
                        align .5, .5
                        action NullAction()
                        text_color "gold"
                        text_style "interactions_text"
                        text_size 18
                        text_outlines [(1, "#3a3a3a", 0, 0)]
                button:
                    style "paging_green_button_right"
                    yalign .5
                    action SetField(guild, "selected_log_type", temp[(focused_type_index + 1) % len(temp)])

            # Days for the selected type:
            null height 5
            viewport:
                draggable True
                mousewheel True
                xalign .5
                xysize 310, 550
                vbox:
                    xfill True
                    #xalign .5
                    style_prefix "dropdown_gm2"
                    for day in days:
                        textbutton ("Day %d" % day):
                            xalign .5
                            xysize 220, 24
                            if log_entry == day:
                                action Function(guild.jump_to_entry, None, None)
                                selected True
                            else:
                                action Function(guild.jump_to_entry, selected_log_type, day)
                            text_color "limegreen"
                            text_selected_color "gold"

screen building_management_midframe_gladiators_guild_mode:
    if bm_mid_frame_mode.view_mode == "upgrades":
        use building_management_midframe_businesses_mode
    elif bm_mid_frame_mode.view_mode == "team":
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
                    drag:
                        dragged dragged
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

                        add w.show("portrait", resize=(46, 46), cache=True)

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
                    dragged dragged
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

    elif bm_mid_frame_mode.view_mode == "arena":
        $ guild = bm_mid_frame_mode 
        $ selected_team = guild.selected_team
        $ events = guild.gui_events
        vbox:
            xalign .5
            frame: # Image
                xalign .5
                padding 5, 5
                background Frame("content/gfx/frame/MC_bg3.png", 10 ,10)
                add im.Scale("content/gfx/bg/be/battle_arena_1.webp", 600, 100)

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
                        tooltip "Filter the scheduled matches by the selected type!" 

                    $ options = OrderedDict([("inhouse", "Inhouse"), ("dogfight", "Dogfight"), ("matchfight", "Matchfight"), ("chainfight", "Chainfight"), (None, "-")])
                    use dropdown_box(options, max_rows=6, row_size=(160, 30), pos=(538, 162), value=guild.combat_type, field=(guild, "combat_type"))

                    textbutton "Schedule":
                        style "basic_button"
                        action Return(["guild", "schedule"])
                        sensitive (selected_team is not None and guild.combat_type is not None)
                        tooltip "Schedule a match for the selected team with the selected type!" 

                # Paging II.
                button:
                    style "paging_green_button_right"
                    xalign .9
                    action Function(events.next_page)
                    sensitive events.page != events.max_page()
                    tooltip "Next Page"

            # scheduled fights
            null height 5
            for e in events.page_content():
                $ enemy = e.opponent
                $ type = e.type
                frame:
                    #background Frame(im.Alpha("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
                    background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                    xpadding 10 
                    xysize (620, 60)
                    style_group "proper_stats"
                    hbox:
                        # Re-schedule the fight
                        frame:
                            xysize 20, 40
                            yalign .5
                            background None
                            if (e.result is None or e.repeat) and (e.day is None or e.day == day) and any((t.task != GladiatorTask for t in e.guild_chars())):
                                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_l.png", 16, 16)
                                imagebutton:
                                    align .5, .5
                                    idle img
                                    hover_background PyTGFX.bright_img(img, .15)
                                    action Function(guild.reschedule_event, e)
                                    tooltip "Update task of the team members (Re-schedule the fight)!"

                        $ temp = e.team.gui_name
                        $ tmp = PyTGFX.txt_font_size(temp, 150, 24, min_size=10)
                        frame:
                            xysize 155, 40
                            yalign .5
                            background None
                            text temp yalign .5 size tmp
                        
                        $ temp = 1
                        if type == "matchfight":
                            $ temp += len(enemy)
                        frame:
                            xysize 60, 60
                            yalign .5
                            background None
                            imagebutton:
                                idle PyTGFX.scale_img("content/gfx/interface/images/vs_%d.webp" % temp, 60, 60)
                                action NullAction()
                                tooltip type.capitalize()

                        $ temp = e.enemy_name()
                        $ tmp = PyTGFX.txt_font_size(temp, 150, 24, min_size=10)
                        frame:
                            xysize 155, 40
                            yalign .5
                            background None
                            text temp yalign .5

                        $ temp = e.day
                        frame:
                            xysize 60, 40
                            yalign .5
                            background None
                            if temp is not None:
                                text str(temp) align .5, .5

                        $ temp = e.result
                        # run the fight now
                        frame:
                            xysize 100, 60
                            background None
                            has vbox yalign .5 spacing 1
                            if temp is None:
                                if (e.day is None or e.day == day):
                                    textbutton "Fight":
                                        xalign .5
                                        style "basic_button"
                                        text_size 15
                                        action Return(["guild", "fight", e])
                                        tooltip "Let them fight!"
                                    textbutton "Watch":
                                        xalign .5
                                        style "basic_button"
                                        text_size 15
                                        action Return(["guild", "watch", e])
                                        tooltip "Watch the encounter!"
                            else:
                                $ temp = temp[0]
                                if type == "inhouse":
                                    if temp is None:
                                        $ tmp = temp = "Draw"
                                        $ color = "bisque"
                                    else:
                                        $ tmp = "Done"
                                        $ temp = "Win by %s" % temp.gui_name
                                        $ color = "orange"
                                else:
                                    if temp == e.team:
                                        $ tmp = temp = "Victory"
                                        $ color = "lime"
                                    else:
                                        $ tmp = temp = "Defeat"
                                        $ color = "red"
                                textbutton tmp:
                                    background None
                                    align .5, .5
                                    action NullAction()
                                    text_color color
                                    text_italic True
                                    text_size 16
                                    if temp != tmp:
                                        tooltip temp

                        # schedule a repeated fight
                        frame:
                            xysize 25, 40
                            yalign .5
                            background None
                            if type in ["inhouse", "chainfight"]:
                                if getattr(e, "repeat", False):
                                    $ temp = "content/gfx/interface/icons/checkbox_checked.png"
                                else:
                                    $ temp = "content/gfx/interface/icons/checkbox_unchecked.png"
                                button:
                                    xysize (25, 25)
                                    yalign 0.5
                                    background Frame(im.Alpha("content/gfx/frame/MC_bg2.png", alpha=.55), 5, 5)
                                    action Function(guild.toggle_repeat, e)
                                    add (im.Scale(temp, 20, 20)) align .5, .5
                                    tooltip 'Repeat'
                        # Un-schedule the fight
                        frame:
                            xysize 20, 40
                            yalign .5
                            background None
                            if type != "matchfight" and e.result is None:
                                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 20, 20)
                                imagebutton:
                                    yalign .5
                                    idle img
                                    hover_background PyTGFX.bright_img(img, .15)
                                    action Function(guild.remove_event, e)
                                    tooltip "Cancel the event!"
                null height 2

    elif bm_mid_frame_mode.view_mode == "log":
        $ guild = bm_mid_frame_mode
        $ log_entry = guild.selected_log_entry
        if log_entry is None:
            frame: # Image
                xalign .5
                padding 5, 5
                background Frame("content/gfx/frame/MC_bg3.png", 10 ,10)
                add im.Scale("content/gfx/bg/buildings/log.webp", 600, 390)
        else:
            $ log_type, log_idx = log_entry
            $ match_logs = guild.match_logs[log_type]
            $ left_page = match_logs[log_idx]
            $ right_page = match_logs[log_idx+1] if len(match_logs) > (log_idx+1) else None 
            if right_page is not None and right_page.day != left_page.day:
                $ right_page = None
            frame:
                background Frame(im.Alpha("content/gfx/frame/mes11.webp", alpha=.9), 10, 10)
                xysize (620, 90)
                xalign .5
                ymargin 1
                ypadding 1
                text log_type.capitalize() color "gold" style "interactions_text" size 35 outlines [(1, "#3a3a3a", 0, 0)] align (.5, .2)
                text "Day %d" % left_page.day color "orange" style "interactions_text" size 20 outlines [(1, "#3a3a3a", 0, 0)] align (.5, .85)

            # Log Book:
            frame:
                background Frame("content/gfx/frame/open_book.png", 10, 10)
                xysize 608, 570
                xalign .5
                ypos 100
                fixed:
                    xysize 620, 570
                    # Paging:
                    if log_idx != 0:
                        $ img = "content/gfx/interface/buttons/book_pager_l.png"
                        imagebutton:
                            pos 2, 538
                            idle img
                            #hover PyTGFX.bright_img(img, .15)
                            action Function(guild.page_previous)
                            tooltip "Previous Page"

                    if len(match_logs) > (log_idx + (1 if right_page is None else 2)):
                        $ img = "content/gfx/interface/buttons/book_pager_r.png" 
                        imagebutton:
                            pos 572, 538
                            idle img
                            #hover PyTGFX.bright_img(img, .15)
                            action Function(guild.page_next)
                            tooltip "Next Page"

                    # Left Page
                    frame:
                        background Frame("content/gfx/frame/ink_box.png", 10, 10)
                        xysize 270, 534
                        pos 14, 15
                        has viewport draggable 1 mousewheel 1
                        # battle_log
                        text "\n".join(left_page.combat_log) style "stats_value_text" size 13 color "ivory"

                    # Right Page
                    if right_page:
                        frame:
                            background Frame("content/gfx/frame/ink_box.png", 10, 10)
                            xysize 270, 534
                            pos 310, 15
                            has viewport draggable 1 mousewheel 1
                            # battle_log
                            text "\n".join(right_page.combat_log) style "stats_value_text" size 14 color "ivory"

screen building_management_rightframe_gladiators_guild_mode:
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
                        action SetField(bm_mid_frame_mode, "view_mode", "arena")
                        tooltip ("On this screen you can organize the matches.")
                        text "Arena" size 15
                    button:
                        xysize (150, 40)
                        yalign .5
                        action SetField(bm_mid_frame_mode, "view_mode", "log")
                        tooltip "For each of your teams, recorded one last adventure, which you can see here in detail."
                        text "Log" size 15
                    button:
                        xysize 150, 40
                        yalign .5
                        action Return(["bm_mid_frame_mode", None])
                        tooltip ("Back to the main overview of the building.")
                        text "Back" size 15

screen building_management_inhouse_gladiators(off_team, use_return=False):
    # FIXME same as arena_dogfights!
    default container = [t for t in bm_mid_frame_mode.teams_to_fight() if t is not off_team]
    modal True
    zorder 1

    frame:
        style_group "content"
        background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
        xysize (721, 565)
        at slide(so1=(0, 1200), t1=.7, eo2=(0, 1200), t2=.7)
        pos (280, 154)

        side "c r":
            pos (5, 5)
            maximum (710, 515)
            viewport:
                id "vp_dogfights"
                draggable True
                mousewheel True
                child_size (700, 10000)
                has vbox spacing 5
                for team in sorted(container, key=methodcaller("get_level")):
                    frame:
                        style_group "content"
                        padding 5, 3
                        xalign .5
                        xysize (695, 150)
                        background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                        has hbox xalign .5
                        button:
                            style "arena_channenge_button"
                            action Hide("building_management_inhouse_gladiators"), Return(["challenge", "start_dogfight", team])
                            $ level = team.get_level()
                            vbox:
                                align (.5, .5)
                                text "Challenge!" style "arena_badaboom_text" size 40 outlines [(2, "#3a3a3a", 0, 0)]
                                text "Enemy level: [level]" style "arena_badaboom_text" size 30 outlines [(1, "#3a3a3a", 0, 0)]

                        add PyTGFX.scale_img("content/gfx/interface/images/vs_1.webp", 130, 130) yalign .5

                        frame:
                            style "arena_channenge_frame"
                            $ name = team.gui_name
                            $ size = 15 if len(name) > 15 else 25
                            frame:
                                align .5, .0
                                padding 5, 1
                                background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                text ("[name]"):
                                    align .5, .0
                                    size size
                                    style "proper_stats_text"
                                    color "gold"
                            hbox:
                                spacing 3
                                align .5, 1.0
                                for fighter in team:
                                    frame:
                                        padding 2, 2
                                        background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                                        add fighter.show("portrait", resize=(60, 60), cache=True)

            vbar value YScrollValue("vp_dogfights")

        button:
            style_group "basic"
            action If(use_return, true=Return(False), false=Hide("building_management_inhouse_gladiators"))
            minimum(50, 30)
            align (.5, .9995)
            text  "Close"
            keysym "mousedown_3"
