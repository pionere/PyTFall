init python:

    # Holds the current quest being looked at.
    quest_log_current_quest = None

    class QuestLogAction(Action):
        """
        Special action for the Quest log.
        """

        def __init__(self, data, mode="set"):
            """
            Creates a new QuestLogAction.
            data = The data this action executes.
            mode = How the data is used.
                "set" = Sets the data to be the current quest.
                "popup" = Sets whether the player receives quest notifications.
            """
            self.data = data
            self.mode = mode

        def __call__(self):
            """
            Actions the QuestLogAction.
            """
            global quest_log_current_quest

            q = pytfall.world_quests.get(self.data)

            if self.mode == "set":
                quest_log_current_quest = self.data

            renpy.restart_interaction()



# Screen used for the in-game quest log
# Set up as screen only (avoiding label) for easier checking during scenes as and when quest updates, etc.
#
screen quest_log():

    zorder 10

    default display_mode = "active"
    default modes = ["active", "complete", "failed"]

    frame:
        ypos 42
        background Frame("content/gfx/frame/p_frame5.png", 10, 10)
        xalign .5
        xysize (1272, 44)
        hbox:
            style_group "basic"
            spacing 10
            yalign .5
            null width 120
            $ if DEBUG and "unstarted" not in modes: modes = modes + ["unstarted"]
            for mode in modes:
                button:
                    action SetVariable("quest_log_current_quest", None), SetScreenVariable("display_mode", mode), SelectedIf(mode == display_mode)
                    text mode.capitalize() size 16

    frame:
        ypos 78
        background Frame("content/gfx/frame/p_frame5.png", 10, 10)
        xalign .5
        xysize (1270, 638)
        hbox:
            frame:
                background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                xysize (300, 628)
                viewport:
                    scrollbars "vertical"
                    draggable True
                    mousewheel True
                    xysize (270, 617)
                    ypos 10
                    if display_mode == "active":
                        vbox:
                            style_group "basic"
                            frame:
                                style_group "content"
                                xalign .5
                                xysize (270, 50)
                                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                                label (u"Active:") text_size 23 text_color ivory align .5, .6
                            null height 20
                            for i in pytfall.world_quests.active:
                                textbutton i.name action [QuestLogAction(i.name), SelectedIf(i.name == quest_log_current_quest)]

                    elif display_mode == "complete":
                        vbox:
                            style_group "basic"
                            frame:
                                style_group "content"
                                xalign .5
                                xysize (270, 50)
                                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                                label (u"Complete:") text_size 23 text_color ivory align(.5, .6)
                            null height 20
                            for i in pytfall.world_quests.complete:
                                textbutton i.name action [QuestLogAction(i.name), SelectedIf(i.name == quest_log_current_quest)]

                    elif display_mode == "failed":
                        vbox:
                            style_group "basic"
                            frame:
                                style_group "content"
                                xalign .5
                                xysize (270, 50)
                                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                                label (u"Failed:") text_size 23 text_color ivory align(.5, .6)
                            null height 20
                            for i in pytfall.world_quests.failed:
                                textbutton i.name action [QuestLogAction(i.name), SelectedIf(i.name == quest_log_current_quest)]

                    elif display_mode == "unstarted":
                        vbox:
                            style_group "basic"
                            frame:
                                style_group "content"
                                xalign .5
                                xysize (270, 50)
                                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                                label (u"Unstarted:") text_size 23 text_color ivory align(.5, .6)
                            null height 20
                            for i in pytfall.world_quests.quests:
                                if not i.active and not i.complete and not i.failed:
                                    textbutton i.name action [QuestLogAction(i.name), SelectedIf(i.name == quest_log_current_quest)]

            frame:
                style_group "content"
                background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                xysize (954, 623)
                ypos 2
                viewport:
                    pos (15, 20)
                    scrollbars "vertical"
                    draggable True
                    mousewheel True
                    xysize (930, 617)
                    has vbox xsize 850
                    if quest_log_current_quest is not None:
                        $ temp = list(reversed(pytfall.world_quests.get(quest_log_current_quest).prompts))
                        if temp:
                            text temp[0] style "TisaOTMolxm" size 20 xpos 20 xanchor .0
                            $ temp = temp[1:]
                            null height 2
                            text "------------------------------------" style "TisaOTMolxm" size 20
                            null height 2
                            for i in temp:
                                text i color (211, 211, 211, 180) style "TisaOTMolxm" size 18 xpos 20 xanchor .0

    use top_stripe(True, show_lead_away_buttons=False)
