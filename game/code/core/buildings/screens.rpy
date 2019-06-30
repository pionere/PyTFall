label building_management:
    python:
        # Some Global Vars we use to pass data between screens:
        bm_building = hero.buildings[bm_index]
        bm_mid_frame_mode = getattr(store, "bm_mid_frame_mode", None)

        # special cursor for DragAndDrop and the original value
        mouse_drag = {"default" :[("content/gfx/interface/cursors/hand.png", 0, 0)]}
        mouse_cursor = config.mouse

    scene bg scroll

    show screen building_management
    with fade

    $ global_flags.set_flag("keep_playing_music")

    while 1:
        $ result = ui.interact()
        if not result or not isinstance(result, (list, tuple)):
            pass
        elif result[0] == "bm_mid_frame_mode":
            $ bm_mid_frame_mode = result[1]
            if bm_mid_frame_mode is None:
                # cleanup after EG
                python hide:
                    cleanup = ["workers", "guild_teams",
                              "bm_exploration_view_mode", "bm_selected_log_area",
                              "bm_selected_exp_area", "bm_selected_exp_area_sub"]
                    for i in cleanup:
                        if hasattr(store, i):
                            delattr(store, i)
            elif isinstance(bm_mid_frame_mode, ExplorationGuild):
                $ bm_mid_frame_mode.load_gui()
        elif result[0] == "fg_team":
            python hide:
                action = result[1]
                if action == "create":
                    n = renpy.call_screen("pyt_input", "", "Enter Name", 20)
                    if len(n):
                        t = bm_mid_frame_mode.new_team(n)
                        guild_teams.pager_content.append(t)
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
                    elif action == "remove":
                        char = result[3]
                        workers.add(char)
                        team.remove(char)
                    elif action == "dissolve":
                        for i in team:
                            workers.add(i)
                        bm_mid_frame_mode.remove_team(team)
                        guild_teams.pager_content.remove(team)
                    elif action == "transfer":
                        dest_guild = result[3]
                        dest_building = dest_guild.building
                        for i in team:
                            i.mod_workplace(dest_building)
                        dest_guild.add_team(team)
                        bm_mid_frame_mode.remove_team(team)
                        guild_teams.pager_content.remove(team)
        elif result[0] == "building":
            if result[1] == 'items_transfer':
                hide screen building_management
                $ items_transfer(result[2])
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
                python hide:
                    global bm_building, bm_index
                    price = int(bm_building.get_market_price()*.9)

                    if renpy.call_screen("yesno_prompt",
                                         message="Are you sure you wish to sell %s for %d Gold?" % (bm_building.name, price),
                                         yes_action=Return(True), no_action=Return(False)):
                        hero.add_money(price, reason="Property")
                        hero.remove_building(bm_building)

                        if hero.buildings:
                            if bm_index >= len(hero.buildings):
                                bm_index = 0
                            bm_building = hero.buildings[bm_index]
                        else:
                            jump("building_management_end")
        # Upgrades:
        elif result[0] == 'upgrade':
            if result[1] == "build":
                python hide:
                    temp = result[2]
                    if isinstance(temp, Business):
                        bm_building.build_business(temp, in_game=True)
                    else:
                        result[3].build_upgrade(temp)
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

    $ del bm_index, bm_building, bm_mid_frame_mode, mouse_drag, mouse_cursor
    jump buildings_list
    with dissolve

