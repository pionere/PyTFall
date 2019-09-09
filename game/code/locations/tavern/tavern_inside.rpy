label tavern_town:
    scene bg tavern_inside
    with dissolve

    if pytfall.enter_location("tavern", music=False, env="tavern"):
        show expression npcs["Rita_tavern"].get_vnsprite() as npc
        with dissolve
        npcs["Rita_tavern"].say "Oh, hello! Welcome to our tavern! We will always have a seat for you! *wink*"
        hide npc
        with dissolve
        $ pytfall.shops_stores["Tavern"].status = "cozy"
    else:
        if pytfall.shops_stores["Tavern"].status == "after brawl": # after a brawl tavern will be unavailable until the next turn
            show expression npcs["Rita_tavern"].get_vnsprite() as npc
            with dissolve
            npcs["Rita_tavern"].say "I'm sorry, we are closed for maintenance. Please return tomorrow."
            jump city

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

label city_tavern_menu: # "lively" status is limited by drunk effect; every action rises drunk counter, and every action with drunk effect active decreases AP
    if 'Drunk' in hero.effects:
        if not hero.has_flag("dnd_tavern_dizzy"):
            "You feel a little dizzy... Perhaps you should go easy on drinks."
            $ hero.set_flag("dnd_tavern_dizzy")
        $ PyTGFX.double_vision_on("bg tavern_inside")
    $ temp = pytfall.shops_stores["Tavern"].status
    python hide:
        dir = content_path("events", "tavern_entry", temp)
        images = [file for file in listfiles(dir) if check_content_extension(file)]
        img = os.path.join(dir, choice(images))
        img = PyTGFX.scale_content(img, 1000, 600)
        renpy.show("drunkards", what=img, at_list=[truecenter])
        renpy.with_statement(dissolve)
    # comment on the state of the tavern, but only on the first time
    if not hero.has_flag("dnd_was_in_tavern"):
        if temp == "cozy":
            "The tavern is warm and cozy with only a handful of drunkards enjoying the stay."
        elif temp == "lively":
            "The place is loud and lively today, with townsmen drinking and talking at every table."
        else:
            $ del temp
            $ pytfall.enter_location("tavern", music=False, env="brawl")
            #renpy.music.play("brawl.mp3", channel="world")
            "You step into the room... right into a fierce tavern brawl!"
            menu:
                "Join it!":
                    $ hero.mod_stat("reputation", -1)
                    jump city_tavern_brawl_fight
                "Leave while you can":
                    jump city
        $ hero.set_flag("dnd_was_in_tavern")
    $ del temp

    show screen city_tavern_inside
    while 1:
        $ result = ui.interact()

        hide screen city_tavern_inside
        if result == "shop":
            jump city_tavern_shopping
        elif result == "look_around":
            jump mc_action_tavern_look_around
        elif result == "relax":
            jump mc_action_tavern_relax
        elif result == "blackjack":
            jump city_tavern_play_dice
        elif result == "poker":
            jump city_tavern_play_poker
        elif result == "bet":
            jump city_tavern_choose_label
        else:
            jump city

label city_tavern_choose_label:
    $ bet = pytfall.shops_stores["Tavern"].bet
    "Here you can set how much to bet to avoid doing it before every game in the tavern. The more your tier, the higher bets are available."
    "The current bet is [bet] Gold."
    menu:
        "How much Gold do you wish to bet?"
        "5":
            $ bet = 5
        "10":
            $ bet = 10
        "25" if hero.tier >= 1:
            $ bet = 25
        "50" if hero.tier >= 2:
            $ bet = 50
        "100" if hero.tier >= 3:
            $ bet = 100
        "200" if hero.tier >= 4:
            $ bet = 200
        "500" if hero.tier >= 5:
            $ bet = 500
    $ pytfall.shops_stores["Tavern"].bet = bet
    $ del bet
    jump city_tavern_menu

screen city_tavern_inside():
    use top_stripe(False)
    frame:
        xalign .95
        ypos 50
        background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
        xpadding 10
        ypadding 10
        vbox:
            style_prefix "wood"
            align (.5, .5)
            spacing 10
            button:
                xysize (120, 40)
                yalign .5
                action Return("shop")
                text "Buy a drink" size 15
            $ temp = pytfall.shops_stores["Tavern"].status
            if hero.has_ap():
                if temp == "lively":
                    button:
                        xysize (120, 40)
                        yalign .5
                        action Return("look_around")
                        text "Look around" size 15
                if temp == "cozy" and not hero.has_flag("dnd_rest_in_tavern"):
                    button:
                        xysize (120, 40)
                        yalign .5
                        action Return("relax")
                        text "Relax" size 15
                if temp == "cozy":
                    button:
                        xysize (120, 40)
                        yalign .5
                        action Return("blackjack")
                        text "Blackjack" size 15
                if temp == "cozy":
                    button:
                        xysize (120, 40)
                        yalign .5
                        action Return("poker")
                        text "Poker" size 15
            if temp == "cozy":
                button:
                    xysize (120, 40)
                    yalign .5
                    action Return("bet")
                    text "Set dice bet" size 15
            button:
                xysize (120, 40)
                yalign .5
                action Return("leave")
                text "Leave" size 15
                keysym "mousedown_3"

