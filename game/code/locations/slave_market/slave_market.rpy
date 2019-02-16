label slave_market:
    # Music related:
    if not "slavemarket" in ilists.world_music:
        $ ilists.world_music["slavemarket"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("slavemarket")]
    play world choice(ilists.world_music["slavemarket"]) fadein 1.5

    if not global_flags.has_flag("visited_sm"):
        $ global_flags.set_flag("visited_sm")
        scene bg slave_market
        with dissolve
        show slave_market_slaves at truecenter

        "What's this?"
        extend " WHAT THE HELL IS THIS???"

        play sound "content/sfx/sound/be/whip_attack_2.mp3"

        "What's that look on your faces? Unhappiness? Doubt? Defiance?!?!"

        play sound "content/sfx/sound/be/whip_attack_2.mp3"

        "This lot requires more training, get them out of here!"

        play sound "content/sfx/sound/be/whip_attack_2.mp3"
        pause .1
        play sound "content/sfx/sound/be/whip_attack_2.mp3"

        "{color=[red]} Yes, Ma'am! Yes, Ma'am! Yes, Ma'am!"
        "And bring out some decent slaves to shop!"

        hide slave_market_slaves with fade
        show expression npcs["Blue_slavemarket"].get_vnsprite() as blue with dissolve

        $ g = Character("?????", color=aliceblue, show_two_window=True)

        menu:
            g "Hah? And who might you be?!"
            "Just want to check out the slave market":
                g "Oh? We didn't expect to see any customers here so early."
            "You should not be so hard on those poor creatures":
                g "DON'T TELL ME HOW TO DO MY JOB YOU @$$#^*!!!"
                extend " ... but I guess that since you had to witness that, I'll let this slide."
            "Omg stfu I just need to test something!" if config.developer:
                jump slave_market_controls
        g "Everyone calls me Blue. Original isn't it?"

        $ g = npcs["Blue_slavemarket"].say

        g "We usually try to prevent customers from seeing anything they might find unpleasant."
        g "But that weasel Stan is always trying to push 'unfinished' products."
        g "I mean what's the point? Reputation is much more important!"

        $ s = npcs["Stan_slavemarket"].say

        show expression npcs["Stan_slavemarket"].get_vnsprite() as stan at mid_left with dissolve

        s "Hey, hey there!"
        s "Is there anyone here talking about me?"
        s "Just the cool things I assume!?"
        g "What the hell are you talking about? Those slaves were a disgrace to our good rep!"
        s "Temper, temper my dear... the quality of those slaves are your problem."
        s "Keeping the cash flowing, gold rolling, so Mr. Big is satisfied, is mine!"
        s "I am going to get some measure of today's lots and what we can get for them!"
        s "Don't bother our prospective clients and play with your slaves while {color=[red]}I{/color} take care of real work! <Smirks>"

        hide stan with dissolve
        show expression npcs["Blue_slavemarket"].get_vnsprite() as blue at center with move

        g "That damn baboon only thinks about money! No sense of duty or love for the craft!"
        g "You see it too, don't you?"
        g "In any case, if you're looking to whip some slave into shape or get a fair deal on one. Find me. I'll set you up!"
        g "Ah, visit our club as well, we do presentations, and you can do 'some sampling' if you have the Gold."
        g "You won't be disappointed!"
        g "Goodbye!"

label slave_market_controls:
    hide blue
    hide stan
    hide slave
    with dissolve
    show bg slave_market

    python:
        # Build the actions
        if pytfall.world_actions.location("slave_market"):
            pytfall.world_actions.slave_market(pytfall.sm, index=0)
            pytfall.world_actions.add(1, "Free Slaves", Jump("sm_free_slaves"))
            pytfall.world_actions.add(2, "Find Blue", Jump("blue_menu"), condition=Iff(global_flag_complex("visited_sm")))
            pytfall.world_actions.work(Iff(global_flag_complex("visited_sm")),
                                       index=100, name="Work all day", returned="mc_action_work_in_slavemarket_all_day")

            pytfall.world_actions.look_around(index=1000)
            pytfall.world_actions.finish()

    scene bg slave_market

    show screen slavemarket
    with fade

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    $ loop = True
    while loop:
        $ result = ui.interact()

        if result[0] == "buy":
            $ char = pytfall.sm.get_char()
            $ msg = pytfall.sm.buy_slave(char)
            if msg:
                call screen message_screen(msg)

            if not pytfall.sm.chars_list:
                hide screen slave_shopping
        elif result[0] == "control":
            if result[1] == "work":
                $ use_ap = 1
                jump mc_action_work_in_slavemarket
            elif result[1] == "mc_action_work_in_slavemarket_all_day":
                $ use_ap = hero.AP
                jump mc_action_work_in_slavemarket
            elif result[1] == "jumpclub":
                hide screen slavemarket
                jump slave_market_club
            elif result[1] == "return":
                if not renpy.get_screen("slave_shopping"):
                    $ loop = False

    $ renpy.music.stop(channel="world")
    hide screen slavemarket
    jump city

