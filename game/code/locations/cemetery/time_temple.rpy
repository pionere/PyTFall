label time_temple:
    # Music
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("cemetery", fadein=.5)
    $ global_flags.del_flag("keep_playing_music")

    scene bg time_temple
    with dissolve
    show screen time_temple

    if global_flags.has_flag("visited_time_temple"):
        show expression npcs["time_miel"].get_vnsprite() as npc
        with dissolve
        $ t = npcs["time_miel"].say
        t "Welcome to the Temple. May I help you?"
    else:
        $ global_flags.set_flag("visited_time_temple")
        "You enter a massive dimly lit building. Strange voiceless figures in the hoods sweep the floor and replace burned-out candles."
        show expression npcs["time_miel"].get_vnsprite() as npc
        with dissolve
        $ t = npcs["time_miel"].say
        "A strange girl of unknown race approaches you. Most of her belly is a giant, working hourglass."
        t "Welcome to the Temple of Time, stranger. I'm Miel, its caretaker."
        t "If you need something, I'm here to help. Please don't bother others."

    menu time_temple_menu:
        "Healing":
            if not global_flags.has_flag("asked_miel_about_healing"):
                $ global_flags.set_flag("asked_miel_about_healing")
                t "Indeed, like any other temple we can heal your body and soul."
                t "Or rather, reverse the time and restore them to former condition."
                t "But we do it only once per day. Such is the natural limitation of time flow."

            $ temp, tmp = dict(), list()
            python hide:
                for i in hero.team:
                    val = 0
                    for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                        val += i.get_max(stat) - i.get_stat(stat)
                    if "Food Poisoning" in i.effects:
                        val += 100
                    if "Poisoned" in i.effects:
                        val += 100
                    if "Down with Cold" in i.effects:
                        val += 50
                    if "Injured" in i.effects:
                        val += 150

                    if val > 0:
                        if i.has_flag("dnd_time_healing_day"):
                            tmp.append(i)
                        else:
                            temp[i] = val*(i.tier+3)

            if not temp:
                if tmp:
                    t "I'm sorry, it's impossible to perform the procedure twice per day."
                else:
                    t "I don't see the need in healing right now."
                    "Miel can only restore characters in your team, including the main hero."
            else:
                $ tmp = sum(temp.values())

                if len(temp) == 1:
                    if hero in temp:
                        $ msg = "you"
                    else:
                        $ msg = "that %s" % ("girl" if next(iter(temp)).gender == "female" else "guy")
                else:
                    $ msg = "some of you"
                t "I see [msg] could use our services."
                extend " It will be {color=gold}[tmp] Gold{/color}."
                $ del msg
                if hero.gold < tmp:
                    "Unfortunately, you don't have enough money."
                else:
                    "Do you want to pay {color=gold}[tmp] Gold{/color} to perform the procedure?"
                    menu:
                        "Yes":
                            play sound "content/sfx/sound/events/clock.ogg"
                            python hide:
                                hero.take_money(tmp, reason="Time Temple")

                                img = "content/gfx/bg/locations/deep_sea.webp"
                                img = im.Alpha(PyTGFX.bright_img(img, .3), alpha=.85) 
                                renpy.show("sea", what=img)
                                renpy.with_statement(Dissolve(.5))
                                renpy.hide("sea")
                                renpy.with_statement(Dissolve(.3))

                                for i in temp:
                                    for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                                        i.gfx_mod_stat(stat, i.get_max(stat) - i.get_stat(stat))

                                    i.disable_effect("Poisoned")
                                    i.disable_effect("Food Poisoning")
                                    i.disable_effect("Down with Cold")
                                    i.disable_effect("Injured")

                                    i.set_flag("dnd_time_healing_day")

                            t "Done. Please come again if you need our help."
                        "No":
                            t "Very well."
            $ del tmp, temp
            jump time_temple_menu
                        
        "Restore AP":
            if not global_flags.has_flag("asked_miel_about_ap"):
                $ global_flags.set_flag("asked_miel_about_ap")
                t "I can return you the time you spent. But it's an expensive procedure."
                "Miel can restore action points, as long as you can pay for it."

            $ temp, tmp = list(), None
            python hide:
                for i in hero.team:
                    if i.PP < i.setPP:
                        temp.append(i)

            if not temp:
                t "Sorry, but I can't help you at the moment."
                "Miel can only restore the action points of your team members, including the main hero."
            elif hero.gold < 100000:
                "Unfortunately, you don't have {color=gold}100 000 Gold{/color} coins to pay."
            else:
                $ tmp = temp[0]
                menu time_temple_ap_menu:
                    "Pay {color=gold}100 000 Gold{/color} to restore your action points" if tmp is hero:
                        $ pass
                    "Pay {color=gold}100 000 Gold{/color} to restore the action points of [tmp.name]" if tmp is not hero:
                        $ pass
                    "Pick another character" if len(temp) > 1:
                        call screen character_pick_screen(temp)
                        if _return:
                            $ tmp = _return
                        jump time_temple_ap_menu
                    "Nevermind":
                        t "All right then."
                        $ tmp = None
                if tmp is not None:
                    play sound "content/sfx/sound/events/clock.ogg"
                    python hide:
                        hero.take_money(100000, reason="Time Temple")

                        img = "content/gfx/bg/locations/forest_1.webp"
                        img = Transform(img, alpha=.8, xpos=-(850*5), xzoom=5, yzoom=4)
                        renpy.show("forest", what=img)
                        renpy.with_statement(Dissolve(.6))
                        renpy.hide("forest")
                        renpy.with_statement(Dissolve(.4))

                        tmp.PP = tmp.setPP
                    $ t("Time has been returned to %s. Come again if you need me." % ("you" if tmp is hero else tmp.name))
            $ del temp, tmp
            jump time_temple_menu

        "Remove injuries":
            if not global_flags.has_flag("asked_miel_about_wounds"):
                $ global_flags.set_flag("asked_miel_about_wounds")
                t "Yes, among other things we can heal injuries as well."
                t "It's a common problem among adventurers these days."
            $ temp, tmp = dict(), None
            python hide:
                for i in hero.team:
                    if "Injured" in i.effects:
                        temp[i] = 150*(i.tier+3)

            if not temp:
                t "No one seems to be injured here."
                "Miel can only heal characters in your team, including the main hero."
            else:
                $ tmp = sum(temp.values())

                if len(temp) == 1:
                    if hero in temp:
                        $ msg = "I see you have a quite bad wound there."
                    else:
                        $ msg = "I see that %s has a quite serious wound." % ("girl" if next(iter(temp)).gender == "female" else "guy")
                else:
                    $ msg = "I see many of you are injured."
                t "[msg]"
                extend " It will be {color=gold}[tmp] Gold{/color}."
                $ del msg
                if hero.gold < tmp:
                    "Unfortunately, you don't have enough money."
                else:
                    menu:
                        "Do you want to pay {color=gold}[tmp] Gold{/color} to heal the injuries?"
                        "Yes":
                            play sound "content/sfx/sound/events/clock.ogg"
                            python hide:
                                hero.take_money(tmp, reason="Time Temple")

                                img = "content/gfx/bg/locations/ocean_underwater.webp"
                                img = im.Alpha(PyTGFX.bright_img(img, .3), alpha=.85)
                                renpy.show("sea", what=img)
                                renpy.with_statement(Dissolve(.5))
                                renpy.hide("sea")
                                renpy.with_statement(Dissolve(.3))

                                for i in temp:
                                    i.disable_effect("Injured")
                            t "Done. Come again if you need me."
                        "No":
                            t "Fine."
            $ del tmp, temp
            jump time_temple_menu

        "Ask about this place":
            t "This is the Temple of Time. Locals come here to to pray to almighty gods of time and space."
            t "We also provide additional services, for a fee."
            jump time_temple_menu
        "Ask about her" if not global_flags.has_flag("asked_about_miel"):
            $ global_flags.set_flag("asked_about_miel")
            t "Me? I'm just a servant of time."
            t "I will exist forever with this temple as long as I'm taking care of it."
            t "This is all you need to know."
            jump time_temple_menu
        "Leave":
            t "See you soon."

    hide npc
    with dissolve
    hide screen time_temple
    $ del t
    $ global_flags.set_flag("keep_playing_music")
    stop sound
    jump graveyard_town

screen time_temple():
    use top_stripe(True, show_lead_away_buttons=False)
    use team_status(interactive=False)

#label clone_character(character, add_to_hero=True):
#    python:
#        char = copy_char(character)
#        store.chars[char.id + str(global_flags.get_flag("clone_id", 0))] = char
#        char.init() # Normalize.
#        char.apply_trait(traits["Temporal Clone"])
#        if add_to_hero:
#            hero.add_char(char)
#        global_flags.up_counter("clone_id")
#    return
