screen building_management_leftframe_gladiators_guild_mode:
    if bm_mid_frame_mode.view_mode == "upgrades":
        use building_management_leftframe_businesses_mode
    elif bm_mid_frame_mode.view_mode == "team":
        use building_management_leftframe_teambuilder
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

                        $ temp = "Arena Reputation (Team: %d)" % team.get_rep()
                        for f in team:
                            $ temp += "\n  - %s: %d" % (f.name, f.arena_rep)
                        textbutton str(team.get_rep()):
                            background None
                            xalign .5
                            ypos 30
                            action NullAction()
                            text_color "red"
                            text_size 16
                            text_outlines [(1, "#3a3a3a", 0, 0)]
                            tooltip temp

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
        use building_management_midframe_teambuilder
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
                    use dropdown_box(options, max_rows=6, row_size=(160, 30), pos=(538, 165), value=guild.combat_type, field=(guild, "combat_type"))

                    textbutton "Schedule":
                        style "basic_button"
                        action Return(["guild", "schedule", None])
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
                            text temp yalign .5 size tmp

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
                                    $ tmp = "Watch the encounter!"
                                    if type == "matchfight":
                                        $ tmp += " Entry fee: {color=gold}%d Gold{/color}." % Arena.match_entry_fee(e.team, enemy)
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
                                        tooltip tmp
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
