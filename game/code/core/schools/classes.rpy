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

            # set price
            price = get_average_wage()
            price = price + price * difficulty
            self.price = round_int(price)

            self.set_image()

        def __repr__(self):
            return str(self.name + " Course")

        def set_image(self):
            dir = content_path("schools", self.data["image"])
            images = [fn for fn in listfiles(dir) if check_content_extension(fn)]
            self.img = os.path.join(dir, choice(images)) if images else IMG_NOT_FOUND_PATH

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
            students = self.students
            if len(students) == 0:
                return
            if len(students) >= 3 and dice(25):
                best_student = choice(students)
            else:
                best_student = None

            data = self.data
            stats = [(s, 30) for s in data["primary_stats"]]
            stats += [(s, 10) for s in data["secondary_stats"]]

            skills = [(s, 30) for s in data["primary_skills"]]
            skills += [(s, 10) for s in data["secondary_skills"]]

            school = pytfall.school
            difficulty = self.difficulty
            price = self.price
            effectiveness = self.effectiveness/100.0
            for char in students[:]:
                txt = [] # Append all events we want to relay to the player.
                flag_green = False
                charmod = None

                temp = "%s is taking a %s Course!" % (char.fullname, self.name)
                txt.append(temp)

                # Pay for the class:
                if hero.take_money(price, reason="-PyTFall Educators-"):
                    char.fin.log_logical_expense(price, "-PyTFall Educators-")
                    temp = "You've covered a fee of {color=gold}%s Gold{/color}!" % price
                    txt.append(temp)
                else:
                    char.set_task(None)
                    temp = "\nYou failed to cover the fee of {color=gold}%d Gold{/color}!" % price
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

                    # Effectiveness mod (simple)
                    mod = ap_spent * effectiveness

                    # Add exp/stats/skills mods.
                    if char == best_student:
                        temp = "%s has been a perfect student today and went every extra mile %s could." % (char.name, char.p)
                        temp += " {color=lawngreen}+50% Stats/Skills/EXP Bonus!{/color}"
                        flag_green = True
                        txt.append(temp)
                        mod *= 1.5

                    if char in self.completed:
                        mod *= .8
                        temp = "%s has already finished this course!" % char.nickname
                        temp += " {color=red}-20% Stats/Skills/EXP Bonus!{/color}"
                        txt.append(temp)
                    elif completed:
                        school.successfully_completed += 1
                        self.completed.add(char)
                        mod *= 2
                        temp = "%s has completed the course today!" % char.nickname
                        temp += " {color=lawngreen}+100% Stats/Skills/EXP Bonus!{/color}"
                        flag_green = True
                        txt.append(temp)

                    # Add Exp:
                    exp = exp_reward(char, difficulty, exp_mod=mod)
                    char.mod_exp(exp)

                    # Add Stats/Skills:
                    #  prepare charmod
                    charmod = dict() # Dict of changes of stats and skills for ND
                    charmod["exp"] = exp
                    if stats:
                        sm = weighted_list(stats, dice_int(mod))
                        sm = collections.Counter(sm)
                        for s, m in sm.items():
                            charmod[s] = char.mod_stat(s, stat_reward(char, difficulty, s, 1))
                    if skills:
                        sm = weighted_list(skills, dice_int(mod*2))
                        sm = collections.Counter(sm)
                        for s, m in sm.items():
                            charmod[s] = char.mod_skill(s, 1, skill_reward(char, difficulty, 1))

                if self.days_remaining <= 0:
                    txt.append("This Course has ended, all students have been sent back home.")
                    char.set_task(None)
                    school.students_dismissed += 1

                self.build_nd_report(char, charmod=charmod,
                                     flag_green=flag_green, txt=txt)

        def build_nd_report(self, char, charmod=None, type="normal",
                            txt=None, flag_green=False):
            txt = "\n".join(txt)

            if type == "normal":
                # Get char image from data:
                img = self.data
                img = char.show(*img["imageTags"], exclude=img["noImageTags"], type=img["imageMode"], add_mood=False)
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
                     img="content/schools/school_s.webp"):
            super(School, self).__init__(id=id, name=id)
            self.img = img
            self.courses = []
            self.students = {} # cached map of student:course pairs for faster access

            # gui
            self.tier_filter = 0
            self.type_filter = {"xxx", "combat", None}

        @classmethod
        def load_courses(cls):
            courses = load_db_json("school_courses.json")
            for data in courses.itervalues():
                # Add mandatory fields:
                if "imageMode" not in data:
                    data["imageMode"] = "reduce"
                if "imageTags" not in data:
                    data["imageTags"] = ["profile"]
                if "noImageTags" not in data:
                    data["noImageTags"] = []
                # Prepare stats/skills:
                for mode in ("primary", "secondary"):
                    ss = data.pop(mode, [])
                    cstats, cskills = [], []
                    for s in ss:
                        if is_stat(s):
                            cstats.append(s)
                        elif is_skill(s):
                            cskills.append(s)
                        else:
                            raise Exception("%s is not a valid stat/skill for %s course (%s)." % (s, data["id"], mode))
                    data[mode+"_stats"] = cstats
                    data[mode+"_skills"] = cskills
            cls.all_courses = courses

        def toggle_type_filter(self, type):
            type_filter = self.type_filter
            if type in type_filter:
                type_filter.remove(type)
            else:
                type_filter.add(type)

        def add_courses(self):
            school_courses = self.all_courses
            courses = self.courses

            keys = school_courses.keys()
            num_courses = len(keys)*MAX_TIER/2
            num_courses += randint(0, num_courses/2)
            num_courses -= len(courses)
            if num_courses > 0:
                self.new_courses_created = True
                for i in range(num_courses):
                    # create course
                    id = choice(keys)

                    difficulty = randint(0, MAX_TIER)

                    duration = 7 * randint(3, 6)
                    days_to_complete = round_int(duration*random.uniform(.5, .75))
                    effectiveness = randint(60, 100)
                    data = school_courses[id]

                    course = SchoolCourse(id, difficulty, duration,
                                          days_to_complete, effectiveness,
                                          data)
                    courses.insert(0, course)

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

            if calendar.weekday() == "Monday":
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

            txt = "\n".join(txt)

            evt = NDEvent(type=type, txt=txt, img=self.img)
            NextDayEvents.append(evt)