label sm_free_slaves:
    hide screen slavemarket

    $ s = npcs["Stan_slavemarket"].say
    show expression npcs["Stan_slavemarket"].get_vnsprite() as stan at mid_left with dissolve

    if not global_flags.has_flag("asked_about_freeing_slaves"):
        $ global_flags.set_flag("asked_about_freeing_slaves")
        s "Oh, you want to give freedom to one of your slaves? Sure, sure, we can arrange it... for a price!"
        s "You see, every freed slave is a blow to the city's economy. We get a new worker, but not a new workplace."
        $ renpy.notify("Freeing a slave will cost you three month of their full wages!")
        s "So you'll have to pay for their freedom, make sure they can support themselves for couple of month without being a burden."
        s "And there is always also a flat 1000 Gold government fee!"
        s "I hope those sluts will be grateful at least!"

    $ chrs = list(i for i in hero.team if i.status == "slave" and i.location is None)
    if not chrs:
        s "Are you kidding me? You don't have any slaves with you!"
        s "Don't bother me without a good reason!!!"
        "You need to bring slaves as a part of your team to free them!"
        jump slave_market_controls
    else:
        $ our_char = None
        menu:
            "[chrs[0].fullname]":
                $ our_char = chrs[0]
            "[chrs[1].fullname]" if len(chrs) > 1:
                $ our_char = chrs[1]
            "Nevermind":
                $ del our_char
                $ del chrs
                jump slave_market_controls

        show expression our_char.get_vnsprite() as slave at mid_right with dissolve

        if char.get_stat("disposition") > 0:
            if our_char.get_stat("disposition") >= 700 or check_lovers(hero, our_char):
                $ our_char.override_portrait("portrait", "shy")
                $ our_char.say("I don't really mind being your slave, [hero.name]...  ")
            elif "Dedicated" in our_char.traits or "Masochist" in our_char.traits:
                $ our_char.override_portrait("portrait", "shy")
                $ our_char.say("Are you sure, master? I like being your slave.")
            else:
                $ our_char.override_portrait("portrait", "happy")
                $ our_char.say("You want to free me? Oh, thank you, master!")

        $ cost = 1000 + round_int(our_char.expected_wage*30*3) # 3 Month wage to free the salve.

        s "Alright, that will be [cost] gold!"
        if hero.gold < cost:
            "Unfortunately, you don't have enough money."
            s "Pff, beggars..."
        else:
            menu:
                "Do you wish to pay [cost] gold to free your slave?"
                "Yes":
                    $ hero.take_money(cost, reason="Slave Freedom")
                    s "Done and done! Congrats, I hope it was worth it."
                    $ our_char.gfx_mod_stat("disposition", randint(400, 500))
                    $ our_char.status = "free"
                    $ our_char.autobuy = True
                    $ our_char.home = pytfall.city
                    $ set_location(our_char, None)
                    # We give about a third of cash to the ex-slave. Idea is that the rest goes to pay
                    # for a place to live and covering basic needs.
                    $ our_char.add_money(round_int((cost-1000)/3), "Freedom Fee")
                    "[our_char.name] is now a very grateful free citizen! She will also keep about a third of the fee for shopping needs!"
                "No":
                    s "Pff, beggars..."

        $ our_char.restore_portrait()
    $ del our_char
    $ del chrs
    jump slave_market_controls

label mc_action_work_in_slavemarket:
    pause 0.01

    if dice(50):
        $ narrator(choice(["You did some chores around the Slave Market!",
                           "Pay might be crap, but it's still money.",
                           "You've helped out in da Club!"]))
    else:
        $ hero.say(choice(["What a boring job...",
                           "There's gotta be faster way to make money..."]))