# Screens:
screen building_management():
    if hero.buildings:
        # Main Building mode:
        frame:
            background Frame(im.Alpha("content/gfx/frame/p_frame6.png", alpha=.98), 10, 10)
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
            background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
            xysize (330, 680)
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
            background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
            xysize (330, 680)
            xalign 1.0
            ypos 40
            has vbox xfill True
            if bm_mid_frame_mode is None:
                use building_management_rightframe_building_mode
            elif isinstance(bm_mid_frame_mode, ExplorationGuild):
                use building_management_rightframe_exploration_guild_mode
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
        background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.9), 5, 5)
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
            python:
                bm_building_chars = set(bm_building.inhabitants)
                if hasattr(bm_building, "all_workers"):
                    bm_building_chars.update(bm_building.all_workers)
                bm_building_chars = list(bm_building_chars)
                bm_building_chars.sort(key=attrgetter("name"))
                bm_building_chars.insert(0, hero)
                if hasattr(bm_building, "inventory"):
                    bm_building_chars.insert(0, bm_building)
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
            background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.9), 5, 5)
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
        $ managers = [w for w in bm_building.all_workers if w.job == ManagerJob]
        vbox:
            xalign .5
            $ temp = ("Current manager" if len(managers) == 1 else "Managers") if managers else "No manager" 
            text "[temp]" align (.5, .5) size 25 color "goldenrod" drop_shadow [(1, 2)] drop_shadow_color "black" antialias True style_prefix "proper_stats"                
            if len(managers) <= 1:
                frame:
                    xmaximum 220
                    ymaximum 220

                    xalign .5
                    background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.95), 10, 10)
                    if managers:
                        $ w = managers[0]
                        $ img = w.show("profile", resize=(190, 190), add_mood=True, cache=True)
                        imagebutton:
                            idle img
                            hover PyTGFX.bright_content(img, .15)
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
                                    hover PyTGFX.bright_content(img, .15)
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
    frame:
        xalign .5
        xysize 260, 40
        background Frame("content/gfx/frame/namebox5.png", 10, 10)
        label str(bm_mid_frame_mode.name) text_size 18 text_color "ivory" align .5, .6

    if isinstance(bm_mid_frame_mode, Business):
        null height 10
        if bm_mid_frame_mode.active:
            $ img = "content/gfx/images/open.webp"
            $ temp = "Close the business!"
        else:
            $ img = "content/gfx/images/closed.webp"
            $ temp = "Open the business!"
        $ img = PyTGFX.scale_img(img, 80, 40)
        imagebutton:
            xalign .5
            idle img
            hover PyTGFX.bright_img(img, .15)
            action ToggleField(bm_mid_frame_mode, "active")
            tooltip temp

        if hasattr(bm_building, "all_workers"):
            $ workers = [w for w in bm_building.all_workers if w.job in bm_mid_frame_mode.jobs]
            if workers:
                $ workers.sort(key=attrgetter("level"), reverse=True)
                null height 10
                frame:
                    style_prefix "content"
                    xysize 315, 500
                    background Null()
                    hbox:
                        xsize 315
                        text "Staff:" align (.5, .5) size 25 color "goldenrod" drop_shadow [(1, 2)] drop_shadow_color "black" antialias True style_prefix "proper_stats"

                    vpgrid:
                        pos -2, 30
                        style_group "dropdown_gm"
                        xysize 310, 460
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
                                    hover PyTGFX.bright_content(img, .15)
                                    action If(w.is_available, true=[SetVariable("char", w),
                                                                    SetVariable("eqtarget", w),
                                                                    SetVariable("equip_girls", [w]),
                                                                    SetVariable("came_to_equip_from", last_label),
                                                                    Jump("char_equip")],
                                                              false=NullAction())
                                    tooltip "Check %s's equipment" % w.name

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
                    xysize 150, 40
                    yalign .5
                    action Return(["bm_mid_frame_mode", None])
                    tooltip ("Back to the main overview of the building.")
                    text "Back" size 15

