import enum
import json


universityClassesFile = "UniversityClasses.txt"
studentsFile = "Students.txt"


class StudentSpec(enum.IntEnum):
    Student = 0
    Status = 1
    Rating = 2
    Raters = 3


class UniversityClass:
    def __init__(self, name, identification, haveTaken=None, areTaking=None):
        if haveTaken is None:
            haveTaken = []
        if areTaking is None:
            areTaking = []

        self.name = name
        self.identification = identification
        self.haveTaken = haveTaken
        self.areTaking = areTaking

    def __eq__(self, other):
        return self.identification == other.identification

    def takenIndex(self, student):
        for i in range(len(self.haveTaken)):
            if self.haveTaken[i][StudentSpec.Student] == student.username:
                return i
        return -1

    def takingIndex(self, student):
        for i in range(len(self.areTaking)):
            if self.areTaking[i][StudentSpec.Student] == student.username:
                return i
        return -1

    def isTutor(self, student):
        i = self.takenIndex(student)
        return self.haveTaken[i][StudentSpec.Status] if i >= 0 else False

    def isTutoree(self, student):
        i = self.takingIndex(student)
        return self.areTaking[i][StudentSpec.Status] if i >= 0 else False

    def updateTutorStatus(self, tutor, status):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutor.username:
                student[StudentSpec.Status] = status
                return True
        return False

    def updateTutoreeStatus(self, tutoree, status):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutoree.username:
                student[StudentSpec.Status] = status
                return True
        return False

    def rateTutor(self, tutor, rater, rating):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutor.username:
                if rater.username in student[StudentSpec.Raters]:
                    return False
                student[StudentSpec.Rating] = (student[StudentSpec.Rating] * len(student[StudentSpec.Raters]) + min(max(rating, 1), 5)) / (len(student[StudentSpec.Raters]) + 1)
                student[StudentSpec.Raters].append(rater.username)
                return True
        return False

    @staticmethod
    def sortingKey(e):
        return e[StudentSpec.Rating] + (0 if e[StudentSpec.Status] else -5)

    def sortTutors(self):
        self.haveTaken.sort(reverse=True, key=UniversityClass.sortingKey)

    def toDictionary(self):
        return {"name": self.name, "identification": self.identification, "haveTaken": self.haveTaken, "areTaking": self.areTaking}

    @staticmethod
    def fromDictionary(dict):
        return UniversityClass(dict["name"], dict["identification"], dict["haveTaken"], dict["areTaking"])