label mc_action_work_in_slavemarket_reward:
    python:
        result = 0
        for skill in STATIC_CHAR.SEX_SKILLS:
            result += hero.get_skill(skill)
        result /= len(STATIC_CHAR.SEX_SKILLS)
        result += hero.expected_wage*6

        if dice(hero.get_stat("luck")*.1):
            result += hero.level*5

        result = gold_reward(hero, result, use_ap)

        if dice(.5 + hero.get_stat("luck")*.1):
            hero.gfx_mod_stat("charisma", use_ap)
            hero.gfx_mod_skill("sex", 0, use_ap)

        hero.add_money(result, reason="Job")
        gfx_overlay.random_find(result, 'work')
        hero.gfx_mod_exp(exp_reward(hero, hero, ap_used=use_ap))
        hero.take_ap(use_ap)

        del result
        del use_ap
    jump slave_market_controls

label blue_menu:
    $ g = npcs["Blue_slavemarket"].say
    scene bg slave_market with fade
    show expression npcs["Blue_slavemarket"].get_vnsprite() as blue with dissolve
    g "[hero.nickname]!"
    g "Welcome back to our fine establishment!"
    $ loop = True
    while loop:
        menu:
            g "Slave Training is an Art!"
            "Tell me about Slave Training.":
                "PlaceHolder until we figure out how ST works :)"
            "Ask about Captured Girls." if False: # fg in hero.buildings:
                if not global_flags.flag("blue_cg"):
                    g "So, you now own an Exploration Guild?"
                    g "Well done, it's a well-known source of slaves of all kinds."
                    g "Once a fresh slave is processed in the jail and registered with the authorities, I can train her to obey and do her job."
                    g "I don't train for any specific task but rather uncover their hidden talents. My price is 2000 Gold to be paid up front."
                    g "The training will take 30 days, and you don't have to worry because I always deliver :)"
                    $ global_flags.set_flag("blue_cg")
                else:
                    if pytfall.sm.blue_slaves:
                        $ num = len(pytfall.sm.blue_slaves)
                        $ var = plural("slave", num)
                        g "I am currently training [num] [var] for you."
                        g "Don't worry. They'll all be ready as promised."
                    else:
                        g "I'll train anyone, without fail! Just send them my way!"
            "That will be all":
                g "Goodbye!"
                $ loop = False

    jump slave_market

screen slavemarket():

    use top_stripe(True)

    use r_lightbutton(img=im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True), return_value =['control', 'jumpclub'], align=(.01, .5))

    use location_actions("slave_market")

