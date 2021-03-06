init python:
    register_quest("Frog Princess!")
    if DEBUG_QE:
        register_event("show_frog", locations=["forest_entrance"], dice=100, run_type="screen", restore_priority=1, priority=300, start_day=1, max_runs=20, trigger_type="auto")
    else:
        register_event("show_frog", locations=["forest_entrance"], dice=90, run_type="screen", restore_priority=1, priority=300, start_day=choice([15, 25, 35]), max_runs=20, trigger_type="auto")

screen show_frog:
    zorder 10
    if renpy.get_screen("forest_entrance"):
        $ img = Transform(animate(content_path("quests", "frog_princess", "img", "frog_jump"), loop=True), zoom=.2)
        imagebutton:
            pos (237, 586)
            idle img
            hover img
            action Jump("start_frog_event")
    else:
        timer 0.01 action Hide("show_frog")

screen show_frog_final:
    zorder 10
    if renpy.get_screen("forest_entrance"):
        $ img = im.Scale("content/quests/frog_princess/img/frog.webp", 70, 70)
        imagebutton:
            pos (237, 586)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Jump("final_frog_event")
    else:
        timer 0.01 action Hide("show_frog_final")

label start_frog_event:
    hide screen forest_entrance
    with dissolve
    show expression Transform(animate(content_path("quests", "frog_princess", "img", "frog_jump"), loop=True), zoom=.4) as frog:
        pos (257, 536)
    "How odd. There is a rather large frog jumping around, even though there are no water bodies nearby."

    menu:
        "Approach with curiosity to have a closer look.":
            hide frog
            show expression "content/quests/frog_princess/img/frog.webp" as frog
            with dissolve
            menu:
                "You approach the frog. Upon further inspection, it appears to be wearing a crown."

                "Poke the frog with a stick.":
                    jump frog1_event_poke
                "Try to snatch the crown":
                    "You quickly grab the crown before the frog realizes your intentions!"
                    hide frog
                    play events "events/clap.mp3"
                    show expression HitlerKaputt("content/quests/frog_princess/img/frog.webp", 50) as death
                    pause 1.5
                    "As soon as the crown is off of the frogs head, its body disappears with a soft clap..."
                    $ item = items["Gilded Crown"]
                    $ hero.add_item(item)
                    $ gfx_overlay.random_find(item, 'items')
                    $ del item
                    "But on the bright side the crown is yours now. Local merchants will give you some gold for it."
                    $ finish_quest("Frog Princess!", "You've retrieved the frog's crown. Possibly killing the frog.")
                    hide death
                "Leave the frog alone":
                    "Not interested in green slime bags, you continue your quest looking for some fun bags."
                    $ finish_quest("Frog Princess!", "You've rejected the Frog Princess Quest! It's further fate is unknown.")
        "Leave the frog alone.":
            "Not interested in green slime bags, you continue your quest looking for some fun bags."
            $ finish_quest("Frog Princess!", "You've rejected the Frog Princess Quest! It's further fate is unknown.")
    $ kill_event("show_frog")
    jump forest_entrance

