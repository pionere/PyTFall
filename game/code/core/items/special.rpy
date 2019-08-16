#-------------------------------------------------------------------------------
# this rpy handles jumps from special consumables which have jump_to_label field
#-------------------------------------------------------------------------------
label special_items_slime_bottle:
    scene bg h_profile with dissolve
    menu:
        "It's an old bottle with unknown, thick substance inside. Do you want to open it?"
        "Yes":
            "The seal is durable, but eventually, it gives up, and pressurized liquid is released."
            $ new_slime = build_rc(id="Slime",
                                   tier=locked_random("uniform", max(hero.tier, .5), hero.tier+.7),
                                   set_status="free" if locked_dice(80) else "slave")

            $ new_slime.gfx_mod_stat("disposition", 300)
            $ new_slime.gfx_mod_stat("affection", affection_reward(new_slime))

            $ char_ref = "girl" if new_slime.gender == "female" else "boy"
            "The liquid quickly took the form of a [char_ref]."

            $ spr = new_slime.get_vnsprite()
            $ ns = new_slime.say
            if locked_dice(50):
                $ new_slime.override_portrait("portrait", "happy")
                show expression spr with dissolve
                if new_slime.status == "free":
                    ns "Finally, someone opened it! Thanks a lot!"
                    ns "They promised me to smuggle me into the city, but something must have gone wrong!"
                    ns "I thought that I'd die in that bottle."
                    ns "All I wanted is a steady job and a roof over my head..."
                    menu:
                        "Propose to work for you":
                            ns "Gladly!"
                            $ hero.add_char(new_slime)
                            "It looks like you have a new worker."
                        "Leave [new_slime.op] be":
                            "Thanks again, [hero.name]."
                            hide expression spr with dissolve
                            "[new_slime.pC] leaves."
                else:
                    ns "Hello. Are you my new owner? I was stored in that bottle for transport."
                    menu:
                        "Yes":
                            ns "It's a pleasure to serve you."
                            ns "It was very uncomfortable to be trapped in that small container for so long."
                            $ hero.add_char(new_slime)
                            "It looks like you have a new slave."
                        "No":
                            $ new_slime.override_portrait("portrait", "sad")
                            ns "Oh, this is bad... What should I do now? I guess I'll try to find my old master then..."
                            menu:
                                "Propose to become [new_slime.pd] owner":
                                    $ new_slime.override_portrait("portrait", "happy")
                                    $ hero.add_char(new_slime)
                                    ns "Of course! It's a pleasure to serve you."
                                    "You have a new slave."
                                "Leave [new_slime.op] be":
                                    hide expression spr with dissolve
                                    "[new_slime.pC] leaves."
            else:
                $ new_slime.override_portrait("portrait", "angry")
                show expression spr with dissolve
                ns "AAAAGHHHHHH!"
                "[new_slime.pC] attacks you!"

                #$ new_slime.front_row = 1
                $ enemy_team = Team(name="Enemy Team")
                $ enemy_team.add(new_slime)
                $ result = run_default_be(enemy_team, background="b_dungeon_1", end_background="h_profile",
                                          track="random", prebattle=True)

                if result is True:
                    "You managed to beat [new_slime.op]. [new_slime.pdC] liquid body quickly decays. It looks like [new_slime.p] spent way too long in captivity and lost [new_slime.pd] mind..."
                    $ kill_char(new_slime)
                else:
                    jump game_over
                $ del result, enemy_team
            $ new_slime.restore_portrait()
            $ del new_slime, char_ref, spr, ns
        "No":
            "Maybe another time."
            $ inv_source.add_item("Unusual Bottle")
    jump char_equip

label special_items_empty_extractor:
    if eqtarget.exp <= 200:
        if eqtarget == hero:
            $ PyTGFX.message("Unfortunately, you are not experienced enough yet to share your knowledge with anybody.")
        else:
            show expression eqtarget.get_vnsprite()
            with dissolve
            $ PyTGFX.message("Unfortunately, [eqtarget.name] is not experienced enough yet to share [eqtarget.pd] knowledge with anybody.")
        $ inv_source.add_item("Empty Extractor")
    else:
        scene bg h_profile
        if eqtarget == hero:
            "This device will extract some of your experience."
        else:
            show expression eqtarget.get_vnsprite()
            with dissolve
            "This device will extract some of [eqtarget.name]'s experience."
            $ eqtarget.gfx_mod_stat("disposition", -randint(25, 50))
            $ eqtarget.gfx_mod_stat("affection", -randint(2, 5))
            if eqtarget.get_stat("joy") >= 55:
                $ eqtarget.gfx_mod_stat("joy", -10)

        menu:
            "Do you want to use it?"
            "Yes":
                if eqtarget == hero:
                    "For a moment you feel weak, but unpleasant pain somewhere inside your head."
                else:
                    "[eqtarget.pC] slightly shudders when the device starts to work."
                    $ eqtarget.gfx_mod_stat("disposition", -randint(20, 30))
                    $ eqtarget.gfx_mod_stat("affection", -randint(2, 3))
                $ eqtarget.gfx_mod_exp(-200)
                $ hero.add_item("Full Extractor", 1)
                "The device seems to be full of energy."
            "No":
                $ inv_source.add_item("Empty Extractor")
    jump char_equip

