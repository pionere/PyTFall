init -10 python:
    def convert_ap_to_jp(char):
        # Do not convert AP when Char is in school.
        char.PP += char.AP*100 # += is safer here. PP_PER_AP
        char.AP = 0

    def payout(job, effectiveness, difficulty, building, business, worker, clients, log):
        """
        Calculates payout for jobs based of effectiveness and other modifications.
        Writes to log accordingly.
        """
        earned = pytfall.economy.get_clients_pay(job, difficulty)

        is_plural = False
        if isinstance(clients, (set, list, tuple)):
            if len(clients) > 1:
                is_plural = True
                client_name = "clients"
                earned *= len(clients) # Make sure we adjust the payout to the actual number of clients served.
            else:
                client_name = "client"
        else:
            client_name = clients.name

        me = building.manager_effectiveness
        if effectiveness <= 33: # Worker sucked so much, client just doesn't pay.
            if is_plural:
                temp = "Clients leave the {} refusing to pay for the inadequate service {} provided.".format(
                                business.name, worker.name)
            else:
                temp = "{} leaves the {} refusing to pay for the inadequate service {} provided.".format(
                                set_font_color(client_name.capitalize(), "beige"), business.name, worker.name)
            log.append(temp)
            earned = 0
        elif effectiveness <= 90: # Worker sucked but situation may be salvageable by Manager.
            if is_plural:
                temp = "Due to inadequate service provided by {} clients refuse to pay the full price.".format(worker.name)
            else:
                temp = "Due to inadequate service provided by {} client refuses to pay the full price.".format(worker.name)
            log.append(temp)
            if me >= 90 and building.help_ineffective_workers and building._dnd_manager.PP >= 1:
                manager = building._dnd_manager
                temp = "Your skilled manager {} intervened and straitened things out.".format(manager.name)
                manager._dnd_mlog.append("{} helped to calm a client down after {}'s poor performance and salvaged part of the payment!".format(
                                                    manager.name, worker.name))
                manager.PP -= 1

                if me >= 150 and dice(85):
                    if is_plural:
                        temp += " Clients were so pleased for the attention and ended up paying full price."
                    else:
                        temp += " Client was so pleased for the attention and ended up paying full price."
                elif dice(75):
                    if is_plural:
                        temp += " Clients agree to pay three quarters of the price."
                    else:
                        temp += " Client agreed to pay three quarters of the price."
                    earned *= .75
                else:
                    earned *= .6
                    temp += " You will get 60%..."
                log.append(temp)
            else:
                earned *= .5
                temp = " You will get half..."
                log.append(temp)
        elif effectiveness <= 150:
            if is_plural:
                temp = "Clients are very happy with {} service and pay the full price.".format(worker.name)
            else:
                temp = "Client is very happy with {} service and pays the full price.".format(worker.name)
            log.append(temp)
        else:
            if is_plural:
                temp = "Clients are ecstatic! {} service was beyond any expectations. +20% to payout!".format(worker.name)
            else:
                temp = "Client is ecstatic! {} service was beyond any expectations. +20% to payout!".format(worker.name)
            log.append(temp)
            earned *= 1.2

        # Passive manager effect:
        if me >= 120 and dice(50):
            temp = "Manager paid some extra attention to the %s. +20%% to payout!" % plural("client", is_plural)
            log.append(temp)
            earned *= 1.2

        earned = round_int(earned)
        if earned:
            # uncomment these if there is a possibility to log multiple shifts in one NDEvent 
            #temp = "You've earned {} Gold!".format(earned)
            #log.append(temp)
            log.earned += earned

        return earned

    def nd_report_image(bg_img, workers, *show_args, **show_kwargs):
        """This will create a sidescrolling displayable to show off all portraits/images in team efforts if they don't fit on the screen in a straight line.

        We will attempt to detect a size of a single image and act accordingly. Spacing is 15 pixels between the images.
        Dimensions of the whole displayable are: 820x705, default image size is 90x90.
        xmax is used to determine the max size of the viewport/fixed returned from here
        """
        # See if we can get a required image size:
        img = [bg_img]
        for w in workers:
            img.append(w.show(*show_args, **show_kwargs))

        return img

        #size = (150, 150)
        #show_kwargs["resize"] = size
        #xpos_offset = size[0] + 15
        #xsize = xpos_offset * lenw
        #ysize = size[1]

        #if xsize < xmax:
        #    vp = Fixed(xysize=(xsize, ysize))
        #    xpos = 0
        #    for i in workers:
        #        _ = i.show(*show_args, **show_kwargs)
        #        vp.add(Transform(_, xpos=xpos))
        #        xpos += xpos_offset
        #else:
        #    d = Fixed(xysize=(xsize, ysize))
        #    xpos = 0
        #    for i in workers:
        #        _ = i.show(*show_args, **show_kwargs)
        #        d.add(Transform(_, xpos=xpos))
        #        xpos += xpos_offset

        #    c = Fixed(xysize=(xsize*2, ysize))
        #    atd = At(d, mm_clouds(xsize, 0, 25))
        #    atd2 = At(d, mm_clouds(0, -xsize, 25))
        #    c.add(atd)
        #    c.add(atd2)
        #    vp = Viewport(child=c, xysize=(xmax, ysize))
        #img.add(Transform(vp, align=(.5, .9)))
        #return img

    def can_do_work(c, check_ap=True, log=None):
        """Checks whether the character is injured/tired/has AP and sets her/him to auto rest.

        AP check is optional and if True, also checks for action points.
        """
        # We do not want girls in school to AutoRest,
        # Idea is that the school is taking care of this.
        if c.action.__class__ in [StudyingJob, ExplorationJob]:
            return True

        if c.get_stat("health") < c.get_max("health")/4:
            if log:
                log.append("%s is injured and in need of medical attention! "%c.name)
            # self.img = c.show("profile", "sad", resize=(740, 685))
            if c.autocontrol['Rest'] and c.action.__class__ not in [Rest, AutoRest]:
                c.set_task(simple_jobs["AutoRest"])
                if log:
                    log.append("And going to take few days off to heal. ")
            return False
        if c.get_stat("vitality") <= c.get_max("vitality")/5:
            if log:
                log.append("%s is too tired! "%c.name)
            # self.img = c.show("profile", "sad", resize=(740, 685))
            if c.autocontrol['Rest'] and c.action.__class__ not in [Rest, AutoRest]:
                c.set_task(simple_jobs["AutoRest"])
                if log:
                    log.append("And going to take few days off to recover. ")
            return False
        if "Exhausted" in c.effects:
            if log:
                log.append("%s is exhausted! " % c.name)
            # self.img = c.show("profile", "sad", resize=(740, 685))
            if c.autocontrol['Rest'] and c.action.__class__ not in [Rest, AutoRest]:
                c.set_task(simple_jobs["AutoRest"])
                if log:
                    log.append("And needs a day to recover. ")
            return False
        if 'Food Poisoning' in c.effects:
            if log:
                log.append("%s is suffering from Food Poisoning! "%c.name)
            # self.img = c.show("profile", "sad", resize=(740, 685))
            if c.autocontrol['Rest'] and c.action.__class__ not in [Rest, AutoRest]:
                c.set_task(simple_jobs["AutoRest"])
                if log:
                    log.append("And going to take few days off to recover. ")
        if check_ap:
            if c.AP <= 0 and c.PP <= 0:
                return False

        return True

    def slave_siw_check(c): # slaves-SIWs allow more than other characters
        if c.status == "slave" and ("SIW" in c.gen_occs) and c.get_stat("disposition") >= -150:
            return True
        else:
            return False

    def check_submissivity(c):
        """Here we determine how submissive the character is, thus if she's willing to do something she doesn't want to, or for example take the initiative in certain cases.
        """
        mult = c.get_max("character")
        if mult == 0:
            return -1 # should never happen, but better than a div-zero in a simpy process...

        # the idea is based on the character stat, we check how close is she to max possible character at her level
        mult = c.get_stat("character")/float(mult)
        # and traits, they can make mult more or less
        # for example even low character tsundere might be more stubborn than high character dandere
        traits = ["Impersonal", "Imouto", "Dandere", "Tsundere", "Kamidere", "Bokukko", "Ane",
                  "Yandere", "Courageous", "Coward", "Shy", "Aggressive", "Natural Leader", "Natural Follower"]
        traits = list(i.id for i in c.traits if i.id in traits)

        for i in traits:
            if i == "Impersonal":
                mult -= .1
            elif i == "Imouto":
                mult -= .05
            elif i == "Dandere":
                mult -= .15
            elif i == "Tsundere":
                mult += .2
            elif i == "Kuudere":
                mult += .15
            elif i == "Kamidere":
                mult += .23
            elif i == "Bokukko":
                mult += .2
            elif i == "Ane":
                mult += .05
            elif i == "Yandere":
                # in case of yandere disposition is everything
                if c.get_stat("disposition") <= 500:
                    mult += .25
                else:
                    mult -= .25
            elif i == "Courageous":
                mult += .05
            elif i == "Coward":
                mult -= .05
            elif i == "Shy":
                mult -= .05
            elif i == "Aggressive":
                mult += .05
            elif i == "Natural Leader":
                mult += .05
            elif i == "Natural Follower":
                mult -= .05

        if c.status == "slave":
            mult -= .1

        if mult < .35: # there are 3 levels of submissiveness, we return -1, 0 or 1, it's very simple to use in further calculations
            return -1
        elif mult > .67:
            return 1
        else:
            return 0