label frog1_event_poke:
    $ f1 = Character("Frog", color="green", what_color="lawngreen", show_two_window=True)
    hero.say "How do you like that?."
    "It easily dodges your stick and..."
    f1 "Another one came to laugh at my misfortune. Come on. Let's be done with it."
    "The animal's ability to use human language totally surprised you. You are just standing there not knowing what to do."
    f1 "Hey boy, you look like had never seen a talking frog before? Maybe you could help me out? What do you say?"

    menu:
        "Listen.":
            f1 "Once I was a beautiful princess. A few years ago I was traveling through this woods to wed my beloved in PyTFall. On my travel, I met an older woman that turned me into this creature. Please, could you help a maiden in distress? "
            $ i = True
            while i:
                menu:
                    "Ask about groom":
                        f1 "We met shortly after the event. He wanted to see his bride as soon as possible, so he came to meet me halfway."
                        f1 "Not knowing what happened to me I spoke first. He thought that I was hiding behind the frog, trying to trick him. But when he realized the truth, he broke on his knees crying."
                        f1 "Then I realized what had happened to me. We swore to each other that we would be strong and find a solution."
                        f1 "Because of this curse, I am unable to leave the forest, so for the first few weeks, he came to see me every day."
                        f1 "But weeks grew into months, and he started to come less frequently. After five months he stopped visiting me, and I didn’t saw him ever since…"
                    "Ask about older women":
                        f1 "I can't tell you much about her. The only thing that I remember about her is that she approached me on the road mumbling something and blew some sparkly dust in my face."
                    "Ask about Frog Princess":
                        f1 "So you would like to know more about me. Sure I will tell you. Once I was a maiden of incomparable beauty."
                        f1 "Being  the first daughter of Eastern Yatta Clan I had many admirers. But I fell in love with a merchants son."
                        f1 "I planned my escape carefully. On a starless night, I slipped out my father castle to be with my beloved and met that old crow on my way there."
                    "Promise her that you will find a way to break this spell.":
                        "You promised her that you would try to find a solution. But do you know someone who uses magic and brews potions?"
                        $ i = False
                        $ hero.take_ap(1)
                        $ advance_quest("Frog Princess!", "You've met a talking frog who claims to be a princess! She asked you to help restore her original form.", manual=True)
                        $ menu_extensions.add_extension("Abby The Witch Main", ("Ask about the Frog", Jump("frog1_event_abby")))
                    "Fuck this. I'm going home.":
                        "Not being interested in a talking frog tale you had left the forest."
                        $ finish_quest("Frog Princess!", "You've rejected the Frog Princess Quest! It's further fate is unknown.")
                        $ i = False
            $ del i
        "Run!":
            "You turn around and run towards the city, screaming like a little bitch."
            $ finish_quest("Frog Princess!", "You've rejected the Frog Princess Quest! It's further fate is unknown.")
    $ kill_event("show_frog")
    $ del f1
    jump forest_entrance


label frog1_event_abby:
    $ w = npcs["Abby_the_witch"].say
    hide screen shopping
    hide screen witches_hut_shopping
    with dissolve

    if not global_flags.flag("frog_spoke_abby"):
        w "Frog transmutation, heh? I could look into it, but it will cost ya!"
        extend " Let me see..."
        w "{color=gold}1000 Gold{/color} for my research!"

    menu:
        w "How about it?"
        "Pay her." if hero.gold >= 1000:
            w "I should have the answer soon. Visit me in few days."
            $ advance_quest("Frog Princess!", "For a hefty sum of 1000 Gold Abby the witch promised to look into the frog matter. You should visit her again in a few days.")
            $ hero.take_money(1000, reason="Events")
            $ hero.set_flag("cnd_frog1_event_abby_2", day+10)
            $ menu_extensions.add_extension("Abby The Witch Main", ("Ask about the frog (again)", Jump("frog1_event_abby_2"), "day > {}".format(day)))
            $ menu_extensions.remove_extension("Abby The Witch Main", "Ask about the Frog")
            $ global_flags.del_flag("frog_spoke_abby")
        "I don't have that kind of money right now.":
            w "That's too bad. Come back when you have the money."
            $ global_flags.set_flag("frog_spoke_abby")
        "1000??? I'm not paying!":
            "Being the last ray of hope for a princess turned into a talking frog to regain her humanity, you decided that spending 1000 gold was too much."
            extend "{color=red} Way to go cheapskate!"
            $ finish_quest("Frog Princess!", "You've rejected the Frog Princess Quest! Its further fate is unknown.")
            $ menu_extensions.remove_extension("Abby The Witch Main", "Ask about the Frog")
            $ global_flags.del_flag("frog_spoke_abby")
    $ del w
    jump forest_entrance

label frog1_event_abby_2:
    $ w = npcs["Abby_the_witch"].say
    hide screen shopping
    hide screen witches_hut_shopping
    with dissolve

    hero.say "Did you found anything?"
    if hero.has_flag("dnd_frog1_event_abby_2"):
        w "As I said, I am still going through my books and scrolls. Now if you wont stop bother me I'm never going to find a solution."
        $ hero.up_counter("cnd_frog1_event_abby_2")
    elif hero.get_flag("cnd_frog1_event_abby_2", 0) - day >= 7:
        w "Sorry, but I had other things to do. Come back later."
        $ hero.set_flag("dnd_frog1_event_abby_2")
    elif dice(60 - (day - hero.get_flag("cnd_frog1_event_abby_2", day))*8):
        w "I am still going through my books and scrolls. Come back later."
        $ hero.set_flag("dnd_frog1_event_abby_2")
    else:
        w "I found a solution. A rare magic potion should do the trick, but that's not the hard part..."
        extend " I need another 10 000 gold to buy the necessary ingredients, but the real trick will be getting a goblin champion eye."

        $ menu_extensions.remove_extension("Abby The Witch Main", "Ask about the frog (again)")
        $ hero.del_flag("cnd_frog1_event_abby_2")

        menu:
            "I will get you the money and the eye...":
                $ advance_quest("Frog Princess!", "Abby asked you to acquire another 10000 Gold for ingredients and an eye of a Goblin Champion...")
                $ menu_extensions.add_extension("Xeona Main", ("Enquire about an eye of a Goblin Champion!", Jump("frog_event_arena")))

            "10 000? Not a chance...":
                "You gave up :("
                $ finish_quest("Frog Princess!", "You've rejected the Frog Princess Quest! It's further fate is unknown.")
    $ del w
    jump forest_entrance

