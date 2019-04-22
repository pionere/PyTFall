init -11 python:
    def count_owned_items(char, item):
        # Includes iventory and equipped.
        if isinstance(item, basestring):
            item = items[item]

        return char.inventory[item] + char.eqslots.values().count(item)

    def has_items(item, char, equipped=True):
        if isinstance(item, basestring):
            item = items[item]

        if equipped:
            amount = char.eqslots.values().count(item)
        else:
            amount = char.inventory[item]

        return amount

    # when it's true, we assume that equipment screen was called from unusual place,
    # so all things which can break it are disabled
    equipment_safe_mode = False

    def equip_item(item, char, silent=False):
        """First level of checks, all items should be equipped through this function!
        """
        if not can_equip(item, char, silent=silent):
            return

        char.equip(item)

    def transfer_items(source, target, item, amount=1, silent=False, force=False):
        """Transfers items between characters.

        This will also log a fact of transfer between a character and MC is appropriate.
        @param: force: Option to forcibly take an item from a character.
        """
        if isinstance(item, basestring):
            item = items[item]

        given = amount * len(target) if isinstance(target, PytGroup) else amount

        if not can_transfer(source, target, item, amount=given, silent=silent, force=force):
            return False

        if not source.inventory.remove(item, given):
            return False

        received = amount * len(source) if isinstance(source, PytGroup) else amount

        if not any([item.slot == "consumable", (item.slot == "misc" and item.mdestruct)]):

            if isinstance(source, Char) and source.status != "slave":
                source.given_items[item.id] = source.given_items.get(item.id, 0) - given

            elif isinstance(source, PytGroup):
                for c in source.lst:
                    if c.status != "slave":
                        c.given_items[item.id] = c.given_items.get(item.id, 0) - given

            if isinstance(target, Char) and target.status != "slave":
                target.given_items[item.id] = target.given_items.get(item.id, 0) + received

            elif isinstance(target, PytGroup):
                for c in target.lst:
                    if c.status != "slave":
                        c.given_items[item.id] = c.given_items.get(item.id, 0) + received

        target.inventory.append(item, received)
        return True

    def can_equip(item, character, silent=True):
        """Checks if it is legal for a character to use/equip the item.

        @param: silent: If False, game will notify the player with a reason why an item cannot be equipped.
        """
        if item.slot == 'consumable':
            if equipment_safe_mode and item.jump_to_label:
                if not silent:
                    renpy.show_screen("message_screen", "Special items cannot be used right now.")
                return

            if item in character.consblock:
                if not silent:
                    turns = character.consblock[item]
                    renpy.show_screen("message_screen", "This item has been used recently by %s, it cannot be used again for %d %s." % (character.name, turns, plural("turn", turns)))
                return

        elif item.slot == 'misc':
            if item in character.miscblock:
                if not silent:
                    renpy.show_screen("message_screen", "This item has been already used by %s, and cannot be used again." % character.name)
                return

        if isinstance(character, PytGroup):
            if item.jump_to_label:
                return

            # downstream function can trigger a response assuming char is a character
            global char
            for char in character.shuffled:
                if not can_equip(item, char, silent):
                    char = character
                    return
            char = character
            return True
        temp = character.gender
        if getattr(item, "gender", temp) != temp:
            if not silent:
                renpy.show_screen('message_screen', "This item cannot be equipped on a %s character." % character.gender)
            return
        elif item.unique and item.unique != character.id:
            if not silent:
                renpy.show_screen("message_screen", "This unique item cannot be equipped on %s." % character.name)
            return
        elif item.type == "scroll": # prevents using scroll if it gives already known spell
            battle_skill = store.battle_skills[item.add_be_spells[0]]
            if battle_skill in character.magic_skills:
                if not silent:
                    renpy.show_screen('message_screen', "%s already knows this spell." % character.name)
                return
        elif not item.usable:
            if not silent:
                renpy.show_screen("message_screen", "This item cannot be used or equipped.")
            return
        elif item.type == "food" and 'Food Poisoning' in character.effects:
            if not silent:
                renpy.show_screen('message_screen', "%s is already suffering from food poisoning. More food won't do any good." % character.name)
            return
        elif character.status == "slave":
            if item.slot == "weapon" and item.type != "tool":
                if not silent:
                    renpy.show_screen('message_screen', "Slaves are forbidden to use large weapons by law.")
                return
            elif item.type == "armor":
                if not silent:
                    renpy.show_screen('message_screen', "Slaves are forbidden to wear armor by law.")
                return
            elif item.type == "shield":
                if not silent:
                    renpy.show_screen('message_screen', "Slaves are forbidden to use shields by law.")
                return
        return True

    def can_transfer(source, target, item, amount=1, silent=True, force=False):
        """Checks if it is legal for a character to transfer the item.

        @param: silent: If False, game will notify the player with a reason why an item cannot be equipped.
        @param: force: Option to forcibly take an item from a character.
        """
        if isinstance(source, PytGroup):
            if item.jump_to_label:
                return

            for c in source.shuffled:
                if not can_transfer(c, target, item, amount, silent, force):
                    return
            return True
        if isinstance(target, PytGroup):
            if item.jump_to_label:
                return

            for c in target.shuffled:
                if not can_transfer(source, c, item, amount, silent, force):
                    return
            return True

        if item.unique and (not isinstance(target, Building)) and item.unique != ("mc" if target == hero else target.id):
            if not silent:
                renpy.show_screen("message_screen", "This unique item cannot be given to {}!".format(target.name))
            return
        if not item.transferable:
            if not silent:
                renpy.show_screen('message_screen', "This item cannot be transferred!")
            return

        # Free girls should always refuse giving up their items unless MC gave it to them:
        # (Unless action is forced):
        if not force:
            if all([isinstance(source, Char), source.status != "slave", not(item.price <= interactions_influence(source)*10*(source.tier + 1) and check_lovers(source, hero))]):
                if any([item.slot == "consumable", (item.slot == "misc" and item.mdestruct), source.given_items.get(item.id, 0) < amount]):
                    if not silent:
                        source.override_portrait("portrait", "indifferent")
                        if "Impersonal" in source.traits:
                            source.say(choice(["Denied. It belongs only to me.", "You are not authorised to dispose of my property."]))
                        elif "Shy" in source.traits and dice(50):
                            source.say(choice(["W... what are you doing? It's not yours...", "Um, could you maybe stop touching my things, please?"]))
                        elif "Dandere" in source.traits:
                            source.say(choice(["Don't touch my stuff without permission.", "I'm not giving it away."]))
                        elif "Kuudere" in source.traits:
                            source.say(choice(["Would you like fries with that?", "Perhaps you would like me to give you the key to my flat where I keep my money as well?"]))
                        elif "Yandere" in source.traits:
                            source.say(choice(["Please refrain from touching my property.", "What do you think you doing with my belongings?"]))
                        elif "Tsundere" in source.traits:
                            source.say(choice(["Like hell am I giving away!", "Hey, hands off!"]))
                        elif "Imouto" in source.traits:
                            source.say(choice(["No way! Go get your own!", "Don't be mean! It's mine!"]))
                        elif "Bokukko" in source.traits:
                            source.say(choice(["Hey, why do ya take my stuff?", "Not gonna happen. It's mine alone."]))
                        elif "Kamidere" in source.traits:
                            source.say(choice(["And what makes you think I will allow anyone to take my stuff?", "Refrain from disposing of my property unless I say otherwise."]))
                        elif "Ane" in source.traits:
                            source.say(choice(["Please, don't touch it. Thanks.", "Excuse me, I do not wish to part with it."]))
                        else:
                            source.say(choice(["Hey, I need this too, you know.", "Eh? Can't you just buy your own?"]))
                        source.restore_portrait()
                    return

        return True

    def equipment_access(character, item=None, silent=False, unequip=False):
        # Here we determine if a character would be willing to give MC access to her equipment:
        # Like if MC asked this character to equip or unequip an item.
        # We return True if access is granted!
        #
        # with unequip=False (default) check whether we are allowed to equip the item,
        # with unequip=True, check whether we are allowed to *un*equip
        if character == hero:
            return True # Would be weird if we could not access MCs inventory....

        if isinstance(character, PytGroup):
            if item and item.jump_to_label:
                return False

            # get a response from one single individual
            for c in character.shuffled:
                if not equipment_access(c, item, silent, unequip):
                    store.char = c
                    return False
            store.char = character
            return True

        # Always the same here as well...
        if character.status == "slave":
            return True

        # Always refuse if character hates the player:
        char_dispo = character.get_stat("disposition")
        if char_dispo <= -500:
            if not silent:
                interactions_girl_disp_is_too_low_to_give_money(character) # turns out money lines are perfect here
            return False

        if item:
            if unequip:
                if char_dispo >= 900 or check_lovers(character, hero) or check_friends(character, hero):
                    return True

                if item.eqchance <= 20 or item.badness >= 80:
                    return True

                if not item.badtraits.isdisjoint(character.traits):
                    return True

            else:
                # Bad Traits:
                if not item.badtraits.isdisjoint(character.traits):
                    if not silent:
                        interactions_character_doesnt_want_bad_item(character)
                    return False

                # Always allow restorative items:
                if item.type == "restore" and item.eqchance > 0:
                    return True

                if item.type == "alcohol" and item.eqchance > 0:
                    if 'Drunk' in character.effects or 'Depression' in character.effects or "Heavy Drinker" in character.traits: # green light for booze in case of suitable effects
                        return True

                if item.type == "food" and "Always Hungry" in character.traits and item.eqchance > 0: # same for food
                    return True

                # Good traits:
                if not item.goodtraits.isdisjoint(character.traits):
                    return True

                # Just an awesome item in general:
                if item.eqchance >= 70:
                    return True
                elif item.eqchance <= 0: # 0 eqchance will make item unavailable, unless there is good trait or slave status
                    if not silent:
                        interactions_character_doesnt_want_bad_item(character)
                    return False

        if char_dispo < 900 and not check_lovers(character, hero):
            if not silent:
                interactions_character_doesnt_want_to_equip_item(character)
            return False

        return True

    def give_to_mc_item_reward(types, price=None, tier=None, locations=["Exploration"]):
        if tier is None:
            tier = hero.tier
        item = get_item_drops(types=types, price=price, tier=tier, locations=locations)
        if not item:
            return False
        hero.add_item(item)
        gfx_overlay.random_find(item, 'items')
        hero.say("I found %s..." % item.id)
        return True

    def get_item_drops(types, price=None, tier=None, locations=None, amount=1): # va calls gives to mc a random item based on type and max price
        """Sort out items for drops/rewards in places such as Arena/Forest/Quests and etc.

        types are item types we want enemies to drop, a list.
        We expect it to be a list, or shove it in one otherwise
        'all' will check for all types available here
        (look in the code for types you can use)

        locatons: a list/set is expected, we'll match it vs item.location field.

        Can be sorted on price or tier or both (price will have the priority).
        Well return a list of items if amount is greater than 1 (be careful with this)
        """
        if isinstance(types, basestring) and types != "all":
            types = [types]

        if locations is not None:
            locations = set(locations)

        picked = []
        for item in items.values():
            if price is not None:
                if item.price > price:
                    continue

            if tier is not None:
                if item.tier > tier:
                    continue

            if locations is not None:
                if locations.isdisjoint(item.locations):
                    continue

            if types == "all" or item.type in types:
                picked.append(item)
                continue

            if "consumable" in types:
                if item.slot == "consumable" and item.type not in ("food", "alcohol"):
                    picked.append(item)
                    continue

            if "armor" in types:
                if item.slot in ("body", "head", "feet", "wrist") and item.type not in ("dress", "tool"):
                    picked.append(item)
                    continue

            if "weapon" in types:
                if item.slot in ("weapon", "smallweapon") and item.type != "tool":
                    picked.append(item)
                    continue

            if "loot" in types:
                if item.slot == "loot":
                    picked.append(item)
                    continue

        choices = []
        for i in picked:
            choices.append([i, i.chance])
        return weighted_sample(choices, amount)