screen slave_shopping(source, buy_button, buy_tt):
    modal True
    zorder 1

    if source.chars_list:
        $ char = source.get_char()

        # Data (Left Frame): =============================================================================>>>
        frame:
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            xysize 270, 678
            ypos 41
            style_group "content"
            has vbox

            # Name: =============================================================================>>>
            frame:
                xysize 250, 50
                xalign .5
                background Frame(Transform("content/gfx/frame/namebox5.png", alpha=.95), 250, 50)
                label "[char.fullname]":
                    text_color gold
                    text_outlines [(2, "#424242", 0, 0)]
                    align (.5, .5)
                    if len(char.fullname) < 20:
                        text_size 21

            # Info: =============================================================================>>>
            null height 5
            label "Info:":
                text_color ivory
                text_size 20
                text_bold True
                xalign .5
                text_outlines [(2, "#424242", 0, 0)]
            vbox:
                style_group "proper_stats"
                spacing 5
                frame:
                    background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                    xsize 258 xalign .5
                    padding 6, 6
                    has vbox spacing 1 xmaximum 246
                    frame:
                        xysize 244, 20
                        text ("{color=#79CDCD}{size=-1}Class:") pos (1, -4)
                        label "{size=-3}[char.traits.base_to_string]" align (1.0, .5) ypos 10
                    frame:
                        xysize 245, 20
                        text "{color=#79CDCD}{size=-1}Level:" pos (1, -4)
                        label (u"{size=-5}%s"%char.level) align (1.0, .5) ypos 10
                    frame:
                        xysize 244, 20
                        text "{color=#79CDCD}{size=-1}Market Price:" pos (1, -4)
                        label (u"{color=[gold]}{size=-5}%s"%char.fin.get_price()) align (1.0, .5) ypos 10
                    frame:
                        xysize 244, 20
                        text "{color=#79CDCD}{size=-1}Upkeep:" pos (1, -4)
                        label (u"{size=-5}%s"%char.fin.get_upkeep()) align (1.0, .5) ypos 10

            # Stats: ==============================================================================>>>
            null height 5
            label (u"Stats:"):
                text_color ivory
                text_size 20
                text_bold True
                xalign .5
                text_outlines [(2, "#424242", 0, 0)]
            frame:
                background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                xsize 258
                xalign .5
                padding 6, 6
                style_group "proper_stats"
                has vbox spacing 1 xmaximum 246
                frame:
                    xysize 245, 20
                    text "{color=#79CDCD}{size=-1}Health:" pos (1, -4)
                    label (u"{size=-5}%s/%s"%(char.get_stat("health"), char.get_max("health"))) align (1.0, .5) ypos 10
                frame:
                    xysize 245, 20
                    text "{color=#79CDCD}{size=-1}Vitality:" pos (1, -4)
                    label (u"{size=-5}%s/%s"%(char.get_stat("vitality"), char.get_max("vitality"))) align (1.0, .5) ypos 10
                frame:
                    xysize 245, 20
                    text "{color=#79CDCD}Agility{size=-1}:" pos (1, -4)
                    label (u"{size=-5}%s/%s"%(char.get_stat("agility"), char.get_max("agility"))) align (1.0, .5) ypos 10
                frame:
                    xysize 245, 20
                    text "{color=#79CDCD}{size=-1}Charisma:" pos (1, -4)
                    label (u"{size=-5}%s/%s"%(char.get_stat("charisma"), char.get_max("charisma"))) align (1.0, .5) ypos 10
                frame:
                    xysize 245, 20
                    text "{color=#79CDCD}{size=-1}Character:" pos (1, -4)
                    label (u"{size=-5}%s/%s"%(char.get_stat("character"), char.get_max("character"))) align (1.0, .5) ypos 10
                frame:
                    xysize 245, 20
                    text "{color=#79CDCD}{size=-1}Constitution:" pos (1, -4)
                    label (u"{size=-5}%s/%s"%(char.get_stat("constitution"), char.get_max("constitution"))) align (1.0, .5) ypos 10
                frame:
                    xysize 245, 20
                    text "{color=#79CDCD}{size=-1}Intelligence:" pos (1, -4)
                    label (u"{size=-5}%s/%s"%(char.get_stat("intelligence"), char.get_max("intelligence"))) align (1.0, .5) ypos 10

            # Skills: =============================================================================>>>
            null height 5
            label (u"Skills:"):
                text_color ivory
                text_size 20
                text_bold True
                xalign .5
                text_outlines [(2, "#424242", 0, 0)]
            $ base_ss = char.stats.get_base_ss()
            frame:
                style_prefix "proper_stats"
                style_suffix "main_frame"
                xalign .5
                has viewport xysize (236, 236) mousewheel 1 draggable 1 # child_size (255, 1000)
                vbox:
                    spacing 1
                    xpos 5
                    for skill in char.stats.skills:
                        $ skill_val = int(char.get_skill(skill))
                        $ skill_limit = int(char.get_max_skill(skill))
                        # We don't care about the skill if it's less than 10% of limit:
                        if skill in base_ss or skill_val/float(skill_limit) > .1:
                            hbox:
                                xsize 224
                                text "{}:".format(skill.capitalize()):
                                    style_suffix "value_text"
                                    color gold
                                    xalign .0
                                    size 18
                                hbox:
                                    xalign 1.0
                                    yoffset 8
                                    $ step = skill_limit/10.0
                                    for i in range(5):
                                        if (2*step) <= skill_val:
                                            add Transform("content/gfx/interface/icons/stars/star2.png", size=(18, 18))
                                            $ skill_val -= 2*step
                                        elif step <= skill_val:
                                            add Transform("content/gfx/interface/icons/stars/star3.png", size=(18, 18))
                                            $ skill_val -= step
                                        else:
                                            add Transform("content/gfx/interface/icons/stars/star1.png", size=(18, 18))
                vbox:
                    spacing 1
                    for skill in char.stats.skills:
                        $ skill_val = int(char.get_skill(skill))
                        $ skill_limit = int(char.get_max_skill(skill))
                        # We don't care about the skill if it's less than 10% of limit:
                        if skill in base_ss or skill_val/float(skill_limit) > .1:
                            if skill in base_ss:
                                fixed:
                                    xysize 20, 26
                                    button:
                                        xysize 20, 20
                                        background pscale("content/gfx/interface/icons/stars/legendary.png", 20, 20)
                                        action NullAction()
                                        tooltip "This is a Class Skill!"
                            else:
                                null height 26

        # Image (Mid-Top): =============================================================================>>>
        frame:
            pos 265, 41
            xysize 669, 423
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=1.0), 10, 10)
            frame:
                align .5, .5
                background Frame("content/gfx/frame/MC_bg.png", 10, 10)
                add char.show("nude", "no clothes", resize=(560, 400), exclude=["rest", "outdoors", "onsen", "beach", "pool", "living"], type="first_default", label_cache=True) align .5, .5

        # Traits:
        frame:
            pos (928, 41)
            style_group "content"
            xysize (350, 351)
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            has vbox xalign .5 #ypos 5
            null height 5
            label (u"{size=20}{color=[ivory]}{b}Visible Traits") xalign .5 text_outlines [(2, "#424242", 0, 0)]
            null height 5
            $ temp = list(t for t in char.traits if t.market and not t.hidden)
            $ long = len(temp) > 10
            frame:
                left_padding 15
                ypadding 10
                #xsize 226
                background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                has viewport xysize ((210 if long else 200), min(260, 26 * len(temp))) draggable long mousewheel long scrollbars ("vertical" if long else None)
                vbox:
                    style_group "proper_stats"
                    spacing 1
                    for trait in temp:
                        frame:
                            xalign .5
                            xysize (195, 25)
                            button:
                                background Null()
                                xysize (195, 25)
                                action NullAction()
                                text trait.id idle_color bisque size 18 align .5, .5 hover_color crimson text_align .5:
                                    if len(trait.id) >= 15:
                                        size 15
                                tooltip trait.desc
                                hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

        # Buttons:
        frame:
            pos(928, 387)
            style_group "content"
            xysize (350, 73)
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            hbox:
                ysize 63
                xalign .5
                $ img=im.Scale("content/gfx/interface/buttons/arrow_button_metal_gold_left.png", 50, 50)
                imagebutton:
                    align(.5, .5)
                    idle img
                    hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                    action (Function(source.previous_index))
                    tooltip "Previous Slave"

                null width 10

                frame:
                    align(.5, .5)
                    style_group "dropdown_gm"
                    padding (5, 5)
                    has vbox
                    $ text_s = 20
                    if source.chars_list == pytfall.jail.captures:
                        $ text_s = 14
                        textbutton "Sell":
                            xsize 150
                            text_size text_s
                            action Function(pytfall.jail.sell_captured, char)
                            tooltip "Sell %s for %d Gold." % (char.name, source.sell_price(char))
                    textbutton "[buy_button]":
                        xsize 150
                        text_size text_s
                        action Return(['buy', char])
                        tooltip buy_tt % source.get_price(char)

                null width 10

                $ img=im.Scale("content/gfx/interface/buttons/arrow_button_metal_gold_right.png", 50, 50)
                imagebutton:
                    align(.5, .5)
                    idle img
                    hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                    action (Function(source.next_index))
                    tooltip "Next Slave"

        # Girl choice:
        frame:
            # pos 265, 459
            pos 265, 455
            background Frame(Transform("content/gfx/frame/p_frame53.png", alpha=.98), 10, 10)
            side "c t":
                yoffset -2
                viewport id "sm_vp_list":
                    xysize 1003, 238
                    draggable True
                    mousewheel True
                    edgescroll [100, 200]
                    has hbox spacing 5
                    for idx, c in enumerate(source.chars_list):
                        $ img = c.show("vnsprite", resize=(180, 206), cache=True)
                        frame:
                            yalign .5
                            background Frame("content/gfx/frame/Mc_bg3.png", 10, 10)
                            imagebutton:
                                idle img
                                hover (im.MatrixColor(img, im.matrix.brightness(.15)))
                                action Function(source.set_char, idx)
                                tooltip u"{=proper_stats_text}%s\n{size=-5}{=proper_stats_value_text}%s"%(c.name, c.desc)
                bar value XScrollValue("sm_vp_list")

    use top_stripe(show_return_button=True, return_button_action=[Hide("slave_shopping"), With(dissolve)], show_lead_away_buttons=False)