screen building_management_leftframe_building_mode:
    frame:
        background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
        style_prefix "proper_stats"
        xsize 317
        padding 12, 12
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
                $ temp = temp[min(9, round_int(tmp/10))]
                text "%s (%d %%)" % (temp, tmp) xalign .98 style_suffix "value_text" yoffset 4
        # Threat
        if bm_building.maxthreat != 0:
            frame:
                xysize (296, 27)
                text "Threat:" xalign .02 color "crimson"
                text "%d %%" % bm_building.get_threat_percentage():
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

    if bm_building.businesses:
        null height 5
        frame:
            background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            xsize 317
            #padding 12, 12
            xpadding 12
            top_padding 12
            bottom_padding 60 # FIXME WTF!!!! Thanks RenPy!
            yfill True
            frame:
                xalign .5
                background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                xysize (180, 40)
                label 'Businesses' text_color "ivory" xalign .5 text_bold True
            viewport:
                ypos 45
                xfill True
                mousewheel True
                scrollbars "vertical"
                draggable True
                has vbox
                # Businesses
                for u in bm_building.businesses:
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 5, 5)
                        xysize 280, 90
                        frame:
                            xpos 5
                            yalign .5
                            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.95), 5, 5)
                            margin 0, 0
                            padding 2, 2
                            add PyTGFX.scale_content(u.img, 105, 70) align .5, .5
                        vbox:
                            xpos 115
                            yalign .6
                            xysize 155, 60
                            text "[u.name]" xalign .5 style "proper_stats_text" size 19
                            null height 2
                            textbutton "{size=15}{font=fonts/TisaOTM.otf}{color=goldenrod}Details":
                                background Frame(im.Alpha("content/gfx/interface/images/story12.png", alpha=.8))
                                hover_background Frame(PyTGFX.bright_img("content/gfx/interface/images/story12.png", .15))
                                tooltip "View details or expand {}.\n{}".format(u.name, u.desc)
                                xalign .5
                                top_padding 3
                                action Return(["bm_mid_frame_mode", u])

                        if u.can_close():
                            $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 20, 20)
                            imagebutton:
                                align 1.0, 0 offset 2, -2
                                idle temp
                                hover PyTGFX.bright_img(temp, .15)
                                action Show("yesno_prompt",
                                            message="Are you sure you wish to remove the %s for %d Gold?" % (u.name, u.get_cost()[0]),
                                            yes_action=[Function(bm_building.close_business, u), Hide("yesno_prompt")], no_action=Hide("yesno_prompt"))
                                tooltip "Remove the business"