class Student:
    def __init__(self, username, name, email, password, department=None, description=None, style=None, courses=None):
        if courses is None:
            courses = []

        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.department = department
        self.description = description
        self.style = style
        self.courses = courses

    def __eq__(self, other):
        return self.username == other.username

    def __str__(self):
        tutoringClasses = self.findTutoringClasses()
        return f"Name: {self.name}\nUsername: {self.username}\nDepartment: {'N/A' if self.department is None else self.department}\nDescription: {'N/A' if self.description is None else self.description}\nStyle: {'N/A' if self.style is None else self.style}\nAvailable for tutoring sessions in {', '.join(tutoringClasses) if len(tutoringClasses) > 0 else 'nothing'}"

    def __repr__(self):
        return self.__str__()

    def updateName(self, name):
        self.name = name

    def updateDepartment(self, department):
        def departmentFromClasses(department):
            for course in System.classes.keys():
                if department == course[:4]:
                    return True
            return False

        if departmentFromClasses(department):
            self.department = department
            return True

        return False

    def updateDescription(self, description):
        self.description = description

    def updateStyle(self, style):
        self.style = style

    def findMatches(self):
        matches = {}
        for course in self.courses:
            if System.classes[course].isTutoree(self):
                if len(System.classes[course].haveTaken) > 0:
                    matches[course] = System.classes[course].haveTaken
                    System.classes[course].sortTutors()
        return matches

    def findTutoringClasses(self):
        classes = []
        for course in self.courses:
            if System.classes[course].isTutor(self):
                classes.append(f"{System.classes[course].name} ({course})")
        return classes

    def addClass(self, course, finished=False, help=True):
        if course.identification in self.courses or course.identification not in System.classes.keys():
            return False

        self.courses.append(course.identification)
        if finished:
            course.haveTaken.append([self.username, help, 5, []])
        else:
            course.areTaking.append([self.username, help])

        return True

    def updateClass(self, course, finished, help):
        if course.identification not in self.courses:
            return False

        if finished:
            i = course.takingIndex(self)
            if i >= 0:
                course.areTaking.pop(i)
            j = course.takenIndex(self)
            if j >= 0:
                course.haveTaken[j][StudentSpec.Status] = help
                return True
            course.haveTaken.append([self.username, help, 5, []])
        else:
            i = course.takenIndex(self)
            if i >= 0:
                course.haveTaken.pop(i)
            j = course.takingIndex(self)
            if j >= 0:
                course.areTaking[j][StudentSpec.Status] = help
                return True
            course.areTaking.append([self.username, help])

        return True

    def removeClass(self, course):
        if course.identification not in self.courses:
            return False

        self.courses.remove(course.identification)

        i = course.takingIndex(self)
        if i >= 0:
            course.areTaking.pop(i)
            return True

        j = course.takenIndex(self)
        if j >= 0:
            course.haveTaken.pop(j)

        return True

    def rateTutor(self, tutor, course, rating):
        if not course.isTutoree(self):
            return False
        return course.rateTutor(tutor, self, rating)

    def toDictionary(self):
        return {"username": self.username, "name": self.name, "email": self.email, "password": self.password, "department": self.department, "description": self.description, "style": self.style, "courses": self.courses}

    @staticmethod
    def fromDictionary(dict):
        return Student(dict["username"], dict["name"], dict["email"], dict["password"], dict["department"], dict["description"], dict["style"], dict["courses"])


class System:
    students = {}
    classes = {}

    @staticmethod
    def initialize():
        with open(studentsFile, "r") as file:
            for line in file:
                student = Student.fromDictionary(json.loads(line.strip()))
                System.students[student.username] = student
        with open(universityClassesFile, "r") as file:
            for line in file:
                universityClass = UniversityClass.fromDictionary(json.loads(line.strip()))
                System.classes[universityClass.identification] = universityClass

    @staticmethod
    def logIn(username, password):
        if System.students.get(username) is None:
            return None

        student = System.students.get(username)
        if System.students is not None:
            if student.password == password:
                return student
        return None

    @staticmethod
    def registerAccount(username, name, email, password):
        def emailInAccounts(email):
            for account in System.students.values():
                if account.email == email:
                    return True
            return False

        if System.students.get(username) is not None or emailInAccounts(email):
            return None

        System.students[username] = Student(username, name, email, password)
        return System.students[username]

    @staticmethod
    def deleteAccount(username):
        if System.students.get(username) is None:
            return False

        for course in System.students[username].courses:
            System.students[username].removeClass(System.classes[course])
        System.students.pop(username)
        return True

    @staticmethod
    def registerUniversityClass(name, codification):
        if System.classes.get(codification) is not None:
            return None

        System.classes[codification] = UniversityClass(name, codification)
        return System.classes[codification]

    @staticmethod
    def deleteUniversityClass(codification):
        if System.classes.get(codification) is None:
            return False

        for student in System.classes[codification].areTaking:
            System.students[student[StudentSpec.Student]].courses.remove(codification)

        for student in System.classes[codification].haveTaken:
            System.students[student[StudentSpec.Student]].courses.remove(codification)

        System.classes.pop(codification)

        return True

    @staticmethod
    def searchByDepartment(department):
        list = []
        for value in System.students.values():
            if value.department == department:
                list.append(value.username)
        return list

    @staticmethod
    def searchByStyle(style):
        list = []
        for value in System.students.values():
            if value.style == style:
                list.append(value.username)
        return list

    @staticmethod
    def save():
        with open(studentsFile, "w", newline="") as file:
            for student in System.students.values():
                file.write(json.dumps(student.toDictionary()) + "\n")
        with open(universityClassesFile, "w", newline="") as file:
            for universityClass in System.classes.values():
                file.write(json.dumps(universityClass.toDictionary()) + "\n")