label frog_event_arena:
    hide screen arena_outside
    "You find Xeona to ask about the eye."
    $ ax = npcs["Xeona_arena"].say
    show expression npcs["Xeona_arena"].get_vnsprite() as xeona
    with dissolve

    ax "An eye of the goblin champion you say?"
    ax "I sure hope it's not some weird fetish you're into..."
    ax "It can be arranged I suppose, as you may know, dampening field prevents fatal blows in the Arena, often even to Monsters but a proper DeathMatch can be arranged."
    ax "Come back in three days and make certain you are well equipped. You may even consider bringing a couple of friends along with you."
    ax "A real G-Champ will be bloody hard to kill and in a deathmatch you'll die if your party is wiped out."
    ax "Also, don't expect him to be alone even if you are. People will expect a vicious fight since deathmatches are rare enough. You better be prepared!"
    $ hero.take_ap(1)
    $ advance_quest("Frog Princess!", "Xeona agreed to set up a match per your request but you've been warned that it is a {color=red}very{/color} dangerous endeavour and it would be a good idea to bring some backup!")
    $ menu_extensions.remove_extension("Xeona Main", "Enquire about an eye of a Goblin Champion!")
    $ menu_extensions.add_extension("Xeona Main", ("Deathfight vs Goblin Champ!", Jump("frog_deathfight"), "day == {}".format(day+3)))
    $ menu_extensions.add_extension("Xeona Main", ("Missed Deathfight...", Jump("missed_frog_deathfight"), "day > {}".format(day+3)))
    $ del ax
    jump arena_outside

label missed_frog_deathfight:
    hide screen arena_outside
    "You find Xeona to talk about the missed fight."
    $ ax = npcs["Xeona_arena"].say
    show expression npcs["Xeona_arena"].get_vnsprite() as xeona
    with dissolve

    $ menu_extensions.remove_extension("Xeona Main", "Deathfight vs Goblin Champ!")
 
    ax "Well, well, well..."
    ax "It seems that someone forgot something."
    ax "The Goblin Champ was really pissed by the events. If you want to have a fight, you need to pay a compensation of {color=gold}2000 Gold{/color}."
    ax "Are you willing to pay the price?"
    menu:
        "Yes, of course." if hero.gold >= 2000:
            $ hero.take_money(2000, reason="Events")
            ax "Great! The fight is going to be in three days as usual. Do not forget this time."
            $ menu_extensions.add_extension("Xeona Main", ("Deathfight vs Goblin Champ!", Jump("frog_deathfight"), "day == {}".format(day+3)))
            $ menu_extensions.remove_extension("Xeona Main", "Missed Deathfight...")
            $ menu_extensions.add_extension("Xeona Main", ("Missed Deathfight...", Jump("missed_frog_deathfight"), "day > {}".format(day+3)))

        "Sorry, it is too much.":
            ax "As you wish, come back if you changed your mind."

    $ del ax
    jump arena_outside

label frog_deathfight:
    hide screen arena_outside
    $ ax = npcs["Xeona_arena"].say
    show expression npcs["Xeona_arena"].get_vnsprite() as xeona
    with dissolve
    stop world

    ax "Well, I hope that you're ready! Best of luck!"
    python hide:
        enemy_team = Team(name="Enemy Team")
        mob = build_mob("Goblin Warrior", level=50)
        enemy_team.add(mob)

        for i in xrange(2):
            mob = build_mob("Goblin Archer", level=20)
            enemy_team.add(mob)

        result = run_default_be(enemy_team, background="battle_arena_1", end_background="arena_outside")

        if result is not True:
            jump("game_over")

    show expression npcs["Xeona_arena"].get_vnsprite() as xeona
    with dissolve

    ax "Great Fight! I was rooting for you! I am sure getting to the eye will be no problem."
    $ advance_quest("Frog Princess!", "You got the eye! You should visit Abby yet again!")
    $ menu_extensions.add_extension("Abby The Witch Main", ("Give her the eye", Jump("frog1_event_abby_3")))
    $ kill_event("show_frog_arena_eye")
    $ menu_extensions.remove_extension("Xeona Main", "Deathfight vs Goblin Champ!")
    $ menu_extensions.remove_extension("Xeona Main", "Missed Deathfight...")

    $ del ax
    jump arena_outside