screen building_management_leftframe_businesses_mode:
    frame:
        background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
        style_group "proper_stats"
        xsize 317
        padding 12, 12
        has vbox spacing 1
        # Slots:
        frame:
            xysize (296, 27)
            text "Indoor Slots:" xalign .02 color "ivory"
            text "[bm_mid_frame_mode.in_slots]"  xalign .98 style_suffix "value_text"
        frame:
            xysize (296, 27)
            text "Exterior Slots:" xalign .02 color "ivory"
            text "[bm_mid_frame_mode.ex_slots]"  xalign .98 style_suffix "value_text"
        if bm_mid_frame_mode.capacity or getattr(bm_mid_frame_mode, "expands_capacity", False):
            frame:
                xysize (296, 27)
                text "Capacity:" xalign .02 color "ivory"
                $ cap = bm_mid_frame_mode.capacity
                if getattr(bm_mid_frame_mode, "reserved_capacity", False):
                    $ cap = "%d/%d" % (cap-bm_mid_frame_mode.reserved_capacity, cap)
                text str(cap)  xalign .98 style_suffix "value_text"

    if getattr(bm_mid_frame_mode, "expands_capacity", False):
        null height 5
        frame:
            background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            style_prefix "proper_stats"
            xsize 317
            padding 12, 12
            has vbox spacing 1

            hbox:
                xfill True
                text "To Expand:" xalign .0
                $ duration = bm_mid_frame_mode.exp_cap_duration
                if duration is not None:
                    $ duration = duration[0]
                    if duration != 0:
                        text ("%d %s"%(duration, plural("day", duration))) xalign 1.0

            $ cost, materials, in_slots, ex_slots = bm_mid_frame_mode.get_expansion_cost()
            $ can_build = not any(icu[0] == "capacity" for icu in bm_mid_frame_mode.in_construction_upgrades)

            # Materials and GOLD
            vpgrid:
                cols 3
                xsize 296
                spacing 2
                frame:
                    xysize (97, 27)
                    has hbox xysize (97, 27)
                    button:
                        background Frame("content/gfx/animations/coin_top 0.13 1/1.webp")
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
                        xysize (97, 27)
                        has hbox xysize (97, 27)
                        button:
                            background Frame(r.icon)  # TODO scale_content ?
                            xysize 20, 20
                            align 0.2, .5
                            action NullAction()
                            tooltip r.id
                        if hero.inventory[r.id] >= amount:
                            text "[amount]" xalign .9 style_suffix "value_text"
                        else:
                            $ can_build = False
                            text "[amount]" xalign .9 color "grey" style_suffix "value_text"

            vpgrid:
                cols 2
                xsize 296
                spacing 2
                if in_slots:
                    frame:
                        xysize (147, 27)
                        has hbox xysize (147, 27)
                        text "Indoor Slots:" xalign .1
                        if (bm_building.in_slots_max - bm_building.in_slots) >= in_slots:
                            text "[in_slots]" xalign .8 style_suffix "value_text"
                        else:
                            $ can_build = False
                            text "[in_slots]" xalign .8 color "grey" style_suffix "value_text"
                if ex_slots:
                    frame:
                        xysize (147, 27)
                        has hbox xysize (147, 27)
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
                frame:
                    xysize (296, 27)
                    text "Indoor Slots Freed:" xalign .02 color "ivory"
                    text "[in_slots]"  xalign .98 style_suffix "value_text"
                frame:
                    xysize (296, 27)
                    text "Exterior Slots Freed:" xalign .02 color "ivory"
                    text "[ex_slots]"  xalign .98 style_suffix "value_text"
                frame:
                    xysize (296, 27)
                    text "Cost:" xalign .02 color "ivory"
                    text "[cost]"  xalign .98 style_suffix "value_text"
            null height 1
            textbutton "Reduce Capacity":
                style "pb_button"
                xalign .5
                if bm_mid_frame_mode.in_construction_upgrades:
                    action NullAction()
                    tooltip "Construction in progress!"
                elif bm_mid_frame_mode.can_reduce_capacity():
                    action Function(bm_mid_frame_mode.reduce_capacity)
                    tooltip "Add more space to the building!"

    if bm_mid_frame_mode.upgrades or bm_mid_frame_mode.in_construction_upgrades:
        null height 5
        frame:
            background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
            xsize 317
            #padding 12, 12
            xpadding 12
            top_padding 12
            bottom_padding 60 # FIXME WTF!!!! Thanks RenPy!
            yfill True
            frame:
                xalign .5
                background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                xysize (180, 40)
                label 'Extensions' text_color "ivory" xalign .5 text_bold True
            vpgrid:
                ypos 45
                xfill True
                mousewheel True
                scrollbars "vertical"
                draggable True
                cols 2
                spacing 2
                $ box_size = (139, 80)
                $ entry_size = (100, 66)
                # Active extensions
                for u in bm_mid_frame_mode.upgrades:
                    $ desc = "{u}{i}%s{/u}{/i}\n%s" % (u.name, u.desc)
                    $ img = PyTGFX.scale_content(u.img, *entry_size)
                    frame:
                        background Null()
                        xysize box_size
                        margin 0, 0
                        padding 0, 0
                        frame:
                            align .5, .5
                            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.95), 5, 5)
                            margin 0, 0
                            padding 2, 2
                            fixed:
                                xysize entry_size
                                imagebutton:
                                    #xysize entry_size
                                    align .5, .5
                                    idle img
                                    hover PyTGFX.bright_content(img, .15)
                                    action NullAction()
                                    tooltip desc
                                $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 16, 16)
                                imagebutton:
                                    align 1.0, 0 offset 2, -2
                                    idle temp
                                    hover PyTGFX.bright_img(temp, .15)
                                    action Show("yesno_prompt",
                                                message="Are you sure you wish to remove the %s for %d Gold?" % (u.name, u.get_cost()[0]),
                                                yes_action=[Function(bm_mid_frame_mode.remove_upgrade, u), Hide("yesno_prompt")], no_action=Hide("yesno_prompt"))
                                    tooltip "Remove upgrade"

                # Under construction
                for icu in bm_mid_frame_mode.in_construction_upgrades:
                    python:
                        u, d, m = icu
                        if u == "capacity":
                            desc = "{u}{i}Capacity expansion{/u}{/i} - %d %s" % (d, plural("day", d))
                            img = getattr(bm_mid_frame_mode, "img", None)
                        else:
                            desc = "{u}{i}%s{/u}{/i} - %d %s\n%s" % (u.name, d, plural("day", d), u.desc)
                            img = getattr(u, "img", None)
                        if img:
                            img = im.Scale(img, *entry_size)
                        else:
                            img = Solid("black", xysize=entry_size)
                        img = im.Sepia(img)
                    frame:
                        background Null()
                        xysize box_size
                        margin 0, 0
                        padding 0, 0
                        frame:
                            align .5, .5
                            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.95), 5, 5)
                            margin 0, 0
                            padding 2, 2
                            fixed:
                                xysize entry_size
                                imagebutton:
                                    xysize entry_size
                                    idle img
                                    action NullAction()
                                    tooltip desc
                                $ uc_img = im.Scale("content/gfx/images/under_construction.webp", 60, 40)
                                imagebutton:
                                    xysize (60, 40)
                                    align .5, .5
                                    focus_mask True
                                    idle uc_img
                                    hover PyTGFX.bright_img(uc_img, .15)
                                    action Function(bm_mid_frame_mode.cancel_construction, icu)
                                    tooltip "Stop Construction!"

