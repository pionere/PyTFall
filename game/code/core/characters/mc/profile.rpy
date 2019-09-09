label hero_profile:
    scene bg h_profile
    with dissolve

    $ pytfall.enter_location("management", music=True, env=None)

    show screen hero_profile
    while 1:
        $ result = ui.interact()

        # To kill input error during team renaming:
        if not result:
            pass
        elif result[0] == "rename":
            $ n = None
            if result[1] == "name":
                $ n = renpy.call_screen("pyt_input", hero.name, "Enter Name", 20)
                if len(n):
                    $ hero.name = n
                    $ hero.nickname = hero.name
                    $ hero.fullname = hero.name
            elif result[1] == "nick":
                $ n = renpy.call_screen("pyt_input", hero.name, "Enter Name", 20)
                if len(n):
                    $ hero.nickname = renpy.call_screen("pyt_input", hero.name, "Enter Nick Name", 20)
            elif result[1] == "full":
                $ n = renpy.call_screen("pyt_input", hero.name, "Enter Full Name", 20)
                if len(n):
                    $ hero.fullname = n
            $ del n
        elif result[0] == "item":
            if result[1] == "transfer":
                hide screen hero_profile
                $ items_transfer([hero, hero.home])
                show screen hero_profile
        elif result[0] == 'control':
            if result[1] == 'return':
                hide screen hero_profile
                $ last_label, hero_profile_entry = hero_profile_entry, None
                jump expression last_label
        elif result[0] == "dropdown":
            if result[1] == "workplace":
                $ renpy.show_screen("set_workplace_dropdown", hero, pos=renpy.get_mouse_pos())
            elif result[1] == "home":
                $ renpy.show_screen("set_home_dropdown", hero, pos=renpy.get_mouse_pos())
            elif result[1] == "action":
                $ renpy.show_screen("set_action_dropdown", hero, pos=renpy.get_mouse_pos())
        elif result[0] == 'hero':
            if result[1] == 'equip':
                $ came_to_equip_from = "hero_profile"
                $ eqtarget = hero
                jump char_equip
        elif result[0] == "remove_from_team":
            $ hero.team.remove(result[1])
        elif result[0] == "rename_team":
            if result[1] == "set_name":
                $ n = renpy.call_screen("pyt_input", hero.team.name, "Enter Team Name", 20, (350, 200))
                if len(n):
                    $ hero.team.name = n
                $ del n
        elif result[0] == "meetup":
            hide screen mc_friends_list
            with dissolve

            python hide:
                char = result[1]
                locations_list = []
                if char.has_image("girlmeets", "beach"):
                    locations_list.append("beach")
                if char.has_image("girlmeets", "urban"):
                    locations_list.append("urban")
                if char.has_image("girlmeets", "suburb"):
                    locations_list.append("urban")
                    locations_list.append("suburb")
                if char.has_image("girlmeets", "nature"):
                    locations_list.append("nature")
                if locations_list:
                    tag = random.choice(locations_list)
                else:
                    tag = "urban"

                if tag == "beach":
                    bg = ["city_beach_cafe", "beach_cafe"]
                elif tag == "urban":
                    bg = ["main_street", "main_street"]
                elif tag == "suburb":
                    bg = ["beach_rest", "beach_main"]
                else:
                    bg = ["city_park", "city_park"]

                iam.start_int(char, img=char.show("girlmeets", tag, label_cache=True, type="reduce", gm_mode=True), bg=bg, exit="hero_profile")

