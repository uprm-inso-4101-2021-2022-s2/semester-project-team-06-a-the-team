import enum
import json


universityClassesFile = "UniversityClasses.txt"
studentsFile = "Students.txt"


class StudentSpec(enum.IntEnum):
    Student = 0
    Status = 1
    Rating = 2
    TotalRatings = 3


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
            if self.haveTaken[i][StudentSpec.Student] == student.email:
                return i
        return -1

    def takingIndex(self, student):
        for i in range(len(self.areTaking)):
            if self.areTaking[i][StudentSpec.Student] == student.email:
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
            if student[StudentSpec.Student] == tutor.email:
                student[StudentSpec.Status] = status
                return True
        return False

    def updateTutoreeStatus(self, tutoree, status):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutoree.email:
                student[StudentSpec.Status] = status
                return True
        return False

    def rateTutor(self, tutor, rating):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutor.email:
                student[StudentSpec.Rating] = (student[StudentSpec.Rating] * student[StudentSpec.TotalRatings] + min(max(rating, 1), 5)) / (student[StudentSpec.TotalRatings] + 1)
                student[StudentSpec.TotalRatings] += 1
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
    def __init__(self, name, lastname, email, password, courses=None):
        if courses is None:
            courses = []

        self.name = name
        self.lastname = lastname
        self.email = email
        self.password = password
        self.courses = courses

    def __eq__(self, other):
        return self.email == other.email

    def findMatches(self):
        matches = {}
        for course in self.courses:
            if System.classes[course].isTutoree(self):
                matches[course] = System.classes[course].haveTaken
                System.classes[course].sortTutors()
        return matches

    def addClass(self, course, finished=False, help=True):
        if course.identification in self.courses:
            return False

        self.courses.append(course.identification)
        if finished:
            course.haveTaken.append([self.email, help, 5, 0])
        else:
            course.areTaking.append([self.email, help])

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
            course.haveTaken.append([self.email, help, 5, 0])
        else:
            i = course.takenIndex(self)
            if i >= 0:
                course.haveTaken.pop(i)
            j = course.takingIndex(self)
            if j >= 0:
                course.areTaking[j][StudentSpec.Status] = help
                return True
            course.areTaking.append([self.email, help])

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

    def toDictionary(self):
        return {"name": self.name, "lastname": self.lastname, "email": self.email, "password": self.password, "courses": self.courses}

    @staticmethod
    def fromDictionary(dict):
        return Student(dict["name"], dict["lastname"], dict["email"], dict["password"], dict["courses"])


class System:
    students = {}
    classes = {}

    @staticmethod
    def initialize():
        with open(studentsFile, "r") as file:
            for line in file:
                student = Student.fromDictionary(json.loads(line.strip()))
                System.students[student.email] = student
        with open(universityClassesFile, "r") as file:
            for line in file:
                universityClass = UniversityClass.fromDictionary(json.loads(line.strip()))
                System.classes[universityClass.identification] = universityClass

    @staticmethod
    def logIn(email, password):
        if System.students.get(email) is None:
            return None

        student = System.students.get(email)
        if System.students is not None:
            if student.password == password:
                return student
        return None

    @staticmethod
    def registerAccount(name, lastname, email, password):
        if System.students.get(email) is not None:
            return None

        System.students[email] = Student(name, lastname, email, password)
        return System.students[email]

    @staticmethod
    def deleteAccount(email):
        if System.students.get(email) is None:
            return False

        for course in System.students[email].courses:
            System.students[email].removeClass(System.classes[course])
        System.students.pop(email)
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
    def save():
        with open(studentsFile, "w", newline="") as file:
            for student in System.students.values():
                file.write(json.dumps(student.toDictionary()) + "\n")
        with open(universityClassesFile, "w", newline="") as file:
            for universityClass in System.classes.values():
                file.write(json.dumps(universityClass.toDictionary()) + "\n")


System.initialize()

user = None

while True:
    try:
        answer = input()
        if answer == "register account":
            print("Account already registered") if System.registerAccount(input("Enter name: "), input("Enter lastname: "), input("Enter email: "), input("Enter password: ")) is None else print("Account registered")
        elif answer == "login":
            user = System.logIn(input("Enter email: "), input("Enter password: "))
            print("Invalid credentials") if user is None else print(f"Logged in as {user.name} {user.lastname}")
        elif answer == "register class":
            print("Class already registered") if System.registerUniversityClass(input("Enter name: "), input("Enter codification: ")) is None else print("Class registered")
        elif answer == "delete account":
            print("Account deleted") if System.deleteAccount(input("Enter email: ")) else print("Account does not exist")
        elif answer == "delete class":
            print("Class deleted") if System.deleteUniversityClass(input("Enter identification: ")) else print("Class does not exist")
        elif answer == "rate tutor":
            print("Tutor rated") if System.classes[input("Enter codification: ")].rateTutor(System.students[input("Enter tutor email: ")], int(input("Enter rating: "))) else print("Tutor not found")
        elif answer == "find matches":
            if user is None:
                print("Not signed in")
                continue
            print(user.findMatches())
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
