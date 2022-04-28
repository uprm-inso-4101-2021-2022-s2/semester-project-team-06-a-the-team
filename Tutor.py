from User import User
class Tutor:
    """
    Creates an Tutor that stores its values
    """
    def __init__(self, name,lastname,department,profile_URL,calendly_URL,courses=[]):
        self.name=name
        self.department=department
        self.lastname=lastname
        self.courses=courses
        self.profile_URL=profile_URL
        self.calendly=calendly_URL

    @staticmethod
    def create_Tutor(name, lastname, department, profile_URL,courses,calendly_URL, database):
        t = Tutor(name, lastname, department, profile_URL,calendly_URL,courses)
        Tutor_document = t.to_json()
        collection = database.db.Tutors
        print(Tutor_document)
        collection.insert_one(Tutor_document)
        return t
    
    @staticmethod
    def get_Tutors(database):
        collection = database.db.Tutors
        Tutors = collection.find()
        return list(Tutors)

    @staticmethod
    def get_filtered_Tutors(database, filters):
        collection = database.db.Tutors
        filtered_Tutors = []
        for filter in filters.keys():
            if(filter != 'department'):
                filtered_Tutors.append(filter)
        if('department' in filters.keys()):
            if(len(filtered_Tutors) == 0):
                return list(collection.find({'department': filters}))
            else:
                return list(collection.find({'department': filters, 'courses':{'$in': filtered_Tutors}}))
        else:
            if(len(filtered_Tutors) == 0):
                return []
            return list(collection.find({'courses':{'$in': filtered_Tutors}}))

    def to_json(self):
        return {'name': self.name, 'lastname': self.lastname , 'department': self.department,'courses': self.courses, 'profile_URL': self.profile_URL}
  
    def __str__(self) -> str:
        extra_hyphens = len(self.name)
        return(f'-----------------<{self.name}  {self.lastname}>-----------------\n   image url: {self.profile_URL}\n   department: {self.department}\n   courses: {self.courses}\n ')