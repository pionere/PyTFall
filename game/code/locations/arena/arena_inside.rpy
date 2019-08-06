label arena_inside:
    # Music related:
    $ PyTFallStatic.play_music("arena_inside", fadein=1.5)

    scene bg battle_arena_1
    show screen arena_inside
    with fade

    # Predicting:
    python:
        arena_img_predict = ["chainfights", "bg battle_dogfights_1", "bg battle_arena_1"]
        arena_scr_predict = ["arena_mobs", "arena_minigame", "confirm_chainfight",
                             "arena_finished_chainfight", "arena_rep_ladder",
                             "arena_matches", "arena_ladders", "arena_dogfights",
                             "arena_bestiary", "arena_aftermatch", "arena_report"]
        renpy.start_predict(*arena_img_predict)
    python hide:
        for scr in store.arena_scr_predict:
            renpy.start_predict_screen(scr)

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")
    $ renpy.retain_after_load()

    while 1:
        $ result = ui.interact()

        if result[0] == "control":
            if result[1] == "return":
                jump arena_inside_end

        elif result[0] == "show":
            if result[1] == "bestiary":
                hide screen arena_inside
                show screen arena_bestiary

        elif result[0] == "challenge":
            if result[1] == "matches":
                $ pytfall.arena.match_challenge(result[2])
            elif result[1] == "start_dogfight":
                $ result = result[2]
                if pytfall.arena.check_arena_fight("dogfight", hero.team, result):
                    hide screen arena_inside
                    $ pytfall.arena.run_dogfight(result)
                    jump arena_inside
            elif result[1] == "start_matchfight":
                # Figure out who we're fighting:
                python:
                    for result in itertools.chain(pytfall.arena.matches_1v1, pytfall.arena.matches_2v2, pytfall.arena.matches_3v3):
                        if result[2] == day and result[0].leader == hero:
                            break

                if pytfall.arena.check_arena_fight("matchfight", hero.team, result[1]):
                    python hide:
                        # register fighting day for the other members
                        # TODO might not be the best place, but for now...
                        for t in hero.team:
                            if t != hero:
                                t.fighting_days.append(day)
                    hide screen arena_inside
                    $ pytfall.arena.run_matchfight(result)
                    jump arena_inside
            elif result[1] == "start_chainfight":
                if pytfall.arena.check_arena_fight("chainfight", hero.team, None):
                    hide screen arena_inside
                    $ pytfall.arena.run_chainfight(result[2])
                    jump arena_inside

label arena_inside_end:
    $ renpy.stop_predict(*arena_img_predict)
    python hide:
        for scr in store.arena_scr_predict:
            renpy.stop_predict_screen(scr)
    $ del arena_img_predict, arena_scr_predict

    stop world fadeout 1.5
    hide screen arena_inside
    jump arena_outside

