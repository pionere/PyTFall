# Screen used for the in-game quest log
# Set up as screen only (avoiding label) for easier checking during scenes as and when quest updates, etc.
#
screen quest_log():
    zorder 10

    default display_mode = "active"
    default modes = ["active", "complete", "failed"] + (["unstarted"] if DEBUG else [])
    default current_quest = None

    frame:
        ypos 40
        background Frame("content/gfx/frame/p_frame5.png", 10, 10)
        hbox:
            ypos 5
            ysize 40
            spacing 10
            xalign .5
            for mode in modes:
                textbutton mode.capitalize():
                    xysize (120, 40)
                    style "smenu1_button"
                    action [SetScreenVariable("display_mode", mode), SetScreenVariable("current_quest", None)]
                    text_size 16
                    selected mode == display_mode

        hbox:
            spacing 10
            $ quests = pytfall.world_quests
            if display_mode == "active":
                $ quests = quests.active
            elif display_mode == "complete":
                $ quests = quests.complete
            elif display_mode == "failed":
                $ quests = quests.failed
            else: #if display_mode == "unstarted":
                $ quests = [i for i in quests.quests if not any((i.active, i.complete, i.failed))]
            viewport:
                draggable True
                mousewheel True
                xysize (270, 607)
                ypos 50
                has vbox
                for i in quests:
                    textbutton i.name:
                        xysize (250, 30)
                        style "basic_choice2n_button"
                        action SetScreenVariable("current_quest", i)
                        selected current_quest == i

            viewport:
                draggable True
                mousewheel True
                xysize (1000, 607)
                ypos 50
                has vbox xfill True
                if current_quest is not None:
                    $ temp = list(reversed(i.prompts))
                    if temp:
                        text temp[0] style "TisaOTMolxm" size 20 xalign .5
                        $ temp = temp[1:]
                        null height 2
                        text "------------------------------------" style "TisaOTMolxm" size 20 xalign .5 
                        null height 2
                        for i in temp:
                            text i color (211, 211, 211, 180) style "TisaOTMolxm" size 18 xalign .5

    use top_stripe(True, show_lead_away_buttons=False)
