init python hide:
    # Add quest
    # Alex: We've changed manual to True to be used as a default setting for all quests.
    q = register_quest("Strange Idol", manual=None)

    # Add first event
    # q.condition(stage, strict, *flags) allows for run conditions based on the current status of the quest
    # stage=What stage the quest is at
    # strict=Whether to check == or >= for the stage
    # flags=Flags to check for as well
    #
    # (Yes, setting dice to 100 would have worked as well, but I wanted to show off the condition function)
    register_event("strange_idol1", locations=["main_street"], dice=None, run_conditions=[q.condition(0, True)], max_runs=1)

label strange_idol1(event):
    hero.say "Huh?"
    "You bend down to pick something up off the floor."
    # Advance quest
    $ advance_quest(event.quest, "You found a piece of an idol! How strange.", piece1=True) # Can access the quest straight in the event.
    hero.say "Its... part of a statue?"
    "You try to place the piece aside, but after fighting against your impulses, you decide to take it with you."
    # Remove event
    $ kill_event("strange_idol1")

    # Create second part of quest
    $ register_event("strange_idol2", locations=["main_street"], dice=100, max_runs=2, restore_priority=1)

    return

label strange_idol2(event):
    hero.say "Huh?"
    "You bend down to pick something up off the floor."

    python:
        # Use in syntax for easy flag checking
        if pytfall.world_quests.quest_instance(event.quest).stage == 2:
            advance_quest(event.quest, "You found another piece of the idol! I think its complete.", piece3=True)

            # Remove event
            kill_event("strange_idol2")

            # Create third part of quest
            register_event("strange_idol3", locations=["mainscreen"], trigger_type="auto", dice=100, max_runs=1, start_day=day+1)

        else:
            advance_quest(event.quest, "You found another piece of the idol! I wonder how many there are?", piece2=True)
    hero.say "Its... another part of that statue!"
    "You take the piece with you, wondering how many there are."
    return

label strange_idol3(event):
    "As you wake you feel a strange sensation move through you, almost as if your very soul was being caressed."
    "Suddenly a bright flash makes you bolt out of bed, staring towards its source."
    # Use the finish command to end the quest. Works the same as next() (but no 'to' param)
    $ finish_quest(event.quest, "You completed the idol! It disappeared though.", complete=True)
    "The place where you stored those pieces of the strange idol is slightly scorched, the pieces themselves nowhere to be found."
    "Worriedly you continue with your morning feeling... {i}better{/i}."
    "{color=red}Your sex skills improved considerably!{/color}"

    # Remove event
    $ kill_event("strange_idol3")

    # Improve sex?
    $ hero.gfx_mod_skill("sex", 0, 50)
    $ hero.gfx_mod_skill("sex", 1, 50)
    $ hero.gfx_mod_skill("vaginal", 0, 50)
    $ hero.gfx_mod_skill("vaginal", 1, 50)
    $ hero.gfx_mod_skill("oral", 0, 50)
    $ hero.gfx_mod_skill("oral", 1, 50)
    return
