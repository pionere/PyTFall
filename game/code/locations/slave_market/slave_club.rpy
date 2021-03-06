label slave_market_club: 
    scene bg slave_market_club

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen slavemarket_club
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()
        
        if result == ["control", "return"]: 
            hide screen slavemarket_club
            jump slave_market

screen slavemarket_club():
    use top_stripe(True)

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Look Around":
            action Function(pytfall.look_around)

    $ img = im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80)
    imagebutton:
        align (.99, .5)
        idle img
        hover PyTGFX.bright_img(img, .15)
        action Return(['control', 'return'])