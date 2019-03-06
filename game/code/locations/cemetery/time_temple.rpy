label time_temple:
    if not "cemetery" in ilists.world_music:
        $ ilists.world_music["cemetery"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("cemetery")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["cemetery"]) fadein .5

    $ global_flags.del_flag("keep_playing_music")

    scene bg time_temple
    with dissolve
    show screen time_temple

    if not global_flags.has_flag("visited_time_temple"):
        $ global_flags.set_flag("visited_time_temple")
        "You enter a massive dimly lit building. Strange voiceless figures in the hoods sweep the floor and replace burned-out candles."
        show expression npcs["time_miel"].get_vnsprite() as npc
        with dissolve
        $ t = npcs["time_miel"].say
        "A strange girl of unknown race approaches you. Most of her belly is a giant, working hourglass."
        t "Welcome to the Temple of Time, stranger. I'm Miel, its caretaker."
        t "If you need something, I'm here to help. Please don't bother others."
    else:
        show expression npcs["time_miel"].get_vnsprite() as npc
        with dissolve
        $ t = npcs["time_miel"].say
        t "Welcome to the Temple. May I help you?"

    menu time_temple_menu:
        "Healing":
            if hero.has_flag("dnd_time_healing_day"):
                t "I'm sorry, it's impossible to perform the procedure twice per day."
                jump time_temple_menu

            if not global_flags.has_flag("asked_miel_about_healing"):
                $ global_flags.set_flag("asked_miel_about_healing")
                t "Indeed, like any other temple we can heal your body and soul."
                t "Or rather, reverse the time and restore them to former condition."
                t "But we do it only once per day. Such is the natural limitation of time flow."

            python:
                temp_charcters = {}
                for i in hero.team:
                    temp = i.get_max("health") + i.get_max("mp") + i.get_max("vitality") - \
                           (i.get_stat("health") + i.get_stat("mp") + i.get_stat("vitality"))
                    if temp > 0:
                        temp_charcters[i] = temp
                del i

            if not temp_charcters:
                t "I don't see the need in healing right now."
                "Miel can only restore characters in your team, including the main hero."
                $ del temp_charcters
                jump time_temple_menu
            else:
                $ res = sum(temp_charcters.values())

                t "I see your team could use our services. It will be [res] gold."
                if hero.gold < res:
                    "Unfortunately, you don't have enough money."
                else:
                    menu:
                        "Pay":
                            $ hero.set_flag("dnd_time_healing_day")
                            play sound "content/sfx/sound/events/clock.ogg"
                            python hide:
                                hero.take_money(res, reason="Time Temple")

                                img = "content/gfx/bg/locations/deep_sea.webp"
                                img = im.MatrixColor(img, im.matrix.brightness(.3))
                                img = Transform(img, alpha=.85)
                                renpy.show("sea", what=img)
                                renpy.with_statement(Dissolve(.5))
                                renpy.hide("sea")
                                renpy.with_statement(Dissolve(.3))

                                for i in temp_charcters:
                                    i.gfx_mod_stat("health", i.get_max("health") - i.get_stat("health"))
                                    i.gfx_mod_stat("mp", i.get_max("mp") - i.get_stat("mp"))
                                    i.gfx_mod_stat("vitality", i.get_max("vitality") - i.get_stat("vitality"))
                            t "Done. Please come again if you need our help."
                        "Don't Pay":
                            t "Very well."
                $ del res, temp_charcters
                jump time_temple_menu
                        
        "Restore AP":
            if not global_flags.has_flag("asked_miel_about_ap"):
                $ global_flags.set_flag("asked_miel_about_ap")
                t "I can return you the time you spent. But it's an expensive procedure."
                "Miel can restore your action points, as long as you can pay for it."
                "Only you can use this option, your teammates are not affected."
            if hero.AP >= hero.setAP:
                "Your action points are maxed out already at the moment."
                jump time_temple_menu
            if hero.gold < 100000:
                "Unfortunately, you don't have 100000 gold coins to pay."
            else:
                "Do you wish to pay 100000 gold to restore AP for [hero.name]?"
                menu:
                    "Yes":
                        play sound "content/sfx/sound/events/clock.ogg"
                        python hide:
                            hero.take_money(100000, reason="Time Temple")

                            img = "content/gfx/bg/locations/forest_1.webp"
                            img = Transform(img, alpha=.8, xpos=-(850*5), xzoom=5, yzoom=4)
                            renpy.show("forest", what=img)
                            renpy.with_statement(Dissolve(.6))
                            renpy.hide("forest")
                            renpy.with_statement(Dissolve(.4))

                            hero.AP = hero.setAP
                        t "Your time has been returned to you. Come again if you need me."
                    "No":
                        $ pass
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

    use top_stripe(True, None, False, True, False)

label clone_character(character, add_to_hero=True):
    python:
        char = copy_char(character)
        store.chars[char.id + str(global_flags.get_flag("clone_id", 0))] = char
        char.init() # Normalize.
        char.apply_trait("Temporal Clone")
        if add_to_hero:
            store.hero.add_char(char)
        global_flags.up_counter("clone_id")
    return