def listListDictionaryToString(dict):
    def keyValueToString(key, value):
        s = str(key) + "\n"
        for elm in value[:len(value)-1]:
            s += f" - Username: {elm[0]}, Tutoring: {'Yes' if elm[1] else 'No'}, Rating: {elm[2]}, Ratings Count: {len(elm[3])}\n"
        s += f" - Username: {value[len(value)-1][0]}, Tutoring: {'Yes' if value[len(value)-1][1] else 'No'}, Rating: {value[len(value)-1][2]}, Ratings Count: {len(value[len(value)-1][3])}"
        return s
    return "\n".join([keyValueToString(key, dict[key]) for key in dict.keys()])


System.initialize()

user = None

while True:
    try:
        answer = input()
        if answer == "register account":
            username = input("Enter username: ")
            print("Account already registered with same username or email") if System.registerAccount(username, input("Enter name: "), input("Enter email: "), input("Enter password: ")) is None else print("Account registered")
            user = System.students.get(username)
        elif answer == "login":
            user = System.logIn(input("Enter username: "), input("Enter password: "))
            print("Invalid credentials") if user is None else print(f"Logged in as {user.name}")
        elif answer == "register class":
            print("Class already registered") if System.registerUniversityClass(input("Enter name: "), input("Enter codification: ")) is None else print("Class registered")
        elif answer == "delete account":
            print("Account deleted") if System.deleteAccount(input("Enter username: ")) else print("Account does not exist")
        elif answer == "delete class":
            print("Class deleted") if System.deleteUniversityClass(input("Enter identification: ")) else print("Class does not exist")
        elif answer == "rate tutor":
            if user is None:
                print("Not signed in")
                continue
            print("Tutor rated") if user.rateTutor(System.students[input("Enter tutor username: ")], System.classes[input("Enter identification: ")], int(input("Enter rating: "))) else print("Tutor was not rated")
        elif answer == "update name":
            if user is None:
                print("Not signed in")
                continue
            user.updateName(input("Enter name: "))
            print("Name updated")
        elif answer == "update department":
            if user is None:
                print("Not signed in")
                continue
            print("Department updated") if user.updateDepartment(input("Enter department: ")) else print("Department does not exist")
        elif answer == "update description":
            if user is None:
                print("Not signed in")
                continue
            user.updateDescription(input("Enter description: "))
            print("Description updated")
        elif answer == "update style":
            if user is None:
                print("Not signed in")
                continue
            user.updateStyle(input("Enter style: "))
            print("Style updated")
        elif answer == "find matches":
            if user is None:
                print("Not signed in")
                continue
            matches = user.findMatches()
            print(listListDictionaryToString(matches) if len(matches) > 0 else "No matches found")
        elif answer == "add class":
            if user is None:
                print("Not signed in")
                continue
            print("Class added") if user.addClass(System.classes[input("Enter identification: ")], True if input("Enter if finished (T/F): ") == "T" else False, True if input("Enter tutor/tutoree status (T/F): ") == "T" else False) else print("Class already added")
        elif answer == "remove class":
            if user is None:
                print("Not signed in")
                continue
            print("Class removed") if user.removeClass(System.classes[input("Enter identification: ")]) else print("Class is not present")
        elif answer == "update class":
            if user is None:
                print("Not signed in")
                continue
            print("Class updated") if user.updateClass(System.classes[input("Enter identification: ")], True if input("Enter if finished (T/F): ") == "T" else False, True if input("Enter tutor/tutoree status (T/F): ") == "T" else False) else print("Class is not present")
        elif answer == "search by username":
            username = input("Enter username: ")
            print(System.students[username]) if System.students.get(username) else print("Student not found")
        elif answer == "search by department":
            students = System.searchByDepartment(input("Enter department: "))
            print(students if len(students) > 0 else "No students found")
        elif answer == "search by style":
            students = System.searchByStyle(input("Enter style: "))
            print(students if len(students) > 0 else "No students found")
        elif answer == "save":
            System.save()
            print("Data saved")
        elif answer == "exit":
            break
        elif answer.strip() == "":
            continue
        else:
            print("Invalid Command")
    except:
        print("An Error Occurred")

System.save()
