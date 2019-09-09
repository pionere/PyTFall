label game_over:
    #$ pytfall.enter_location("game_over", music=False, env=None)
    python hide:
        for i in renpy.audio.audio.channels:
            renpy.audio.audio.channels[i].callback = None # FIXME should not be necessary
            renpy.music.stop(i)
    $ hs()
    scene bg game_over
    with dissolve
    show screen game_over
    play events "events/game_over.mp3"
    $ ui.interact()

screen game_over:
    timer 6.0 action MainMenu(confirm=False)
    key "mousedown_1" action Stop("events"), MainMenu(confirm=False)
    key "mousedown_3" action Stop("events"), MainMenu(confirm=False)