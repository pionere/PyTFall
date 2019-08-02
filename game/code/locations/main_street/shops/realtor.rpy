label realtor_agency:
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("shops", fadein=1.5)
    $ global_flags.del_flag("keep_playing_music")

    scene bg realtor_agency
    with dissolve

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    $ g = npcs["Rose_estate"].say

    if global_flags.has_flag("visited_ra"):
        "The room is still bright and filled with the same sweet scent."
    else:
        $ nvl_ra = Character(None, kind=nvl)
        nvl_ra "After entering the real-estate office, the first thing that hit you was the brightness."
        nvl_ra "It was far brighter than the outside world. Your eyes quickly adapted and you noticed the source of the light."
        nvl_ra "This medium size room, without windows, probably was a part of a bigger apartment, have been highly illuminated with a large chandelier, hanging from the ceiling over the central part of the room and a standing lamp near the desk."
        nvl_ra "On the left side, there were two couches opposing each other separated with a coffee table."
        extend " On the right side, there was a cupboard and a door that is probably leading further inside the house."
        nvl_ra "In the middle, under the chandelier was standing a desk with a single chair. There were also multiple painting hanging on the walls."
        nvl_ra "But that all escaped your mind the moment you noticed the owner."
        nvl_ra "She was a mature type woman with glasses, that surely wasn't ashamed of her female attributes."
        nvl_ra "Blouse and skirt that she wore was well fitted, and stick really tightly to her body emphasizing her breasts and hips."
        nvl_ra "The black stockings that she was wearing also matched her perfectly, underlining her beautiful legs. The finishing touch was her shoes with little, cute roses on the toes that you almost didn't notice."

        show expression npcs["Rose_estate"].get_vnsprite() as rose with dissolve:
            yoffset 100

        g "Welcome to Rose Real Estates."
        extend " My name is Rose. I'm the owner and the realtor."
        g "Please have a seat and take a look at some of our offers."

        hide rose
        $ del nvl_ra
        $ global_flags.set_flag("visited_ra")
    show expression npcs["Rose_estate"].get_vnsprite() at right as rose with dissolve

    $ market_buildings = sorted(set(buildings.values()) - set(hero.buildings), key=attrgetter("id"))
    $ focus = None
    if not market_buildings:
        g "I'm sorry, we don't have anything for sale at the moment."
    show screen realtor_agency

    while 1:
        $ result = ui.interact()

        if result[0] == 'select':
            $ focus = result[1]
        elif result[0] == 'buy':
            if not hero.has_ap():
                show screen message_screen("You don't have enough Action Points!")
            elif not hero.take_money(result[1].price, reason="Property"):
                show screen message_screen("You don't have enough Gold!")
            else:
                $ hero.take_ap(1)
                $ renpy.play("content/sfx/sound/world/purchase_1.ogg")
                $ hero.add_building(result[1])
                $ market_buildings.remove(result[1])
                $ focus = None
        elif result == ['control', 'return']:
            hide screen realtor_agency
            with dissolve
            hide rose

            $ del market_buildings, focus, g, result
            jump main_street