# Screens:
screen hero_profile():
    default lframe_display = "status"
    default rframe_display = "skills"
    default base_ss = hero.stats.get_base_ss()

    # HERO SPRITE ====================================>
    add Transform(hero.show("vnsprite", resize=(550, 550), cache=True), alpha=.97) align .65, .9

    # BASE FRAME 2 "bottom layer" and portrait ====================================>
    add hero.show("portrait", resize=(100, 100), cache=True) pos (64, 8) # portrait should be between "Base Frame 2" and "Base Frame 1" :Gismo
    add "content/gfx/frame/h_profile1.webp"

    # BATTLE STATS ====================================>
    fixed:
        xysize (270, 270)
        pos (300, 413)
        $ temp = [float(hero.get_stat("attack"))/hero.get_max("attack"),
                  float(hero.get_stat("defence"))/hero.get_max("defence"),
                  float(hero.get_stat("agility"))/hero.get_max("agility"),
                  float(hero.get_stat("luck"))/hero.get_max("luck"),
                  float(hero.get_stat("magic"))/hero.get_max("magic")]
        add Transform(child=RadarChart(temp, 112, 126, 148, "darkgreen"), alpha=.4) align (.5, .5)
        add Transform(child=RadarChart(temp, 65, 126, 148, "green"), alpha=.3) align (.5, .5)
        add Transform(child=RadarChart(temp, 33, 126, 148, "lightgreen"), alpha=.2) align (.5, .5)
        add PyTGFX.scale_img("content/gfx/interface/images/pentagon1.png", 250, 250) align (.01, .5)

    fixed:
        $ stats = [("attack", (375, 402), "content/gfx/interface/images/atk.png", "red"),
                   ("defence", (223, 483), "content/gfx/interface/images/def.png", "darkorange"), # "chocolate" #   "#dc762c"
                   ("agility", (255, 643), "content/gfx/interface/images/agi.png", "dodgerblue"),
                   ("luck", (495, 643), "content/gfx/interface/images/luck.png", "lime"), #"springgreen" #"#00FA9A"
                   ("magic", (526, 483), "content/gfx/interface/images/mag.png", "#8470FF")] #"" #""

        for stat, pos, img, color in stats:
            $ temp = hero.get_max(stat)
            $ tmp = 80 if temp < 100 else (100 if temp < 1000 else 120)
            frame:
                pos pos
                background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                xysize tmp, 30
                hbox:
                    align .5, .5
                    add im.Scale(img, 24, 24)
                    text("{size=-5}%d|%d"%(hero.get_stat(stat), temp)):
                        yalign .5
                        font "fonts/Rubius.ttf"
                        color color
                        outlines [(1, "#0d0d0d", 0, 0)]
                if stat in base_ss:
                    button:
                        xysize 20, 20
                        offset -6, -12
                        background PyTGFX.scale_img("content/gfx/interface/icons/stars/legendary.png", 16, 16)
                        action NullAction()
                        tooltip "This is a Class Stat!"

    # LEFT FRAME (Stats/Friends/Etc) ====================================>
        # NAME^   LVL   (ok for 1m lvls) ====================================>
    fixed:
        xsize 217
        pos (2, 112)
        hbox:
            xfill True
            ysize 48
            $ temp = hero.name
            textbutton temp:
                background Null()
                text_style "TisaOTMol"
                text_size (18 if len(temp) > 12 else 28) 
                text_outlines [(2, "#424242", 0, 0)]
                align .5, .5
                action Show("char_rename", char=hero)
                tooltip "Click to rename yourself."
        hbox:
            xfill True
            ypos 52
            label "Lvl [hero.level]" text_color "#CDAD00" text_font "fonts/Rubius.ttf" text_size 16 text_outlines [(1, "#3a3a3a", 0, 0)] xalign .5
        hbox:
            xfill True
            ypos 70
            label "Tier [hero.tier]" text_color "#CDAD00" text_font "fonts/Rubius.ttf" text_size 16 text_outlines [(1, "#3a3a3a", 0, 0)] xalign .5

    vbox:
        xsize 217
        pos (8, 202)
        style_prefix "proper_stats"

        if lframe_display == "status":
            # STATS ====================================>
            vbox:
                style_group "proper_stats"
                spacing 1
                xsize 212
                $ stats = [("health", "#CD4F39"), ("mp", "#009ACD"), ("vitality", "#43CD80")]
                for stat, color in stats:
                    frame:
                        xysize (212, 27)
                        xalign .5
                        text stat.capitalize() xalign .02 color color
                        if stat in base_ss:
                            button:
                                xysize 16, 16
                                offset -5, -5
                                background PyTGFX.scale_img("content/gfx/interface/icons/stars/legendary.png", 16, 16)
                                action NullAction()
                                tooltip "This is a Class Stat!"
                        $ temp, tmp = hero.get_stat(stat), hero.get_max(stat)
                        text "%s/%s"%(temp, tmp) color ("red" if temp <= tmp*.3 else "#F5F5DC") xalign 1.0 style_suffix "value_text" xoffset -6 yoffset 4

                $ stats = ["constitution", "charisma", "intelligence", "joy"]
                for stat in stats:
                    frame:
                        xysize (212, 27)
                        xalign .5
                        text stat.capitalize() xalign .02 color "#79CDCD"
                        if stat in base_ss:
                            button:
                                xysize 16, 16
                                offset -5, -5
                                background PyTGFX.scale_img("content/gfx/interface/icons/stars/legendary.png", 16, 16)
                                action NullAction()
                                tooltip "This is a Class Stat!"
                        text "%d/%d"%(hero.get_stat(stat), hero.get_max(stat)) xalign 1.0 style_suffix "value_text" xoffset -6 yoffset 4

            null height 5

            # LOCATION ====================================>
            # No point in Work here...?
            $ circle_green = im.Scale("content/gfx/interface/icons/move15.png", 14, 14)
            hbox:
                add circle_green yalign 0.5 xoffset -2
                fixed:
                    xysize 40, 16
                    yalign .5
                    text "Home:" color "ivory" yalign .5 size 16
                button:
                    style_group "ddlist"
                    xalign .0
                    action Return(["dropdown", "home"])
                    tooltip "Choose a place to live at!"
                    text "[hero.home]":
                        if len(str(hero.home)) > 18:
                            size 14
                        else:
                            size 16
            hbox:
                add circle_green yalign 0.5 xoffset -2
                fixed:
                    xysize 40, 16
                    yalign .5
                    text "Work:" color "ivory" yalign .5 size 16
                button:
                    style_group "ddlist"
                    xalign .0
                    action Return(["dropdown", "workplace"])
                    tooltip "Choose a place to work at!"
                    text "[hero.workplace]":
                        if len(str(hero.workplace)) > 18:
                            size 14
                        else:
                            size 16
            hbox:
                add circle_green yalign 0.5 xoffset -2
                fixed:
                    xysize 40, 16
                    yalign .5
                    text "Action:" color "ivory" yalign .5 size 16
                $ temp = action_str(hero)
                button:
                    style_group "ddlist"
                    xalign .0
                    action Return(["dropdown", "action"])
                    tooltip "Pick a task!"
                    text temp size 16:
                        if len(temp) > 18:
                            size 14

        elif lframe_display == "skills":
            viewport:
                xysize (217, 500)
                mousewheel True
                vbox:
                    spacing 1
                    for skill in hero.stats.skills:
                        $ skill_val = int(hero.get_skill(skill))
                        $ skill_limit = int(hero.get_max_skill(skill))
                        # We don't care about the skill if it's less than 10% of limit:
                        if skill in base_ss or skill_val > skill_limit/10:
                            frame:
                                xoffset -4
                                xysize (212, 27)
                                xpadding 7
                                background Null()
                                text skill.capitalize() color "gold" size 18 xoffset 10 # style_suffix "value_text" 
                                if skill in base_ss:
                                    button:
                                        xysize 16, 16
                                        xoffset -3
                                        background PyTGFX.scale_img("content/gfx/interface/icons/stars/legendary.png", 16, 16)
                                        action NullAction()
                                        tooltip "This is a Class Skill!"
                                hbox:
                                    xalign 1.0
                                    yoffset 4
                                    use stars(skill_val, skill_limit)

    # BUTTONS on the "bottom layer" ------------------------------------>
    hbox:
        style_group "pb"
        spacing 1
        pos (1142, 156)
        button:
            action SetScreenVariable("rframe_display", "skills")
            text "Skills" style "pb_button_text"
        button:
            action SetScreenVariable("rframe_display", "traits")
            text "Traits" style "pb_button_text"

    # RIGHT FRAME ====================================>
    vbox:
        pos (1124, 60)
        xsize 153
        frame:
            xalign .5
            yfill True
            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
            xysize (142, 60)
            text (u"Day [day]") color "#CDAD00" font "fonts/Rubius.ttf" size 26 outlines [(1, "#3a3a3a", 0, 0)] align (.5, .6)
        null height 2
        frame:
            xalign .5
            xysize 142, 22
            style_prefix "proper_stats"
            text "Gold:" size 16  outlines [(1, "#3a3a3a", 0, 0)] color "gold" xalign .1
            text "[hero.gold]" size 14 outlines [(1, "#3a3a3a", 0, 0)] style_suffix "value_text" color "gold" xalign .9 yoffset 2

    # ATTACKS/MAGIC SKILLS ====================================>
    if rframe_display == "skills":
        vbox:
            pos (1125, 205)
            style_group "proper_stats"

            frame:
                background Frame("content/gfx/frame/hp_1.png", 5, 5)
                xysize (150, 192)
                has vbox
                label (u"Attacks:") text_size 20 text_color "ivory" text_bold True xalign .45 text_outlines [(3, "#424242", 0, 0), (2, "#8B0000", 0, 0), (1, "#424242", 0, 0)]
                viewport:
                    xysize (150, 155)
                    edgescroll (40, 40)
                    draggable True
                    mousewheel True
                    has vbox spacing 2 xfill True 
                    for skill in list(sorted(hero.attack_skills, key=attrgetter("menu_pos"))):
                        use skill_info(skill, 142, 22)

            frame:
                background Frame("content/gfx/frame/hp_1.png", 5, 5)
                xysize (150, 192)
                has vbox
                label (u"Spells:") text_size 20 text_color "ivory" text_bold True xalign .45 text_outlines [(3, "#424242", 0, 0), (2, "#104E8B", 0, 0), (1, "#424242", 0, 0)]
                viewport:
                    xysize (150, 155)
                    edgescroll (40, 40)
                    draggable True
                    mousewheel True
                    has vbox spacing 2 xfill True
                    for skill in list(sorted(hero.magic_skills, key=attrgetter("menu_pos"))):
                        use skill_info(skill, 142, 22)


    # TRAITS ====================================>
    elif rframe_display == "traits":
        frame:
            pos (1125, 205)
            background Frame("content/gfx/frame/hp_1long.png", 5, 5)
            xysize (150, 389)
            style_group "proper_stats"
            has vbox
            label (u"Traits:") text_size 20 text_color "ivory" text_bold True xalign .45
            viewport:
                xysize (150, 150)
                edgescroll (40, 40)
                draggable True
                mousewheel True
                has vbox spacing 2 xfill True
                for trait in list(t for t in hero.traits if not any([t.personality, t.race, t.elemental])):
                    if not trait.hidden:
                        use trait_info(trait, 142, 22)

            null height 10

            label (u"Effects:") text_size 20 text_color "ivory" text_bold True xalign .45
            viewport:
                xysize (150, 150)
                edgescroll (40, 40)
                draggable True
                mousewheel True
                has vbox spacing 2 xfill True
                for effect in hero.effects.itervalues():
                    use effect_info(effect, 142, 22)

    # BASE FRAME 1 "top layer" ====================================>
    add "content/gfx/frame/h_profile2.webp"

    # BUTTONS and UI elements on the "top layer" ====================================>
    hbox:
        style_prefix "pb"
        spacing 2
        pos (472, 9)
        button:
            action SetScreenVariable("lframe_display", "status"), With(dissolve)
            text "Stats" style "pb_button_text"
            tooltip "Inspect your personal statistics and place of residence"
        button:
            action SetScreenVariable("lframe_display", "skills"), With(dissolve)
            text "Skills" style "pb_button_text"
            tooltip "Check the progress of your skills"
        button:
            action Show("hero_team")
            text "Teams" style "pb_button_text"
            tooltip "Manage your teams."
        button:
            action Return(['hero', 'equip'])
            text "Equipment" style "pb_button_text"
            tooltip "Browse and manage your own inventory and equipment"
        button:
            action Show("finances", None, hero, mode="main")
            text "Finance" style "pb_button_text"
            tooltip "View the log of financial information, letting you see your income and expenses"
        button:
            action Show("mc_friends_list")
            text "Friends" style "pb_button_text"
            tooltip "Show the list friends and lovers who don't work for {}, allowing you to find them immediately when needed".format(hero.name)
        # Items Transfer to Home Location Inventory:

    # Storage button:
    frame:
        background Frame("content/gfx/frame/settings1.webp", 10, 10)
        pos 300, 5
        style_prefix "pb"
        xysize 100, 40
        showif hasattr(hero.home, "inventory"):
            button:
                align .5, .5
                action Return(["item", "transfer"])
                text "Storage" style "pb_button_text"
                tooltip "Open the location storage to leave or take items"

    imagebutton:
        pos (900, 7) # (178, 70)
        idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
        hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
        action Return(['control', 'return'])
        tooltip "Return to previous screen!"
        keysym "mousedown_3"

    # EXP BAR ====================================>
    fixed:
        pos (259, 697)
        bar:
            value hero.stats.exp + hero.stats.goal_increase - hero.stats.goal
            range hero.stats.goal_increase
            left_bar ("content/gfx/interface/bars/exp_full.png")
            right_bar ("content/gfx/interface/bars/exp_empty.png")
            thumb None
            maximum (324, 18)
        hbox:
            spacing 10
            pos (90, -17)
            xmaximum 160
            xfill True
            add "content/gfx/interface/images/exp_b.png" ypos 2 xalign .8
            text "[hero.exp]/[hero.goal]" style "proper_stats_value_text" bold True outlines [(1, "#181818", 0, 0)] color "#DAA520"

    # Race/Elements
    use race_and_elements(align=(.78, .98), char=hero)

    # AP ====================================>
    frame:
        align .5, .95
        background PyTGFX.scale_img("content/gfx/frame/frame_ap2.webp", 190, 80)
        $ temp = hero.PP / 100 # PP_PER_AP
        label str(temp):
            pos (130, -2)
            style "content_label"
            text_color "ivory"
            text_size 22

