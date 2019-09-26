init python:
    if DEBUG_QE:
        register_event("angelica_meet", locations=["mages_tower"], run_type="jump", priority=1000, start_day=1, max_runs=1)
    else:
        register_event("angelica_meet", locations=["mages_tower"], run_conditions=["dice(global_flags.flag('mt_counter')*30)"], run_type="jump", priority=100, start_day=1, max_runs=1)
        register_event("pre_angelica_meet", locations=["mages_tower"], run_conditions=["global_flags.up_counter('mt_counter') or True"], run_type="background", label=None, priority=200, start_day=1, max_runs=3)

label angelica_meet:
    $ a = npcs["Angelica_mage_tower"].say

    hide screen mages_tower
    show expression npcs["Angelica_mage_tower"].get_vnsprite() as angelica
    with dissolve

    if pytfall.enter_location("angelica", music=True, env="mages_tower"):
        # cleanup
        $ global_flags.del_flag("mt_counter")
        $ kill_event("pre_angelica_meet")

        a "Hi! I am Angelica!"
        a "I noticed you've been hanging around the Tower."
        menu:
            a "Are you interested in magic?"
            "Yes":
                a "Great! You cannot join us in the tower at the moment, but there are things I can help you with!"
                a "I for once am one of the very few people in this part of the world who can unlock add and remove elemental alignments from a person."
                a "It is not an easy task so don't think that you will be able to get away with being a cheapskate!"
                a "It takes a lot out of me, so I expect to be very well compensated. If you believe that you can find a better deal elsewhere... I do dare you to try."
                $ global_flags.set_flag("angelica_free_alignment")
                a "You look like you have some potential... so I'll give you one freebie. "
                extend "Do not expect that to happen again!"
                a "I charge {color=gold}10 000 Gold{/color} as a base cost and an additional {color=gold}5 000 Gold{/color} per elements you already have!"
                a "If you want to lose one, it is a lot trickier... elements are not shoes you can put on and off. Each one goes with a price of {color=gold}50 000 Gold{/color}."
                a "And feel free to bring your teammates, I can do it for pretty much anyone."

                $ temp = BE_Core.TYPE_TO_COLOR_MAP
                $ temp = "%s and %s" % (set_font_color("Light", temp["light"]), set_font_color("Darkness", temp["darkness"])) 
                a "I can also teach you basics of [temp] magic."
                $ del temp
            "Not really":
                a "Oh? Well, never mind then..."
                a "I'll be around if you change your mind."
                jump mages_tower

    $ pytfall.shops_stores["Angelica Shop"].visible = True # done here so it is not enabled if the user is not interested in magic, but also not barred forever 
    a "How can I be of assistance?"

label angelica_menu:
    show screen angelica_menu
    with dissolve
    while 1:
        $ result = ui.interact()

        hide screen angelica_menu
        if result == "spells":
            jump angelica_spells
        elif result == "add_alignment":
            jump angelica_add_alignment
        elif result == "remove_alignment":
            jump angelica_remove_alignment
        else:
            a "Later!"
            hide angelica with dissolve
            $ del a
            jump mages_tower

label angelica_spells:
    a "Magic is knowledge and knowledge is power!"
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Angelica Shop"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_1

    hide screen shopping
    with dissolve
    a "Use your magic responsibly."
    $ del shop, focus, item_price, amount, purchasing_dir
    jump angelica_menu

label angelica_add_alignment:
    a "Let's take a look."
    if len(hero.team) > 1:
        a "Who is it going to be?"
        call screen character_pick_screen
        $ character = _return
    else:
        $ character = hero
    if not character:
        a "Ok then."
        $ del character
        jump angelica_menu

    if all(el in character.traits for el in tgs.real_elemental):
        a "Oh. It looks like you already have them all. It's not wise. Maybe you should remove a few?"
    else:
        call screen alignment_choice(character)
        $ alignment = _return
        if alignment:
            $ price = 10000
            if "Neutral" not in character.traits:
                $ price += len(character.elements)*5000
            if global_flags.flag("angelica_free_alignment") or hero.take_money(price, reason="Element Purchase"):
                a "There! All done!"
                a "Don't let these new powers go into your head and use them responsibly!"
                $ global_flags.del_flag("angelica_free_alignment")
                $ character.apply_trait(alignment)
            else:
                a "You don't have enough money. It will be {color=gold}[price] Gold{/color}."
            $ del price
        $ del alignment
    $ del character
    jump angelica_menu

