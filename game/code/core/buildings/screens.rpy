label building_management:
    python:
        # Some Global Vars we use to pass data between screens:
        if hero.buildings:
            bm_index = getattr(store, "bm_index", 0)
            if bm_index >= len(hero.buildings):
                bm_index = 0

            bm_building = hero.buildings[bm_index]
            bm_mid_frame_mode = getattr(store, "bm_mid_frame_mode", None)

            # special cursor for DragAndDrop and the original value
            mouse_drag = {"default" :[("content/gfx/interface/cursors/hand.png", 0, 0)]}
            mouse_cursor = config.mouse

    scene bg scroll

    $ renpy.retain_after_load()
    show screen building_management
    with fade

    $ global_flags.set_flag("keep_playing_music")

    while 1:
        $ result = ui.interact()
        if not result or not isinstance(result, (list, tuple)):
            pass
        elif result[0] == "bm_mid_frame_mode":
            $ bm_mid_frame_mode = result[1]
            if isinstance(bm_mid_frame_mode, ExplorationGuild):
                # Looks pretty ugly... this might be worth improving upon just for the sake of esthetics.
                $ workers = CoordsForPaging(all_chars_for_se(), columns=6, rows=3,
                        size=(80, 80), xspacing=10, yspacing=10, init_pos=(46, 9))

                $ fg_filters = CharsSortingForGui(all_chars_for_se)
                $ fg_filters.occ_filters.add("Combatant")
                $ fg_filters.target_container = [workers, "content"]
                $ fg_filters.filter()

                $ guild_teams = CoordsForPaging(bm_mid_frame_mode.idle_teams(), columns=3, rows=3,
                                size=(208, 83), xspacing=0, yspacing=5, init_pos=(4, 344))

                $ bm_exploration_view_mode = "explore"
                $ bm_selected_log_area = None
                $ bm_selected_exp_area = None

        elif result[0] == "fg_team":
            python hide:
                action = result[1]
                if action == "create":
                    n = renpy.call_screen("pyt_input", "", "Enter Name", 20)
                    if len(n):
                        t = bm_mid_frame_mode.new_team(n)
                        guild_teams.add(t)
                else:
                    team = result[2]
                    if action == "rename":
                        n = renpy.call_screen("pyt_input", team.name, "Enter Name", 20)
                        if len(n):
                            team.name = n
                    elif action == "clear":
                        for i in team:
                            workers.add(i)
                        del team.members[:]
                    elif action == "dissolve":
                        for i in team:
                            workers.add(i)
                        bm_mid_frame_mode.remove_team(team)
                        guild_teams.remove(team)
        elif result[0] == "building":
            if result[1] == 'items_transfer':
                python:
                    it_members = list(result[2])
                    it_members.sort(key=attrgetter("name"))
                hide screen building_management
                $ items_transfer(it_members)
                $ del it_members
                show screen building_management
            elif result[1] == "sign" or result[1] == "celeb":
                python hide:
                    ad = result[2]
                    price = ad['price']
                    if hero.take_money(price, reason="Building Ads"):
                        bm_building.fin.log_logical_expense(price, "Ads")
                        ad['active'] = True
                    else:
                        renpy.show_screen("message_screen", "Not enough cash on hand!")
            elif result[1] == "sell":
                python:
                    price = int(bm_building.get_price()*.9)

                    if renpy.call_screen("yesno_prompt",
                                         message="Are you sure you wish to sell %s for %d Gold?" % (bm_building.name, price),
                                         yes_action=Return(True), no_action=Return(False)):
                        if hero.home == bm_building:
                            hero.home = pytfall.streets
                        if hero.workplace == bm_building:
                            hero.reset_workplace_action()

                        retire_chars_from_building(hero.chars, bm_building)

                        hero.add_money(price, reason="Property")
                        hero.remove_building(bm_building)
                        # 'cleanup' the building
                        for price in bm_building.adverts:
                            price['active'] = False
                        del price
                        bm_building.dirt = 0
                        bm_building.threat = 0

                        if hero.buildings:
                            if bm_index >= len(hero.buildings):
                                bm_index = 0
                            bm_building = hero.buildings[bm_index]
                        else:
                            jump("building_management_end")
                    else:
                        del price
        # Upgrades:
        elif result[0] == 'upgrade':
            if result[1] == "build":
                python hide:
                    temp = result[2]
                    if isinstance(temp, Business):
                        bm_building.add_business(temp, normalize_jobs=True, pay=True)
                    else:
                        result[3].add_upgrade(temp, pay=True)
        elif result[0] == "maintenance":
            python:
                # Cleaning controls
                if result[1] == "clean":
                    price = bm_building.get_cleaning_price()
                    if hero.take_money(price, reason="Pro-Cleaning"):
                        bm_building.fin.log_logical_expense(price, "Pro-Cleaning")
                        bm_building.dirt = 0
                    else:
                        renpy.show_screen("message_screen", "You do not have the required funds!")
                    del price
                elif result[1] == "clean_all":
                    if hero.take_money(result[2], reason="Pro-Cleaning"):
                        for i in hero.dirty_buildings:
                            i.fin.log_logical_expense(i.get_cleaning_price(), "Pro-Cleaning")
                            i.dirt = 0
                        del i
                    else:
                        renpy.show_screen("message_screen", "You do not have the required funds!")
                elif result[1] == "toggle_clean":
                    bm_building.auto_clean = 50 if bm_building.auto_clean == 100 else 100
                elif result[1] == "rename_building":
                    bm_building.name = renpy.call_screen("pyt_input", default=bm_building.name, text="Enter Building name:")
        elif result[0] == 'control':
            if result[1] == 'return':
                jump building_management_end

            if result[1] == 'left':
                $ bm_index -= 1
                if bm_index < 0:
                    $ bm_index = len(hero.buildings) - 1
            else: # if result[1] == 'right':
                $ bm_index += 1
                if bm_index >= len(hero.buildings):
                    $ bm_index = 0

            $ bm_building = hero.buildings[bm_index]

