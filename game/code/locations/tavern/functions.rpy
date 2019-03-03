init python:
    def throw_a_normal_dice(): # throwing a classic dice
        i = locked_random("randint", 1, 6)
        return i

    def dice_poker_calculate(dice_list): # check combinations for dice poker and calculate relative scores based on them
        counter = collections.Counter(dice_list)
        if len(counter) == 1:
            return ["Five-of-a-Kind", 8] # all dices are the same
        elif len(counter) == 2: # two groups of the same number
            if 4 in counter.values():
                return ["Four-of-a-Kind", 7] # 4 of 5 are equal
            else:
                return ["Full House", 6] # pair of one value and Three-of-a-Kind of another
        elif len(counter) == 3:
            if 3 in counter.values(): # three dice showing the same value
                return ["Three-of-a-Kind", 3]
            else:
                return ["Two Pairs", 2] # two pairs of dice showing the same value
        elif len(counter) == 4: # one pair
            return ["One Pair", 1]
        else:
            checking_list = [2, 3, 4, 5, 6]
            result = list(i for i in dice_list if i in checking_list)
            if len(result) == 5:
                return ["Six High Straight", 5] # dice showing values from 2 through 6, inclusive
            else:
                checking_list = [1, 2, 3, 4, 5]
                result = list(i for i in dice_list if i in checking_list)
                if len(result) == 5:
                    return ["Five High Straight", 4] # dice showing values from 1 through 5, inclusive
        return ["Nothing", 0] # all checks failed, no combinations

    def check_if_should_throw_dice(own_dice, other_dice, other_passed): # check how close an enemy to the victory, and based on it either throw (true) or don't (false) dice
        if own_dice >= 21 or other_dice > 21:
            return False
        elif other_passed:
            if own_dice > other_dice:
                return False
            elif own_dice == other_dice:
                if dice((21-own_dice)*10):
                    return True
                else:
                    return False
            else:
                return True
        elif (21-own_dice) >= 6:
            return True
        elif other_dice == 21 and own_dice < 21:
            return True
        else:
            if dice((21-own_dice)*10):
                return True
            else:
                return False

    def dice_poker_ai_decision(dice_1, dice_2): # handles ai logic in poker
        counter = collections.Counter(dice_1)

        if len(counter) == 1: # Five-of-a-Kind
        # if ai wins, no throws are needed; if ai loses, nothing can be done anyway since you need at least 5 throws to get a better hand
            return 0

        if len(counter) == 2: # two groups of the same number
            if 4 in counter.values(): # Four-of-a-Kind; at this point it won't hurt to try getting Five-of-a-Kind
                result_1 = list(k for k, v in counter.iteritems() if v == 1) # we find the single left dice value
                result = dice_1.index(result_1[0]) + 1 # and return its index
                return result
            else: # Full House
                if dice_poker_decide_winner(dice_1, dice_2) in [1, 0]: # ai already has good hand
                    return 0
                else: # if not then it throws the lesser dice in hopes to get a good Four-of-a-Kind
                    i = min(counter.keys())
                    result = dice_1.index(i) + 1
                    return result

        # here we check Straights, since they are more important than combinations below
        checking_list = [2, 3, 4, 5, 6]
        result = result_1 = []
        for i in dice_1:
            if i in checking_list and not (i in result):
                result.append(i)
        if len(result) == 5: # Six High Straight; at this point it's guaranteed win or lose, since Full House will need 4 throws at least
            return 0

        checking_list = [1, 2, 3, 4, 5]
        result = result_1 = []
        for i in dice_1:
            if i in checking_list and not (i in result):
                result.append(i)
        if len(result) == 5: # Five High Straight
            if dice_poker_decide_winner(dice_1, dice_2) in [1, 0]: # ai already has good hand
                return 0
            else: # if not than going for Six High Straight is the only chance, which means turning 1 to 6 ie throwing the lesser dice
                i = min(counter.keys())
                result = dice_1.index(i) + 1
                return result

        # if we are here, it means no Straights exist, but now we should check if just one throw can change it

        checking_list = [2, 3, 4, 5, 6]
        result = result_1 = []
        for i in dice_1:
            if i in checking_list and not (i in result):
                result.append(i)
        if len(result) == 4: # no pairs and one wrong dice for High Straight, like [1, 3, 4, 5, 6]; we should throw the wrong one ie 1
            for i in dice_1:
                if i in checking_list:
                    result_1.append(i)
                    checking_list.remove(i)
            result = dice_1.index(result_1[0]) + 1
            return result

        checking_list = [1, 2, 3, 4, 5]
        result = result_1 = []
        for i in dice_1:
            if i in checking_list and not (i in result):
                result.append(i)
        if len(result) == 4:
            for i in dice_1:
                if i in checking_list:
                    result_1.append(i)
                    checking_list.remove(i)
            result = dice_1.index(result_1[0]) + 1
            return result

        # if we are here, no Straights are available, so we continue with other combinations

        if len(counter) == 3:  # either Three-of-a-Kind or Two Pairs, it doesn't matter for ai, it just throws a single dice
            result_1 = list(k for k, v in counter.iteritems() if v == 1)
            random.shuffle(result_1)
            result = dice_1.index(result_1[0]) + 1
            return result

        if len(counter) == 4: # one pair; we already checked for High Straight combinations, so it only can be improved by making it Three-of-a-Kind
            result_1 = list(k for k, v in counter.iteritems() if v == 1)
            random.shuffle(result_1)
            result = dice_1.index(result_1[0]) + 1
            return result


        # if we are here, there is no combinations at all; so ai just throws a dice with min value
        result_1 = min(dice_1)
        result = dice_1.index(result_1[0]) + 1
        return result

    def dice_poker_decide_winner(dice_1, dice_2): # returns 1 if dice_1 is winner, 2 if dice_2 is winner, 0 if it's a draw
        score_1 = dice_poker_calculate(dice_1)[1]
        score_2 = dice_poker_calculate(dice_2)[1]
        if score_1 > score_2:
            return 1
        elif score_2 > score_1:
            return 2
        else: # if dice combinations give the same scores, we look at dices numbers themselves; the highest one wins
            if sum(dice_1) > sum(dice_2):
                return 1
            elif sum(dice_2) > sum(dice_1):
                return 2
            else: return 0

