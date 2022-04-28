from User import User
from Tutor import Tutor
"""
    Class is in charge of managing and creating user profiles which contains their username, ratings, 
    the amount of raters that have reviewed this user and the profile image URL. It also contains the Tutors
    the user is currently selling 


    Attrbibutes:
        username (str): username of user
        ratings(float): is the average rating given by all the raters that have reviewed this user
        raters_amount (int): amount of raters that have reviewed this user upon buying from them.
        profile_image (str): Contains the URL of the profile picture of the user.
        """
class Profile():
    def __init__(self,username, ratings,raters_amount, profile_image):
        # super().__init__(email, password,username,user_type)
        if (type(ratings) is not float):
            raise TypeError("review must be a float")
        if (ratings<0) or (ratings>5):
            raise ValueError("ratings must be between 0 and 5")
        if(type(raters_amount) != int):
            raise TypeError("raters amount must be and integer")
        if (raters_amount<0):
            raise ValueError("raters total must be higher or equal to 0")
        if(type(profile_image) != str):
            raise TypeError("URL must be of type string")
        
        self.username=username
        self.raters_amount=raters_amount
        self.user_Tutors = []
        self.ratings = ratings
        self.profile_image=profile_image
    '''
    function that takes in a new rating for the seller from which the Tutor was bought and updates that user's rating
    taking into account the number of their previous raters and rating. It then returns the updated rating of that seller
    in two decimal places
    '''
    @staticmethod
    def create_profile(username, rating, raters_amount, profile_image,database):
        profile = Profile(username, rating, raters_amount, profile_image)
        profile_document = profile.to_json()
        collection = database.db.profiles
        print(profile)
        collection.insert_one(profile_document)
        return profile

    @staticmethod
    def get_user_Tutors(username,database):
        collection = database.db.Tutors
        # Tutors=collection.find( { "username": username}, { "_id": 0, "name": 0, "size": 0,"price":0,"style":0,"gender":0,"description":0,"image":1,"username":0} )
        Tutors=collection.find({"username":"kevilin"})
        # Tutors = collection.find_one({"username": username}).project({"user_Tutors":1})
        return Tutors

    @staticmethod
    def get_profile(username,database):
        collection=database.db.profiles
        profile=collection.find_one({"username":username})
        return profile
        
    def to_json(self):
        return {'username': self.username, 'ratings': self.ratings , 'raters_amount': self.raters_amount, 'user_Tutors': self.user_Tutors, 'profile_image': self.profile_image}

    def _Review_Score(self, new_review):
        if(type(self.ratings)==None):
            raise ValueError
        if(type(new_review)==None):
            raise ValueError("Cannot be type None")
        if (type(new_review) != int):
            raise TypeError("ratings must be an integer")
        if (new_review<0) or (new_review>5):
            raise ValueError("ratings must be between 0 and 5")
        total_ratings=self.raters_amount*self.ratings
        self.raters_amount=self.raters_amount+1
        self.ratings=(total_ratings+new_review)/self.raters_amount
        return round(self.ratings,2)
    '''
    Function that takes an Tutor that the user wants to add to the Tutors they are currently selling and updates their list of Tutors
    '''
    
    def Add_Tutor_to_Sell(self,Tutor):
        
        if(type(Tutor)==None):
            raise ValueError("Cannot be type None")
        if(type(Tutor) != Tutor):
            raise TypeError("object has to be of type Tutor")
        if(self.username != Tutor.username):
            raise ValueError("Incorrect Owner")
        self.user_Tutors.append(Tutor)
    @staticmethod
    def Add_Tutor_to_SellDb(username,Tutor,database):
        collection = database.db.profiles
        collection.update({'username':username},{'$push':{'user_Tutors':Tutor.to_json()}})
        if(type(Tutor)==None):
            raise ValueError("Cannot be type None")
        if(type(Tutor) != Tutor):
            raise TypeError("object has to be of type Tutor")
        if(username != Tutor.username):
            raise ValueError("Incorrect Owner")
    @staticmethod
    def get_user_Tutors(username,database):
        collection = database.db.Tutors
        Tutors = collection.find_one({'username':username})
        return Tutors
    @staticmethod
    def get_profile(username,database):
        collection = database.db.profiles
        profile = collection.find_one({'username':username})
        return profile

    '''
    Function that takes in an Tutor and deletes it from the user's list of Tutors on sale, this is done when a 
    user chooses to stop selling and Tutor or when an Tutor is bought
    '''
    def Remove_Tutor(self,Tutor):
        if(type(Tutor)==None):
            raise ValueError("Cannot be type None")
        if(type(Tutor) != Tutor):
            raise TypeError("object has to be of type Tutor")
        if(Tutor not in self.user_Tutors):
            raise ValueError("user is not owner of Tutor")
        self.user_Tutors.remove(Tutor)