screen realtor_agency():
    if market_buildings:
        frame:
            style_group "content"
            background Frame("content/gfx/frame/p_frame53.png", 10, 10)
            xalign .003
            ypos 42
            xysize (420, 675)
            side "c r":
                viewport id "realtor_vp":
                    xysize (410, 645)
                    draggable True
                    mousewheel True
                    has vbox
                    for building in market_buildings:
                        frame:
                            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 5, 5)
                            xysize (395, 310)
                            vbox:
                                xalign .5
                                null height 5
                                frame:
                                    style_group "content"
                                    xalign .5
                                    xysize (340, 50)
                                    background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                                    label (u"[building.name]") text_size 23 text_color "ivory" align(.5, .5)
                                null height 5
                                frame:
                                    background Frame("content/gfx/frame/mes11.webp", 5, 5)
                                    padding 5, 5
                                    xalign .5
                                    $ img = PyTGFX.scale_content(building.img, 300, 220) #
                                    imagebutton:
                                        idle img
                                        hover PyTGFX.bright_content(img, .25)
                                        action Return(["select", building])
                vbar value YScrollValue("realtor_vp")

    if focus:
        frame:
            style_group "content"
            background Frame("content/gfx/frame/p_frame53.png", 10, 10)
            xalign .5
            ypos 42
            xysize (420, 675)
            viewport id "info_vp":
                xysize (410, 645)
                draggable True
                mousewheel True
                vbox:
                    xfill True
                    null height 50
                    frame:
                        style_group "content"
                        xalign .5
                        xysize (350, 60)
                        background Frame("content/gfx/frame/namebox5.png", 10, 10)
                        label (u"[focus.name]") text_size 23 text_color "ivory" align (.5, .8)
                    null height 50
                    hbox:
                        style_group "proper_stats"
                        frame:
                            padding 12, 12
                            background Frame(im.Alpha("content/gfx/frame/p_frame4.png", alpha=.98), 10, 10)
                            vbox:
                                spacing -1
                                frame:
                                    xysize 380, 24
                                    text "Price:" color "gold" yalign .5
                                    label "[focus.price]" text_color "gold" align 1.0, .5
                                frame:
                                    xysize 380, 24
                                    text "Quarter:" color "ivory" yalign .5
                                    label "[focus.location]" text_color "ivory" align 1.0, .5
                                if focus.in_slots_max != 0:
                                    frame:
                                        xysize 380, 24
                                        text "Interior Space:" yalign .5
                                        label ("%s/%s" % (focus.in_slots, focus.in_slots_max)) text_color "ivory" align 1.0, .5
                                if focus.ex_slots_max != 0:
                                    frame:
                                        xysize 380, 24
                                        text "Exterior Space:" yalign .5
                                        label ("%s/%s" % (focus.ex_slots, focus.ex_slots_max)) text_color "ivory" align 1.0, .5
                                if focus.maxfame != 0:
                                    frame:
                                        xysize 380, 24
                                        text "Fame:" yalign .5
                                        label (u"%s/%s" % (focus.fame, focus.maxfame)) align 1.0, .5
                                if focus.maxrep != 0:
                                    frame:
                                        xysize 380, 24
                                        text "Reputation:" yalign .5
                                        label (u"%s/%s" % (focus.rep, focus.maxrep)) align 1.0, .5
                                frame:
                                    xysize 380, 24
                                    text "Tier:" yalign .5
                                    label "[focus.tier]" align (1.0, .5)

                    null height 10

                    hbox:
                        xalign .5
                        xysize (400,30)
                        hbox:
                            xalign .5
                            spacing 4
                            for business in focus.allowed_businesses:
                                $ img = im.Scale("content/buildings/upgrades/icons/" + business.__class__.__name__ + ".png", 26, 26)
                                if not (focus.has_extension(business.__class__)):
                                    $ img = im.Grayscale(img)
                                imagebutton:
                                    xpadding 3
                                    ypadding 2
                                    background Frame("content/gfx/frame/MC_bg3.png", 1, 1)
                                    xysize 32, 30
                                    tooltip ("%s" % (business.name))
                                    action NullAction()
                                    idle img

                    null height 10

                    hbox:
                        xalign .5
                        xysize (400, 100)
                        frame:
                            style_group "content"
                            background Frame("content/gfx/frame/ink_box.png", 10, 10)
                            xsize 400
                            xpadding 10
                            ypadding 10
                            text "[focus.desc]" color "ivory"

                    null height 50

                    button:
                        xalign .5
                        style "blue1"
                        xpadding 15
                        ypadding 10
                        text "Buy" align .5, .5 style "black_serpent" color "ivory" hover_color "red"
                        action Return(['buy', focus])
    use top_stripe(True, show_lead_away_buttons=False)
