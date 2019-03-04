#-------------------------------------------------------------------------------
# this rpy handles jumps from special consumables which have jump_to_label field
#-------------------------------------------------------------------------------
label special_items_slime_bottle:
    scene bg h_profile with dissolve
    menu:
        "It's an old bottle with unknown, thick substance inside. Do you want to open it?"
        "Yes":
            "The seal is durable, but eventually, it gives up, and pressurized liquid is released."
            $ tier = locked_random("uniform", max(hero.tier, .5), hero.tier+.7)
            if locked_dice(80):
                $ status_ = "free"
                $ patterns_ = ["Combatant", "Server"]
            else:
                $ status_ = "slave"
                $ patterns_ = ["Server"]
            $ new_slime = build_rc(id="Slime", tier=tier, bt_go_patterns=patterns_, set_status=status_)
            $ del status_
            $ del patterns_
            $ del tier

            $ new_slime.gfx_mod_stat("disposition", 300)
            $ new_slime.gfx_mod_stat("affection", affection_reward(new_slime))
            $ spr = new_slime.get_vnsprite()
            if locked_dice(50):
                $ new_slime.override_portrait("portrait", "happy")
                "The liquid quickly took the form of a girl."
                show expression spr at center with dissolve
                if new_slime.status == "free":
                    new_slime.say "Finally, someone opened it! Thanks a lot!"
                    new_slime.say "They promised me to smuggle me into the city, but something must have gone wrong!"
                    new_slime.say "I thought that I'd die in that bottle."
                    new_slime.say "All I wanted is a steady job and a roof over my head..."
                    menu:
                        "Propose to work for you":
                            new_slime.say "Gladly!"
                            $ hero.add_char(new_slime)
                            "It looks like you have a new worker."
                        "Leave her be":
                            "Thanks again, [hero.name]."
                            hide expression spr with dissolve
                            "She leaves."
                else:
                    new_slime.say "Hello. Are you my new owner? I was stored in that bottle for transport."
                    menu:
                        "Yes":
                            new_slime.say "It's a pleasure to serve you."
                            new_slime.say "It was very uncomfortable to be trapped in that small container for so long."
                            $ hero.add_char(new_slime)
                            "It looks like you have a new slave."
                        "No":
                            $ new_slime.override_portrait("portrait", "sad")
                            new_slime.say "Oh, this is bad... What should I do now? I guess I'll try to find my old master then..."
                            menu:
                                "Propose to become her owner":
                                    $ new_slime.override_portrait("portrait", "happy")
                                    $ hero.add_char(new_slime)
                                    new_slime.say "Of course! It's a pleasure to serve you."
                                    "You have a new slave."
                                "Leave her be":
                                    hide expression spr with dissolve
                                    "She leaves."
            else:
                $ new_slime.override_portrait("portrait", "angry")
                "The liquid quickly took the form of a girl."
                show expression spr at center with dissolve
                new_slime.say "AAAAGHHHHHH!"
                "She attacks you!"

                $ new_slime.front_row = True
                $ enemy_team = Team(name="Enemy Team", max_size=3)
                $ enemy_team.add(new_slime)
                $ result = run_default_be(enemy_team, slaves=True,
                                          background="content/gfx/bg/be/b_dungeon_1.webp",
                                          track="random", prebattle=True, death=False,
                                          use_items=True)

                if not (result):
                    jump game_over
                else:
                    scene bg h_profile
                    "You managed to beat her. Her liquid body quickly decays. It looks like she spent way too long in captivity and lost her mind..."
                    $ kill_char(new_slime)
                    python:
                        for member in hero.team:
                            member.gfx_mod_exp(exp_reward(member, enemy_team))
        "No":
            "Maybe another time."
            $ inv_source.add_item("Unusual Bottle")
            jump char_equip

    $ new_slime.restore_portrait()
    jump char_equip

