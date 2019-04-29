init python:
    class SchoolCourse(_object):
        def __init__(self, name, difficulty, duration, days_to_complete,
                     effectiveness, data):
            self.name = name
            # self.trainer = trainer # restore after ST.
            self.difficulty = difficulty
            self.students = []
            self.students_progress = {}
            self.completed = set() # Students that completed this course
            self.duration = self.days_remaining = duration
            self.days_to_complete = days_to_complete # 25 or about 80% of duration is normal.
            self.effectiveness = effectiveness

            self.data = data

            self.set_image()
            self.set_price()

        def __repr__(self):
            return str(self.name + " Course")

        def set_price(self):
            price = get_average_wage()
            price = price + price*self.difficulty
            self.price = round_int(price)

        def set_image(self):
            images = []
            folder = os.path.join("content", "schools", self.data["image"])
            path = os.path.join(gamedir, folder)
            if os.path.isdir(path):
                for fn in os.listdir(path):
                    if fn.endswith(IMAGE_EXTENSIONS):
                        images.append(os.path.join(folder, fn)) 

            img = choice(images) if images else IMG_NOT_FOUND_PATH
            self.img = renpy.displayable(img)

        def get_status(self, char):
            if char in self.students:
                return "Active!"

            days_to_complete = self.days_to_complete
            duration = self.duration

            if days_to_complete < duration*.65:
                dtc = " and Fast"
            elif days_to_complete < duration*.75:
                dtc = ""
            else:
                dtc = " and Slow"

            if self.difficulty >= char.tier+2:
                temp = "Great"
            elif self.difficulty >= char.tier:
                temp = "Good"
            else:
                temp = "Bad"

            return temp + dtc

        @property
        def tooltip(self):
            tt = self.data.get("desc", "No Description Available")

            if self.students:
                tt += "\nStudents: %s" % (", ".join([s.nickname for s in self.students]))

            return tt

        def add_student(self, student):
            self.students.append(student)
            if student not in self.students_progress:
                self.students_progress[student] = 0

        def remove_student(self, student):
            self.students.remove(student)

        def next_day(self):
            self.days_remaining -= 1

            school = pytfall.school

            if len(self.students) >= 3 and dice(25):
                best_student = choice(self.students)
            else:
                best_student = None

            for char in self.students[:]:
                txt = [] # Append all events we want to relay to the player.
                flag_green = False
                charmod = None

                temp = "%s is taking a %s Course!" % (char.fullname, self.name)
                txt.append(temp)

                # Pay for the class:
                if hero.take_money(self.price, reason="-PyTFall Educators-"):
                    char.fin.log_logical_expense(self.price, "-PyTFall Educators-")
                    temp = "You've covered a fee of {color=gold}%s Gold{/color}!" % self.price
                    txt.append(temp)
                else:
                    char.set_task(None)
                    temp = "\nYou failed to cover the fee of {color=gold}%d Gold{/color}!" % self.price
                    temp += " The student has been kicked from the class!"
                    txt.append(temp)

                    self.build_nd_report(char, type="failed_to_pay", txt=txt)
                    continue

                ap_spent = char.PP/100 # PP_PER_AP
                if ap_spent != 0:
                    self.students_progress[char] += 1
                    completed = self.days_to_complete == self.students_progress[char]
                    char.take_ap(ap_spent)
                    school.students_attended += 1

                    primary_stats = []
                    secondary_stats = []

                    primary_skills = []
                    secondary_skills = []

                    for s in self.data["primary"]:
                        if is_stat(s):
                            if char.stats.stats[s] < char.get_max(s):
                                primary_stats.append(s)
                        elif is_skill(s):
                            primary_skills.append(s)
                        else:
                            raise Exception("%s is not a valid stat/skill for %s course." % (s, self.name))

                    for s in self.data["secondary"]:
                        if is_stat(s):
                            if char.stats.stats[s] < char.get_max(s):
                                secondary_stats.append(s)
                        elif is_skill(s):
                            secondary_skills.append(s)
                        else:
                            raise Exception("%s is not a valid stat/skill for %s course." % (s, self.name))

                    stats = primary_stats*3 + secondary_stats
                    skills = primary_skills*3 + secondary_skills

                    # Add stats/skills/exp mods.
                    exp_mod = 1.0
                    points = max(1, self.difficulty-char.tier)
                    if char == best_student:
                        temp = "%s has been a perfect student today and went every extra mile %s could." % (char.name, char.p)
                        temp += " {color=lawngreen}+50% Stats/Skills/EXP Bonus!{/color}"
                        flag_green = True
                        txt.append(temp)
                        points *= 1.5
                        exp_mod = 1.5

                    if char in self.completed:
                        points *= .8
                        exp_mod *= .8
                        temp = "%s has already finished this course!" % char.nickname
                        temp += " {color=red}-20% Stats/Skills/EXP Bonus!{/color}"
                        txt.append(temp)
                    elif completed:
                        school.successfully_completed += 1
                        self.completed.add(char)
                        points *= 2
                        exp_mod *= 2
                        temp = "%s has completed the course today!" % char.nickname
                        temp += " {color=lawngreen}+100% Stats/Skills/EXP Bonus!{/color}"
                        flag_green = True
                        txt.append(temp)

                    # Effectiveness mod (simple)
                    effectiveness = self.effectiveness/100.0
                    points *= effectiveness

                    stats_pool = round_int(points*ap_spent)
                    skills_pool = 2*stats_pool

                    exp = exp_reward(char, self.difficulty, exp_mod=ap_spent*exp_mod)
                    char.mod_exp(exp)

                    charmod = defaultdict(int) # Dict of changes of stats and skills for ND
                    charmod["exp"] = exp
                    if stats:
                        for i in xrange(stats_pool):
                            stat = choice(stats)
                            char.mod_stat(stat, 1)
                            charmod[stat] += 1
                    if skills:
                        for i in xrange(skills_pool):
                            skill = choice(skills)
                            char.mod_skill(skill, 1, 1)
                            charmod[skill] += 1

                if self.days_remaining <= 0:
                    txt.append("This Course has ended, all students have been sent back home.")
                    char.set_task(None)
                    school.students_dismissed += 1

                self.build_nd_report(char, charmod=charmod,
                                     flag_green=flag_green, txt=txt)

        def build_nd_report(self, char, charmod=None, type="normal",
                            txt=None, flag_green=False):
            if txt is None:
                txt = str(self.name) + " Testing string."
            else:
                txt = "\n".join(txt)

            if type == "normal":
                # Get char image from data:
                tags = self.data.get("imageTags", ["profile"])
                mode = self.data.get("imageMode", "reduce")
                kwargs = dict(exclude=self.data.get("noImageTags", []), type=mode, add_mood=False)
                img = char.show(*tags, **kwargs)
                flag_red = False

            elif type == "failed_to_pay":
                img = char.show("profile", "sad")
                flag_red = True

            evt = NDEvent(type="course_nd_report",
                          red_flag=flag_red,
                          green_flag=flag_green,
                          loc=pytfall.school,
                          char=char,
                          charmod=charmod,
                          img=img,
                          txt=txt)
            NextDayEvents.append(evt)


    class School(BaseBuilding):
        def __init__(self, id="-PyTFall Educators-",
                     img="content/schools/school.webp"):
            super(School, self).__init__(id=id, name=id)
            self.img = renpy.displayable(img)
            self.courses = []
            self.students = {} # cached map of student:course pairs to faster access

        def add_courses(self):
            forced = max(0, 12-len(self.courses))
            for i in range(forced):
                self.create_course()

            if dice(50) and len(self.courses) < 20:
                self.create_course()

            if dice(10) and len(self.courses) < 30:
                self.create_course()

        def create_course(self):
            id = choice(school_courses.keys())

            v0 = max(0, hero.tier - 1)
            v1 = min(MAX_TIER, hero.tier + 3)
            difficulty = randint(v0, v1)

            duration = randint(20, 40)
            days_to_complete = round_int(duration*random.uniform(.5, .75))
            effectiveness = randint(60, 100)
            data = school_courses[id]

            course = SchoolCourse(id, difficulty, duration,
                                  days_to_complete, effectiveness,
                                  data)
            self.new_courses_created = True
            self.courses.insert(0, course)

        def get_course(self, student):
            return self.students.get(student, None)

        def add_student(self, student, course):
            course.add_student(student)
            self.students[student] = course

        def remove_student(self, student):
            course = self.students.pop(student)
            course.remove_student(student)

        def next_day(self):
            # Resets:
            self.new_courses_created = False
            self.successfully_completed = 0
            self.students_dismissed = 0
            self.students_attended = 0

            for c in self.courses:
                c.next_day()

            self.courses = [c for c in self.courses if c.days_remaining > 0]

            self.add_courses()
            self.build_nd_report()

        def build_nd_report(self):
            txt = []
            type = "school_nd_report"

            temp = "{} Report: \n".format(self.name)
            txt.append(temp)

            if self.students_attended == 0:
                txt.append("Excellent courses are available here today! Remember our Motto: Education is Gold!")
            else:
                txt.append("You currently have %d %s training with us!" % (self.students_attended, plural("student", self.students_attended)))

            if self.new_courses_created:
                txt.append("New Courses are available from today!")

            if self.successfully_completed:
                txt.append("Today %d %s completed a course here!" % (self.successfully_completed, plural("student", self.successfully_completed)))

            if self.students_dismissed:
                txt.append("The course has ended for %d %s, have a look at our other courses!" % (self.students_dismissed, plural("student", self.students_dismissed)))

            img = pscale(self.img, 820, 705)
            txt = "\n".join(txt)

            evt = NDEvent(type=type, txt=txt, img=img)
            NextDayEvents.append(evt)