label building_management_end:
    hide screen building_management

    jump mainscreen
    with dissolve

init:
    # Screens:
    screen building_management():
        if hero.buildings:
            # Main Building mode:
            frame:
                background Frame(Transform("content/gfx/frame/p_frame6.png", alpha=.98), 10, 10)
                style_prefix "content"
                xysize (630, 680)
                xalign .5
                ypos 40
    
                if bm_mid_frame_mode is None:
                    use building_management_midframe_building_mode
                elif isinstance(bm_mid_frame_mode, ExplorationGuild):
                    use building_management_midframe_exploration_guild_mode
                else: # Upgrade mode:
                    use building_management_midframe_businesses_mode

            ## Stats/Upgrades - Left Frame
            frame:
                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                xysize (330, 680)
                # xanchor .01
                ypos 40
                style_group "content"
                has vbox xfill True
                if bm_mid_frame_mode is None:
                    use building_management_leftframe_building_mode
                elif isinstance(bm_mid_frame_mode, ExplorationGuild):
                    use building_management_leftframe_exploration_guild_mode
                else: # Upgrade mode:
                    use building_management_leftframe_businesses_mode

            ## Right frame:
            frame:
                xysize (330, 680)
                ypos 40
                xalign 1.0
                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                has vbox xfill True spacing 1
                if bm_mid_frame_mode is None:
                    use building_management_rightframe_building_mode
                else: # Upgrade mode:
                    use building_management_rightframe_businesses_mode
        else:
            text "You don't own any buildings.":
                size 50
                color "ivory"
                align .5, .5
                style "TisaOTM"

        use top_stripe(True, show_lead_away_buttons=False)
        if not bm_mid_frame_mode is None:
            key "mousedown_3" action Function(setattr, config, "mouse", mouse_cursor), Return(["bm_mid_frame_mode", None])
        else:
            key "mousedown_4" action Return(["control", "right"])
            key "mousedown_5" action Return(["control", "left"])

    screen building_management_rightframe_building_mode:
        # Buttons group:
        frame:
            xalign .5
            style_prefix "wood"
            xpadding 0
            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.9), 5, 5)
            has hbox xalign .5 spacing 5 xsize 315
            null height 16
            vbox:
                spacing 5
                button:
                    xysize (135, 40)
                    action Show("building_adverts")
                    sensitive len(bm_building.adverts) != 0
                    tooltip 'Advertise this building to attract more and better customers'
                    text "Advertise"
                $ bm_building_chars = set(bm_building.inhabitants)
                if hasattr(bm_building, "all_workers"):
                    $ bm_building_chars.update(bm_building.all_workers)
                if hasattr(bm_building, "inventory"):
                    $ bm_building_chars.add(bm_building)
                $ bm_building_chars.add(hero)
                button:
                    xysize (135, 40)
                    action Return(['building', "items_transfer", bm_building_chars])
                    tooltip 'Transfer items between characters in this building'
                    sensitive len(bm_building_chars) > 1
                    text "Transfer Items"
                button:
                    xysize (135, 40)
                    action Show("building_controls")
                    tooltip 'Perform maintenance of this building'
                    text "Controls"
            vbox:
                spacing 5
                button:
                    xysize (135, 40)
                    action SetField(hero, "home", bm_building)
                    tooltip 'Settle in the building!'
                    sensitive hero.home != bm_building and bm_building.vacancies > 0
                    text "Settle"
                button:
                    xysize (135, 40)
                    action Show("finances", None, bm_building, mode="logical")
                    tooltip 'Show finance log for this building'
                    sensitive hasattr(bm_building, "fin")
                    text "Finance Log"
                button:
                    xysize (135, 40)
                    action Return(["building", "sell"])
                    tooltip 'Get rid of this building'
                    sensitive bm_building.can_sell()
                    text "Sell"

        # Slots for New Style Buildings:
        $ c0 = bm_building.in_slots_max != 0
        $ c1 = bm_building.ex_slots_max != 0 
        $ c2 = bm_building.workable
        $ c3 = bm_building.habitable
        if any([c0, c1, c2, c3]):
            frame:
                xalign .5
                style_prefix "proper_stats"
                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.9), 5, 5)
                padding 10, 10
                has vbox xalign .5 spacing 2

                if c0:
                    frame:
                        xysize (296, 27)
                        text "Indoor Slots:" xalign .02 color "ivory"
                        text "%d/%d" % (bm_building.in_slots, bm_building.in_slots_max) xalign .98 style_suffix "value_text"
                if c1:
                    frame:
                        xysize (296, 27)
                        text "Outdoor Slots:" xalign .02 color "ivory"
                        text "%d/%d" % (bm_building.ex_slots, bm_building.ex_slots_max) xalign .98 style_suffix "value_text"
                if c2:
                    frame:
                        xysize (296, 27)
                        text "Workable Capacity:" xalign .02 color "ivory"
                        text "[bm_building.workable_capacity]" xalign .98 style_suffix "value_text"
                if c3:
                    frame:
                        xysize (296, 27)
                        text "Inhabitants:" xalign .02 color "ivory"
                        text "%d/%d" % (len(bm_building.inhabitants),bm_building.habitable_capacity) xalign .98 style_suffix "value_text"

            null height 20

        # Manager?
        if getattr(bm_building, "needs_manager", False):
            $ managers = simple_jobs["Manager"]
            $ managers = [w for w in bm_building.all_workers if w.job == managers]
            vbox:
                xalign .5
                $ temp = ("Current manager" if len(managers) == 1 else "Managers") if managers else "No manager" 
                text "[temp]" align (.5, .5) size 25 color "goldenrod" drop_shadow [(1, 2)] drop_shadow_color "black" antialias True style_prefix "proper_stats"                
                if len(managers) <= 1:
                    frame:
                        xmaximum 220
                        ymaximum 220

                        xalign .5
                        background Frame(Transform("content/gfx/frame/MC_bg3.png", alpha=.95), 10, 10)
                        if managers:
                            $ w = managers[0]
                            $ img = w.show("profile", resize=(190, 190), add_mood=True, cache=True)
                            imagebutton:
                                idle img
                                hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                                action If(w.is_available, true=[SetVariable("char", w),
                                                                SetVariable("eqtarget", w),
                                                                SetVariable("equip_girls", [w]),
                                                                SetVariable("came_to_equip_from", last_label),
                                                                Jump("char_equip")],
                                                          false=NullAction())
                                tooltip "Check %s's equipment" % w.name
                else:
                    $ managers.sort(key=attrgetter("level"), reverse=True)
                    frame:
                        background Null()
                        
                        xysize 300, 220
                        vpgrid:
                            xpos 5
                            style_group "dropdown_gm"
                            xysize 300, 200
                            cols 5
                            spacing 2
                            draggable True
                            mousewheel True
                    
                            for w in managers:
                                frame:
                                    xysize 60, 60
                                    padding 5, 5
                                    background Frame("content/gfx/frame/p_frame53.png", 5, 5)
                                    $ img = w.show("portrait", resize=(50, 50), cache=True)
                                    imagebutton:
                                        idle img
                                        hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                                        action If(w.is_available, true=[SetVariable("char", w),
                                                                        SetVariable("eqtarget", w),
                                                                        SetVariable("equip_girls", [w]),
                                                                        SetVariable("came_to_equip_from", last_label),
                                                                        Jump("char_equip")],
                                                                  false=NullAction())
                                        tooltip "Check %s's equipment" % w.name

            null height 20
        if bm_building.desc:
            text bm_building.desc xalign.5 style_prefix "proper_stats" text_align .5 color "goldenrod" outlines [(1, "#3a3a3a", 0, 0)]

    screen building_management_rightframe_businesses_mode:
        $ frgr = Fixed(xysize=(315, 680))
        $ frgr.add(ProportionalScale("content/gfx/images/e1.png", 315, 600, align=(.5, .0)))
        $ frgr.add(ProportionalScale("content/gfx/images/e2.png", 315, 600, align=(.5, 1.0)))
        frame:
            style_prefix "content"
            xysize 315, 680
            background Null()
            foreground frgr
            frame:
                pos 25, 20
                xysize 260, 40
                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                label str(bm_mid_frame_mode.name) text_size 18 text_color "ivory" align .5, .6

            if isinstance(bm_mid_frame_mode, Business) and hasattr(bm_building, "all_workers"):
                $ workers = [w for w in bm_building.all_workers if w.job in bm_mid_frame_mode.jobs]
                if workers:
                    $ workers.sort(key=attrgetter("level"), reverse=True)
                    hbox:
                        pos (0, 70)
                        xsize 315
                        text "Staff:" align (.5, .5) size 25 color "goldenrod" drop_shadow [(1, 2)] drop_shadow_color "black" antialias True style_prefix "proper_stats"
                        
                    vpgrid:
                        pos (5, 120)
                        style_group "dropdown_gm"
                        xysize 300, 420
                        cols 5
                        spacing 2
                        draggable True
                        mousewheel True
                
                        for w in workers:
                            frame:
                                xysize 60, 60
                                padding 5, 5
                                background Frame("content/gfx/frame/p_frame53.png", 5, 5)
                                $ img = w.show("portrait", resize=(50, 50), cache=True)
                                imagebutton:
                                    idle img
                                    hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                                    action If(w.is_available, true=[SetVariable("char", w),
                                                                    SetVariable("eqtarget", w),
                                                                    SetVariable("equip_girls", [w]),
                                                                    SetVariable("came_to_equip_from", last_label),
                                                                    Jump("char_equip")],
                                                              false=NullAction())
                                    tooltip "Check %s's equipment" % w.name
                               
            
            frame:
                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                align .5, .95
                padding 10, 10
                vbox:
                    style_group "wood"
                    align .5, .5
                    spacing 10
                    if isinstance(bm_mid_frame_mode, ExplorationGuild):
                        use building_management_rightframe_exploration_guild_mode
                    button:
                        xysize 150, 40
                        yalign .5
                        action Return(["bm_mid_frame_mode", None])
                        tooltip ("Back to the main overview of the building.")
                        text "Back" size 15

    screen building_management_leftframe_building_mode:
        frame:
            background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            style_prefix "proper_stats"
            xsize 316
            padding 10, 10
            has vbox spacing 1

            frame:
                xysize (296, 27)
                text "Location:" xalign .02 color "ivory"
                text "[bm_building.location]" xalign .98 style_suffix "value_text" yoffset 4

            # Dirt:
            if bm_building.maxdirt != 0:
                frame:
                    xysize (296, 27)
                    text "Dirt:" xalign .02 color "brown"
                    $ tmp = bm_building.get_dirt_percentage()
                    $ temp = ("Immaculate", "Sterile", "Spotless", "Clean", "Tidy",
                              "Messy", "Dirty", "Grimy", "Filthy", "Disgusting")
                    $ temp = temp[min(9, tmp/10)]
                    text "%s (%d %%)" % (temp, tmp) xalign .98 style_suffix "value_text" yoffset 4
            # Threat
            if bm_building.maxthreat != 0:
                frame:
                    xysize (296, 27)
                    text "Threat:" xalign .02 color "crimson"
                    text "%s %%" % bm_building.get_threat_percentage():
                        xalign .98
                        style_suffix "value_text"
                        yoffset 4
            if hasattr(bm_building, "tier"):
                frame:
                    xysize (296, 27)
                    text "Tier:" xalign .02 color "ivory"
                    text "%s" % (bm_building.tier) xalign .98 style_suffix "value_text" yoffset 4

            # Fame/Rep:
            if bm_building.maxfame != 0:
                frame:
                    xysize (296, 27)
                    text "Fame:" xalign .02 color "ivory"
                    text "%s/%s" % (bm_building.fame, bm_building.maxfame) xalign .98 style_suffix "value_text" yoffset 4
            if bm_building.maxrep != 0:
                frame:
                    xysize (296, 27)
                    text "Reputation:" xalign .02 color "ivory"
                    text "%s/%s" % (bm_building.rep, bm_building.maxrep) xalign .98 style_suffix "value_text" yoffset 4

        null height 5
        frame:
            background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            xysize (317, 480)
            if bm_building._businesses or bm_building._upgrades:
                frame:
                    align .5, .02
                    background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                    xysize (180, 40)
                    label 'Constructed:' text_color "ivory" xalign .5 text_bold True
                viewport:
                    pos 3, 55
                    xysize 310, 406
                    mousewheel True
                    scrollbars "vertical"
                    draggable True
                    has vbox
                    # Businesses
                    for u in bm_building._businesses:
                        frame:
                            xalign .6
                            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 5, 5)
                            has fixed xysize 280, 80
                            frame:
                                align .05, .1
                                background Frame(Transform("content/gfx/frame/MC_bg3.png", alpha=.95), 10, 10)
                                if hasattr(u, "img"):
                                    add im.Scale(u.img, 100, 65) align .5, .5
                                else:
                                    add Solid("black", xysize=(100, 65)) align .5, .5
                            vbox:
                                xpos 125
                                yalign .5
                                xysize 150, 60
                                text "[u.name]" xalign .5 style "proper_stats_text" size 20
                                null height 2
                                textbutton "{size=15}{font=fonts/TisaOTM.otf}{color=goldenrod}Details":
                                    background Transform(Frame("content/gfx/interface/images/story12.png"), alpha=.8)
                                    hover_background Transform(Frame(im.MatrixColor("content/gfx/interface/images/story12.png", im.matrix.brightness(.15))), alpha=1)
                                    tooltip "View details or expand {}.\n{}".format(u.name, u.desc)
                                    xalign .5
                                    top_padding 4
                                    action Return(["bm_mid_frame_mode", u])

                            if u.can_close():
                                imagebutton:
                                    align 1.0, 0 offset 2, -2
                                    idle ProportionalScale("content/gfx/interface/buttons/close4.png", 20, 24)
                                    hover ProportionalScale("content/gfx/interface/buttons/close4_h.png", 20, 24)
                                    action Show("yesno_prompt",
                                                message="Are you sure you wish to close this %s for %d Gold?" % (u.name, u.get_cost()[0]),
                                                yes_action=[Function(bm_building.close_business, u), Hide("yesno_prompt")], no_action=Hide("yesno_prompt"))
                                    tooltip "Close the business"
                    # Upgrades
                    for u in bm_building._upgrades:
                        frame:
                            xalign .6
                            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 5, 5)
                            has fixed xysize 280, 80
                            frame:
                                align .05, .1
                                background Frame(Transform("content/gfx/frame/MC_bg3.png", alpha=.95), 10, 10)
                                if hasattr(u, "img"):
                                    add im.Scale(u.img, 100, 65) align .5, .5
                                else:
                                    add Solid("black", xysize=(100, 65)) align .5, .5

    screen building_management_leftframe_businesses_mode:
        frame:
            background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            style_group "proper_stats"
            xsize 314
            padding 12, 12
            margin 0, 0
            has vbox spacing 1
            # Slots:
            frame:
                xysize (290, 27)
                xalign .5
                text "Indoor Slots:" xalign .02 color "ivory"
                text "[bm_mid_frame_mode.in_slots]"  xalign .98 style_suffix "value_text"
            frame:
                xysize (290, 27)
                xalign .5
                text "Exterior Slots:" xalign .02 color "ivory"
                text "[bm_mid_frame_mode.ex_slots]"  xalign .98 style_suffix "value_text"
            if bm_mid_frame_mode.capacity or getattr(bm_mid_frame_mode, "expands_capacity", False):
                frame:
                    xysize (290, 27)
                    xalign .5
                    text "Capacity:" xalign .02 color "ivory"
                    text "[bm_mid_frame_mode.capacity]"  xalign .98 style_suffix "value_text"

        if getattr(bm_mid_frame_mode, "expands_capacity", False):
            null height 5
            frame:
                background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                style_prefix "proper_stats"
                xsize 314
                padding 12, 12
                margin 0, 0
                has vbox spacing 1

                text "To Expand:"

                $ cost, materials, in_slots, ex_slots = bm_mid_frame_mode.get_expansion_cost()
                $ can_build = True

                # Materials and GOLD
                vpgrid:
                    cols 3
                    xsize 290
                    spacing 2
                    frame:
                        xysize (95, 27)
                        has hbox xysize (95, 27)
                        imagebutton:
                            idle ProportionalScale("content/gfx/animations/coin_top 0.13 1/1.webp", 20, 20)
                            xysize 20, 20
                            align 0.2, .5
                            action NullAction()
                            tooltip "Gold"
                        if hero.gold >= cost:
                            text "[cost]" xalign .9 style_suffix "value_text"
                        else:
                            $ can_build = False
                            text "[cost]" xalign .9 color "grey" style_suffix "value_text"

                    for r, amount in materials.items():
                        $ r = items[r]
                        frame:
                            xysize (95, 27)
                            has hbox xysize (95, 27)
                            imagebutton:
                                idle ProportionalScale(r.icon, 20, 20)
                                xysize 20, 20
                                align 0.2, .5
                                action NullAction()
                                tooltip "{}".format(r.id)
                            if hero.inventory[r.id] >= amount:
                                text "[amount]" xalign .9 style_suffix "value_text"
                            else:
                                $ can_build = False
                                text "[amount]" xalign .9 color "grey" style_suffix "value_text"

                vpgrid:
                    cols 2
                    xsize 290
                    spacing 2
                    if in_slots:
                        frame:
                            xysize (144, 27)
                            has hbox xysize (144, 27)
                            text "Indoor Slots:" xalign .1
                            if (bm_building.in_slots_max - bm_building.in_slots) >= in_slots:
                                text "[in_slots]" xalign .8 style_suffix "value_text"
                            else:
                                $ can_build = False
                                text "[in_slots]" xalign .8 color "grey" style_suffix "value_text"
                    if ex_slots:
                        frame:
                            xysize (144, 27)
                            has hbox xysize (144, 27)
                            text "Exterior Slots:" xalign .1
                            if (bm_building.ex_slots_max - bm_building.ex_slots) >= ex_slots:
                                text "[ex_slots]" xalign .8 style_suffix "value_text"
                            else:
                                $ can_build = False
                                text "[ex_slots]" xalign .8 color "grey" style_suffix "value_text"
                null height 1
                textbutton "Expand Capacity":
                    style "pb_button"
                    xalign .5
                    action [Function(bm_mid_frame_mode.expand_capacity),
                            Play("audio", "content/sfx/sound/world/purchase_1.ogg"), SensitiveIf(can_build)]
                    tooltip "Expand the business!"
                null height 5
                text "To Cut Back:"
                vbox:
                        #has vbox
                        frame:
                            xysize (290, 27)
                            xalign .5
                            text "Indoor Slots Freed:" xalign .02 color "ivory"
                            text "[in_slots]"  xalign .98 style_suffix "value_text"
                        frame:
                            xysize (290, 27)
                            xalign .5
                            text "Exterior Slots Freed:" xalign .02 color "ivory"
                            text "[ex_slots]"  xalign .98 style_suffix "value_text"
                        frame:
                            xysize (290, 27)
                            xalign .5
                            text "Cost:" xalign .02 color "ivory"
                            text "[cost]"  xalign .98 style_suffix "value_text"
                null height 1
                textbutton "Reduce Capacity":
                    style "pb_button"
                    xalign .5
                    if bm_mid_frame_mode.can_reduce_capacity():
                        action [Function(bm_mid_frame_mode.reduce_capacity),
                            Play("audio", "content/sfx/sound/world/purchase_1.ogg")]
                        tooltip "Add more space to the building!"
                    else:
                        action NullAction()
                        tooltip "The only remaining option is to close the business"

        if getattr(bm_mid_frame_mode, "upgrades", None):
            null height 5
            frame:
                align .5, .02
                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                xysize (180, 40)
                label 'Constructed:' text_color "ivory" xalign .5 text_bold True
            viewport:
                pos 3, 10
                xysize 310, 406
                mousewheel True
                scrollbars "vertical"
                has vbox
                for u in bm_mid_frame_mode.upgrades:
                    button:
                        xsize 309
                        style "pb_button"
                        text "[u.name]":
                            align .5, .5
                            color "ivory"
                        action NullAction()
                        tooltip u.desc

    screen building_management_midframe_building_mode:
        frame:
            xalign .5
            xysize (380, 50)
            background Frame("content/gfx/frame/namebox5.png", 10, 10)
            label (u"[bm_building.name]") text_size 23 text_color "ivory" align (.5, .6)

        frame:
            align .5, .0
            ypos 60
            background Frame(Transform("content/gfx/frame/MC_bg3.png", alpha=.95), 10, 10)
            add pscale(bm_building.img, 600, 444)

        # Left/Right Controls + Expand button:
        vbox:
            align .5, .99
            frame:
                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.9), 10, 10)
                has hbox xysize (600, 74)
                button:
                    align .1, .5
                    xysize (140, 40)
                    style "left_wood_button"
                    action Return(['control', 'left'])
                    text "Previous" style "wood_text" xalign .69
                frame:
                    background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                    xysize 200, 50
                    align (.5, .5)
                    if len(bm_building.all_possible_extensions()) != 0:
                        button:
                            style_prefix "wood"
                            align .5, .5
                            xysize 135, 40
                            action Return(["bm_mid_frame_mode", bm_building])
                            tooltip 'Open a new business or upgrade this building!'
                            text "Expand"
                button:
                    align .9, .5
                    xysize (140, 40)
                    style "right_wood_button"
                    action Return(['control', 'right'])
                    text "Next" style "wood_text" xalign .39

    screen building_management_midframe_businesses_mode:
        viewport:
            xysize 620, 668
            mousewheel True
            xalign .5
            has vbox xsize 618
            if hasattr(bm_mid_frame_mode, "all_possible_extensions"):
                for u in bm_mid_frame_mode.all_possible_extensions():
                    if not bm_mid_frame_mode.has_extension(u.__class__):
                        frame:
                            xalign .5
                            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                            has fixed xysize 500, 150

                            $ cost, materials, in_slots, ex_slots = u.get_cost()
                            $ can_build = True
                            hbox:
                                xalign .5
                                xsize 340
                                textbutton "[u.name]":
                                    xalign .5
                                    ypadding 2
                                    style "stats_text"
                                    text_outlines [(1, "black", 0, 0)]
                                    text_size 23
                                    action NullAction()
                                    tooltip u.desc

                            # Materials and GOLD
                            vbox:
                                pos 5, 36
                                box_wrap True
                                xysize 340, 80
                                spacing 2
                                frame:
                                    background Frame("content/gfx/frame/p_frame5.png", 5, 5)
                                    xsize 100
                                    has hbox xsize 90
                                    button:
                                        background Frame("content/gfx/animations/coin_top 0.13 1/1.webp")
                                        xysize 25, 25
                                        align 0, .5
                                        action NullAction()
                                        tooltip "Gold"
                                    style_prefix "proper_stats"
                                    if hero.gold >= cost:
                                        text "[cost]" align .95, .5
                                    else:
                                        $ can_build = False
                                        text "[cost]" align .95, .5 color "grey"

                                # We presently allow for 3 resources each upgrade. If more, this needs to be a conditioned viewport:
                                for r, amount in materials.items():
                                    $ r = items[r]
                                    frame:
                                        background Frame("content/gfx/frame/p_frame5.png", 5, 5)
                                        xsize 100
                                        has hbox xsize 90
                                        button:
                                            xysize 25, 25
                                            background Frame(r.icon)
                                            align 0, .5
                                            action NullAction()
                                            tooltip "{}".format(r.id)
                                        style_prefix "proper_stats"
                                        if hero.inventory[r.id] >= amount:
                                            text "[amount]" align .95, .5
                                        else:
                                            $ can_build = False
                                            text "[amount]" align .95, .5 color "grey"

                            hbox:
                                align .01, .98
                                spacing 2
                                style_prefix "proper_stats"
                                if in_slots:
                                    text "Indoor Slots:"
                                    if (bm_building.in_slots_max - bm_building.in_slots) >= in_slots:
                                        text "[in_slots]"
                                    else:
                                        $ can_build = False
                                        text "[in_slots]" color "grey"
                                if ex_slots:
                                    text "Exterior Slots:"
                                    if (bm_building.ex_slots_max - bm_building.ex_slots) >= ex_slots:
                                        text "[ex_slots]"
                                    else:
                                        $ can_build = False
                                        text "[ex_slots]" color "grey"

                            vbox:
                                align 1.0, .8
                                xsize 150
                                spacing 4
                                button:
                                    xalign .5
                                    xysize 133, 83
                                    background Frame("content/gfx/frame/MC_bg3.png", 3, 3)
                                    foreground Transform(u.img, size=(120, 75), align=(.5, .5))
                                    action NullAction()
                                    tooltip u.desc
                                textbutton "Build":
                                    xalign .5
                                    style "pb_button"
                                    text_size 15
                                    action [Return(["upgrade", "build", u, bm_mid_frame_mode]),
                                            SensitiveIf(can_build)]

    screen building_controls():
        modal True
        zorder 1

        frame:
            style_prefix "content"
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            at slide(so1=(600, 0), t1=.7, eo2=(1300, 0), t2=.7)
            xpos 936
            yalign .95
            xysize(343, 675)

            # Controls themselves ---------------------------------->
            vbox:
                style_group "basic"
                xalign .5 ypos 30

                button:
                    xysize (200, 32)
                    xalign .5
                    action Return(['maintenance', "rename_building"])
                    tooltip "Give new name to your Building!"
                    text "Rename Building"

                if bm_building.maxthreat != 0:
                    null height 20
                    label (u"Guarding Options:"):
                        style "proper_stats_label"
                        align .5, .05
                        text_bold True
                    null height 5

                    hbox:
                        xysize(200,32)
                        xalign .5
                        if bm_building.auto_guard != 0:
                            button:
                                xysize(170,32)
                                xalign .1
                                selected True
                                text "%d Gold a day" % bm_building.auto_guard
                                tooltip "Hired guards are protecting your building for % Gold per day." % bm_building.auto_guard
                                action SetField(bm_building, "auto_guard", 0)
                            vbox:
                                xysize 20, 32
                                xalign 1.0
                                button:
                                    xysize 20, 16
                                    background None
                                    text "+" style "proper_stats_text" hover_color "red" align (.5, .5)
                                    action SensitiveIf(bm_building.auto_guard < 9900), SetField(bm_building, "auto_guard", bm_building.auto_guard+100)
                                button:
                                    xysize 20, 16
                                    background None
                                    text "_" style "proper_stats_text" hover_color "red" align (.5, 1.1)
                                    action SetField(bm_building, "auto_guard", bm_building.auto_guard-100)
                        else:
                            button:
                                xysize(200,32)
                                xalign .5
                                action SetField(bm_building, "auto_guard", 100)
                                tooltip "Hire professional guards to protect your building."
                                text "Hire Guards"

                if bm_building.maxdirt != 0:
                    null height 20
                    label (u"Cleaning Options:"):
                        style "proper_stats_label"
                        align .5, .05
                        text_bold True
                    null height 5

                    hbox:
                        xysize(200,32)
                        xalign .5
                        bar:
                            xmaximum 120
                            align (.5, .5)
                            if bm_building.auto_clean == 100:
                                value 100
                                range 100
                            else:
                                value FieldValue(bm_building, "auto_clean", 99, style='scrollbar', offset=0, step=1)
                                thumb 'content/gfx/interface/icons/move15.png'
                                tooltip "Cleaners are called if dirt is more than %d%%" % bm_building.auto_clean 
                        button:
                            xalign 1.0
                            action Return(['maintenance', "toggle_clean"])
                            selected bm_building.auto_clean != 100
                            tooltip "Toggle automatic hiring of cleaners"
                            text "Auto"

                    button:
                        xysize(200, 32)
                        xalign .5
                        action Return(['maintenance', "clean"])
                        tooltip "Hire cleaners to completely clean this building for %d Gold." % bm_building.get_cleaning_price()
                        text "Clean This Building"

                    python:
                        price = 0
                        for i in hero.buildings:
                            if i.maxdirt != 0:
                                price += i.get_cleaning_price()

                    button:
                        xysize(200, 32)
                        xalign .5
                        action Return(['maintenance', "clean_all", price])
                        tooltip "Hire cleaners to completely clean all buildings for %d Gold." % price
                        text "Clean All Buildings"

                if bm_building.needs_manager:
                    null height 20
                    label u"Management Options:":
                        style "proper_stats_label"
                        xalign .5
                        text_bold True
                    null height 5

                    default fields = [
                        "init_pep_talk", "cheering_up", "asks_clients_to_wait",
                                     "help_ineffective_workers", "works_other_jobs"]
                    default human_readable = [
                        "Pep Talk", "Cheer Up", "Meeting Clients",
                        "Handle Clients", "Work Other Jobs"]
                    default tts = [
                        "Manager will talk to workers before the start of every workday to try and motivate them.",
                        "Manager will try to cheer up girls who seem sad or tired.",
                        "Manager will ask clients to wait if there is no spot available in their favorite business.",
                        "Manager will try to talk down clients who received inadequate service and attempt to salvage payment for the service provided.",
                        "Manager will work other Jobs than their own if there are no dedicated worker available."]

                    for field, name, tt in zip(fields, human_readable, tts):
                        button:
                            xysize 200, 32
                            xalign .5
                            action ToggleField(bm_building, field)
                            tooltip tt
                            text "[name]"

                    null height 5
                    python:
                        desc0 = "==> {} Rule".format(bm_building.workers_rule.capitalize())
                        desc1 = "Choose a rule your workers are managed by!"
                        desc2 = bm_building.WORKER_RULES_DESC[bm_building.workers_rule]
                        desc = "\n".join([desc0, desc1, desc2])
                    button:
                        xysize (200, 32)
                        xalign .5
                        action Function(bm_building.toggle_workers_rule)
                        tooltip "{}".format(desc)
                        text "WR: {}".format(bm_building.workers_rule.capitalize())

            button:
                style_group "dropdown_gm"
                action Hide("building_controls"), With(dissolve)
                minimum 50, 30
                align .5, .97
                text "OK"
                keysym "mousedown_3"

    screen building_adverts():
        modal True
        zorder 1

        frame:
            style_group "content"
            at slide(so1=(600, 0), t1=.7, eo2=(1300, 0), t2=.7)
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            xpos 936
            yalign .95
            xysize(343, 675)

            label (u"{size=20}{color=ivory}{b}Advertise!") text_outlines [(2, "#424242", 0, 0)] align (.5, .16)

            # Buttons themselves ---------------------------------->
            hbox:
                align(.5, .4)
                box_wrap True
                spacing 20
                for advert in bm_building.adverts:
                    vbox:
                        style_group "basic"
                        align (.5, .5)
                        # else:
                        if advert['name'] == "Sign" and not advert['active']:
                            button:
                                xysize(280, 32)
                                tooltip advert['desc']
                                action Return(["building", 'sign', advert])
                                text "Put Up Sign for 200 gold" color "black" align (.5, .5) size 15
                        elif advert['name'] == "Celebrity":
                            button:
                                xysize(280, 32)
                                tooltip advert['desc']
                                action Return(["building", 'celeb', advert])
                                sensitive not advert['active']
                                if not advert['active']:
                                    text "Hire a Celeb!" color "black" align (.5, .5) size 15
                                else:
                                    text "Celebrity hired!" color "black" align (.5, .5) size 15
                        else:
                            button:
                                xysize(280, 32)
                                tooltip advert['desc']
                                action ToggleDict(advert, "active")
                                if advert['active']:
                                    text ("Stop %s!" % advert['name']) color "black" align (.5, .5)
                                elif advert['price'] == 0:
                                    text ("Use %s for %s Gold a day!" % (advert['name'], advert['upkeep'])) color "black" align (.5, .5) size 15
                                elif advert['upkeep'] == 0:
                                    text ("Use %s for %s Gold!" % (advert['name'], advert['price'])) color "black" align (.5, .5) size 15
                                else:
                                    text ("Use %s for %s Gold and %s a day!" % (advert['name'], advert['price'], advert['upkeep'])) color "black" align (.5, .5) size 15

            button:
                style_group "dropdown_gm"
                action Hide("building_adverts"), With(dissolve)
                minimum(50, 30)
                align (.5, .97)
                text  "OK"
                keysym "mousedown_3"