label special_items_full_extractor:
    if eqtarget == hero:
        $ PyTGFX.message("The energy of knowledge slowly flows inside you. You became more experienced.")
    else:
        show expression eqtarget.get_vnsprite()
        with dissolve
        $ PyTGFX.message("The energy of knowledge slowly flows inside [eqtarget.name]. [eqtarget.pC] became more experienced.")
        if eqtarget.get_stat("disposition") < 750:
            $ eqtarget.gfx_mod_stat("disposition", randint(25, 50))
        if eqtarget.get_stat("affection") < 750:
            $ eqtarget.gfx_mod_stat("affection", affection_reward(eqtarget))

    if eqtarget.get_stat("joy") < 50:
        $ eqtarget.gfx_mod_stat("joy", 10)
    $ eqtarget.gfx_mod_exp(exp_reward(eqtarget, eqtarget, exp_mod=150.0/DAILY_EXP_CORE))

    jump char_equip

label special_items_one_for_all:
    if "Undead" in eqtarget.traits:
        $ PyTGFX.message("This item can't be used on undead characters.")
        $ inv_source.add_item("One For All")
        jump char_equip
        
    if eqtarget.status <> "slave":
        $ PyTGFX.message("It would be unwise to use it on a free character, unless you'd like to spend the rest of your live in prison.")
        $ inv_source.add_item("One For All")
        jump char_equip

    if eqtarget.get_stat("health") < 50 and eqtarget.get_stat("mp") < 50 and eqtarget.get_stat("vitality") < 50:
        $ PyTGFX.message("[eqtarget.pdC] body is in a poor condition. It will be a waste to use this item on [eqtarget.op].")
        $ inv_source.add_item("One For All")
        jump char_equip

    $ spr = eqtarget.get_vnsprite()
    scene bg h_profile
    show expression spr
    with dissolve

    menu:
        "Using this item will kill [eqtarget.name] on the spot. Continue?"
        "Yes":
            $ pass
        "No":
            $ inv_source.add_item("One For All")
            $ del spr
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
    "[eqtarget.name]'s body crumbles as [eqtarget.pd] life energies turn into potions in your inventory."
    $ eqtarget.mod_stat("disposition", -1000) # in case if we'll have reviving one day
    $ eqtarget.mod_stat("affection", -1000)   # in case if we'll have reviving one day
    $ kill_char(eqtarget)
    $ del spr, n, health, mp, vitality 
    jump mainscreen

label special_items_herbal_extract:
    $ h = eqtarget.get_max("health") - eqtarget.get_stat("health")
    $ v = eqtarget.get_stat("vitality")
    if h <= 0 or v <= 10:
        if h <= 0:
            $ PyTGFX.message("There is no need to use it at the moment, health is full.")
        else:
            $ PyTGFX.message("Not enough vitality to use it.")
        $ inv_source.add_item("Herbal Extract")
    else:
        if h <= v:
            $ v = h
        $ eqtarget.mod_stat("health", v)
        $ eqtarget.mod_stat("vitality", -v)
        play events "events/item_2.wav"
    $ del h, v
    jump char_equip

label special_items_emerald_tincture:
    python hide:
        h = eqtarget.get_max("health") - eqtarget.get_stat("health")
        eqtarget.mod_stat("health", h/2)
        h = eqtarget.get_max("vitality") - eqtarget.get_stat("vitality")
        eqtarget.mod_stat("vitality", h/2)
        eqtarget.mod_stat("mp", -eqtarget.get_max("mp")/4)
    play events "events/item_2.wav"
    jump char_equip

label special_items_flashing_extract:
    if eqtarget.flag("drunk_flashing_extract"):
        $ PyTGFX.message("[eqtarget.name] already used it before, it can be used only once.")
        $ inv_source.add_item("Flashing Extract")
    else:
        $ PyTGFX.message("[eqtarget.name] becomes a bit faster (+1 AP).")
        $ eqtarget.set_flag("drunk_flashing_extract")
        $ eqtarget.basePP += 100 # PP_PER_AP
        play events "events/item_3.wav"
    jump char_equip

label special_items_puke_cola:
    if 'Food Poisoning' in eqtarget.effects:
        $ PyTGFX.message("[eqtarget.name] is already suffering from food poisoning. More of this «puke» stuff won't do any good.")
        $ inv_source.add_item("Puke-a-Cola")
    else:
        $ eqtarget.mod_stat("health", randint(85, 255))
        $ eqtarget.up_counter("dnd_food_poison_counter", 5)
        if eqtarget.flag("dnd_food_poison_counter") >= 7:
            $ eqtarget.enable_effect('Food Poisoning')
        play events "events/item_cola.mp3"
    jump char_equip

label special_items_cleaning_cloud:
    $ i = None
    $ clean_list = list(i for i in hero.buildings if i.dirt > 0)
    if clean_list:
        python:
            PyTGFX.message("You release the cloud, making all your buildings cleaner.")
            for i in clean_list:
                i.moddirt(-200)
        play events "events/item_1.wav"
        with Fade(.5, .2, .0, color="yellow")
    else:
        $ PyTGFX.message("You don't own any buildings which require cleaning, using this item is meaningless.")
        $ inv_source.add_item("Cleaning Cloud")
    $ del i, clean_list
    jump char_equip