screen building_management_midframe_building_mode:
    frame:
        xalign .5
        xysize (380, 50)
        background Frame("content/gfx/frame/namebox5.png", 10, 10)
        label (u"[bm_building.name]") text_size 23 text_color "ivory" align (.5, .6)

    frame:
        align .5, .0
        ypos 60
        background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.95), 10, 10)
        add PyTGFX.scale_content(bm_building.img, 600, 444)

    # Left/Right Controls + Expand button:
    vbox:
        align .5, .99
        frame:
            background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.9), 10, 10)
            has hbox xysize (600, 74)
            button:
                align .1, .5
                xysize (140, 40)
                style "left_wood_button"
                action Return(['control', 'left'])
                text "Previous" style "wood_text" xalign .69
            frame:
                background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
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
                $ can_build = not bm_mid_frame_mode.has_extension(u.__class__)
                $ can_build = can_build and not [up for (up, d, m) in bm_mid_frame_mode.in_construction_upgrades if u == up]
                if can_build:
                    frame:
                        xalign .5
                        background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                        has fixed xysize 500, 150
                        $ cost, materials, in_slots, ex_slots = u.get_cost()
                        $ duration = u.duration

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
                                        background Frame(r.icon) # TODO scale_content ?
                                        xysize 25, 25
                                        align 0, .5
                                        action NullAction()
                                        tooltip r.id
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
                            if duration and duration[0] >= 1:
                                text "Days:"
                                text str(duration[0])

                        vbox:
                            align 1.0, .8
                            xsize 150
                            spacing 4
                            frame:
                                background Frame("content/gfx/frame/MC_bg3.png", 3, 3)
                                xysize 124, 83
                                xalign .5
                                imagebutton:
                                    align .5, .5
                                    idle PyTGFX.scale_content(u.img, 120, 80)
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
                    "Manager will try to cheer up workers who seem sad or tired.",
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
