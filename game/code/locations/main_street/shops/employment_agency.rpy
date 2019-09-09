label employment_agency:
    scene bg realtor_agency
    with dissolve

    show expression npcs["Charla_ea"].get_vnsprite() at Transform(align=(.9, 1.0)) as charla
    with dissolve

    $ ea = npcs["Charla_ea"].say

    if pytfall.enter_location("employment_agency", music=True, env="shops"):
        ea "Welcome to my Employment Agency, my name is Charla."
        ea "I am always on a lookout for perspective Employees and Employers."
        ea "You certainly look like one of the Employers!"
        ea "My fee for hooking you up with a capable worker is one month worth of their wages."
        ea "Take a look at the files I got on hand!"

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen employment_agency
    while 1:
        $ result = ui.interact()

        if result[0] == 'hire':
            if not hero.has_ap():
                show screen message_screen("You don't have time (Action Point) for that!")
            else:
                $ char, cost = result[1], result[2]
                $ block_say = True
                if hero.gold >= cost:
                    menu:
                        ea "The fee to hire [char.name] is [cost]! What do you say?"
                        "Yes":
                            python hide:
                                hero.take_ap(1)
                                PyTSFX.purchase()
                                hero.take_money(cost, reason="Hiring Workers")
                                hero.add_char(char)
                                for k, v in pytfall.ea.chars.iteritems():
                                    if char in v:
                                        v.remove(char)
                        "No":
                            "Would you like to pick someone else?"
                else:
                    ea "You look a bit light on Gold [hero.name]..."
                $ block_say = False
                $ del char, cost

        elif result == ['control', 'return']:
            hide screen employment_agency
            with dissolve
            hide charla
            $ del ea, result
            jump main_street

screen employment_agency():
    vbox:
        spacing 5
        ypos 58
        for k, v in sorted(pytfall.ea.chars.iteritems(), key=itemgetter(0)):
            $ v = [w for w in v if not w.arena_active] # prevent arena active workers to be hired
            if v:
                hbox:
                    spacing 5
                    frame:
                        background Frame("content/gfx/frame/frame_bg.png", 10, 10)
                        xysize 200, 100
                        yalign .5
                        text k align .5, .5
                    for entry in v:
                        $ img = entry.show("portrait", cache=True, resize=(90, 90))
                        $ price = EmploymentAgency.calc_hire_price(entry)
                        vbox:
                            frame:
                                padding (2, 2)
                                background Frame("content/gfx/frame/MC_bg3.png")
                                imagebutton:
                                    idle img
                                    hover PyTGFX.bright_content(img, .15)
                                    action [SetVariable("char_profile_entry", "employment_agency"),
                                            SetVariable("girls", v),
                                            SetVariable("char", entry),
                                            Hide("employment_agency"),
                                            Jump("char_profile")]
                                    tooltip "View %s's Detailed Info.\nClasses: %s" % (entry.fullname, entry.traits.base_to_string)
                            button:
                                padding (2, 2)
                                xsize 94
                                background Frame("content/gfx/frame/gm_frame.png")
                                label "Tier [entry.tier]" xalign .5 text_color "#DAA520"
                                if entry.location != pytfall.jail:
                                    action Return(["hire", entry, price])
                                    tooltip "Hire %s\nFee: %d Gold" % (entry.fullname, price)
                                else:
                                    action NullAction()
                                    tooltip "Currently in jail"
    use top_stripe(True, show_lead_away_buttons=False)
