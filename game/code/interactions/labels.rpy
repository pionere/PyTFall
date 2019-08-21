label test_interactions:
    python:
        char = hero.get_flag("test_interactions", None)
        if char is None:
            # Prepare the hero
            for i in ("Proper Mercenary Clothes", "High Fur Boots", "Jeweled Poignard", "Warm Scarf", "Wizard Robes", "Ceremonial Sabre", "General Helmet", "Dealer Gloves", "Ring of Physique", "Ring of Physique", "Woody Ring"):
                hero.equip(items[i], remove=False, aeq_mode=True)

            for stat in hero.stats:
                hero.mod_stat(stat, hero.get_max(stat))

            hero.gold = 10000

            # build char
            char = build_rc(tier=2)
            char.remove_trait(traits["Lesbian"])
            char.preferences = {p : .5 for p in char.preferences}
            hero.set_flag("test_interactions", char)

        # start interaction
        iam.start_int(char, img=iam.select_beach_img_tags(char), exit="mainscreen")

label test_interactions_mid:
    python:
        char = hero.get_flag("test_interactions", None)
        if char is None:
            # Prepare the hero
            tier_up_to(hero, 4)

            for i in ("Fae Robe", "Fae Boots", "Vibranium Shield", "Master Charm", "Mantle of the Keeper", "Magic Bow", "General Helmet", "Fae Bracers", "Ring of Charisma", "Ring of Charisma", "Ring of Charisma"):
                hero.equip(items[i], remove=False, aeq_mode=True)
            #"Reflector", "Fae Hood"

            for stat in hero.stats:
                hero.mod_stat(stat, hero.get_max(stat))

            hero.gold = 1000000

            # build char
            char = build_rc(tier=6)
            char.remove_trait(traits["Lesbian"])
            char.preferences = {p : .5 for p in char.preferences}
            hero.set_flag("test_interactions", char)

        # start interaction
        iam.start_int(char, img=iam.select_beach_img_tags(char), exit="mainscreen")
