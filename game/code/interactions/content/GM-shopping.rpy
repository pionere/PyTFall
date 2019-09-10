label interactions_shopping:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end

    if iam.flag_count_checker(char, "interactions_shopping") != 0:
        $ iam.refuse_because_tired(char)
        jump girl_interactions

    if not iam.want_shopping(char):
        $ char.gfx_mod_stat("disposition", -randint(1, 2))
        $ iam.int_reward_exp(char, .1)
        $ iam.refuse_invite_any(char)
        jump girl_interactions

    $ iam.accept_invite(char)
    hide screen girl_interactions

    $ iam.set_img("girlmeets", ("no bg", "simple bg", "indoors"), exclude=["swimsuit", "indoor", "wildness", "suburb", "beach", "pool", "onsen", "nature"], resize=(300, 300), type="ptls", gm_mode=True)

    scene bg tailor_store
    with dissolve

    show expression npcs["Kayo_Sudou"].get_vnsprite() as npc
    with dissolve

    $ t = npcs["Kayo_Sudou"].say
    if pytfall.enter_location("tailor_store", music=False, env="shops"):
        t "Welcome to my store!"
        t "Just the best clothing you'll ever see!"
        $ txt = "partner" if char.status == "free" else ("girl" if char.gender == "female" else "guy")
        t "Check out our latest collection. Your [txt] will love it:"
    else:
        t "Welcome back!"
        if char.status == "free":
            $ txt = "a lady" if char.gender == "female" else "a gentleman"
        else:
            $ txt = "one of your %s" % ("ladies" if char.gender == "female" else "guys")
        t "Ah with [txt]. Let see what they'd like!"

    hide npc with dissolve

    python:
        focus = False
        item_price = 0
        purchasing_dir = None
        shop = pytfall.shops_stores["Tailor Store"]
        char.inventory.set_page_size(18)

    show screen interactions_shopping
    with dissolve

    python:
        temp, txt = None, []
        while True:
            result = ui.interact()
            if result[0] == "item":
                if result[1] == char:
                    purchasing_dir = "sell"
                    item_price = shop.sell_margin
                else:
                    purchasing_dir = "buy"
                    item_price = shop.buy_margin
                focus = result[2]
                item_price = int(focus.price * item_price)
            elif result[0] == "shop":
                if result[1] == "buy":
                    if count_owned_items(focus, char) != 0:
                         iam.refuse_shop(char)
                    elif not can_equip(focus, char, silent=True):
                         iam.items_deny_bad_item(char)
                    elif hero.take_money(item_price, reason="Gifts"):
                        PyTSFX.purchase()

                        t = [t for t in char.basetraits if set(t.base_skills).intersection(focus.mod_skills)]
                        if char.status == "free":
                            if t:
                                t = choice(t)
                                txt.append("%s will definitly make me a better %s." % (focus.id, t.id))
                                char.gfx_mod_stat('disposition', 1)
                                char.gfx_mod_stat("affection", affection_reward(char))

                            if item_price > 1000:
                                txt.append("Ohh, thank you! I love the %s. Thank you so much." % focus.id)
                                char.gfx_mod_stat('disposition', 6)
                                char.gfx_mod_stat("affection", affection_reward(char, 1.5, stat="gold"))
                                char.gfx_mod_stat('joy', 4)
                            else:
                                txt.append("Thank you. I like it very much.")
                                char.gfx_mod_stat('disposition', 3)
                                char.gfx_mod_stat("affection", affection_reward(char, stat="gold"))
                                char.gfx_mod_stat('joy', 3)
                        else: # a slave
                            if t:
                                t = choice(t)
                                txt.append("%s will definitly make me a better %s for %s." % (focus.id, t.id, char.mc_ref))
                                char.gfx_mod_stat('disposition', 1)
                                char.gfx_mod_stat("affection", affection_reward(char))

                            if char.get_stat("joy") < 40:
                                if item_price > 1000:
                                    txt.append("Thank you very much %s. I will put the %s to good use." % (char.mc_ref, focus.id))
                                    char.gfx_mod_stat('disposition', 4)
                                    char.gfx_mod_stat('joy', 2)
                                else:
                                    txt.append("Thank you %s for the %s." % (char.mc_ref, focus.id))
                                    char.gfx_mod_stat('disposition', 2)
                                    char.gfx_mod_stat('joy', 1)

                            elif char.get_stat("joy") < 80:
                                if item_price > 1000:
                                    txt.append("Thank you *KISS* very *VERY* much %s *KISS* for the %s ." % (char.mc_ref, focus.id))
                                    char.gfx_mod_stat('disposition', 5)
                                    char.gfx_mod_stat('joy', 3)
                                else:
                                    txt.append("*KISS* Thank you %s. I like the %s." % (char.mc_ref, focus.id))
                                    char.gfx_mod_stat('disposition', 2)
                                    char.gfx_mod_stat('joy', 2)

                            else:
                                if item_price > 1000:
                                    txt.append("%s! I love the %s. Thank you so much." % (char.mc_ref.upper(), focus.id))
                                    txt.append("%s gives you a kiss that leaves you breathless for a moment." % char.pC)
                                    char.gfx_mod_stat('disposition', 6)
                                    char.gfx_mod_stat('joy', 4)
                                else:
                                    txt.append("%s *KISS* Thank you %s. I like the %s." % (char.mc_ref, char.mc_ref, focus.id))
                                    char.gfx_mod_stat('disposition', 3)
                                    char.gfx_mod_stat('joy', 3)

                        shop.inventory.remove(focus)
                        char.inventory.append(focus)
                        shop.gold += item_price
                        shop.total_items_price -= item_price
                        break
                    else:
                        PyTGFX.message("You don't have enough Gold!")
                elif result[1] == "sell" and can_transfer(char, hero, focus):
                    t = shop.check_sell(focus, item_price)
                    if t is None:
                        shop.gold -= item_price
                        shop.total_items_price += item_price
                        if char.status == "free":
                            char.add_money(item_price, reason="Items")
                        else:
                            hero.add_money(item_price, reason="Items")
                        char.inventory.remove(focus)
                        shop.inventory.append(focus)

                        PyTSFX.purchase()

                        iam.accept_sell(char)

                        focus = False
                    else:
                        narrator(t)

            elif result == ["control", "return"]:
                break

    hide screen interactions_shopping
    with dissolve

    python:
        if txt:
            for t in txt:
                char.say(t)
            iam.int_reward_exp(char)
            if char.autoequip:
                char.auto_equip(char.last_known_aeq_purpose)
        else:
            iam.dispo_reward(char, -randint(4, 6))
            iam.disappointed(char)

    $ iam.restore_img()
    $ PyTSFX.set_env(iam.env_cache)

    $ del t, txt, temp, shop, focus, item_price, purchasing_dir
    jump girl_interactions

