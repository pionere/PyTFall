init -2 python:
    # Interactions (Girlsmeets decisions):
    class InteractionsDecisions(_object):
        @staticmethod
        def become_lovers(character):
            l_ch = 600 + check_submissivity(character) * 50

            char_traits = character.traits
            if "Shy" in char_traits:
                l_ch += 20
            if "Virgin" in char_traits:
                l_ch += 40
            elif "MILF" in char_traits:
                l_ch -= 40
            if "Nymphomaniac" in char_traits:
                l_ch -= 50
            if "Frigid" in char_traits:
                l_ch += 50

            return character.get_stat("affection") > l_ch

        @staticmethod
        def want_hug(character):
            if iam.slave_siw_check(character):
                return True

            l_ch = check_submissivity(character) * 50
            if "SIW" not in character.gen_occs:
                l_ch += 200

            diff = l_ch - character.get_stat("affection")
            if diff < 0:
                return True
            if diff > 50:
                return "blowoff"
            return False

        @staticmethod
        def want_buttgrab(character):
            if iam.slave_siw_check(character):
                return True

            l_ch = 50 + (check_submissivity(character) * 50)
            if "SIW" not in character.gen_occs:
                l_ch += 200

            diff = l_ch - character.get_stat("affection")
            if diff < 0:
                return True
            if diff > 50:
                return "blowoff"
            return False

        @staticmethod
        def want_breastgrab(character):
            if iam.slave_siw_check(character):
                return True

            l_ch = 100 + (check_submissivity(character) * 50)
            if "SIW" not in character.gen_occs:
                l_ch += 200

            diff = l_ch - character.get_stat("affection")
            if diff < 0:
                return True
            if diff > 50:
                return "blowoff"
            return False

        @staticmethod
        def want_kiss(character):
            if iam.slave_siw_check(character):
                return True

            l_ch = 100 + (check_submissivity(character) * 50)
            if "SIW" not in character.gen_occs:
                l_ch += 250

            diff = l_ch - character.get_stat("affection")
            if diff < 0:
                return True
            if diff > 50:
                return "blowoff"
            return False

        @staticmethod
        def want_sex(character):
            sub = check_submissivity(character)
            if check_lovers(character): # a clear way to calculate how much disposition is needed to make her agree
                l_ch = randint(0, 100) + sub*200 # probably a placeholder until it becomes more difficult to keep lover status
            else:
                l_ch = randint(600, 700) + sub*100 # thus weak willed characters will need from 500 to 600 disposition, strong willed ones from 700 to 800, if there are no other traits that change it

            if 'Horny' in character.effects:
                l_ch -= randint(200, 300)

            if character.status == "slave":
                l_ch -= 500
                if "SIW" in character.gen_occs:
                    l_ch -= 500
            else:
                if "SIW" in character.gen_occs:
                    if character.get_stat("disposition") >= 400:
                        l_ch -= randint(50, 100)
                    else:
                        l_ch += randint(50, 100)

            if character.flag("quest_sex_anytime"): # special flag for cases when we don't want character to refuse unless disposition is ridiculously low
                l_ch -= 1000

            if character.has_flag("flag_int_had_sex_with_mc"):
                l_ch -= 50 + character.flag("flag_int_had_sex_with_mc")*10 # the more char does it with MC, the less needed disposition is, despite everything else

            # so normal (without flag) required level of disposition could be from 200 to 1200 for non lovers
            if "Open Minded" in character.traits: # open minded trait greatly reduces the needed disposition level
                l_ch -= randint(400, 500)
            if l_ch < -500:
                l_ch = -500 # normalization, no free sex with too low disposition no matter the character

            diff = l_ch - character.get_stat("affection")
            if diff < 0:
                return True
            if diff > 100:
                return "blowoff"
            return False