screen hero_team():
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
            xminimum (285*len(hero.team))
            hbox:
                spacing 2
                xalign .5
                label "[hero.team.name]" xalign .5 text_color "#CDAD00" text_size 30
                $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/edit.png", 24, 24)
                imagebutton:
                    idle temp
                    hover PyTGFX.bright_img(temp, .15)
                    action Return(["rename_team", "set_name"]), With(dissolve)
                    tooltip "Rename the team"

            imagebutton:
                align (1.0, .0)
                idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
                hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
                action Hide("hero_team"), With(dissolve)
                keysym "mousedown_3"
                tooltip "Close team screen"

        # Members
        hbox:
            xalign .5
            for member in hero.team:
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
                            action If(member.is_available, true=[Hide("hero_profile"),
                                                                      Hide("hero_team"),
                                                                      SetVariable("girls", [member]),
                                                                      SetVariable("char", member),
                                                                      SetVariable("char_profile_entry", "hero_profile"),
                                                                      Jump("char_profile")],
                                                                false=NullAction())
                            tooltip "See character profile"

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
                        if not member == hero:
                            $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 20, 20)
                            imagebutton:
                                xalign .92
                                idle temp
                                hover PyTGFX.bright_img(temp, .15)
                                action Return(["remove_from_team", member])
                                tooltip "Remove %s from %s"%(member.nickname, hero.team.name)

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

        # Preset teams
        for team in hero.teams:
            hbox:
                style_group "pb"
                spacing 10
                imagebutton:
                    if hero.team == team:
                        action None
                        idle im.Scale("content/gfx/interface/buttons/arrow_button_metal_gold_right.png", 24, 24)
                    else:
                        action Function(hero.remove_team, team)
                        idle im.Scale("content/gfx/interface/buttons/round_blue.png", 24, 24)
                        hover im.Scale("content/gfx/interface/buttons/round_blue_h.png", 24, 24)
                        tooltip "Dissolve"
                button:
                    xminimum 100
                    action Function(hero.select_team, team) 
                    sensitive hero.team != team
                    text "[team.name]" style "pb_button_text"
                    tooltip "Select {}".format(team.name)

        button:
            style_group "pb"
            xalign .5
            xsize 120
            action [Function(hero.new_team), Return(["rename_team", "set_name"])]
            text "..." style "pb_button_text"
            tooltip "Create new team"

