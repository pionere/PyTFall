label employment_agency:
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("shops", fadein=1.5)
    $ global_flags.del_flag("keep_playing_music")

    scene bg realtor_agency
    with dissolve

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show expression npcs["Charla_ea"].get_vnsprite() at Transform(align=(.9, 1.0)) as charla with dissolve

    $ ea = npcs["Charla_ea"].say

    if not global_flags.has_flag("visited_employment_agency"):
        $ global_flags.set_flag("visited_employment_agency", True)
        ea "Welcome to my Employment Agency, my name is Charla."
        ea "I am always on a lookout for perspective Employees and Employers."
        ea "You certainly look like one of the Employers!"
        ea "My fee for hooking you up with a capable worker is one month worth of their wages."
        ea "Take a look at the files I got on hand!"

    show screen employment_agency
    while 1:
        $ result = ui.interact()

        if result[0] == 'hire':
            $ char = result[1]
            $ cost = EmploymentAgency.calc_hire_price(char) # Two month of wages to hire.
            $ block_say = True
            if hero.gold >= cost:
                menu:
                    ea "The fee to hire [char.name] is [cost]! What do you say?"
                    "Yes":
                        python hide:
                            renpy.play("content/sfx/sound/world/purchase_1.ogg")
                            hero.take_money(cost, reason="Hiring Workers")
                            hero.add_char(char)
                            eachars = pytfall.ea.chars
                            for occ in char.gen_occs:
                                if char in eachars[occ]:
                                    eachars[occ].remove(char)
                    "No":
                        "Would you like to pick someone else?"
            else:
                ea "You look a bit light on the Gold [hero.name]..."
            $ block_say = False
            $ del char, cost

        elif result == ['control', 'return']:
            hide screen employment_agency
            with dissolve
            hide charla
            $ del ea, result
            jump main_street

screen employment_agency():
    modal True
    zorder 1

    vbox:
        spacing 5
        yalign .5
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
                                    tooltip "View {}'s Detailed Info.\nClasses: {}".format(entry.fullname, entry.traits.base_to_string)
                            button:
                                padding (2, 2)
                                xsize 94
                                background Frame("content/gfx/frame/gm_frame.png")
                                label "Tier [entry.tier]" xalign .5 text_color "#DAA520"
                                if entry.location != pytfall.jail:
                                    action Return(['hire', entry, v])
                                    tooltip "Hire {}.\nFee: {}G".format(entry.fullname, EmploymentAgency.calc_hire_price(entry))
                                else:
                                    action NullAction()
                                    tooltip "Currently in jail"
    use exit_button()