label angelica_remove_alignment:
    a "Let's take a look."
    if len(hero.team) > 1:
        a "Who is it going to be?"
        call screen character_pick_screen
        $ character = _return
    else:
        $ character = hero
    if not character:
        a "Ok then."
        $ del character
        jump angelica_menu

    if "Neutral" in character.traits:
        a "You have no elements that I can remove."
    else:
        call screen alignment_removal_choice(character)
        $ alignment = _return
        if alignment:
            if alignment == "clear_all":
                $ elements = character.elements
                $ msg = "There! All elements were removed."
            else:
                $ elements = [alignment]
                $ msg = "There! I removed it."
            $ price = 50000 * len(elements)
            if hero.take_money(price, reason="Element Purchase"):
                a "[msg]"
                python hide:
                    for el in elements:
                        character.remove_trait(el)
            else:
                a "You don't have enough money. It will be {color=gold}[price] Gold{/color}."
            $ del price, msg, elements
        $ del alignment
    $ del character
    jump angelica_menu

screen alignment_choice(character):
    vbox:
        style_group "wood"
        xalign .5
        button:
            xysize (250, 40)
            yalign .5
            action Return("")
            text "Finish" size 15
            keysym "mousedown_3"

    python:
        char_elements = character.elements
        elements = [el for el in tgs.real_elemental if el not in char_elements]
        step = 360 / len(elements)
        var = 0

    for el in elements:
        python:
            img = PyTGFX.scale_content(el.icon, 120, 120)
            angle = var
            var = var + step
        imagebutton at circle_around(t=10, angle=angle, radius=250):
            idle img
            hover PyTGFX.bright_content(img, .25)
            action Return(el)
            tooltip "Add " + el.id

    vbox:
        align .5, .65
        # Elements icon:
        $ img = build_multi_elemental_icon(char_elements, size=90)
        $ img_h = build_multi_elemental_icon(char_elements, size=90, mc=im.matrix.brightness(.10))
        $ ele = ", ".join([e.id for e in char_elements])
        frame:
            xalign .0
            yfill True
            background Frame(im.Alpha("content/gfx/frame/MC_bg3.png", alpha=.6), 10, 10)
            xysize (100, 30)
            text (u"[character.nickname]") color "#CDAD00" font "fonts/Rubius.ttf" size 20 outlines [(1, "#3a3a3a", 0, 0)] align (.5, .7)
        null height 3
        frame:
            xysize (100, 100)
            background Frame(im.Alpha("content/gfx/frame/frame_it1.png", alpha=.6), 0, 0)
            add im.Scale("content/gfx/interface/images/elements/hover.png", 98, 98) align (.5, .5)
            button:
                xysize 90, 90
                align .5, .5 offset -1, -1
                action NullAction()
                background img
                hover_background img_h
                tooltip "Elements:\n   %s" % ele

screen alignment_removal_choice(character):
    key "mousedown_3" action Return("")

    vbox:
        style_group "wood"
        xalign .5
        button:
            xysize (250, 40)
            yalign .5
            action Return("")
            text "Finish" size 15

    python:
        elements = character.elements
        step = 360 / len(elements)
        var = 0

    for el in elements:
        python:
            img = PyTGFX.scale_content(el.icon, 120, 120)
            angle = var
            var = var + step
        imagebutton at circle_around(t=10, angle=angle, radius=250):
            idle img
            hover PyTGFX.bright_content(img, .25)
            action Return(el)
            tooltip "Remove " + el.id

    $ img = PyTGFX.scale_content(traits["Neutral"].icon, 120, 120)
    imagebutton:
        align (.5, .5)
        idle img
        hover Transform(PyTGFX.bright_content(img, .25), zoom=1.2)
        action Return("clear_all")
        tooltip "Remove all elements"

screen angelica_menu():
    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Spells":
            action Return("spells")
        textbutton "Add Alignment":
            action Return("add_alignment")
        textbutton "Remove Alignment":
            action Return("remove_alignment")
        textbutton "Leave":
            action Return("leave")
            keysym "mousedown_3"