init: # Main Screens:
    style arena_channenge_frame:
        clear
        background Frame("content/gfx/frame/p_frame4.png", 10, 10)
        yalign .5
        yoffset 2
        padding (3, 12)
        margin (0, 0)
        xysize (250, 135)

    style arena_channenge_button:
        yalign .5
        yoffset 2
        margin (0, 0)
        xysize (250, 135)
        background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
        hover_background Frame("content/gfx/frame/p_frame4.png", 10, 10)

    screen arena_inside():
        # Start match button:
        if day in hero.fighting_days and not pytfall.arena.char_in_match_results(hero):
            button:
                align .5, .28
                # xysize (200, 40)
                ypadding 15
                left_padding 15
                right_padding 40
                style "right_wood_button"
                action Return(["challenge", "start_matchfight"])
                text "Start Match!" font "fonts/badaboom.ttf" size 20 color "ivory" hover_color "crimson"

        # Kickass sign:
        frame:
            xalign .5
            ypos 39
            background Frame("content/gfx/frame/Mc_bg.png", 10, 10)
            xysize (725, 120)
            text "Get your ass kicked in our Arena!" align .5, .5 font "fonts/badaboom.ttf" color "crimson" size 45

        # LEFT FRAME:
        # Buttons:
        frame:
            style_group "content"
            pos (2, 39)
            background Frame("content/gfx/frame/p_frame5.png", 10, 10)
            xysize (280, 682)
            has vbox align .5, .03 spacing 1

            # Beast Fights:
            frame:
                background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.7), 5, 5)
                padding 10, 10
                has vbox spacing 2

                frame:
                    xfill True
                    align .5, .5
                    background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                    label "{size=28}{color=bisque}== Beast Fights ==" xalign .5 text_outlines [(1, "#3a3a3a", 0, 0)]
                hbox:
                    style_group "basic"
                    align .5, .5
                    spacing 5
                    textbutton "{size=20}{color=black}Bestiary":
                        action Return(["show", "bestiary"])
                        tooltip "Info about known enemies"
                    textbutton "{size=20}{color=black}Survival":
                        action Show("arena_mobs", transition=dissolve)
                        tooltip "Unranked fights vs beasts and monsters"

            # Ladders (Just Info):
            frame:
                background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.7), 5, 5)
                padding 10, 10
                has vbox spacing 2

                frame:
                    xfill True
                    align .5, .5
                    background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                    label "{size=28}{color=bisque}== Ladders ==" xalign .5 text_outlines [(1, "#3a3a3a", 0, 0)]
                hbox:
                    style_group "basic"
                    align .5, .5
                    spacing 5
                    textbutton "{size=20}{color=black}1v1":
                        action Show("arena_ladders", type="1v1", transition=dissolve)
                        tooltip "Best 1v1 fighters"
                    textbutton "{size=20}{color=black}2v2":
                        action Show("arena_ladders", type="2v2", transition=dissolve)
                        tooltip "Best 2v2 teams"
                    textbutton "{size=20}{color=black}3v3":
                        action Show("arena_ladders", type="3v3", transition=dissolve)
                        tooltip "Best 3v3 teams"

            # Official matches:
            frame:
                background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.7), 5, 5)
                padding 10, 10
                has vbox spacing 2

                frame:
                    xfill True
                    align .5, .5
                    background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                    label "{size=28}{color=bisque}== Matches ==" xalign .5 text_outlines [(1, "#3a3a3a", 0, 0)]
                hbox:
                    align .5, .5
                    spacing 5
                    style_group "basic"
                    textbutton "{size=20}{color=black}1v1":
                        action Show("arena_matches", type="1v1", transition=dissolve)
                        tooltip "Ranked 1v1 fights"
                    textbutton "{size=20}{color=black}2v2":
                        action Show("arena_matches", type="2v2", transition=dissolve)
                        tooltip "Ranked team 2v2 fights"
                    textbutton "{size=20}{color=black}3v3":
                        action Show("arena_matches", type="3v3", transition=dissolve)
                        tooltip "Ranked team fights 3v3 fights"


            # Dogfights:
            frame:
                background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.7), 5, 5)
                padding 10, 10
                has vbox spacing 2

                frame:
                    xfill True
                    align .5, .5
                    background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                    label ("{size=28}{color=bisque}== Dogfights ==") xalign .5 text_outlines [(1, "#3a3a3a", 0, 0)]
                hbox:
                    style_group "basic"
                    align .5, .5
                    spacing 5
                    textbutton "{size=20}{color=black}1v1":
                        action Show("arena_dogfights", type="1v1", transition=dissolve)
                        tooltip "Unranked 1v1 fights"
                    textbutton "{size=20}{color=black}2v2":
                        action Show("arena_dogfights", type="2v2", transition=dissolve)
                        tooltip "Unranked team 2v2 fights"
                    textbutton "{size=20}{color=black}3v3":
                        action Show("arena_dogfights", type="3v3", transition=dissolve)
                        tooltip "Unranked team 3v3 fights"

        # RIGHT FRAME::
        # Hero stats + Some Buttons:
        frame:
            xalign 1.0
            ypos 39
            background Frame("content/gfx/frame/p_frame5.png", 5, 5)
            xysize 282, 682
            style_prefix "proper_stats"
            has vbox align .5, .0

            null height 10

            # Player Stats:
            frame:
                xalign .5
                padding 5, 1
                background Frame("content/gfx/frame/ink_box.png", 5, 5)
                has hbox spacing 2

                frame:
                    background Frame("content/gfx/frame/MC_bg3.png", 5, 5)
                    $ img = hero.show("portrait", resize=(95, 95), cache=True)
                    padding 2, 2
                    yalign .5
                    add img align .5, .5

                # Name + Stats:
                frame:
                    padding 8, 2
                    background Frame(im.Alpha("content/gfx/frame/p_frame2.png", alpha=.6), 5, 5)
                    xsize 155
                    has vbox

                    label "[hero.name]":
                        text_size 16
                        text_bold True
                        yalign .03
                        text_color "ivory"

                    fixed: # HP:
                        ysize 25
                        $ temp, tmp = hero.get_stat("health"), hero.get_max("health")
                        bar:
                            left_bar PyTGFX.scale_img("content/gfx/interface/bars/hp1.png", 150, 20)
                            right_bar PyTGFX.scale_img("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                            value temp
                            range tmp
                            thumb None
                            xysize (150, 20)
                        text "HP" size 14 color "ivory" bold True xpos 8
                        text "[temp]" size 14 color ("red" if temp <= tmp/5 else "ivory") bold True style_suffix "value_text" xpos 125 yoffset -8

                    fixed: # MP:
                        ysize 25
                        $ temp, tmp = hero.get_stat("mp"), hero.get_max("mp")
                        bar:
                            left_bar PyTGFX.scale_img("content/gfx/interface/bars/mp1.png", 150, 20)
                            right_bar PyTGFX.scale_img("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                            value temp
                            range tmp
                            thumb None
                            xysize (150, 20)
                        text "MP" size 14 color "ivory" bold True xpos 8
                        text "[temp]" size 14 color ("red" if temp <= tmp/5 else "ivory") bold True style_suffix "value_text" xpos 125 yoffset -8

                    fixed: # VP:
                        ysize 25
                        $ temp, tmp = hero.get_stat("vitality"), hero.get_max("vitality")
                        bar:
                            left_bar PyTGFX.scale_img("content/gfx/interface/bars/vitality1.png", 150, 20)
                            right_bar PyTGFX.scale_img("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                            value temp
                            range tmp
                            thumb None
                            xysize (150, 20)
                        text "VP" size 14 color "ivory" bold True xpos 8
                        text "[temp]" size 14 color ("red" if temp <= tmp/5 else "ivory") bold True style_suffix "value_text" xpos 125 yoffset -8

            # Rep:
            $ temp = "Reputation: %d" % hero.arena_rep
            $ font_size = PyTGFX.txt_font_size(temp, 250, 25, min_size=10)
            frame:
                background Frame("content/gfx/frame/frame_bg.png", 5, 5)
                xysize (270, 70)
                label temp text_size font_size text_color "ivory" align .5, .5

            # Buttons:
            frame:
                background Frame("content/gfx/frame/frame_bg.png", 5, 5)
                style_group "basic"
                xysize (270, 110)
                vbox:
                    align (.5, .5)
                    spacing 10
                    textbutton "Show Daily Report":
                        xalign .5
                        action Show("arena_report")
                        tooltip "View yesterday's Arena events"
                    textbutton "Reputation Ladder":
                        xalign .5
                        action Show("arena_rep_ladder")
                        tooltip "View top fighters by highest reputation"

        use top_stripe(True, show_lead_away_buttons=False)

    # Screens used to display and issue challenges in the official matches inside of Arena:
    screen arena_matches(type):
        default container = getattr(pytfall.arena, "matches_%s"%type) # .matches_1v1, .matches_2v2 or .matches_3v3
        default vs_img = PyTGFX.scale_img("content/gfx/interface/images/vs_%d.webp" % (int(type[0]) + 1), 100, 100) # vs_2.webp, vs_3.webp or vs_4.webp
        modal True
        zorder 1

        frame:
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            xysize (721, 565)
            at slide(so1=(0, 1200), t1=.7, eo2=(0, 1200), t2=.7)
            pos (280, 154)

            side "c r":
                pos (5, 5)
                maximum (710, 515)
                viewport id "vp_matches":
                    draggable True
                    mousewheel True
                    child_size (710, 10000)
                    has vbox spacing 5

                    for lineup in sorted(container, key=itemgetter(2)):
                        $ off_team, def_team, event_day = lineup
                        if def_team:
                            frame:
                                style_group "content"
                                xalign .5
                                xysize (690, 150)
                                margin 0, 0
                                padding 3, 3
                                background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                                has hbox # xysize (690, 150)

                                # Day of the fight:
                                fixed:
                                    xoffset 15
                                    xysize (100, 100)
                                    align (.5, .5)
                                    frame:
                                        background Frame("content/gfx/frame/rank_frame.png", 10, 10)
                                        xsize 80
                                        vbox:
                                            xalign .5
                                            spacing 10
                                            label "Day:":
                                                xalign .5
                                                text_color "goldenrod"
                                                text_size 20
                                            label str(event_day):
                                                xalign .5
                                                text_color "goldenrod"
                                                text_size 25

                                # Challenge button:
                                if not off_team:
                                    button:
                                        style "arena_channenge_button"
                                        action Return(["challenge", "matches", lineup])
                                        vbox:
                                            align (.5, .5)
                                            style_prefix "arena_badaboom"
                                            text "Challenge!" size 40 
                                            text ("Enemy level: %s" % def_team.get_level()) outlines [(1, "#3a3a3a", 0, 0)]
                                            text ("Reputation: %s" % def_team.get_rep()) size 20 outlines [(1, "#3a3a3a", 0, 0)] 

                                # Or we show the team that challenged:
                                else:
                                    frame:
                                        style "arena_channenge_frame"
                                        $ name = off_team.gui_name
                                        $ font_size = PyTGFX.txt_font_size(name, 236, 20, min_size=10) 
                                        frame:
                                            align .5, .0
                                            xpadding 7
                                            ysize 35
                                            background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                            text name size font_size layout "nobreak" color "gold" style "proper_stats_text" yalign .5
                                        hbox:
                                            spacing 3
                                            align .5, 1.0
                                            for fighter in off_team:
                                                frame:
                                                    background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                                                    padding 2, 2
                                                    add fighter.show("portrait", resize=(60, 60), cache=True)

                                add vs_img yalign .5

                                # Waiting for the challenge or been challenged by former:
                                frame:
                                    style "arena_channenge_frame"
                                    $ name = def_team.gui_name
                                    $ font_size = PyTGFX.txt_font_size(name, 234, 25, min_size=10)
                                    frame:
                                        align .5, .0
                                        xpadding 8
                                        ysize 40
                                        background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                        text name size font_size layout "nobreak" color "gold" style "proper_stats_text" yalign .5
                                    hbox:
                                        spacing 3
                                        align .5, 1.0
                                        for fighter in def_team:
                                            frame:
                                                background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                                                padding 2, 2
                                                add fighter.show("portrait", resize=(60, 60), cache=True)

                vbar value YScrollValue("vp_matches")
            button:
                style_group "basic"
                action Hide("arena_matches"), With(dissolve)
                minimum(50, 30)
                align (.5, .9995)
                text  "Close"
                keysym "mousedown_3"

    screen arena_ladders(type):
        default ladder = getattr(pytfall.arena, "ladder_%s"%type) # .ladder_1v1, .ladder_2v2 or .ladder_3v3
        default ladder_members = getattr(pytfall.arena, "ladder_%s_members"%type) # .ladder_1v1_members, .ladder_2v2_members or .ladder_3v3_members
        modal True
        zorder 1

        frame:
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            at slide(so1=(0, 1200), t1=.7, eo2=(0, 1200), t2=.7)
            style_group "content"
            pos (280, 154)
            xysize (721, 565)

            side "c r":
                pos (5, 5)
                maximum (710, 515)
                viewport:
                    id "arena_ladders"
                    draggable True
                    mousewheel True
                    child_size (700, 10000)
                    has vbox spacing 5
                    for index, (team, members) in enumerate(zip(ladder, ladder_members), 1):
                        frame:
                            xalign .5
                            xysize (695, 60)
                            background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                            padding 1, 1
                            has hbox spacing 5
                            fixed:
                                xysize 60, 55
                                yalign .5
                                label "[index]":
                                    text_color "goldenrod"
                                    text_size 30
                                    align .5, .5
                            if team:
                                $ name = members[0].nickname if len(team) == 1 else team.name
                                $ level = sum((member.level for member in members)) / len(members)
                                frame:
                                    yalign .6
                                    xysize (100, 45)
                                    background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                    text ("Lvl %d" % level) align .5, .5 size 25 style "proper_stats_text" color "gold"
                                hbox:
                                    yoffset 1
                                    yalign .5
                                    spacing 1
                                    ysize 55
                                    for fighter in members:
                                        frame:
                                            yalign .5
                                            background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                                            padding 3, 3
                                            add fighter.show("portrait", resize=(45, 45), cache=True)
                                null width 8
                                $ size = 500 - 51 * len(members)
                                $ font_size = PyTGFX.txt_font_size(name, size, 25, min_size=10)
                                frame:
                                    yalign .6
                                    xysize (size, 45)
                                    background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                    text name size font_size layout "nobreak" color "gold" style "proper_stats_text" align .5, .5

                vbar value YScrollValue("arena_ladders")

            button:
                style_group "basic"
                action Hide("arena_ladders"), With(dissolve)
                minimum(50, 30)
                align (.5, .9995)
                text  "Close"
                keysym "mousedown_3"

    screen arena_rep_ladder():
        modal True
        zorder 1

        frame:
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            xysize (721, 565)
            at slide(so1=(0, 1200), t1=.7, eo2=(0, 1200), t2=.7)
            pos (280, 154)

            side "c r":
                pos (5, 5)
                maximum (710, 515)
                viewport id "arena_rep_vp":
                    draggable True
                    mousewheel True
                    child_size (700, 1000)
                    has vbox spacing 5
                    for index, fighter in enumerate(pytfall.arena.ladder, 1):
                        frame:
                            style_group "content"
                            xalign .5
                            xysize (690, 60)
                            background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                            has hbox spacing 20
                            textbutton "{color=red}[index]":
                                ypadding 5
                                background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                                xysize (50, 50)
                                text_size 20
                                xfill True
                            if fighter:
                                frame:
                                    background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
                                    padding 2, 2
                                    add fighter.show("portrait", resize=(40, 40), cache=True)
                                    yalign .5
                                frame:
                                    align (.5, .5)
                                    xsize 100
                                    background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                    text("Lvl [fighter.level]") align .5, .5 size 25 style "proper_stats_text" color "gold"
                                frame:
                                    xfill True
                                    align (.5, .5)
                                    background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                    hbox:
                                        xfill True
                                        align (.5, .5)
                                        text("[fighter.name]") align .03, .5 size 25 style "proper_stats_text" color "gold"
                                        text("[fighter.arena_rep]") align .99, .5 size 20 style "proper_stats_value_text" color "gold"

                vbar value YScrollValue("arena_rep_vp")

            button:
                style_group "basic"
                action Hide("arena_rep_ladder"), With(dissolve)
                minimum(50, 30)
                align (.5, .9995)
                text  "Close"
                keysym "mousedown_3"

    screen arena_dogfights(type):
        default container = getattr(pytfall.arena, "dogfights_%s"%type) # .dogfights_1v1, .dogfights_2v2 or .dogfights_3v3
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
                                action Hide("arena_dogfights"), Return(["challenge", "start_dogfight", team])
                                $ level = team.get_level()
                                vbox:
                                    align (.5, .5)
                                    text "Challenge!" style "arena_badaboom_text" size 40 outlines [(2, "#3a3a3a", 0, 0)]
                                    text "Enemy level: [level]" style "arena_badaboom_text" size 30 outlines [(1, "#3a3a3a", 0, 0)]

                            add PyTGFX.scale_img("content/gfx/interface/images/vs_1.webp", 130, 130) yalign .5

                            frame:
                                style "arena_channenge_frame"
                                $ name = team.gui_name
                                $ font_size = PyTGFX.txt_font_size(name, 234, 25, min_size=10)
                                frame:
                                    align .5, .0
                                    xpadding 8
                                    ysize 40
                                    background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                    text name size font_size layout "nobreak" color "gold" style "proper_stats_text" yalign .5
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
                action Hide("arena_dogfights"), With(dissolve)
                minimum(50, 30)
                align (.5, .9995)
                text  "Close"
                keysym "mousedown_3"

    screen arena_bestiary(focus_mob=None, return_button_action=Show("arena_inside")):
        default in_focus_mob = focus_mob
        default mob = None
        default scr_mobs = sorted(mobs.values(), key=itemgetter("min_lvl"))

        add("content/gfx/bg/locations/arena_bestiary.webp")

        vpgrid:
            at fade_in_out()
            cols 5
            ysize 720
            draggable True
            mousewheel True
            scrollbars "vertical"
            yinitial (((scr_mobs.index(focus_mob) / 5) * 216) if focus_mob else 0)
            for data in scr_mobs:
                $ creature = data["name"]
                frame:
                    background Frame("content/gfx/frame/bst.png", 5, 5)
                    margin 2, 2
                    has vbox spacing 2 xysize 180, 200
                    if data["id"] not in defeated_mobs: # <------------------------------ Note for faster search, change here to test the whole beasts screen without the need to kill mobs
                        text "-Unknown-" xalign .5 ypos -1 style "TisaOTM" color "indianred"
                        text "?" align .5, .5 size 140 color "silver" outlines [(2, "black", 0, 0)] 
                    else:
                        text creature xalign .5 style "TisaOTM" size 20 color ("ivory" if in_focus_mob == data else "gold"):
                            if len(creature) > 12:
                                size 16
                                yoffset 4
                        $ img = PyTGFX.scale_content(data["battle_sprite"], 150, 150)
                        imagebutton:
                            xalign .5
                            idle img
                            if in_focus_mob != data:
                                hover PyTGFX.bright_content(img, .15)
                                action SetScreenVariable("in_focus_mob", data)
                            else:
                                action NullAction()

        frame:
            xalign 1.0
            background Frame("content/gfx/frame/p_frame5.png")
            xysize 290, 720
            has vbox xfill True
            if in_focus_mob:
                python:
                    if not mob or mob.id != in_focus_mob["id"]:
                        mob = build_mob(id=in_focus_mob["id"])
                    data = in_focus_mob
                    portrait = im.Scale(data["portrait"], 100, 100)

                null height 5
                hbox:
                    spacing 5
                    frame:
                        background Frame("content/gfx/frame/MC_bg.png", 10, 10)
                        imagebutton:
                            xysize (100, 100)
                            background Null()
                            idle portrait
                            hover PyTGFX.bright_content(portrait, 0.15)
                            action Show("popup_info", content="trait_info_content", param=mob)

                    vbox:
                        xalign .5
                        frame:
                            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
                            xysize (145, 30)
                            text "Class" color "#CDAD00" font "fonts/Rubius.ttf" size 20 outlines [(1, "#3a3a3a", 0, 0)] xalign .5
                        vbox:
                            style_group "proper_stats"
                            spacing 1
                            for t in data["basetraits"]:
                                frame:
                                    xalign .5
                                    xysize (145, 30)
                                    text t align .5, .5 style "stats_value_text" color "#79CDCD" size 15

                null height 5
                use race_and_elements(align=(.5,.5), char=mob)
                null height 5
                # Stats:
                frame:
                    xalign .5
                    background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
                    xysize (155, 30)
                    text "Level %s" % data['min_lvl'] color "#CDAD00" font "fonts/Rubius.ttf" size 20 outlines [(1, "#3a3a3a", 0, 0)] xalign .5
                hbox:
                    xalign .5
                    spacing 2
                    vbox:
                        $ stats = ["health", "vitality", "attack", "defence", "agility"]
                        style_group "proper_stats"
                        spacing 1
                        for stat in stats:
                            frame:
                                xysize (130, 22)
                                xalign .5
                                text stat.capitalize() xalign .02 color "#43CD80" size 16
                                text str(mob.get_stat(stat)) xalign .98 style "stats_value_text" color "#79CDCD" size 17
                    vbox:
                        $ stats = ["mp", "charisma", "magic", "intelligence", "luck"]
                        style_group "proper_stats"
                        spacing 1
                        for stat in stats:
                            frame:
                                xysize (130, 22)
                                xalign .5
                                text stat.capitalize() xalign .02 color "#43CD80" size 16
                                text str(mob.get_stat(stat)) xalign .98 style "stats_value_text" color "#79CDCD" size 17
                null height 5

                # Bottom Viewport:
                viewport:
                    xalign .5
                    edgescroll (100, 100)
                    draggable True
                    mousewheel True
                    xysize 278, 328
                    child_size 278, 1000
                    has vbox xfill True
                    # Desc:
                    frame:
                        xalign .5
                        background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
                        xysize (155, 30)
                        text "Description" color "#CDAD00" font "fonts/Rubius.ttf" size 20 outlines [(1, "#3a3a3a", 0, 0)] xalign .5
                    vbox:
                        style_group "proper_stats"
                        xalign .5
                        if data["desc"]:
                                frame:
                                    xalign .5
                                    xsize 261
                                    text (data["desc"]) size 14 align .5, .5 style "stats_value_text" color "#79CDCD"
                        else:
                            frame:
                                xalign .5
                                xysize (150, 30)
                                text "-None-" size 14 align .5, .5 style "stats_value_text" color "indianred"
                    null height 5
                    hbox:
                        xalign .5
                        spacing 2
                    # Attacks:
                        vbox:
                            frame:
                                xalign .5
                                background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
                                xysize (130, 30)
                                text "Attacks" color "#CDAD00" font "fonts/Rubius.ttf" size 20 outlines [(1, "#3a3a3a", 0, 0)] xalign .5

                            vbox:
                                style_group "proper_stats"
                                xalign .5
                                if data["attack_skills"]:
                                    for skill in sorted((battle_skills[s] for s in data["attack_skills"]), key=attrgetter("menu_pos")):
                                        use skill_info(skill, 130, 20)
                                else:
                                    frame:
                                        xalign .5
                                        xysize (130, 20)
                                        text "-None-" size 15 align .5, .5 color "indianred" 

                    # Spells:
                        vbox:
                            frame:
                                xalign .5
                                background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
                                xysize (130, 30)
                                text "Spells" color "#CDAD00" font "fonts/Rubius.ttf" size 20 outlines [(1, "#3a3a3a", 0, 0)] xalign .5

                            vbox:
                                style_group "proper_stats"
                                xalign .5
                                spacing 1
                                if data["magic_skills"]:
                                    for skill in sorted((battle_skills[s] for s in data["magic_skills"]), key=attrgetter("menu_pos")):
                                        use skill_info(skill, 130, 20)
                                else:
                                    frame:
                                        xalign .5
                                        xysize (130, 20)
                                        text "-None-" size 15 align .5, .5 color "indianred"
                    null height 5
                    # Traits
                    frame:
                        xalign .5
                        background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
                        xysize (130, 30)
                        text "Traits" color "#CDAD00" font "fonts/Rubius.ttf" size 20 outlines [(1, "#3a3a3a", 0, 0)] xalign .5

                    vbox:
                        style_group "proper_stats"
                        xalign .5
                        spacing 1

                        if data["traits"]:
                            for trait in sorted(data["traits"]):
                                $ trait = traits[trait]
                                if not trait.hidden:
                                    use trait_info(trait, 147, 20)
                        else:
                            frame:
                                xalign .5
                                xysize (260, 20)
                                text "-None-" size 15 align .5, .5 color "indianred"

        imagebutton:
            pos (1233, 670)
            idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
            hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
            action Hide("arena_bestiary"), return_button_action
            keysym "mousedown_3"

    screen arena_aftermatch(l_team, r_team, combat_stats, result):
        modal True
        zorder 2

        default l_member = l_team[0]
        default r_member = r_team[0]

        if result is True:
            on "show" action Play("music", "content/sfx/music/world/win_screen.mp3")
            on "hide" action Stop(channel="music", fadeout=1.0)

            add "content/gfx/images/battle/victory_l.webp" at move_from_to_pos_with_ease(start_pos=(-config.screen_width/2, 0), end_pos=(0, 0), t=.7, wait=0)
            add "content/gfx/images/battle/victory_r.webp" at move_from_to_pos_with_ease(start_pos=(config.screen_width/2, 0), end_pos=(0, 0), t=.7)
            add "content/gfx/images/battle/battle_c.webp" at fade_from_to(start_val=.5, end_val=1.0, t=2.0, wait=0)
            add "content/gfx/images/battle/victory.webp":
                align (.5, .5)
                at simple_zoom_from_to_with_easein(start_val=50.0, end_val=1.0, t=2.0)
        elif result is False:
            add "content/gfx/images/battle/defeat_l.webp" at move_from_to_pos_with_ease(start_pos=(-config.screen_width/2, 0), end_pos=(0, 0), t=.7)
            add "content/gfx/images/battle/defeat_r.webp" at move_from_to_pos_with_ease(start_pos=(config.screen_width/2, 0), end_pos=(0, 0), t=.7)
            add "content/gfx/images/battle/battle_c.webp" at fade_from_to(start_val=.5, end_val=1.0, t=2.0, wait=0)
            add "content/gfx/images/battle/defeat.webp":
                align (.5, .5)
                at simple_zoom_from_to_with_easein(start_val=50.0, end_val=1.0, t=2.0)
        else:
            add "content/gfx/images/battle/draw_l.webp" at move_from_to_pos_with_ease(start_pos=(-config.screen_width/2, 0), end_pos=(0, 0), t=.7)
            add "content/gfx/images/battle/draw_r.webp" at move_from_to_pos_with_ease(start_pos=(config.screen_width/2, 0), end_pos=(0, 0), t=.7)
            add "content/gfx/images/battle/battle_c.webp" at fade_from_to(start_val=.5, end_val=1.0, t=2.0, wait=0)
            add "content/gfx/images/battle/draw.webp":
                align (.5, .5)
                at simple_zoom_from_to_with_easein(start_val=50.0, end_val=1.0, t=2.0)

        frame:
            background Null()
            xsize 95
            xpos 2
            yalign .5
            padding 8, 8
            margin 0, 0
            has vbox spacing 5 align(.5, .5) box_reverse True
            for i, member in enumerate(l_team):
                $ img = member.show("portrait", resize=(70, 70), cache=True)
                fixed:
                    align (.5, .5)
                    xysize (70, 70)
                    imagebutton:
                        at fade_from_to(start_val=0, end_val=1.0, t=2.0, wait=i)
                        padding 1, 1
                        margin 0, 0
                        align (.5, .5)
                        style "basic_choice2_button"
                        idle img
                        selected_idle Transform(img, alpha=1.05)
                        action SetScreenVariable("l_member", member), With(dissolve)

        frame:
            background Null()
            xsize 95
            align (1.0, .5)
            padding 8, 8
            margin 0, 0
            has vbox spacing 5 align(.5, .5)
            for i, member in enumerate(r_team):
                $ img = member.show("portrait", resize=(70, 70), cache=True)
                fixed:
                    align (.5, .5)
                    xysize (70, 70)
                    imagebutton:
                        at fade_from_to(start_val=0, end_val=1.0, t=2.0, wait=i)
                        padding 1, 1
                        margin 0, 0
                        align (.5, .5)
                        style "basic_choice2_button"
                        idle img
                        selected_idle Transform(img, alpha=1.05)
                        action SetScreenVariable("r_member", member), With(dissolve)

        button:
            xysize (100, 30)
            align (.5, .63)
            style_group "pb"
            action Return(True)
            text "Continue" style "pb_button_text" yalign 1.0 

        # Details Display for the selected members of the teams on the left/right:
        for char, xalign, fade in ((l_member, .2, True), (r_member, .8, False)):
            $ stats = combat_stats[char]
            $ img = char.show('battle_sprite', resize=(200, 200), cache=True)
            if "K.O." in stats:
                $ img = PyTGFX.sepia_content(img)
            fixed:
                xysize 200, 200
                align xalign, .2
                frame:
                    if fade:
                        at fade_from_to_with_easeout(start_val=.0, end_val=1.0, t=.9, wait=0)
                    background Frame("content/gfx/frame/MC_bg.png", 10, 10)
                    add img
                    align .5, .5
            # Show only if the char is or belongs to the hero...
            if (char == hero or getattr(char, "employer", None) == hero):
                frame:
                    style_group "proper_stats"
                    xalign xalign
                    ypos config.screen_height/2
                    background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                    padding 12, 12
                    margin 0, 0
                    has vbox spacing 1
                    for key, value in stats.iteritems():
                        if key == "K.O.":
                            text "{size=+20}{color=red}K.O." xalign 1.0
                        else:
                            frame:
                                xalign .5
                                xysize (190, 27)
                                text key xalign .02 color "#79CDCD"
                                label str(value) xalign 1.0 yoffset -1

        add "content/gfx/frame/h1.webp"

    screen arena_report():
        modal True
        frame:
            at slide(so1=(0, 1200), t1=.7, eo2=(0, 1200), t2=.7)
            pos (280, 154)
            background im.Scale("content/gfx/frame/frame_dec_1.png", 720, 580)
            xysize (720, 580)
            viewport:
                pos (50, 50)
                xysize (620, 400)
                child_size 620, 10000
                mousewheel True
                has vbox xsize 620
                $ temp = pytfall.arena.daily_report
                if not temp:
                    text "Nothing interesting happened yesterday..." color "goldenrod" align .5, .5
                else:
                    text "{size=-4}%s" % "\n".join(temp) color "goldenrod"

            button:
                style_group "basic"
                action Hide("arena_report"), With(dissolve)
                minimum (50, 30)
                align (.5, .9)
                text  "Close"
                keysym "mousedown_3"

init: # ChainFights vs Mobs:
    screen arena_mobs():
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
                for setup in Arena.all_chain_fights:
                    $ id = setup["id"]
                    $ lvl = setup["level"]
                    $ portrait = setup["boss_portrait"]
                    frame:
                        xysize (695, 55)
                        background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                        padding 1, 1
                        hbox:
                            yalign .5
                            $ font_size = PyTGFX.txt_font_size(id, 340, 25, min_size=10)
                            frame:
                                yalign .5
                                xysize (350, 45)
                                background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                text id align .5, .5 size font_size layout "nobreak" style "proper_stats_text" color "gold"
                            frame:
                                yalign .5
                                xysize (45, 45)
                                background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                add PyTGFX.scale_content(portrait, 36, 36) align (.5, .5)
                            frame:
                                yalign .5
                                xysize (100, 45)
                                background Frame("content/gfx/frame/rank_frame.png", 5, 5)
                                text("Lvl [lvl]") align .5, .5 size 25 style "proper_stats_text" color "gold"
                            button:
                                xfill True
                                ysize 60
                                background None
                                action Hide("arena_mobs"), Return(["challenge", "start_chainfight", setup])
                                align (.5, .5)
                                text "Fight!" style "arena_badaboom_text" size 40 outlines [(2, "#3a3a3a", 0, 0)]
            null height 5
            button:
                style_group "basic"
                action Hide("arena_mobs"), With(dissolve)
                minimum(50, 30)
                align (.5, .9995)
                text  "Close"
                keysym "mousedown_3"

    screen arena_minigame(data, length):
        zorder 2
        modal True

        on "show" action Play("music", "content/sfx/music/world/win_screen.mp3")
        on "hide" action Stop(channel="music", fadeout=1.0)

        default rolled = None

        text "Special Bonus Time!":
            align (.5, .1)
            italic True
            color "red"
            style "arena_header_text"
            size 75

        # Bonus Roll: ===========================================================================>>>
        default my_udd = ArenaBarMinigame(data, length)
        style_prefix "dropdown_gm"
        frame:
            align .5, .9
            xysize 300, 460

            add my_udd pos 50, 60

            # Results:
            if not rolled:
                text "Bonus Roll":
                    xalign .5 ypos 10
                    style "arena_header_text"
                    color "red"
                    size 35
            else:
                timer 3.0 action Return()
                key "mousedown_1" action Return()

                if rolled == "health":
                    text "Rolled: HP" style "arena_header_text" color "red" size 30 xalign .5 ypos 10
                elif rolled == "mp":
                    text "Rolled: MP" style "arena_header_text" color "blue" size 30 xalign .5 ypos 10
                elif rolled == "vitality":
                    text "Rolled: Vitality" style "arena_header_text" color "green" size 30 xalign .5 ypos 10
                else:
                    text "Rolled: Bupkis" style "arena_header_text" color "black" size 30 xalign .5 ypos 10

            textbutton "Stop!":
                align .5, .95
                xsize 100
                sensitive my_udd.update
                action [SetField(my_udd, "update", False),
                        SetScreenVariableC("rolled", pytfall.arena.settle_minigame,
                            udd=my_udd, data=data)]

        # Legenda:
        frame:
            align (.99, .99)
            background Frame("content/gfx/frame/p_frame4.png", 10, 10)
            padding (20, 20)
            vbox:
                spacing 10
                for color, text in [("red", "Restore HP"),
                                    ("blue", "Restore MP"),
                                    ("green", "Restore Vitality"),
                                    ("black", "Nothing...")]:
                    hbox:
                        xalign 0
                        spacing 10
                        add Solid(color, xysize=(20, 20))
                        text text style "garamond" color "goldenrod" yoffset -4

    screen confirm_chainfight(setup, encounter, mob):
        modal True

        # Fight Number:
        text "Round  [encounter]":
            at move_from_to_pos_with_ease(start_pos=(560, -100), end_pos=(560, 150), t=.7)
            italic True
            color "red"
            style "arena_header_text"
            size 45

        # Opposing Sprites:
        add hero.show("battle_sprite", resize=(200, 200), cache=True) at slide(so1=(-600, 0), t1=.7, eo2=(-1300, 0), t2=.7) align .35, .5
        add mob.leader.show("battle_sprite", resize=(200, 200)) at slide(so1=(600, 0), t1=.7, eo2=(1300, 0), t2=.7) align .65, .5

        # Title Text and Boss name if appropriate:
        if encounter == 5:
            text "Boss Fight!":
                align .5, .01
                at fade_in_out(t1=1.5, t2=1.5)
                style "arena_header_text"
                size 80
            text setup["boss_name"]:
                align .5, .75
                at fade_in_out(t1=1.5, t2=1.5)
                size 40
                outlines [(2, "black", 0, 0)]
                color "crimson"
                style "garamond"
        else:
            text setup["id"]:
                align .5, .01
                at fade_in_out(t1=1.5, t2=1.5)
                style "arena_header_text"
                size 80

        # hbox at slide(so1=(0, 700), t1=.7, so2=(0, 700), t2=.7):
        frame:
            style_prefix "dropdown_gm"
            align(.5, .9)
            has vbox spacing 10
            hbox:
                xalign .5
                textbutton "Auto":
                    action Return(True)
            hbox:
                spacing 100
                textbutton "Give Up":
                    action Return("break")
                textbutton "Fight":
                    action Return(False)

    screen arena_finished_chainfight(w_team, l_team, combat_stats, rewards):
        zorder  3
        modal True

        default winner = w_team[0]

        on "show" action Play("music", "content/sfx/music/world/win_screen.mp3")
        on "hide" action Stop(channel="music", fadeout=1.0)

        key "mousedown_3" action Return(True)
        timer 9.0 action Return(True)

        text "Victory!":
            at move_from_to_align_with_linear(start_align=(.5, .3), end_align=(.5, .03), t=2.2)
            italic True
            color "red"
            style "arena_header_text"
            size 75

        vbox:
            at fade_from_to_with_easeout(start_val=.0, end_val=1.0, t=.9)
            align .95, .5
            maximum 500, 400 spacing 30
            text "Rewards:":
                xalign .5
                style "arena_header_text"

            hbox:
                xalign .5
                spacing 10
                box_wrap True
                if rewards:
                    for reward in rewards:
                        frame:
                            background Frame("content/gfx/frame/24-1.png", 5, 5)
                            xysize (90, 90)
                            add PyTGFX.scale_content(reward.icon, 80, 80) align .5, .5
                else:
                    text "No extra rewards... this is unlucky :(":
                        xalign .5
                        style "arena_header_text"
                        size 25

        # Chars + Stats
        $ w_stats = combat_stats[winner]
        $ img = winner.show("battle", resize=(426, 376), cache=True)
        if "K.O." in w_stats:
            $ img = PyTGFX.sepia_content(img)
        frame:
            at fade_from_to_with_easeout(start_val=0, end_val=1.0, t=.9, wait=0)
            background Frame("content/gfx/frame/MC_bg.png", 10, 10)
            add img
            align .1, .5

        vbox:
            at arena_stats_slide
            pos (600, 405)
            spacing 1
            for key, value in w_stats.iteritems():
                if key == "K.O.":
                    text "{size=+20}{color=red}K.O." xalign 1.0
                else:
                    fixed:
                        xysize (170, 18)
                        text key xalign .03 style "dropdown_gm2_button_text" color "red" size 25
                        text str(value) xalign .97 style "dropdown_gm2_button_text" color "crimson" size 25
