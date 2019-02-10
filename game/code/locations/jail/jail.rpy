label city_jail:

    # Music related:
    if not "cityjail" in ilists.world_music:
        $ ilists.world_music["cityjail"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("cityjail")]

    python:
        # Build the actions
        if pytfall.world_actions.location("city_jail"):
            pytfall.world_actions.slave_market(pytfall.jail, button="Browse Escapees",
                                               button_tooltip="Claim an escaped slave at reduced price.",
                                               null_condition="not pytfall.jail.slaves",
                                               buy_button="Purchase", buy_tooltip="Claim this slave by paying %s Gold.",
                                               prep_actions=[Function(pytfall.jail.switch_mode, "slaves")],
                                               index=0)
            pytfall.world_actions.slave_market(pytfall.jail, button="Captured Slaves",
                                               button_tooltip="Sell or acquire the slaves captured by your explorers.",
                                               null_condition="not pytfall.jail.captures",
                                               buy_button="Retrieve", buy_tooltip="Acquire this girl by paying %s Gold.",
                                               prep_actions=[Function(pytfall.jail.switch_mode, "captures")],
                                               index=1)
            pytfall.world_actions.add(2, "Browse Cells",
                [Function(pytfall.jail.switch_mode, "cells"), Show('city_jail_cells')],
                null_condition="not pytfall.jail.cells")
            pytfall.world_actions.look_around(100)
            pytfall.world_actions.finish()

    scene bg jail
    with dissolve

    if not global_flags.flag('visited_city_jail'):
        $ global_flags.set_flag('visited_city_jail')
        "The city jail..."
        "Temporary home of miscreants and lawbreakers."
        "Not to mention an occasional escaped slave."

    show screen city_jail

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while True:
        $ result = ui.interact()
        if result[0] == "bail":
            $ char = result[1]
            $ msg = pytfall.jail.bail_char(char)
            if msg:
                call screen message_screen(msg)

            if not pytfall.jail.chars_list:
                hide screen city_jail_cells

        elif result[0] == "control":
            if result[1] == "return":
                hide screen city_jail
                jump city

screen city_jail():

    use top_stripe(True)

    use location_actions("city_jail")

screen city_jail_cells():
    modal True
    zorder 1
    default source = pytfall.jail
    if source.chars_list:
        $ char = source.get_char()

        # Data (Left Frame): =============================================================================>>>
        frame:
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            xysize 270, 678
            ypos 41
            style_group "content"
            has vbox

            # Name: =============================================================================>>>
            frame:
                xysize 250, 50
                xalign .5
                background Frame(Transform("content/gfx/frame/namebox5.png", alpha=.95), 250, 50)
                label "[char.fullname]":
                    text_color gold
                    text_outlines [(2, "#424242", 0, 0)]
                    align (.5, .5)
                    if len(char.fullname) < 20:
                        text_size 21

            # Info: =============================================================================>>>
            null height 5
            label "Info:":
                text_color ivory
                text_size 20
                text_bold True
                xalign .5
                text_outlines [(2, "#424242", 0, 0)]
            vbox:
                style_group "proper_stats"
                spacing 5
                frame:
                    background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                    xsize 258 xalign .5
                    padding 6, 6
                    has vbox spacing 1 xmaximum 246
                    frame:
                        xysize 244, 20
                        text ("{color=#79CDCD}{size=-1}Class:") pos (1, -4)
                        label "{size=-3}[char.traits.base_to_string]" align (1.0, .5) ypos 10
                    frame:
                        xysize 245, 20
                        text "{color=#79CDCD}{size=-1}Level:" pos (1, -4)
                        label (u"{size=-5}%s"%char.level) align (1.0, .5) ypos 10



        # Image (Mid-Top): =============================================================================>>>
        frame:
            pos 265, 41
            xysize 669, 423
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=1.0), 10, 10)
            frame:
                align .5, .5
                background Frame("content/gfx/frame/MC_bg.png", 10, 10)
                add char.show("girlmeets", "sad", "indoors", "dungeon", "ripped", resize=(560, 400), exclude=["nude", "no clothes", "rest", "outdoors", "onsen", "beach", "pool", "living"], type="reduce", label_cache=True) align .5, .5

        # Details:
        frame:
            pos (928, 41)
            style_group "content"
            xysize (350, 361)
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            has vbox xalign .5 #ypos 5
            null height 5
            label (u"{size=20}{color=[ivory]}{b}Details:") xalign .5 text_outlines [(2, "#424242", 0, 0)]
            null height 5
            frame:
                left_padding 15
                ypadding 10
                xsize 226
                background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                vbox:
                    xalign .5
                    style_group "proper_stats"
                    spacing 1
                    hbox:
                        xsize 220
                        $ days = char.flag("release_day") - day
                        text "Remaining time:" xpos 2
                        text "%s %s" % (days, plural("day", days)) xalign .85
                    hbox:
                        xsize 220
                        text "Reason:" xpos 2
                        text "%s" % char.flag("sentence_type") xalign .9

        # Buttons:
        frame:
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            xpadding 5
            pos(928, 397)
            xsize 350
            hbox:
                xalign .5
                $ img=im.Scale("content/gfx/interface/buttons/arrow_button_metal_gold_left.png", 50, 50)
                imagebutton:
                    align(.5, .5)
                    idle img
                    hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                    action (Function(source.previous_index))
                    tooltip "Previous Prisoner"

                null width 10

                frame:
                    align(.5, .5)
                    style_group "dropdown_gm"
                    textbutton "Bail out":
                        xsize 150
                        action Return(["bail", char])
                        tooltip "Release this prisoner by paying their bail of %s Gold." % source.get_bail(char)

                null width 10

                $ img=im.Scale("content/gfx/interface/buttons/arrow_button_metal_gold_right.png", 50, 50)
                imagebutton:
                    align(.5, .5)
                    idle img
                    hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                    action (Function(source.next_index))
                    tooltip "Next Prisoner"

        # Girl choice:
        frame:
            # pos 265, 459
            pos 10, 455
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            side "c t":
                yoffset -2
                viewport id "jail_vp_list":
                    xysize 1256, 230
                    draggable True
                    mousewheel True
                    edgescroll [100, 200]
                    has hbox spacing 5
                    for idx, c in enumerate(source.chars_list):
                        $ img = c.show("vnsprite", resize=(180, 206), cache=True)
                        frame:
                            background Frame("content/gfx/frame/Mc_bg3.png", 10, 10)
                            imagebutton:
                                idle img
                                hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                                action Function(source.set_char, idx)
                                tooltip u"{=proper_stats_text}%s\n{size=-5}{=proper_stats_value_text}%s"%(c.name, c.desc)
                bar value XScrollValue("jail_vp_list")

    use top_stripe(show_return_button=True, return_button_action=[Hide("city_jail_cells"), With(dissolve)], show_lead_away_buttons=False)