label mc_action_tavern_relax:
    hide drunkards with dissolve
    if len(hero.team) < 2:
        if hero.take_money(randint(10, 20), reason="Tavern"):
            $ hero.set_flag("dnd_rest_in_tavern")
            "You sit next to your drink for awhile, but there isn't much to do here. Perhaps it would be more fun if you weren't alone."
            $ hero.gfx_mod_stat("joy", randint(2, 4))
            $ iam.drinking_outside_of_inventory(char=hero, count=randint(10, 15))
        else:
            "You do not even have the means to buy yourself a drink. Maybe it is time to make yourself useful?"
    else:
        if hero.take_money(randint(30, 50), reason="Tavern"):
            $ hero.set_flag("dnd_rest_in_tavern")
            $ members = list(member for member in hero.team if (member != hero))
            if len(members) == 1:
                show expression members[0].get_vnsprite() at center as temp1
                with dissolve
            else:
                show expression members[0].get_vnsprite() at left as temp1
                show expression members[1].get_vnsprite() at right as temp2
                with dissolve
            "You ordered a few drinks and spent some time together."
            python:
                for member in members:
                    member.gfx_mod_stat("joy", randint(4, 8))
                    member.gfx_mod_stat("disposition", randint(3, 5))
                    member.gfx_mod_stat("affection", affection_reward(member))
                    iam.drinking_outside_of_inventory(char=member, count=randint(15, 40))
                hero.gfx_mod_stat("joy", randint(4, 8))
                iam.drinking_outside_of_inventory(char=hero, count=randint(15, 25))
                del member, members
            hide temp1
            hide temp2
            with dissolve
        else:
            "You could spend time with your team, but sadly you are too poor to afford it at the moment."
    jump city_tavern_menu

label city_tavern_brawl_fight:
    if len(hero.team) == 1:
        "You go inside and a few thugs immediately notice you."
    else:
        "You nod to your teammates and go inside. A few thugs immediately notice you."

    $ group_counter = randint(2, 5)
    while group_counter > 0:
        if pytfall.shops_stores["Tavern"].status == "brawl":
            $ pytfall.shops_stores["Tavern"].status = "after brawl"
        else:
            "Another group is approaching you!"
            menu:
                "Fight!":
                    $ pass
                "Run away":
                    $ group_counter = -1

        if group_counter > 0:
            python hide:
                global group_counter
                enemies = ["Thug", "Assassin", "Barbarian"]
                enemy_team = Team(name="Enemy Team")
                for j in range(randint(2, 3)):
                    id = random.choice(enemies)
                    min_lvl = mobs[id]["min_lvl"]
                    mob = build_mob(id=id, level=randint(min_lvl, min_lvl+20))
                    #mob.front_row = 1
                    enemy_team.add(mob)
                back = iam.select_background_for_fight("tavern")
                result = run_default_be(enemy_team, background=back, end_background="tavern_inside", skill_lvl=3,
                                        slaves=False, prebattle=True)

                if result is True:
                    group_counter -= 1
                else:
                    group_counter = -2

    if group_counter == 0:
        "The fight is finally over. You found a few coins in thugs pockets."
        $ hero.add_money(randint(50, 150)*(i+1), reason="Tavern")
    elif group_counter == -1:
        "You quickly leave the tavern."
    else:
        if hero.gold > 50:
            $ hero.take_money(min(hero.gold, randint(50, 150)*(i+1)), reason="Tavern")
            "You were beaten and robbed..."
        else:
            "You were beaten..."
    $ del group_counter
    jump city


label mc_action_tavern_look_around: # various bonuses to theoretical skills for drinking with others in the lively mode
    if hero.take_money(randint(10, 20), reason="Tavern"):
        hide drunkards with dissolve

        $ iam.drinking_outside_of_inventory(char=hero, count=randint(15, 25))
        $ N = random.choice(["fishing", "sex", "exp"])

        if N == "fishing":
            $ name = "content/gfx/images/tavern/fish_" + str(renpy.random.randint(1, 4)) + ".webp"
            show expression name as sign at truecenter with dissolve
            "A group of local fishermen celebrating a good catch in the corner. You join them, and they share a few secrets about fishing with you."
            $ hero.gfx_mod_skill("fishing", 1, randint(2, 5))
            hide sign with dissolve
            $ del name
        elif N == "sex":
            $ character = random.choice(chars.values())
            $ picture = character.show("sex", resize=(500, 600))
            show expression picture as sign at truecenter with dissolve
            "A group of drunk young men and women boasting about their sexual feats. Most of the feats never happened, but you still got a few interesting ideas."
            $ hero.gfx_mod_skill("sex", 1, randint(1, 3))
            hide sign with dissolve
            $ del character, picture
        else:
            show expression "content/gfx/interface/icons/exp.webp" as sign at truecenter with dissolve
            "You are sharing fresh rumors with patrons over a beer."
            $ hero.gfx_mod_exp(exp_reward(hero, hero))
            hide sign with dissolve

        $ del N
    else:
        "You don't have enough money to join others, so there is nothing interesting for you at the moment."

    jump city_tavern_menu

label city_tavern_shopping: # tavern shop with alcohol, available in all modes except brawl
    hide drunkards with dissolve
    show expression npcs["Rita_tavern"].get_vnsprite() as npc
    with dissolve
    npcs["Rita_tavern"].say "Do you want something?"
    python:
        focus = None
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Tavern"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_6

    hide screen shopping
    with dissolve
    hide npc

    $ del shop, focus, item_price, amount, purchasing_dir
    jump city_tavern_menu