label frog1_event_abby_3:
    $ w = npcs["Abby_the_witch"].say
    hide screen shopping
    hide screen witches_hut_shopping
    with dissolve

    w "I see you got the base ingredient. "
    extend "I heard it was one hell of a fight in the Arena!"
    extend " ... too bad I've missed it."
    w "Anyway, I've prepared the potion, so I only need the eye from you (takes the eye)."
    w "And don't worry about the 10000 Gold, I was only joking, most of these ingredients grow right outside my hut..."
    "Three minutes have passed..."
    w "Here is the potion. Now listen. To undo the spell, have the frog to drink the potion and kiss it after it does."
    extend " She should transform right away. It's that simple. If a normal kiss won't work try a more passionate one. Good luck!"
    "You get a little, corked vial, filled with a glowing green liquid called the potion of unfrogging. You rushed in a hurry form the Witches Hut."
    $ advance_quest("Frog Princess!", "Finally, you have the potion! Talk to the frog again!")
    $ renpy.music.stop(channel="world", fadeout=1)
    scene bg forest_entrance at truecenter

    hero.say "Damn, that blasted frog isn't around... Maybe I should come back tomorrow."
    $ menu_extensions.remove_extension("Abby The Witch Main", "Give her the eye")

    $ register_event("show_frog_final", locations=["forest_entrance"], run_type="screen", restore_priority=1, priority=300, start_day=day, max_runs=100, trigger_type="auto")
    $ del w
    jump forest_entrance

label final_frog_event:
    hide screen forest_entrance
    "Having a solution to the frog princes' problem you enter the forest with confidence."
    "Finding her wasn't really a problem, she was sitting on the same rock when you met for the first time."

    $ f1 = Character("Frog", color="green", what_color="lawngreen", show_two_window=True)
    show expression "content/quests/frog_princess/img/frog.webp"
    f1 "So why did you come today?"

    menu:
        "I have found a method to break the spell.":
            f1 "My hero! Thanks a lot!"
        "I know how to break the spell, but it will cost you.":
            f1 "I will do anything just help me. My father is a very rich and powerful man. He surely will pay you any sum when I safely return home."
    stop world
    play sound "content/quests/frog_princess/sfx/kiss_short.mp3"
    "Frog drunk the potion, and you gave it a quick kiss. Nothing happened. You need to be more passionate."
    menu:
        "French kiss":
            "You had French kissed a frog! (side note: frogs eat: flies, mosquitoes, moths, dragonflies, small snakes, mice, baby turtles and sometimes smaller frogs)."
            play sound "content/quests/frog_princess/sfx/kiss_long.mp3"
            scene black
            $ flash = Fade(.25, 0, .75, color="#fff")
            scene bg forest_entrance
            with flash

            play sound "content/sfx/sound/events/good_night.mp3"
            "It worked. A bright flash and the frog was gone. In her place was…"

            $ stranger = "content/quests/frog_princess/img/stranger.webp"
            show expression stranger
            $ b = Character("Stranger", color="red", what_color="green", show_two_window=True)
            b "Thanks, dude. You really saved me. About that princess and gold..."
            $ finish_quest("Frog Princess!", "{color=blue}You've completed the Quest... but the whole thing was a scam...{/color}")
            extend " {color=red} It was all crap! Sorry, gotta go!{/color}"
            hide expression stranger
            with fade
            $ del flash, b, stranger
            "You had lost a lot of time, money, and had an intimate moment with a huge man-frog. But look at the bright side. Now you know that you shouldn't trust a talking frog."
        "It's too disgusting":
            "The first kiss was disgusting enough. This is just too much for you. After dropping the frog you head back home thinking about what a crappy ordeal this was."
            $ finish_quest("Frog Princess!", "You could not bring yourself to kiss the frog properly...")
    $ kill_event("show_frog_final")
    $ del f1
    jump forest_entrance
