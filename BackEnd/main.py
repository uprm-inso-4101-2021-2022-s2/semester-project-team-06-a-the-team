import enum
import pymongo

client = pymongo.MongoClient("mongodb+srv://DevUser:DevUserPasswordYes@tutormatchdb.o2owb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


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

    def __str__(self):
        return f"UniversityClass('{self.name}', '{self.identification}', '{self.haveTaken}', '{self.areTaking}')"

    def __eq__(self, other):
        return self.identification == other.identification

    def takenIndex(self, student):
        for i in range(len(self.haveTaken)):
            if self.haveTaken[i][StudentSpec.Student] == student:
                return i
        return -1

    def takingIndex(self, student):
        for i in range(len(self.areTaking)):
            if self.areTaking[i][StudentSpec.Student] == student:
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
            if student[StudentSpec.Student] == tutor:
                student[StudentSpec.Status] = status

    def updateTutoreeStatus(self, tutoree, status):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutoree:
                student[StudentSpec.Status] = status

    def rateTutor(self, tutor, rating):
        for student in self.haveTaken:
            if student[StudentSpec.Student] == tutor:
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
        return Student(dict["name"], dict["identification"], dict["haveTaken"], dict["areTaking"])


class Student:
    def __init__(self, name, lastname, email, password, courses=None):
        if courses is None:
            courses = []

        self.name = name
        self.lastname = lastname
        self.email = email
        self.password = password
        self.courses = courses

    def __str__(self):
        return f"Student('{self.name}', '{self.lastname}', '{self.email}', '{self.password}', '{self.courses}')"

    def __eq__(self, other):
        return self.email == other.email

    def findMatches(self):
        matches = {}
        for course in self.courses:
            if course.isTutoree(self):
                matches[course.identification] = course.haveTaken
                course.sortTutors()
        return matches

    def addClass(self, course, finished=False, help=True):
        self.courses.append(course)
        if finished:
            course.haveTaken.append([self, help, 5, 0])
        else:
            course.areTaking.append([self, help])

    def updateClass(self, course, finished, help):
        if finished:
            i = course.takingIndex(self)
            if i >= 0:
                course.areTaking.pop()
            j = course.takenIndex(self)
            if j >= 0:
                course.haveTaken[j][StudentSpec.Status] = help
                return
            course.haveTaken.append([self, help, 5, 0])
        else:
            i = course.takenIndex(self)
            if i >= 0:
                course.haveTaken.pop()
            j = course.takingIndex(self)
            if j >= 0:
                course.areTaking[j][StudentSpec.Status] = help
                return
            course.areTaking.append([self, help])

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
                student = eval(line.strip())
                System.students[student.email] = student
        with open(universityClassesFile, "r") as file:
            for line in file:
                universityClass = eval(line.strip())
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
        System.students[email] = Student(name, lastname, email, password)
        return System.students[email]

    @staticmethod
    def deleteAccount(email):
        System.students.pop(email)

    @staticmethod
    def registerUniversityClass(name, codification):
        System.classes[codification] = UniversityClass(name, codification)
        return System.classes[codification]

    @staticmethod
    def save():
        with open(studentsFile, "w", newline="") as file:
            for student in System.students.values():
                file.write(str(student) + "\n")
        with open(universityClassesFile, "w", newline="") as file:
            for universityClass in System.classes.values():
                file.write(str(universityClass) + "\n")

database = client["TutorMatchDB"]

#System.initialize()

System.registerAccount("Kelvin", "Gonzalez", "kelvin.gonzalez11@upr.edu", "password :D")
System.registerAccount("Kelvin", "Gonzalez", "kelvin.gonzalez12@upr.edu", "password :D")
System.registerAccount("Kelvin", "Gonzalez", "kelvin.gonzalez14@upr.edu", "password :D")

System.registerUniversityClass("Intro to Software Engineering", "INSO4101")
System.registerUniversityClass("Algorithms", "CIIC4025")
System.registerUniversityClass("Physics II", "FISI3172")

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

database["Students"].insert_one({"Student1": Student("Kelvin", "Gonzalez", "kelvin.gonzalez11@upr.edu", "password :D")})

#System.save()
