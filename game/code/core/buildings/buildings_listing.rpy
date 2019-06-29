label buildings_list:
    scene bg gallery2

    show screen buildings_list
    with dissolve

    while 1:
        $ result = ui.interact()

        if result[0] == "choice":
            $ bm_index = result[1]
            hide screen buildings_list
            jump building_management
        elif result == ["control", "return"]:
            hide screen buildings_list
            jump mainscreen

screen buildings_list:
    key "mousedown_3" action Return(['control', 'return']) # keep in sync with button - alternate

    # the number of filtered workers
    $ num_buildings = len(hero.buildings)

    # Buildings:
    if hero.buildings:
        vpgrid:
            style_group "content"
            cols 2
            ypos 59
            xalign .5
            xysize 1200, 600
            spacing 10
            draggable True
            mousewheel True

            for idx, building in enumerate(hero.buildings):
                python:
                    building_img = PyTGFX.scale_content(building.img, 93, 68)
                    img = im.Alpha("content/gfx/frame/ink_box.png", alpha=.6)
                    if getattr(building, "needs_manager", False):
                        managers = [w for w in building.all_workers if w.job == ManagerJob]
                        manager_img = PyTGFX.scale_img("content/gfx/interface/buttons/Profile.png", 24, 24)
                        if not managers:
                            manager_img = PyTGFX.sepia_img(manager_img)
                    else:
                        manager_img = None

                    c0 = building.in_slots_max
                    c1 = building.ex_slots_max
                    if c0 or c1:
                        slots = []
                        if c0:
                            slots.append("%d/%d" % (building.in_slots, c0))
                        if c1:
                            slots.append("%d/%d" % (building.ex_slots, c1))
                        slots = ", ".join(slots)
                    else:
                        slots = None

                button:
                    ymargin 0
                    idle_background Frame(img, 10 ,10)
                    hover_background Frame(PyTGFX.bright_img(img, .2), 10 ,10)
                    xysize (595, 120)
                    alternate Return(['control', 'return']) # keep in sync with mousedown_3
                    action Return(['choice', idx])
                    tooltip "Show %s!" % building.name

                    # Image:
                    frame:
                        background Frame("content/gfx/frame/MC_bg3.png", 5, 5)
                        padding 2, 2
                        align 0, .5
                        add building_img align .5, .5

                    # Texts/Status:
                    frame:
                        xpos 120
                        xysize (460, 115)
                        background Frame(im.Alpha("content/gfx/frame/p_frame2.png", alpha=.6), 10, 10)
                        xpadding 10
                        has vbox xfill True spacing 6
                        # Name + manager
                        hbox:
                            xfill True
                            label "[building.name]" text_size 21 text_color "ivory" text_outlines [(1, "black", 0, 0)] xalign .1
                            if manager_img is not None:
                                add manager_img xalign 1.0 xoffset -16 yoffset 4

                        hbox:
                            xfill True
                            vbox:
                                xsize 230
                                # Fame/Rep:
                                if building.maxfame != 0 or building.maxrep != 0:
                                    fixed:
                                        xysize (220, 32)
                                        if building.maxfame != 0:
                                            hbox:
                                                xysize (80, 32)
                                                add PyTGFX.scale_img("content/gfx/interface/images/trumpet.png", 24, 24)
                                                text "%d%%" % building.get_fame_percentage():
                                                    xalign .98
                                                    style_suffix "value_text"
                                                    yoffset 4
                                                    size 18
                                        if building.maxrep != 0:
                                            hbox:
                                                xpos 110
                                                xysize (80, 32)
                                                add PyTGFX.scale_img("content/gfx/interface/images/nobleA.png", 24, 24)
                                                text "%d%%" % building.get_rep_percentage():
                                                    xalign .98
                                                    style_suffix "value_text"
                                                    yoffset 4
                                                    size 18

                                # Dirt/Threat:
                                if building.maxdirt != 0 or building.maxthreat != 0:
                                    fixed:
                                        xysize (220, 32)
                                        if building.maxdirt != 0:
                                            hbox:
                                                xysize (80, 32)
                                                add PyTGFX.sepia_img(PyTGFX.scale_img("content/gfx/interface/buttons/discard.png", 24, 24))
                                                text "%d%%" % building.get_dirt_percentage():
                                                    xalign .98
                                                    style_suffix "value_text"
                                                    yoffset 4
                                                    size 18
                                        # Threat
                                        if building.maxthreat != 0:
                                            hbox:
                                                xpos 110
                                                xysize (80, 32)
                                                add PyTGFX.bright_img(PyTGFX.scale_img("content/gfx/interface/images/theft.png", 24, 24), .3)
                                                text "%d%%" % building.get_threat_percentage():
                                                    xalign .98
                                                    style_suffix "value_text"
                                                    yoffset 4
                                                    size 18

                            vbox:
                                xsize 230
                                # In/Ex-Slots:
                                if slots is not None: 
                                    fixed:
                                        xysize (220, 32)
                                        hbox:
                                            align .5, .5
                                            ysize 32
                                            spacing 5
                                            add PyTGFX.scale_img("content/gfx/interface/images/layout.png", 24, 24) yalign .5
                                            text slots:
                                                xalign .98
                                                style_suffix "value_text"
                                                yoffset 6
                                                size 16

                                # Habitants/Workers:
                                fixed:
                                    xysize (220, 32)
                                    if building.habitable:
                                        hbox:
                                            xalign .5
                                            ysize 32
                                            spacing 5
                                            add PyTGFX.scale_img("content/gfx/interface/images/bed.webp", 24, 24)
                                            text "%d/%d" % (len(building.inhabitants),building.habitable_capacity):
                                                xalign .98
                                                style_suffix "value_text"
                                                #yoffset 4
                                                size 18
                                    if hasattr(building, "all_workers"):
                                        hbox:
                                            xalign .5
                                            ysize 32
                                            spacing 5
                                            add PyTGFX.scale_img("content/gfx/interface/buttons/Group_full.png", 24, 24)
                                            text "%d" % len(building.all_workers):
                                                xalign .98
                                                style_suffix "value_text"
                                                yoffset 2
                                                size 18


    else:
        text "You don't own any buildings.":
            size 40
            color "ivory"
            align .5, .2
            style "TisaOTM"

    use top_stripe()