screen interactions_shopping:
    if controlled_char(char):
        use shop_inventory(ref=char, x=.0)
    else:
        fixed:
            align .01, .5
            xysize 310, 310
            frame:
                background Frame("content/gfx/frame/MC_bg.png", 5, 5)
                add iam.img align .5, .5
    use shop_inventory(ref=shop, x=1.0)

    if focus:
        $ temp = char.eqslots.get(focus.slot, None)
        if temp: # only show the currently equiped item if there is one
            frame:
                background Frame("content/gfx/frame/mes12.jpg", 5, 5)
                align (.5, .05)
                use itemstats(item=temp, size=(580, 300))

        frame:
            background Frame("content/gfx/frame/mes12.jpg", 5, 5)
            align (.5, .98)
            use itemstats(item=focus, size=(540, 300))

        frame:
            background Frame("content/gfx/frame/MC_bg.png", 5, 5)
            align (.765, .75)
            padding 6, 6
            has vbox spacing 4
            #offset -300, 400

            style_prefix "proper_stats"
            text "Price:" size 18 xalign .5
            text str(item_price) color "gold" size 24 xalign .5
            textbutton purchasing_dir.capitalize():
                style "basic_button"
                action Return(["shop", purchasing_dir])
                xsize 75
                xalign .5

    fixed:
        offset -281, 680
        use exit_button