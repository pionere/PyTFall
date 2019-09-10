init -2 python:
    # Interactions (Girlsmeets decisions):
    class InteractionsDecisions(_object):
        @staticmethod
        def become_lovers(char):
            l_ch = 600 - check_submissivity(char) * 50

            char_traits = char.traits
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

            return l_ch < char.get_stat("affection") 

        @staticmethod
        def would_invite(expense):
            members = [] # all chars willing to invite will be in this list
            for member in hero.team:
                if member != hero:
                    if member.status == "free" and member.gold >= expense and (member.get_stat("disposition") >= 200 or member.get_stat("affection") >= 200) and member.get_stat("joy") >= 30:
                        # the chance for a member of MC team to invite team
                        if "Imouto" in member.traits:
                            chance = 60
                        elif "Kamidere" in member.traits:
                            chance = 55
                        elif "Yandere" in member.traits:
                            chance = 50
                        elif "Ane" in member.traits:
                            chance = 45
                        elif "Bokukko" in member.traits:
                            chance = 40
                        elif "Tsundere" in member.traits:
                            chance = 30
                        elif "Kuudere" in member.traits:
                            chance = 20
                        elif "Dandere" in member.traits:
                            chance = 10
                        elif "Impersonal" in member.traits:
                            chance = 5
                        else:
                            chance = 35
                        if dice(chance):
                            members.append(member)
            if members:
                return random.choice(members)
            return None

        @staticmethod
        def want_ice(char):
            if "Down with Cold" in char.effects:
                return False
            if char.status != "free":
                return True
            l_ch = 50 - check_submissivity(char) * 50

            return l_ch < char.get_stat("disposition")

        @staticmethod
        def want_cafe(char):
            if char.status != "free":
                return True
            l_ch = 50 - check_submissivity(char) * 50

            return l_ch < char.get_stat("disposition")

        @staticmethod
        def want_shopping(char):
            if char.status != "free":
                return True
            l_ch = 100 - check_submissivity(char) * 50

            return l_ch < char.get_stat("disposition")

        @staticmethod
        def want_eat(char):
            if char.status != "free":
                return True
            l_ch = 150 - check_submissivity(char) * 50

            return l_ch < char.get_stat("disposition")

        @staticmethod
        def want_study(char, topic):
            if char.status != "free":
                return True
            if "Adventurous" in char.traits or "Aggressive" in char.traits:
                return False
            if not char.has_ap():
                return False

            sub = check_submissivity(char)
            if topic == "sex":
                l_ch = 50 - sub * 50
                if "SIW" not in char.gen_occs:
                    l_ch += 100

                if l_ch >= char.get_stat("affection"):
                    return False

            l_ch = 50 - sub * 25
            l_ch += 250 * (char.tier - hero.tier)

            return l_ch < char.get_stat("disposition")

        @staticmethod
        def want_gift(char, n):
            """
            Decide whether the character wants to accept the Nth gifts from the hero
            """
            l_ch = 3 + check_submissivity(char)
            if check_lovers(char):
                l_ch += 1
            if dice(char.get_stat("affection")/20) or dice(char.get_stat("disposition")/40):
                l_ch += 1

            return l_ch >= n

        @staticmethod
        def want_hug(character):
            if iam.slave_siw_check(character):
                return True

            l_ch = - check_submissivity(character) * 50
            if "SIW" not in character.gen_occs:
                l_ch += 200

            diff = l_ch - character.get_stat("affection")
            if diff < 0:
                return True
            if diff > 50:
                return "blowoff"
            return False

        @staticmethod
        def want_cheektouch(character):
            if iam.slave_siw_check(character):
                return True

            l_ch = 100 - (check_submissivity(character) * 50)
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

            l_ch = 50 - (check_submissivity(character) * 50)
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

            l_ch = 100 - (check_submissivity(character) * 50)
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

            l_ch = 100 - (check_submissivity(character) * 50)
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
                l_ch = randint(0, 100) - sub*200 # probably a placeholder until it becomes more difficult to keep lover status
            else:
                l_ch = randint(600, 700) - sub*100 # thus weak willed characters will need from 500 to 600 disposition, strong willed ones from 700 to 800, if there are no other traits that change it

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
