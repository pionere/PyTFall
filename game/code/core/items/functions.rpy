init -11 python:
    def count_owned_items(item, char):
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

    def transfer_items(source, target, item, amount=1, silent=False, force=False):
        """Transfers items between characters.

        This will also log a fact of transfer between a character and MC is appropriate.
        @param: force: Option to forcibly take an item from a character.
        """
        if isinstance(item, basestring):
            item = items[item]

        if not can_transfer(source, target, item, amount=amount, silent=silent, force=force):
            return False

        if not source.inventory.remove(item, amount):
            return False

        target.inventory.append(item, amount)

        # register transfers to maintain 'ownership' of the items
        if item.slot != "consumable" and (item.slot != "misc" or not item.mdestruct):
            item = item.id
            if isinstance(source, Char) and source.status != "slave":
                new_amount = source.given_items.get(item, 0) - amount
                if new_amount == 0:
                    source.given_items.pop(item, None)
                else:
                    source.given_items[item] = new_amount

            if isinstance(target, Char) and target.status != "slave":
                new_amount = target.given_items.get(item, 0) + amount
                if new_amount == 0:
                    target.given_items.pop(item, None)
                else:
                    target.given_items[item] = new_amount
        return True

    def can_equip(item, character, silent=False):
        """Checks if it is legal for a character to use/equip the item.

        @param: silent: If False, game will notify the player with a reason why an item cannot be equipped.
        """
        if item.slot == 'consumable':
            if equipment_safe_mode and item.jump_to_label:
                if not silent:
                    PyTGFX.message("Special items cannot be used right now.")
                return

            if item in character.consblock:
                if not silent:
                    turns = character.consblock[item]
                    PyTGFX.message("This item has been used recently by %s, it cannot be used again for %d %s." % (character.name, turns, plural("turn", turns)))
                return

        elif item.slot == 'misc':
            if item in character.miscblock:
                if not silent:
                    PyTGFX.message("This item has been already used by %s, and cannot be used again." % character.name)
                return

        temp = character.gender
        if getattr(item, "gender", temp) != temp:
            if not silent:
                PyTGFX.message("This item cannot be equipped on a %s character." % character.gender)
            return
        elif item.unique and item.unique != character.id:
            if not silent:
                PyTGFX.message("This unique item cannot be equipped on %s." % character.name)
            return
        elif item.type == "scroll": # prevents using scroll if it gives already known spell
            battle_skill = item.add_be_spells[0]
            if battle_skill in character.magic_skills:
                if not silent:
                    PyTGFX.message("%s already knows this spell." % character.name)
                return
        elif not item.usable:
            if not silent:
                PyTGFX.message("This item cannot be used or equipped.")
            return
        elif item.type == "food" and 'Food Poisoning' in character.effects:
            if not silent:
                PyTGFX.message("%s is already suffering from food poisoning. More food won't do any good." % character.name)
            return
        elif character.status == "slave":
            if item.slot == "weapon" and item.type != "tool":
                if not silent:
                    PyTGFX.message("Slaves are forbidden to use large weapons by law.")
                return
            elif item.type == "armor":
                if not silent:
                    PyTGFX.message("Slaves are forbidden to wear armor by law.")
                return
            elif item.type == "shield":
                if not silent:
                    PyTGFX.message("Slaves are forbidden to use shields by law.")
                return
        return True

    def eval_inventory(char, inventory, slots, base_purpose, check_money):
        """
        picks items from an inventory for the current character.
        incorporates most of the can_equip function

        :param inventory: the inventory to evaluate items from
        :param slots: a list/tuple/set/dict of slots to be considered
        :param base_purpose: set of strings to match against item.pref_class
        :param check_money: whether check if the char has enough money to buy the item
        """

        # call the functions for these only once
        gold = char.gold if check_money else sys.maxint
        gender = char.gender
        is_slave = char.status == "slave"
        miscblock = char.miscblock
        magic_skills = char.magic_skills

        # per item the nr of weighting criteria may vary. At the end all of them are averaged.
        # if an item has less than the most weights the remaining are imputed with 50 weights
        # Nor sure why????
        # most_weights = {slot: 0 for slot in weighted}
        picks = []
        for item in inventory:
            if item.price > gold:
                aeq_debug("Ignoring item %s on gold.", item)
                continue

            slot = item.slot
            if slot not in slots:
                aeq_debug("Ignoring item %s on slot.", item)
                continue

            # Gender:
            if getattr(item, "gender", gender) != gender:
                aeq_debug("Ignoring item %s on gender.", item)
                continue

            # Handle purposes:
            if base_purpose.isdisjoint(item.pref_class):
                # If no purpose is valid for the item, we want nothing to do with it.
                aeq_debug("Ignoring item %s on purpose.", item)
                continue

            #if not item.eqchance: pref_class filter!
            #    aeq_debug("Ignoring item %s on eqchance (%s) (%s).", item, item.eqchance)
            #    continue
            #if not item.usable: # pref_class filter!
            #    aeq_debug("Ignoring unusable item %s.", item)
            #    continue
            #if item.jump_to_label: # Never pick jump_to_label? pref_class filter!
            #    aeq_debug("Ignoring special item %s with jump to label.", item)
            #    continue
            # no need to check, because uniques can be hold only by their owner
            #if item.unique and item.unique != char.id:
            #    aeq_debug("Ignoring unique item %s which does not belong to char.", item)
            #    continue
            if slot == 'misc' and item in miscblock:
                aeq_debug("Ignoring misc item %s on block", item)
                continue

            type = item.type
            #if type == "permanent": # Never pick permanent? pref_class filter!
            #    aeq_debug("Ignoring item %s because it is permanent.", item)
            #    continue
            if type == "scroll" and magic_skills: # prevents using scroll if it gives already known spell
                battle_skill = item.add_be_spells[0]
                if battle_skill in magic_skills:
                    aeq_debug("Ignoring scroll item %s because it is already known.", item)
                    continue

            #if item.type == "food" and 'Food Poisoning' in character.effects:
            #    aeq_debug("Ignoring food item %s.", item)
            #    continue
            if is_slave is True:
                if slot == "weapon" and type != "tool":
                    aeq_debug("Ignoring weapon item %s because char is a slave.", item)
                    continue
                elif type == "armor":
                    aeq_debug("Ignoring armor item %s because char is a slave.", item)
                    continue
                elif type == "shield":
                    aeq_debug("Ignoring shield item %s because char is a slave.", item)
                    continue

            picks.append(item)

        return picks

    def can_transfer(source, target, item, amount=1, silent=False, force=False):
        """Checks if it is legal for a character to transfer the item.

        @param: silent: If False, game will notify the player with a reason why an item cannot be equipped.
        @param: force: Option to forcibly take an item from a character.
        """
        if item.unique and (not isinstance(target, Building)) and item.unique != ("mc" if target == hero else target.id):
            if not silent:
                PyTGFX.message("This unique item cannot be given to %s!" % target.name)
            return
        if not item.transferable:
            if not silent:
                PyTGFX.message("This item cannot be transferred!")
            return

        # Free girls should always refuse giving up their items unless MC gave it to them:
        # (Unless action is forced):
        if not force:
            if all([isinstance(source, Char), source.status != "slave", not(item.price <= iam.hero_influence(source)*10*(source.tier + 1) and check_lovers(source))]):
                if source.given_items.get(item.id, 0) < amount:
                    if not silent:
                        iam.items_deny_access(source)
                    return

        return True

    def equipment_access(character, item, silent=False, unequip=False):
        # Here we determine if a character would be willing to give MC access to her equipment:
        # Like if MC asked this character to equip or unequip an item.
        # We return True if access is granted!
        #
        # with unequip=False (default) check whether we are allowed to equip the item,
        # with unequip=True, check whether we are allowed to *un*equip
        if character == hero:
            return True # Would be weird if we could not access MCs inventory....

        # Always the same here as well...
        if character.status == "slave":
            return True

        # Refuse based on disposition: # TODO use the hero_influence function? It would kill the gameplay at the moment...
        dispo_max = character.get_max("disposition")
        char_dispo = character.get_stat("disposition")
        hero_influence = get_linear_value_of(char_dispo, dispo_max*.4, .0, dispo_max, 100.0)
        if "Drunk" in character.effects:
            hero_influence *= 1.1

        if unequip:
            if not item.badtraits.isdisjoint(character.traits):
                return True

            diff = hero_influence - item.eqchance
            if diff >= 0: # allow unequip of items with eqchance 100 under 'complete' influence
                return True

            if item.eqchance > 70:
                if not silent:
                    iam.items_deny_good_item(character)
                return False
        else:
            # check the current equipped item
            slot = item.slot
            if slot == "ring":
                # if the last ring-slot is empty, we are free to proceed
                current_item = character.eqslots["ring2"]
                if current_item:
                    # otherwise we are going to try to replace the first one
                    current_item = character.eqslots["ring"]
            elif slot != "consumable":
                current_item = character.eqslots[slot]
            else:
                current_item = None
            if current_item and not equipment_access(character, current_item, silent=silent, unequip=True):
                return False

            # Bad Traits:
            if not item.badtraits.isdisjoint(character.traits):
                if not silent:
                    iam.items_deny_bad_item(character)
                return False

            # Good traits:
            if not item.goodtraits.isdisjoint(character.traits):
                return True

            if item.type == "alcohol" and "Depression" in character.effects: # green light for booze in case of suitable effects
                hero_influence *= 1.2

            diff = hero_influence - (100 - item.eqchance)
            if diff > 0: # items with eqchance 0 should not be equipped in normal circumstances 
                return True

            if item.eqchance < 30:
                if not silent:
                    iam.items_deny_bad_item(character)
                return False

        if not silent:
            if diff < -20:
                iam.items_deny_equip_bad(character)
            else:
                iam.items_deny_equip_neutral(character)
        return False

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
