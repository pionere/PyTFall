# Library of functions
init -11 python:
    def set_font_color(s, color):
        """
        @param: color: should be supplied as a string! Not as a variable!
        Sets font color during interpolation.
        """
        return "".join(["{color=%s}" % color, str(s), "{/color}"])

    def add_dicts(*dicts):
        """Does what I originally expected dict.update method to do many years ago...
        This works with dicts where all values are numbers.
        """
        if isinstance(dicts[0], (list, tuple, set)):
            dicts = dicts[0]

        new = {}
        for d in dicts:
            for key, value in d.iteritems():
                new[key] = new.get(key, 0) + value
        return new

    def merge_dicts(target_dict, other_dict):
        """Adds (number) values of the other dict to the target dict.
        This is the same as add_dicts, but does not create a new dict.
        """
        for key, value in other_dict.iteritems():
            target_dict[key] = target_dict.get(key, 0) + value

    def gold_text(money):
        if money >= 10**12:
            return str(round(float(money)/10**12, 2)) + "T"
        elif money >= 10**9:
            return str(round(float(money)/10**9, 2)) + "B"
        elif money >= 10**6:
            return str(round(float(money)/10**6, 2)) + "M"
        else:
            return str(int(money))

    def get_mean(numbers):
        return float(sum(numbers)) / max(len(numbers), 1)

    def get_linear_value_of(x, x1, y1, x2, y2):
        '''
        Return the y value at x, given a linear function by two points with coordinates
        '''
        dx = (y2-y1)/float(x2-x1)
        return y1 + (x - x1)*dx

    def round_int(value):
        return int(round(value))

    def roman_num(value):
        roman = OrderedDict([(1000, "M"),
                             (900, "CM"),
                             (500, "D"),
                             (400, "CD"),
                             (100, "C"),
                             (90, "XC"),
                             (50, "L"),
                             (40, "XL"),
                             (10, "X"),
                             (9, "IX"),
                             (5, "V"),
                             (4, "IV"),
                             (1, "I")])
        result = []
        for r, v in roman.iteritems():
            n = value / r
            if n != 0:
                result.extend(v*n)
                value -= n * r
                if value <= 0:
                    break
        return "".join(result)

    # ---------------------- Game related:
    # Assists:
    # Function are not named according to PEP8 because we'll be using the living shit out of them in the game:
    def weighted_choice(choices):
        """
        Select a single element from the choices.
        :param choices: the weighted list of choices
        :returns: the selected element
        """
        values, weights = zip(*choices)
        total = 0
        cum_weights = []
        for w in weights:
            total += w
            cum_weights.append(total)
        if total <= 0:
            return None

        x = random.random() * total
        x = bisect.bisect(cum_weights, x)
        return values[x]

    def weighted_sample(choices, amount):
        """
        Select amount number of unique elements from the choices.
        :param choices: the weighted list of choices
        :param amount: the number of elements to select. Must be lower or equal than the number of the choices.
        :returns: the list of selected elements
        """
        if amount == 0:
            return []
        total = sum(c[1] for c in choices)
        result = [None] * amount
        bkp = [None] * amount
        for i in xrange(amount):
            x = random.random() * total
            for c in choices:
                v = c[1]
                x -= v
                if x < 0:
                    result[i] = c
                    bkp[i] = v
                    total -= v
                    c[1] = 0
                    break
        # restore choices
        for c, v in zip(result, bkp):
            c[1] = v
        return [c[0] for c in result]

        """        
        values = []
        cum_weights = []
        total = 0
        for v, w in choices:
            values.append(v)
            total += w
            cum_weights.append(total)
        if total <= 0:
            return None
        result = [None] * amount
        while 1:
            x = random.random() * total
            x = bisect.bisect(cum_weights, x)
            amount -= 1
            result[amount] = values[x]
            if amount == 0:
                break
            d = cum_weights[x]
            if x != 0:
                d -= cum_weights[x-1]
            total -= d
            del cum_weights[x]
            del values[x]
            for i, v in enumerate(cum_weights):
                if i >= x:
                    cum_weights[i] -= d

        return result
        """

    def weighted_list(choices, amount):
        """
        Select amount number of non-unique elements from the choices.
        :param choices: the weighted list of choices
        :param amount: the number of elements to select
        :returns: the list of selected elements
        """
        if amount == 0:
            return []
        values, weights = zip(*choices)
        total = 0
        cum_weights = []
        for w in weights:
            total += w
            cum_weights.append(total)
        if total <= 0:
            return []
        result = [None] * amount
        for i in xrange(amount):
            x = random.random() * total
            x = bisect.bisect(cum_weights, x)
            result[i] = values[x]
        return result

    def plural(string, amount):
        """
        Returns the string as a plural if amount isn't above 1.
        string = The word to pluralise.
        amount = The amount of the 'word' as either a number or a string.
        """
        if isinstance(amount, basestring):
            try:
                if int(amount) == 1: return string
                elif string[-1:] == "x" or string[-2:] in ("ch", "sh", "ss"): return string + "es"
                else: return string + "s"

            except:
                # No valid number
                return string

        else:
            if amount == 1: return string
            elif string[-1:] == "x" or string[-2:] in ("ch", "sh", "ss"): return string + "es"
            else: return string + "s"

    def alpha(string, amount, limit=10):
        result = plural(string, amount)
        if amount <= limit and amount <= 10:
            nums = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
            amount = nums[amount]
        else:
            amount = str(amount)
        return " ".join((amount, result))

    def aoran(string, *overrides):
        """
        Returns "a" or "an" depending on if string begins with a vowel.
        string = The word to base the "a" or "an" on.
        overrides = A list of words to return "an" for, overriding the default logic.
        """
        s = string.lower()
        if s[:1] in ("a", "e", "i", "o", "u"):
            return "an " + string

        if overrides is not None:
            for i in overrides:
                if s.startswith(i): return "an " + string

        return "a " + string

    def hs():
        # Hides the current renpy screen.
        scr = renpy.current_screen()
        if scr is not None:
            renpy.hide_screen(scr.tag)
        else:
            renpy.scene("screens")