screen mc_friends_list:
    modal True
    frame:
        at slide(so1=(-2000, 0), t1=.7, so2=(0, 0), t2=.3, eo2=(-2000, 0))
        xysize (930, 450)
        pos(210, 115)
        background Frame("content/gfx/frame/p_frame7.webp", 5, 5)
        $ temp = list(i for i in chain(hero.friends, hero.lovers) if i.employer != hero and i.is_available)
        $ temp = sorted(temp, key=attrgetter("name"))
        if temp:
            text "Click on the character to meet them in the city" style "TisaOTMol" size 23 xalign .5
        else:
            text "No unhired friends/lovers" style "TisaOTMol" size 23 xalign .5
        imagebutton:
            align (1.0, .0)
            idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
            hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
            action Hide("mc_friends_list"), With(dissolve)
            keysym "mousedown_3"

        vpgrid:
            ypos 40
            cols 5
            draggable True
            mousewheel True
            scrollbars "vertical"
            xysize (930, 390)

            for char in temp:
                frame:
                    background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.6), 5, 5)
                    top_padding 10
                    bottom_padding 3
                    xpadding 5
                    margin 0, 0
                    xminimum 180
                    align (.5, .5)
                    has vbox spacing 1 xalign .5
                    button:
                        padding 1, 1
                        margin 0, 0
                        align (.5, .5)
                        style "basic_choice2_button"
                        add char.show("portrait", resize=(120, 120), cache=True) align (.5, .5)
                        action Return(["meetup", char])

                    text "{=TisaOTMolxm}[char.nickname]" align (.5, 1.0) yoffset 5 xmaximum 190
                    if char in hero.lovers:
                        $ img = "content/gfx/interface/images/love.png"
                    else:
                        $ img = "content/gfx/interface/images/friendship.png"
                    add PyTGFX.scale_img(img, 35, 35) xalign .5
