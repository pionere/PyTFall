label realtor_agency:
    # Music related:
    if not "shops" in ilists.world_music:
        $ ilists.world_music["shops"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("shops")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["shops"]) fadein 1.5

    hide screen main_street

    scene bg realtor_agency
    with dissolve

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    $ g = npcs["Rose_estate"].say

    if not global_flags.has_flag("visited_ra") and not config.developer:
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

        show expression npcs["Rose_estate"].get_vnsprite() at center as rose with dissolve:
            yoffset 100

        g "Welcome to Rose Real Estates."
        extend " My name is Rose. I'm the owner and the realtor."
        g "Please have a seat and take a look at some of our offers."

        $ global_flags.set_flag("visited_ra")
    else:
        "The room is still bright and filled with the same sweet scent."
        show expression npcs["Rose_estate"].get_vnsprite() at right as rose with dissolve
            # yoffset -100

    # Added the next three lines to disable this feature without crashing the game   --fenec250

    $ market_buildings = sorted(set(chain(businesses.values(), buildings.values())) - set(hero.buildings), key = lambda x: x.id)
    $ focus = None

    if not market_buildings:
        npcs["Rose_estate"].say "I'm sorry, we don't have anything for sale at the moment."
    show screen realtor_agency

    while 1:

        $ result = ui.interact()

        if result[0] == 'buy':
            if hero.AP > 0 and hero.take_money(result[1].price, reason="Property"):
                $ hero.AP -= 1
                $ renpy.play("content/sfx/sound/world/purchase_1.ogg")
                $ hero.add_building(result[1])
                $ market_buildings.remove(result[1])
                $ focus = None

                if hero.AP <= 0:
                    $ Return(["control", "return"])()
            else:
                if hero.AP <= 0:
                    $ renpy.call_screen('message_screen', "You don't have enough Action Points!")
                else:
                    $ renpy.call_screen('message_screen', "You don't have enough Gold!")

        if result[0] == 'control':
            if result[1] == 'return':
                jump realtor_exit

label realtor_exit:
    $ renpy.music.stop(channel="world")
    hide screen realtor_agency
    jump main_street


screen realtor_agency():
    modal True
    zorder 1

    if market_buildings:
        frame:
            style_group "content"
            background Frame("content/gfx/frame/p_frame53.png", 10, 10)
            xalign .003
            ypos 42
            xysize (420, 675)
            side "c r":
                viewport id "brothelmarket_vp":
                    xysize (410, 645)
                    draggable True
                    mousewheel True
                    has vbox
                    for building in market_buildings:
                        vbox:
                            xfill True
                            xysize (395, 320)
                            frame:
                                background Frame(Transform("content/gfx/frame/MC_bg3.png", alpha=.6), 5, 5)
                                xysize (395, 320)
                                null height 15
                                vbox:
                                    xalign .5
                                    null height 5
                                    frame:
                                        style_group "content"
                                        xalign .5
                                        xysize (340, 50)
                                        background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                                        label (u"[building.name]") text_size 23 text_color ivory align(.5, .5)
                                    null height 5
                                    frame:
                                        background Frame("content/gfx/frame/mes11.webp", 5, 5)
                                        xpadding 5
                                        ypadding 5
                                        xalign .5
                                        $ img = ProportionalScale(building.img, 300, 220)
                                        imagebutton:
                                            idle (img)
                                            hover (im.MatrixColor(img, im.matrix.brightness(.25)))
                                            action SetVariable("focus", building)
                vbar value YScrollValue("brothelmarket_vp")

    if focus:
        frame:
            style_group "content"
            background Frame("content/gfx/frame/p_frame53.png", 10, 10)
            xalign .5
            ypos 42
            xysize (420, 675)
            side "c l":
                viewport id "info_vp":
                    xysize (410, 645)
                    draggable True
                    mousewheel True
                    vbox:
                        xsize 400
                        xfill True
                        null height 50
                        frame:
                            style_group "content"
                            xalign .5
                            xysize (350, 60)
                            background Frame("content/gfx/frame/namebox5.png", 10, 10)
                            label (u"[focus.name]") text_size 23 text_color ivory align (.5, .8)
                        null height 50
                        hbox:
                            style_group "proper_stats"
                            frame:
                                xpadding 12
                                ypadding 12
                                background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.98), 10, 10)
                                vbox:
                                    spacing -1
                                    frame:
                                        xysize 380, 24
                                        text "{color=[gold]}Price:" yalign .5
                                        label "{color=[gold]}[focus.price]" align 1.0, .5
                                    frame:
                                        xysize 380, 24
                                        text "{color=[ivory]}Quarter:" yalign .5
                                        label "{color=[ivory]}[focus.location]" align 1.0, .5
                                    if isinstance(focus, Building):
                                        frame:
                                            xysize 380, 24
                                            text "Interior Space:" yalign .5
                                            label (u"{color=[ivory]}%s/%s" % (focus.in_slots, focus.in_slots_max)) align 1.0, .5
                                        frame:
                                            xysize 380, 24
                                            text "Exterior Space:" yalign .5
                                            label (u"{color=[ivory]}%s/%s" % (focus.ex_slots, focus.ex_slots_max)) align 1.0, .5
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
                                            text "Level:" yalign .5
                                            label (u"%s" % (focus.tier)) align (1.0, .5)

                        if isinstance(focus, Building):
                            null height 10

                            hbox:
                                xalign .5
                                xysize (400,30)
                                hbox:
                                    xalign .5
                                    for business in focus.allowed_businesses:
                                        $ img = ProportionalScale("content/buildings/upgrades/icons/" + business.__name__ + ".png", 24, 24)
                                        if not (focus.has_extension(business)):
                                            $ img = im.MatrixColor(img, im.matrix.desaturate())
                                        imagebutton:
                                            xpadding 5
                                            ypadding 2
                                            xysize 35, 29
                                            tooltip ("%s" % (business.__name__))
                                            action NullAction()
                                            idle img

                            null height 10
                        else:
                            null height 50

                        hbox:
                            xalign .5
                            xysize (400, 100)
                            frame:
                                style_group "content"
                                background Frame("content/gfx/frame/ink_box.png", 10, 10)
                                xsize 400
                                xpadding 10
                                ypadding 10
                                text ("{=content_text}{color=[ivory]}[focus.desc]")

                        null height 50

                        button:
                            xalign .5
                            style "blue1"
                            xpadding 15
                            ypadding 10
                            text "Buy" align .5, .5 style "black_serpent" color ivory hover_color red
                            action Return(['buy', focus])
    use top_stripe(True)
