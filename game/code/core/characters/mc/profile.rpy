label hero_profile:
    scene bg h_profile

    $ global_flags.set_flag("keep_playing_music")

    # $ pytfall.world_quests.run_quests("auto") Goes against squelching policy?
    $ pytfall.world_events.run_events("auto")
    $ renpy.retain_after_load()

    show screen hero_profile
    with dissolve

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

                jump expression pytfall.hp.came_from
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
                    bg = "city_beach_cafe"
                elif tag == "urban":
                    bg = "main_street"
                elif tag == "suburb":
                    bg = "beach_rest"
                else:
                    bg = "city_park"

                gm.start_gm(char, exit="hero_profile", img=char.show("girlmeets", tag, label_cache=True, resize=(300, 400), type="reduce"), bg=bg)

# Screens:
screen hero_profile():
    default lframe_display = "status"
    default rframe_display = "skills"
    default base_ss = hero.stats.get_base_ss()

    # HERO SPRITE ====================================>
    add Transform(hero.show("profile", resize=(550, 550)), alpha=.97) align .65, .9

    # BASE FRAME 2 "bottom layer" and portrait ====================================>
    add hero.show("portrait", "everyday", type="reduce", resize=(100, 100)) pos (64, 8) # portrait should be between "Base Frame 2" and "Base Frame 1" :Gismo
    add "content/gfx/frame/h_profile.webp"

    # BATTLE STATS ====================================>
    fixed:
        xysize (270, 270)
        pos (300, 413)
        add Transform(child=RadarChart((float(hero.get_stat("attack"))/hero.get_max("attack")), (float(hero.get_stat("defence"))/hero.get_max("defence")), (float(hero.get_stat("agility"))/hero.get_max("agility")),
                                       (float(hero.get_stat("luck"))/hero.get_max("luck")), (float(hero.get_stat("magic"))/hero.get_max("magic")), 112, 126, 148, "darkgreen"), alpha=.4) align (.5, .5)
        add Transform(child=RadarChart((float(hero.get_stat("attack"))/hero.get_max("attack")), (float(hero.get_stat("defence"))/hero.get_max("defence")), (float(hero.get_stat("agility"))/hero.get_max("agility")),
                                       (float(hero.get_stat("luck"))/hero.get_max("luck")), (float(hero.get_stat("magic"))/hero.get_max("magic")), 65, 126, 148, "green"), alpha=.3) align (.5, .5)
        add Transform(child=RadarChart((float(hero.get_stat("attack"))/hero.get_max("attack")), (float(hero.get_stat("defence"))/hero.get_max("defence")), (float(hero.get_stat("agility"))/hero.get_max("agility")),
                                       (float(hero.get_stat("luck"))/hero.get_max("luck")), (float(hero.get_stat("magic"))/hero.get_max("magic")), 33, 126, 148, "lightgreen"), alpha=.2) align (.5, .5)
        add ProportionalScale("content/gfx/interface/images/pentagon1.png", 250, 250) align (.01, .5)

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
                background Frame(Transform("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
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
                        background ProportionalScale("content/gfx/interface/icons/stars/legendary.png", 16, 16)
                        action NullAction()
                        tooltip "This is a Class Stat!"

    # LEFT FRAME (Stats/Friends/Etc) ====================================>
    vbox:
        xsize 217
        pos (8, 110)
        style_prefix "proper_stats"

        # NAME^   LVL   (ok for 1m lvls) ====================================>
        textbutton "[hero.name]":
            background Null()
            text_style "TisaOTMol"
            text_size 28
            text_outlines [(2, "#424242", 0, 0)]
            xalign .492
            ypos 5
            action Show("char_rename", char=hero)
            tooltip "Click to rename yourself."

        hbox:
            xsize 217
            ypos 11
            label "Lvl [hero.level]" text_color "#CDAD00" text_font "fonts/Rubius.ttf" text_size 16 text_outlines [(1, "#3a3a3a", 0, 0)] xalign .5
        hbox:
            xsize 217
            ypos 21
            label "Tier [hero.tier]" text_color "#CDAD00" text_font "fonts/Rubius.ttf" text_size 16 text_outlines [(1, "#3a3a3a", 0, 0)] xalign .5


        if lframe_display == "status":
            # STATS ====================================>
            null height 20
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
                                background ProportionalScale("content/gfx/interface/icons/stars/legendary.png", 16, 16)
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
                                background ProportionalScale("content/gfx/interface/icons/stars/legendary.png", 16, 16)
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
                $ temp = getattr(hero.action, "id", "None")
                button:
                    style_group "ddlist"
                    xalign .0
                    action Return(["dropdown", "action"])
                    tooltip "Pick a task!"
                    text temp size 16:
                        if len(temp) > 18:
                            size 14

        elif lframe_display == "skills":
            null height 26
            viewport:
                xysize (217, 500)
                mousewheel True
                vbox:
                    spacing 1
                    for skill in hero.stats.skills:
                        $ skill_val = int(hero.get_skill(skill))
                        $ skill_limit = int(hero.get_max_skill(skill))
                        # We don't care about the skill if it's less than 10% of limit:
                        if skill in base_ss or skill_val/float(skill_limit) > .1:
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
                                        background ProportionalScale("content/gfx/interface/icons/stars/legendary.png", 16, 16)
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
            background Frame(Transform("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
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
        background ProportionalScale("content/gfx/frame/frame_ap2.webp", 190, 80)
        $ temp = hero.PP / 100 # PP_PER_AP
        label str(temp):
            pos (130, -2)
            style "content_label"
            text_color "ivory"
            text_size 22

screen hero_team():
    zorder 1
    modal True

    add Transform("content/gfx/images/bg_gradient2.webp", alpha=.3)

    # Hero team ====================================>
    frame:
        style_prefix "proper_stats"
        align .58, .4
        background Frame(Transform(im.Twocolor("content/gfx/frame/ink_box.png", "white", "black"), alpha=.7), 5, 5)
        padding 10, 5
        has vbox spacing 10

        # Name of the Team / Close
        hbox:
            xminimum (285*len(hero.team))
            hbox:
                spacing 2
                xalign .5
                label "[hero.team.name]" xalign .5 text_color "#CDAD00" text_size 30
                imagebutton:
                    idle im.Scale("content/gfx/interface/buttons/edit.png", 24, 30)
                    hover im.Scale("content/gfx/interface/buttons/edit_h.png", 24, 30)
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
                        hover img
                        selected_idle Transform(img, alpha=1.05)
                        action None

                    $ img = ProportionalScale("content/gfx/interface/buttons/row_switch.png", 40, 20)
                    if not member.front_row:
                        $ img = im.Flip(img, horizontal=True)

                    imagebutton:
                        align (0, 1.0)
                        idle Transform(img, alpha=.9)
                        hover Transform(img, alpha=1.05)
                        insensitive im.Sepia(img)
                        action ToggleField(member, "front_row", true_value=1, false_value=0)
                        tooltip "Toggle between rows in battle, currently character fights from the %s row" % ("front" if member.front_row else "back")

                    if member != hero:
                        $ img = "content/gfx/interface/buttons/Profile.png"
                        imagebutton:
                            align (1.0, 1.0)
                            idle Transform(img, alpha=.9)
                            hover Transform(img, alpha=1.0)
                            insensitive im.Sepia(img)
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
                    background Frame(Transform("content/gfx/frame/P_frame2.png", alpha=.6), 5, 5)
                    has vbox spacing 4 xfill True
                    fixed:
                        xysize 158, 25
                        xalign .5
                        text "{=TisaOTMolxm}[member.name]" xalign .06
                        if not member == hero:
                            imagebutton:
                                xalign .92
                                idle ProportionalScale("content/gfx/interface/buttons/close4.png", 24, 30)
                                hover ProportionalScale("content/gfx/interface/buttons/close4_h.png", 24, 30)
                                action Return(["remove_from_team", member])
                                tooltip "Remove %s from %s"%(member.nickname, hero.team.name)

                    # HP:
                    fixed:
                        ysize 25
                        $ temp, tmp = member.get_stat("health"), member.get_max("health")
                        bar:
                            left_bar ProportionalScale("content/gfx/interface/bars/hp1.png", 150, 20)
                            right_bar ProportionalScale("content/gfx/interface/bars/empty_bar1.png", 150, 20)
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
                            left_bar ProportionalScale("content/gfx/interface/bars/mp1.png", 150, 20)
                            right_bar ProportionalScale("content/gfx/interface/bars/empty_bar1.png", 150, 20)
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
                            left_bar ProportionalScale("content/gfx/interface/bars/vitality1.png", 150, 20)
                            right_bar ProportionalScale("content/gfx/interface/bars/empty_bar1.png", 150, 20)
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
                        idle ProportionalScale("content/gfx/interface/buttons/arrow_button_metal_gold_right.png", 24, 24)
                    else:
                        action Function(hero.remove_team, team)
                        idle ProportionalScale("content/gfx/interface/buttons/round_blue.png", 24, 24)
                        hover ProportionalScale("content/gfx/interface/buttons/round_blue_h.png", 24, 24)
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

screen hero_finances():
    modal True
    zorder 1

    add Transform("content/gfx/images/bg_gradient2.webp", alpha=.3)
    frame:
        background Frame(Transform("content/gfx/frame/ink_box.png", alpha=.65), 10, 10)
        style_group "content"
        align (.5, .5)
        xysize (1120, 600)
        # side "c r":
            # area (20, 43, 1110, 495)
        viewport id "herofin_vp":
            style_group "stats"
            draggable True
            mousewheel True
            if day > 1:
                $ fin_inc = hero.fin.game_main_income_log[day-1]
                $ fin_exp = hero.fin.game_main_expense_log[day-1]

                if pytfall.hp.finance_filter == 'day':
                    label (u"Fin Report (Yesterday)") xalign .4 ypos 30 text_size 30
                    # Income:
                    vbox:
                        pos (50, 100)
                        label "Income:" text_size 20
                        null height 10
                        hbox:
                            vbox:
                                xmaximum 170
                                xfill True
                                for key in fin_inc:
                                    text "[key]"
                            vbox:
                                null height 1
                                spacing 4
                                for key in fin_inc:
                                    $ val = fin_inc[key]
                                    text "[val]" style_suffix "value_text"

                    # Expense:
                    vbox:
                        pos (450, 100)
                        label "Expense:" text_size 20
                        null height 10
                        hbox:
                            vbox:
                                xmaximum 170
                                xfill True
                                for key in fin_exp:
                                    text ("[key]")
                            vbox:
                                null height 1
                                spacing 4
                                for key in fin_exp:
                                    $ val = fin_exp[key]
                                    text ("[val]") style_suffix "value_text"

                    python:
                        total_income = 0
                        total_expenses = 0
                        for key in fin_inc:
                            total_income += fin_inc[key]
                        for key in fin_exp:
                            total_expenses += fin_exp[key]
                        total = total_income - total_expenses

                    vbox:
                        align (.80, .60)
                        text "----------------------------------------"
                        text ("Revenue: [total]"):
                            size 20
                            xpos 15
                            if total > 0:
                                color "lawngreen" style_suffix "value_text"
                            else:
                                color "red" style_suffix "value_text"

                    hbox:
                        style_group "basic"
                        align (.5, .9)
                        textbutton "Show Total" action SetField(pytfall.hp, "finance_filter", "total")

                elif pytfall.hp.finance_filter == 'total':
                    label (u"Fin Report (Game)") xalign .4 ypos 30 text_size 30
                    python:
                        income = dict()
                        for d in hero.fin.game_main_income_log:
                            for key, value in hero.fin.game_main_income_log[d].iteritems():
                                income[key] = income.get(key, 0) + value
                    # Income:
                    vbox:
                        pos (50, 100)
                        label "Income:" text_size 20
                        null height 10
                        hbox:
                            vbox:
                                xmaximum 170
                                xfill True
                                for key in income:
                                    text ("[key]")
                            vbox:
                                null height 1
                                spacing 4
                                for key in income:
                                    $ val = income[key]
                                    text ("[val]") style_suffix "value_text"

                    python:
                        expenses = dict()
                        for d in hero.fin.game_main_expense_log:
                            for key, value in hero.fin.game_main_expense_log[d].iteritems():
                                expenses[key] = expenses.get(key, 0) + value
                    # Expense:
                    vbox:
                        pos (450, 100)
                        label "Expense:" text_size 20
                        null height 10
                        hbox:
                            vbox:
                                xmaximum 170
                                xfill True
                                for key in expenses:
                                    text ("[key]")
                            vbox:
                                null height 1
                                spacing 4
                                for key in expenses:
                                    $ val = expenses[key]
                                    text ("[val]") style_suffix "value_text"

                    python:
                        game_total = 0
                        total_income = sum(income.values())
                        total_expenses = sum(expenses.values())
                        game_total = total_income - total_expenses

                    vbox:
                        align (.80, .60)
                        text "----------------------------------------"
                        text ("Revenue: [game_total]"):
                            size 20
                            xpos 15
                            style_suffix "value_text"
                            color ("lawngreen" if game_total > 0 else "red") 

                    hbox:
                        style_group "basic"
                        align (.5, .9)
                        textbutton "{size=-3}Show Daily" action SetField(pytfall.hp, "finance_filter", "day")

                hbox:
                    pos (750, 100)
                    vbox:
                        xmaximum 140
                        xfill True
                        if hero.fin.property_tax_debt:
                            text ("Property:\n(Tax Debt") color "red" size 20 outlines [(2, "#424242", 0, 0)]
                        if hero.fin.income_tax_debt:
                            text ("Income:\n(Tax Debt)") color "crimson" size 20 outlines [(2, "#424242", 0, 0)]
                        if day != 1:
                            text "Taxes:\n(This week)" size 20 outlines [(2, "#424242", 0, 0)]
                    vbox:
                        if hero.fin.property_tax_debt:
                            null height 4
                            spacing 4
                            text ("[hero.fin.property_tax_debt]\n ") color "red" style_suffix "value_text"
                        if hero.fin.income_tax_debt:
                            null height 4
                            spacing 4
                            text ("[hero.fin.income_tax_debt]\n ") color "crimson" style_suffix "value_text"
                        if day != 1:
                            python:
                                days = calendar.days.index(calendar.weekday())
                                taxes = hero.fin.get_total_taxes(days)
                            null height 4
                            spacing 4
                            text ("[taxes]\n ") style_suffix "value_text"

            # vbar value YScrollValue("herofin_vp")
        button:
            style_group "basic"
            action Hide('hero_finances'), With(dissolve)
            minimum (250, 30)
            align (.5, .96)
            text "OK"
            keysym "mousedown_3"

screen mc_friends_list:
    modal True
    frame:
        at slide(so1=(-2000, 0), t1=.7, so2=(0, 0), t2=.3, eo2=(-2000, 0))
        xysize (930, 450)
        pos(210, 115)
        background Frame("content/gfx/frame/p_frame7.webp", 5, 5)
        $ temp = list(i for i in chain(hero.friends, hero.lovers) if (i not in hero.chars) and i.is_available)
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
                    background Frame(Transform("content/gfx/frame/ink_box.png", alpha=.6), 5, 5)
                    top_padding 10
                    bottom_padding 3
                    xpadding 5
                    xmargin 0
                    ymargin 0
                    xminimum 180
                    align (.5, .5)
                    has vbox spacing 1 xalign .5
                    button:
                        ypadding 1
                        xpadding 1
                        xmargin 0
                        ymargin 0
                        align (.5, .5)
                        style "basic_choice2_button"
                        add char.show("portrait", resize=(120, 120), cache=True) align (.5, .5)
                        action Return(["meetup", char])

                    text "{=TisaOTMolxm}[char.nickname]" align (.5, 1.0) yoffset 5 xmaximum 190
                    if char in hero.lovers:
                        add ProportionalScale("content/gfx/interface/images/love.png", 35, 35) xalign .5
                    else:
                        add ProportionalScale("content/gfx/interface/images/friendship.png", 35, 35) xalign .5
