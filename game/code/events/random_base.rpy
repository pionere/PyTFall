# Base Events File
init -1 python:
    register_event("found_money_event", locations=["all"], run_conditions=["dice(max(15, hero.get_stat('luck')+10))"], priority=50, restore_priority=0)
    register_event("found_item_event", locations=["all"], run_conditions=["dice(max(35, hero.get_stat('luck')+20))"], priority=50, restore_priority=0)
    register_event("nothing_of_interest", locations=["all"], dice=100, priority=1, restore_priority=0)

label found_money_event(event):
    python hide:
        amount = 50 + hero.get_stat("luck")
        amount = locked_random("randint", amount/2, amount)
        hero.add_money(amount, "Luck")
        gfx_overlay.random_find(amount, 'gold')
        hero.say(choice(["Some money... Excellent.", "Free gold, nice!",
                       "A few coins! I'm lucky today.", "Did someone drop a wallet?"]))
    return

label found_item_event(event):
    python hide:
        if locked_dice(60):
            items_pool = list(item for item in items.itervalues() if "Look around" in item.locations and dice(item.chance))
            found_item = choice(items_pool)
        else:
            found_item = items["Rebels Leaflet"]

        gfx_overlay.random_find(found_item, 'item')
        hero.inventory.append(found_item)

        if found_item != items["Rebels Leaflet"]:
            hero.say(choice(["Hmm. I found something. (%s)",
                             "%s, might be useful...",
                             "%s? Nice, might be useful.",
                             "Oh, %s! Never look a gift horse in the mouth..."]) % found_item.id)
        else:
            hero.say("An old prewar leaflet... I probably shouldn't keep it in my pockets for long.")
    return

label nothing_of_interest(event):
    $ hero.say(choice(["Another time well spent...", "Maybe I should find some work!",
                    "Nothing... Time do something useful.", "This is a nice place, I could spent more time here!"]))
    return
