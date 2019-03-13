init -1 python:
    register_event("found_sad_cat_1", locations=["main_street"], run_conditions=["dice(100)"], priority=5000, dice=0, start_day=1, restore_priority=0, jump=True, times_per_days=(1,0))

label found_sad_cat_1:
    hide screen main_street
    scene bg street_alley
    $ temp = npcs["sad_cat"].show("profile", "tired", resize = (295, 340))
    show expression temp at left
    with dissolve
    hero.say "Oh. There is a cat in that narrow alley. It looks exhausted."
    menu:
        "Pet it":
            hide temp
            $ temp = npcs["sad_cat"].show("profile", "scared", resize = (295, 340))
            show expression temp at left
            "The cat is frightened as you approach, and quickly runs away."
            hide expression temp with dissolve
            hero.say "Maybe a treat of some kind will help? I suppose cats like fish..."
            $ kill_event("found_sad_cat_1")
            $ register_event("found_sad_cat_2", locations=["main_street"], run_conditions=["dice(100)"], priority=5000, dice=0, start_day=day+1, restore_priority=0, jump=True, times_per_days=(1,0))
        "Ignore it":
            "There are plenty of cats in the city. No need to pay any attention."
        "Drive it away":
            hide temp
            $ temp = npcs["sad_cat"].show("profile", "scared", resize = (295, 340))
            show expression temp at left
            "The cat is frightened as you approach, and quickly runs away."
            $ kill_event("found_sad_cat_1")
    $ global_flags.set_flag("keep_playing_music")
    $ del temp
    jump main_street

label found_sad_cat_2:
    hide screen main_street
    scene bg street_alley
    $ temp = npcs["sad_cat"].show("profile", "tired", resize = (295, 340))
    show expression temp at left
    with dissolve
    $ fish = list(i for i in hero.inventory if i.type == "fish" and i.price >= 3)
    if not(fish):
        hero.say "This cat again. Sorry, I have nothing for you."
    else:
        hero.say "This cat again. I have some fish. Maybe it will like it?"
        menu:
            "Give some fish to the cat":
                hide temp
                $ temp = npcs["sad_cat"].show("profile", "indifferent", resize = (295, 340))
                show expression temp at left
                "The cat snatches the fish from your hands and runs away."
                hide temp with dissolve
                hero.say "What an ungrateful animal..."
                $ hero.remove_item(random.choice(fish).id)
                $ kill_event("found_sad_cat_2")
                $ register_event("found_sad_cat_3", locations=["main_street"], run_conditions=["dice(100)"], priority=5000, dice=0, start_day=day+1, restore_priority=0, jump=True, times_per_days=(1,0))
            "Maybe later":
                hero.say "I have a more important business to attend right now."
                hide temp with dissolve
            "Drive it away":
                hide temp
                $ temp = npcs["sad_cat"].show("profile", "scared", resize = (295, 340))
                show expression temp at left
                "The cat is frightened as you approach, and quickly runs away."
                $ kill_event("found_sad_cat_2")
    $ global_flags.set_flag("keep_playing_music")
    $ del temp, fish
    jump main_street

label found_sad_cat_3:
    hide screen main_street
    scene bg street_alley
    $ temp = npcs["sad_cat"].show("profile", "tired", resize = (295, 340))
    show expression temp at left
    with dissolve
    $ fish = list(i for i in hero.inventory if i.type == "fish" and i.price >= 3)
    if not(fish):
        hero.say "This cat again. Sorry, I have nothing for you."
    else:
        hero.say "This cat again. I have some fish too."
        menu:
            "Give some fish to the cat":
                hide temp
                $ temp = npcs["sad_cat"].show("profile", "confident", resize = (295, 340))
                show expression temp at left
                "The cat cautiously approaches and sniffs you, then snatches the fish and runs away."
                hide temp with dissolve
                hero.say "It wasn't as frightened today... I guess."
                $ hero.remove_item(random.choice(fish).id)
                $ kill_event("found_sad_cat_3")
                $ register_event("found_sad_cat_4", locations=["main_street"], run_conditions=["dice(100)"], priority=5000, dice=0, start_day=day+1, restore_priority=0, jump=True)
            "Maybe later":
                hero.say "I have a more important business to attend right now."
                hide temp with dissolve
            "Drive it away":
                hide temp
                $ temp = npcs["sad_cat"].show("profile", "scared", resize = (295, 340))
                show expression temp at left
                "The cat is frightened as you approach, and quickly runs away."
                $ kill_event("found_sad_cat_3")
    $ global_flags.set_flag("keep_playing_music")
    $ del temp, fish
    jump main_street

label found_sad_cat_4:
    hide screen main_street
    scene bg street_alley
    $ cat = npcs["sad_cat"]
    $ temp = cat.show("profile", "in pain", resize = (295, 340))
    show expression temp at left
    with dissolve
    $ npcs["sad_cat"].override_portrait("portrait", "in pain")
    cat.say "Meow..."
    hero.say "It's badly hurt. Those wounds are very deep. They won't heal on their own."
    $ potion = list(i for i in hero.inventory if i.id in ["Small Healing Potion", "Healing Potion", "Great Healing Potion", "Ultimate Healing Potion"])
    if potion:
        hero.say "I can heal it with healing potion..."
        menu:
            "Heal it":
                $ potion.sort(key=attrgetter("price"))
                $ hero.remove_item(potion[0])
                $ flash = Fade(.25, 0, .75, color="red")
                scene bg street_alley
                with flash
                $ del flash
                hide expression temp
                $ temp = cat.show("profile", "happy", resize = (295, 340))
                show expression temp at left
                $ cat.override_portrait("portrait", "happy")
                cat.say "Meow!"
                "The cat looks much better now."
                hero.say "I should go now."
                hide expression temp
                with dissolve
                $ temp = cat.show("vnsprite", "happy", resize = (295, 340))
                show expression temp at center
                cat.say "Meow!"
                hero.say "The cat follows me. I suppose it's not safe for him to stay here."
                extend " I need to give him a name."
                $ n = renpy.call_screen("pyt_input", "Fluffy", "Enter name for your cat", 20)
                if not(len(n)):
                    $ n = "Cat"
                $ cat.name = cat.fullname = cat.nickname = n
                $ cat.update_sayer()
                $ del n
                cat.say "Meow!"
                hero.say "Let's go, [cat.name]."
                $ items["Your Pet"].desc = "%s, the cat you found on city streets. Cute, funny and loyal, all girls just love him." %cat.name
                $ hero.add_item("Your Pet")
                "You got yourself a pet cat."
                $ kill_event("found_sad_cat_4")
            "Don't heal":
                hero.say "I need those potions for myself."
    else:
        hero.say "It still can be healed with a healing potion, but I don't have any right now."

    $ global_flags.set_flag("keep_playing_music")
    $ cat.restore_portrait()
    $ del cat, potion, temp
    jump main_street