label special_items_empty_extractor:
    if eqtarget.exp <= 2000:
        $ inv_source.add_item("Empty Extractor")

        if eqtarget <> hero:
            $ spr = eqtarget.get_vnsprite()
            show expression spr at center with dissolve
            $ renpy.show_screen('message_screen', "Unfortunately, [eqtarget.name] is not experienced enough yet to share her knowledge with anybody.")
        else:
            $ renpy.show_screen('message_screen', "Unfortunately, you are not experienced enough yet to share your knowledge with anybody.")
        jump char_equip
    else:
        scene bg h_profile
        if eqtarget <> hero:
            $ spr = eqtarget.get_vnsprite()
            show expression spr at center with dissolve
            "This device will extract some of [eqtarget.name]'s experience."
            $ eqtarget.gfx_mod_stat("disposition", -randint(25, 50))
            $ eqtarget.gfx_mod_stat("affection", -randint(2, 5))
            if eqtarget.get_stat("joy") >= 55:
                $ eqtarget.gfx_mod_stat("joy", -10)
        else:
            "This device will extract some of your experience."

        menu:
            "Do you want to use it?"
            "Yes":
                if eqtarget <> hero:
                    "She slightly shudders when the device starts to work."
                    $ eqtarget.gfx_mod_stat("disposition", -randint(20, 30))
                    $ eqtarget.gfx_mod_stat("affection", -randint(2, 3))
                else:
                    "For a moment you feel weak, but unpleasant pain somewhere inside your head."
                $ eqtarget.gfx_mod_exp(-2000)
                $ hero.add_item("Full Extractor", 1)
                "The device seems to be full of energy."
            "No":
                $ inv_source.add_item("Empty Extractor")
                $ pass
    jump char_equip

label special_items_full_extractor:
    if eqtarget.has_flag("dnd_exp_extractor"):
        $ renpy.show_screen('message_screen', "Experience already has been transferred to this person today. It cannot be done too often.")
        $ inv_source.add_item("Full Extractor")
        jump char_equip
    $ eqtarget.set_flag("dnd_exp_extractor")

    $ inv_source.add_item("Empty Extractor")
    if eqtarget <> hero:
        $ spr = eqtarget.get_vnsprite()
        show expression spr at center with dissolve
        $ renpy.show_screen('message_screen', "The energy of knowledge slowly flows inside [eqtarget.name]. She became more experienced.")
        if eqtarget.get_stat("disposition") < 750:
            $ eqtarget.gfx_mod_stat("disposition", randint(25, 50))
        if eqtarget.get_stat("affection") < 750:
            $ eqtarget.gfx_mod_stat("affection", affection_reward(eqtarget))
        if eqtarget.get_stat("joy") < 50:
            $ eqtarget.gfx_mod_stat("joy", 10)
    else:
        $ renpy.show_screen('message_screen', "The energy of knowledge slowly flows inside you. You became more experienced.")

    $ eqtarget.gfx_mod_exp(exp_reward(eqtarget, eqtarget, exp_mod=1500.0/DAILY_EXP_CORE))

    jump char_equip

label special_items_one_for_all:
    if "Undead" in eqtarget.traits:
        $ renpy.show_screen('message_screen', "This item can't be used on undead girls.")
        $ inv_source.add_item("One For All")
        jump char_equip
        
    if eqtarget.status <> "slave":
        $ renpy.show_screen('message_screen', "It would be unwise to use it on a free girl, unless you'd like to spend the rest of your live in prison.")
        $ inv_source.add_item("One For All")
        jump char_equip

    if eqtarget.get_stat("health") < 50 and eqtarget.get_stat("mp") < 50 and eqtarget.get_stat("vitality") < 50:
        $ renpy.show_screen('message_screen', "Her body is in a poor condition. It will be a waste to use this item on her.")
        $ inv_source.add_item("One For All")
        jump char_equip

    $ spr = eqtarget.get_vnsprite()
    scene bg h_profile
    show expression spr at center
    with dissolve

    menu:
        "Using this item will kill [eqtarget.name] on the spot. Continue?"
        "Yes":
            $ pass
        "No":
            $ inv_source.add_item("One For All")
            jump char_equip
    $ health = eqtarget.get_stat("health")
    $ n = health/100
    if n > 0:
        $ hero.add_item("Great Healing Potion", amount=n)
        $ health -= n*100
    $ n = health/50
    if n > 0:
        $ hero.add_item("Healing Potion", amount=n)
        $ health -= n*50
    $ n = health/25
    if n > 0:
        $ hero.add_item("Small Healing Potion", amount=n)
        $ health -= n*25
    if health > 0:
        $ hero.add_item("Small Healing Potion")

    $ mp = eqtarget.get_stat("mp")
    $ n = mp/100
    if n > 0:
        $ hero.add_item("Great Mana Potion", amount=n)
        $ mp -= n*100
    $ n = mp/50
    if n > 0:
        $ hero.add_item("Mana Potion", amount=n)
        $ mp -= n*50
    $ n = mp/25
    if n > 0:
        $ hero.add_item("Small Mana Potion", amount=n)
        $ mp -= n*25
    if mp > 0:
        $ hero.add_item("Small Mana Potion")

    $ vitality = eqtarget.get_stat("vitality")
    $ n = vitality/100
    if n > 0:
        $ hero.add_item("Great Potion of Serenity", amount=n)
        $ vitality -= n*100
    $ n = vitality/50
    if n > 0:
        $ hero.add_item("Potion of Serenity", amount=n)
        $ vitality -= n*50
    $ n = vitality/25
    if n > 0:
        $ hero.add_item("Small Potion of Serenity", amount=n)
        $ vitality -= n*25
    if vitality > 0:
        $ hero.add_item("Small Potion of Serenity")

    hide expression spr
    show expression HitlerKaputt(spr, 50) as death
    play events "events/item_4.wav"
    pause 2.5
    hide death
    "[eqtarget.name]'s body crumbles as her life energies turn into potions in your inventory."
    $ eqtarget.mod_stat("disposition", -1000) # in case if we'll have reviving one day
    $ eqtarget.mod_stat("affection", -1000)   # in case if we'll have reviving one day
    $ kill_char(eqtarget)
    jump mainscreen

