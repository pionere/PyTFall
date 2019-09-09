###### j0
# quick navigation, search "j" + number, example: j0 - this panel
#
#  1 - shopping - shopping
###### j1
label interactions_shopping:
    # TODO items/interactions lt: Get rid of this or update it to modern PyTFall!
    #copied from tailor shop
    #then modified for own use
    hide screen girl_interactions

    scene bg tailor_store
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

    python:
        focus = False
        purchasing_dir = None
        shop = pytfall.shops_stores["Tailor Store"]
        char.inventory.set_page_size(18)

    show screen tailor_store_shopping_girl
    with dissolve

    python:
        txt = ''
        while True:
            result = ui.interact()
            if result[0] == 'shop':
                if result[1] == 'first_page':shop.inventory.first()
                elif result[1] == 'last_page':shop.inventory.last()
                elif result[1] == 'next_page':shop.inventory.next()
                elif result[1] == 'prev_page':shop.inventory.prev()
                elif result[1] == 'prev_filter':shop.inventory.apply_filter('prev')
                elif result[1] == 'next_filter':shop.inventory.apply_filter('next')
                else:
                    purchasing_dir = 'buy'
                    focus = shop.inventory.getitem(result[1])

            elif result[0] == 'inv':
                if result[1] == 'first_page':char.inventory.first()
                elif result[1] == 'last_page':char.inventory.last()
                elif result[1] == 'next_page':char.inventory.next()
                elif result[1] == 'prev_page':char.inventory.prev()
                elif result[1] == 'prev_filter':char.inventory.apply_filter('prev')
                elif result[1] == 'next_filter':char.inventory.apply_filter('next')
                else:
                    purchasing_dir = 'sell'
                    focus = char.inventory.getitem(result[1])

            elif result[0] == 'control':
                if result[1] == 'buy/sell':
                    if purchasing_dir == 'buy':
                        result = hero.take_money(focus.price, reason="Gifts")

                        if result:
                            if char.status == "free":
                                for t in char.basetraits:
                                    if set(t.base_skills).intersection(focus.mod_skills):
                                        txt == "%s will definitly make me a better %s.\n" % (focus.id, t.id)
                                        char.gfx_mod_stat('disposition', 1)
                                        char.gfx_mod_stat("affection", affection_reward(char))

                                if focus.price > 1000:
                                    txt += "Ohh, thank you! I love the %s. Thank you so much.\n" % focus.id
                                    char.gfx_mod_stat('disposition', 6)
                                    char.gfx_mod_stat("affection", affection_reward(char, "gold", 1.5))
                                    char.gfx_mod_stat('joy', 4)
                                else:
                                    txt += "Thank you. I like it very much.\n"
                                    char.gfx_mod_stat('disposition', 3)
                                    char.gfx_mod_stat("affection", affection_reward(char, "gold"))
                                    char.gfx_mod_stat('joy', 3)
                            else: # a slave
                                for t in char.basetraits:
                                    if set(t.base_skills).intersection(focus.mod_skills):
                                        txt == "%s will definitly make me a better %s for Master.\n" % (focus.id, t.id)
                                        char.gfx_mod_stat('disposition', 1)
                                        char.gfx_mod_stat("affection", affection_reward(char))

                                if char.get_stat("joy") < 40:
                                    if focus.price > 1000:
                                        txt += "Thank you very much Master. I will put the %s to good use.\n" % focus.id
                                        char.gfx_mod_stat('disposition', 4)
                                        char.gfx_mod_stat('joy', 2)
                                    else:
                                        txt += "Thank you Master for the %s.\n"%focus.id
                                        char.gfx_mod_stat('disposition', 2)
                                        char.gfx_mod_stat('joy', 1)

                                elif char.get_stat("joy") < 80:
                                    if focus.price > 1000:
                                        txt += "Thank you *KISS* very *VERY* much Master *KISS* for the %s .\n" % focus.id
                                        char.gfx_mod_stat('disposition', 5)
                                        char.gfx_mod_stat('joy', 3)

                                    else:
                                        txt += "*KISS* Thank you Master. I like the %s.\n" % focus.id
                                        char.gfx_mod_stat('disposition', 2)
                                        char.gfx_mod_stat('joy', 2)

                                else:
                                    if focus.price > 1000:
                                        txt += "MASTER! I love the %s. Thank you so much.\n%s gives you a kiss that leaves you breathless for a moment.\n" % (focus.id, char.pC)
                                        char.gfx_mod_stat('disposition', 6)
                                        char.gfx_mod_stat('joy', 4)

                                    else:
                                        txt += "Master *KISS* Thank you Master. I like the %s.\n" % focus.id
                                        char.gfx_mod_stat('disposition', 3)
                                        char.gfx_mod_stat('joy', 3)

                            shop.inventory.remove(focus)
                            char.inventory.append(focus)
                            shop.gold += focus.price
                            break

                        focus = False

                    elif purchasing_dir == 'sell':
                        if shop.gold >= focus.price:
                            shop.gold -= focus.price
                            hero.add_money(focus.price, reason="Items")
                            char.inventory.remove(focus)
                            shop.inventory.append(focus)

                            if char.occupation=='Prostitute':
                                txt += "Prostitute test"

                            if char.occupation=='Stripper':
                                txt += "Stripper test"

                            if char.occupation=='Server':
                                txt += "Server test"

                            if char.occupation=='Warrior':
                                txt += "Warrior test"

                            if char.occupation=='Healer':
                                txt += "Healer test"

                            break

                        focus = False

                elif result[1] == 'return':
                    break

    hide screen tailor_store_shopping_girl
    with dissolve

    if txt !='':
        char.say "[txt]"

    $ PyTSFX.set_env(iam.env_cache)

    $ del t, txt, shop, focus, purchasing_dir
    jump girl_interactions

screen tailor_store_shopping_girl():
    frame:
        align (.5, 0)
        xmaximum 600
        ymaximum 120

        hbox:
            null width 30
            add im.Scale("content/gfx/interface/icons/gold.png", 40, 40) align(.5, .5)
            null width 20
            text (u'{size=+1}{color=gold}{b}= %s{/b}' % hero.gold) align(.5, .5)
            null width 60
            text (u'{size=+1}Day  =  %d' % day) align(.5, .5)
            null width 50

    use shop_inventory(ref=char, x=.0, title="Inventory")
    use shop_inventory(ref=shop, x=1.0, title="Tailor Store")

    if focus:
        frame background Frame("content/gfx/frame/mes12.jpg", 5, 5):
            align (.5, .15)
            xmaximum 700
            ymaximum 400 # changed so the other frame can go below
            hbox:
                use itemstats(item=focus,mode='normal')
            frame background Solid((0, 0, 0, 0)):
                align (.5, 1.0)
                hbox:
                    text (u' Price: %s' % focus.price)
                    null width 20
                    textbutton "Buy/Sell" action Return(['control','buy/sell']) maximum (150, 30)
        if char.eqslots['body']: # only show the currently equiped item if there is one
            frame background Frame("content/gfx/frame/mes12.jpg", 5, 5):
                align (.5, .95)
                xmaximum 700
                ymaximum 300
                use itemstats(item=char.eqslots['body']) # added a mode to the itemstats

    $ img = im.Scale("content/gfx/interface/buttons/shape69.png", 40, 40)
    imagebutton:
        align (.99, 0)
        idle img
        hover im.MatrixColor(img, im.matrix.brightness(.15))
        action Return(["control", "return"])