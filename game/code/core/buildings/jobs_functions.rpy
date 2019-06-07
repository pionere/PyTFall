init -10 python:
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
            client_name_c = client_name.capitalize()
        else:
            client_name = client_name_c = set_font_color(clients.name, "beige")
        worker_name = worker.name

        me = building.manager_effectiveness
        if effectiveness <= 33: # Worker sucked so much, client just doesn't pay.
            temp = "are" if is_plural else "is"
            temp = "%s %s leaving without paying for the inadequate service %s provided." % (client_name_c, temp, worker_name)
            log.append(temp)
            earned = 0
        elif effectiveness <= 90: # Worker sucked but situation may be salvageable by Manager.
            temp = "refuse" if is_plural else "refuses"
            temp = "Due to inadequate service provided by %s, %s %s to pay the full price." % (worker_name, client_name, temp)
            log.append(temp)
            if me >= 90 and building.help_ineffective_workers and building._dnd_manager.PP >= 1:
                manager = building._dnd_manager
                temp = "%s helped to calm a client down after %s's poor performance and salvaged part of the payment!" % (manager.name, worker_name)
                manager._dnd_mlog.append(temp)
                temp = "Your skilled manager %s intervened and straitened things out." % manager.name
                manager.PP -= 1

                if me >= 150 and dice(85):
                    tmp = "were" if is_plural else "was"
                    temp += " %s %s pleased for the attention and ended up paying the full price." % (client_name_c, tmp)
                elif dice(75):
                    temp += " %s agreed to pay three quarters of the price." % client_name_c
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
            temp = ("are", "pay") if is_plural else ("is", "pays")
            temp = "%s %s very happy with %s's service and %s the full price." % (client_name_c, temp[0], worker_name, temp[1])
            log.append(temp)
        else:
            temp = "are" if is_plural else "is"
            temp = "%s %s ecstatic! %s's service was beyond any expectations. +20%% to payout!" % (client_name_c, temp, worker_name)
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
        for i in c.traits:
            i = i.id
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
