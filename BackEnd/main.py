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

    def updateTutoreeStatus(self, tutoree, status):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutoree.email:
                student[StudentSpec.Status] = status

    def rateTutor(self, tutor, rating):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutor.email:
                student[StudentSpec.Rating] = (student[StudentSpec.Rating] * student[StudentSpec.TotalRatings] + rating) / (student[StudentSpec.TotalRatings] + 1)
                student[StudentSpec.TotalRatings] += 1

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
            return

        self.courses.append(course.identification)
        if finished:
            course.haveTaken.append([self.email, help, 5, 0])
        else:
            course.areTaking.append([self.email, help])

    def updateClass(self, course, finished, help):
        if course.identification not in self.courses:
            return

        if finished:
            i = course.takingIndex(self)
            if i >= 0:
                course.areTaking.pop(i)
            j = course.takenIndex(self)
            if j >= 0:
                course.haveTaken[j][StudentSpec.Status] = help
                return
            course.haveTaken.append([self.email, help, 5, 0])
        else:
            i = course.takenIndex(self)
            if i >= 0:
                course.haveTaken.pop(i)
            j = course.takingIndex(self)
            if j >= 0:
                course.areTaking[j][StudentSpec.Status] = help
                return
            course.areTaking.append([self.email, help])

    def removeClass(self, course):
        if course.identification not in self.courses:
            return

        self.courses.remove(course.identification)

        i = course.takingIndex(self)
        if i >= 0:
            course.areTaking.pop(i)
            return

        j = course.takenIndex(self)
        if j >= 0:
            course.haveTaken.pop(j)

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
        student = System.students.get(email)
        if System.students is not None:
            if student.password == password:
                return student
        return None

    @staticmethod
    def registerAccount(name, lastname, email, password):
        if System.students.get(email) is not None:
            return

        System.students[email] = Student(name, lastname, email, password)
        return System.students[email]

    @staticmethod
    def deleteAccount(email):
        if System.students.get(email) is None:
            return

        for course in System.students[email].courses:
            System.students[email].removeClass(System.classes[course])
        System.students.pop(email)

    @staticmethod
    def registerUniversityClass(name, codification):
        if System.classes.get(codification) is not None:
            return

        System.classes[codification] = UniversityClass(name, codification)
        return System.classes[codification]

    @staticmethod
    def deleteUniversityClass(codification):
        if System.classes.get(codification) is None:
            return

        for student in System.classes[codification].areTaking:
            System.students[student[StudentSpec.Student]].courses.remove(codification)

        for student in System.classes[codification].haveTaken:
            System.students[student[StudentSpec.Student]].courses.remove(codification)

        System.classes.pop(codification)

    @staticmethod
    def save():
        with open(studentsFile, "w", newline="") as file:
            for student in System.students.values():
                file.write(json.dumps(student.toDictionary()) + "\n")
        with open(universityClassesFile, "w", newline="") as file:
            for universityClass in System.classes.values():
                file.write(json.dumps(universityClass.toDictionary()) + "\n")


System.initialize()

System.registerAccount("Kelvin", "Gonzalez", "kelvin.gonzalez11@upr.edu", "password :D")
System.registerAccount("Kelvin", "Gonzalez", "kelvin.gonzalez12@upr.edu", "password :D")
System.registerAccount("Kelvin", "Gonzalez", "kelvin.gonzalez14@upr.edu", "password :D")

System.registerUniversityClass("Intro to Software Engineering", "INSO4101")
System.registerUniversityClass("Algorithms", "CIIC4025")
System.registerUniversityClass("Physics II", "FISI3172")
System.registerUniversityClass("Linear Algebra and Differential Equations", "MATE4151")

user = System.logIn("kelvin.gonzalez11@upr.edu", "password :D")
user.addClass(System.classes["INSO4101"], True)
System.students["kelvin.gonzalez12@upr.edu"].addClass(System.classes["INSO4101"], True)
System.students["kelvin.gonzalez14@upr.edu"].addClass(System.classes["INSO4101"], True, False)

print(System.classes["INSO4101"].haveTaken)

System.classes["INSO4101"].rateTutor(user, 4)

System.registerAccount("Kelvin", "Gonzalez", "kelvin.gonzalez13@upr.edu", "password :D")
student2 = System.students["kelvin.gonzalez13@upr.edu"]
student2.addClass(System.classes["INSO4101"], False)
print(student2.findMatches())

user.updateClass(System.classes["INSO4101"], True, False)
print(student2.findMatches())

user.addClass(System.classes["MATE4151"], True)
user.updateClass(System.classes["MATE4151"], True, True)

#System.deleteAccount("kelvin.gonzalez13@upr.edu")
#System.deleteUniversityClass("MATE4151")

System.save()
