init python:
    register_event("smc_1", locations=["slave_market_club"], priority=100,
                    start_day=5, dice=100, max_runs=1, trigger_type="auto")

label smc_1(event):
    $ g = npcs["Blue_slavemarket"].say
    show expression npcs["Blue_slavemarket"].get_vnsprite() as blue at right
    with dissolve
    g "Oh [hero.name]! Join us. We're about to test a new gadget!"
    g "Recently delivered from Abby's Crossing! Our tech capital!"
    g "Take a look:"
    show smc initial at left
    with fade
    g "Isn't it nice?"
    g "The crowd seems to be loving it!"
    menu:
        g "How about we turn this baby on? Would you do us the honors?"
        "Let's do this!":
            $ pass
        "I am not really into this...":
            g "Oh look, he's all shy! Well, we  ain't going to let him stop us? Are we?"
            show smc power_on
            with dissolve
            play events "events/machine_up.mp3"
            pause .2
            "..."
            return

    show smc power_on
    with dissolve
    play events "events/machine_up.mp3"
    pause .2
    play events2 "female/aah.mp3"
    g "Just look at her GO! Fantastic!"
    g "This device is just simple enough to be brilliant!"
    show smc getting_bored
    with dissolve
    play events2 "female/uhm.mp3"
    g "But what is this? It looks like she's getting bored! I've trained her well, and something this simple isn't much of a challenge at all!"
    g "So... let us try another setting?!"
    menu:
        g "[hero.name]?"
        "Increase the speed of the console!":
            $ pass
    show smc speed_up
    with dissolve
    play events2 "female/ooh.mp3"
    g "This does the trick! Just look at her go!!!"
    show smc post_speed_up
    with dissolve
    g "She sure looks like she's enjoying this!"
    g "Yet... we got to make the girl cum, don't we?"
    g "And she's one of my personal projects, so she won't go down this easily!"
    menu:
        g "Would you mind?"
        "Push it all the way!":
            $ pass
    show smc speed_max
    with dissolve
    play events2 "female/ooohyeah.mp3"
    g "This is superb! JUST LOOK AT HER GO!"
    g "Let's do a countdown!"
    "10"
    "9"
    show smc speed_max
    with vpunch
    "8"
    "7"
    "6"
    show smc speed_max
    with vpunch
    "5"
    "4"
    "3"
    "2"
    scene bg slave_market_club
    with hpunch
    show smc finish
    with irisin
    "and... 1! Machine Overload!!!"
    play events "events/machine_down.mp3"
    play events2 "female/orgasm.mp3"
    $ renpy.pause(18.0, hard=True)
    hide smc
    with moveouttop
    show expression npcs["Blue_slavemarket"].get_vnsprite() as blue at right
    g "Now wasn't that fun?"
    g "I could bet you my whip that sales will go over the roof today even without that damn weasel!"
    g "Well, see you around and remember that this is the best quality Slave Market in the town!"
    return