label special_items_herbal_extract:
    $ h = eqtarget.get_max("health") - eqtarget.get_stat("health")
    if h <= 0:
        $ inv_source.add_item("Herbal Extract")
        $ renpy.show_screen('message_screen', "There is no need to use it at the moment, health is full.")
        jump char_equip
    $ v = eqtarget.get_stat("vitality")
    if v <= 10:
        $ inv_source.add_item("Herbal Extract")
        $ renpy.show_screen('message_screen', "Not enough vitality to use it.")
        jump char_equip
    if h <= v:
        $ eqtarget.mod_stat("health", h)
        $ eqtarget.mod_stat("vitality", -h)
    else:
        $ eqtarget.mod_stat("health", v)
        $ eqtarget.mod_stat("vitality", -v)
    play events "events/item_2.wav"
    jump char_equip

label special_items_emerald_tincture:
    $ h = eqtarget.get_max("health") - eqtarget.get_stat("health")
    $ eqtarget.mod_stat("health", h/2)
    $ h = eqtarget.get_max("vitality") - eqtarget.get_stat("vitality")
    $ eqtarget.mod_stat("vitality", h/2)
    $ eqtarget.mod_stat("mp", -eqtarget.get_max("mp")/4)
    play events "events/item_2.wav"
    jump char_equip

label special_items_flashing_extract:
    if eqtarget.flag("drunk_flashing_extract"):
        $ renpy.show_screen('message_screen', "[eqtarget.name] already used it before, it can be used only once.")
        $ inv_source.add_item("Flashing Extract")
        jump char_equip
    else:
        $ eqtarget.set_flag("drunk_flashing_extract")
        $ renpy.show_screen('message_screen', "[eqtarget.name] becomes a bit faster (+1 AP).")
        $ eqtarget.baseAP += 1
        play events "events/item_3.wav"
        jump char_equip

label special_items_puke_cola:
    if not 'Food Poisoning' in eqtarget.effects:
        $ eqtarget.mod_stat("health", randint(85, 255))
        $ eqtarget.up_counter("dnd_food_poison_counter", 5)
        if eqtarget.flag("dnd_food_poison_counter") >= 7:
            $ eqtarget.enable_effect('Food Poisoning')
        play events "events/item_cola.mp3"
    else:
        $ renpy.show_screen('message_screen', "{} is already suffering from food poisoning. More of this «puke» stuff won't do any good.".format(eqtarget.name))
        $ inv_source.add_item("Puke-a-Cola")
    jump char_equip

label special_items_cleaning_cloud:
    $ clean_list = list(i for i in hero.buildings if i.dirt > 0)
    if clean_list:
        python:
            for i in clean_list:
                i.moddirt(-200)
            renpy.show_screen('message_screen', "You release the cloud, making all your buildings cleaner.")
        play events "events/item_1.wav"
        with Fade(.5, .2, .0, color=yellow)
    else:
        $ inv_source.add_item("Cleaning Cloud")
        $ renpy.show_screen('message_screen', "You don't own any buildings which require cleaning, using this item is meaningless.")
    jump char_equip
