
# -- Import section --
from typing import Collection
from flask import Flask
from flask import render_template
from flask import request, redirect
from flask_pymongo import PyMongo
from flask import session
from User import User
import secrets
import certifi

from Tutor import Tutor
from Profile import Profile
# -- Initialization section --
app = Flask(__name__)

# name of database
app.config['MONGO_DBNAME'] = 'cluster0'

# URI of database
app.config['MONGO_URI'] = "mongodb+srv://InsoProjectATeam:TutorMatch@tutormatch.bfpj4.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

#Initialize PyMongo
mongo = PyMongo(app, tlsCAFile=certifi.where())

# run this the first time, to create the collection
# mongo.db.create_collection('Tutors')

# -- Session data --
app.secret_key = secrets.token_urlsafe(16)

# Fake users - DB
victor = User("victor@whereever.com", "a12341231", "victorandresvega")
all_users= {"victorandresvega": victor}

# department set:
departments = {"CIIC", "ANTR","INSO","ADEM","INGL","PSIC","EDFU"}

# filter list:
filters = {'CIIC4020','HUMA3011', 'ANTR3011', 'PSIC4010', 'MECU4012', 'INGL3201', 'INGL3204', 'PSIC3010','FILO3180', 'CIIC3020', 'ESPA3101'}

# top sellers this week:
top_sellers = {'Mariana Nuñez', 'Gustavo Álvarez', 'Tayna Rivera'}


# -- Routes section --
# LOGIN Route
@app.route('/')
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        username = request.form['username']
        if username not in all_users:
            return 'Invalid username or password.'
        else:
            user = all_users[username] 
            password = request.form['password']
            password_correct = user.compare_password(password)
            if(password_correct):
                session['username'] = request.form['username']
                return redirect('/landing') 
            else:
               return 'Invalid username or password.' 
   

# LOGOUT Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/landing')

# LANDING Route
@app.route('/landing', methods = ['GET', 'POST'])
def landing():
    if request.method == 'GET':
        Tutors = Tutor.get_Tutors(mongo)
    else:
        Tutors = Tutor.get_filtered_Tutors(mongo, request.form)
    return render_template('landing.html', departments=departments, filters=filters, top_sellers=top_sellers, Tutors=Tutors)

# PROFILE Route
@app.route('/profile',methods = ['GET', 'POST'])
def profile():

    username=session.get('username')
    collection=mongo.db.Tutors
    profile=Profile.get_profile(username,mongo)
    if request.method == 'GET':
        user_Tutors=list(collection.find({"username":username}))
    elif "Remove" in request.form: 
        return redirect('/remove')
    elif "Add" in request.form: 
        return redirect('/Add')
        
        
    return render_template('Profile.html',session=session,user_Tutors=user_Tutors,profile=profile)
@app.route('/remove',methods = ['GET', 'POST'])
def remove():

    username=session.get('username')
    collection=mongo.db.Tutors
    profile=Profile.get_profile(username,mongo)
    if request.method == 'GET':
        user_Tutors=list(collection.find({"username":username}))
    elif request.form["remove_Tutor"]:
        Tutor_to_remove=request.form["remove_Tutor"]
        collection.remove({"name":Tutor_to_remove})
        return redirect('/profile')
    return render_template('RemoveTutor.html',session=session,user_Tutors=user_Tutors,profile=profile)

@app.route('/Add',methods = ['GET', 'POST'])
def Add():
    username=session.get('username')
    collection=mongo.db.Tutors
    if request.method == 'POST':
        user=all_users[username]
        name=request.form["name"]
        lastname=float(request.form["lastname"])
        department=request.form["department"]
        courses=request.form["courses"]
        profile_URL=request.form["profile_URL"]
        Tutor.create_Tutor(name,lastname,department,courses,profile_URL,user,mongo)
        return redirect('/profile')
    return render_template('AddTutor.html',session=session)



@app.route('/seed_Tutors')
def seed_Tutors():
    collection = mongo.db.Tutors
    Tutor.create_Tutor('Carla', "Lopez", 'CIIC','https://engineering.unl.edu/images/staff/Kayla-Person.jpg',"CIIC4020" ,"https://calendly.com", mongo)
    Tutor.create_Tutor('Tayna','Rivera', "EDFU", 'https://images.unsplash.com/photo-1601288496920-b6154fe3626a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8dGVlbiUyMGdpcmx8ZW58MHx8MHx8&w=1000&q=80','HUMA3011',"https://calendly.com",mongo)
    Tutor.create_Tutor('Gustavo','Alvarez',"PSIC", 'https://pomonapeoplepower.com/wp-content/uploads/2020/09/116587312_671814770072925_73351170129650855_o.jpg','PSIC4010',"https://calendly.com",  mongo)
    Tutor.create_Tutor('Mariana', 'Nuñez', "ANTR",'ANTR3011', 'https://live.staticflickr.com/4089/5053238250_aeee8e305d_b.jpg',"https://calendly.com",mongo)
    Tutor.create_Tutor('Michelle', 'Vega', "ADEM","MECU4012",'https://cdn.domestika.org/c_fill,dpr_auto,f_auto,h_256,pg_1,t_base_params,w_256/v1519484035/avatars/000/681/957/681957-original.jpg?1519484035',"https://calendly.com",  mongo)
    # collection = mongo.db.profiles
    # victorP=Profile.create_profile("victorandresvega", 5.0,10,"https://images.unsplash.com/photo-1529665253569-6d01c0eaf7b6?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8cHJvZmlsZXxlbnwwfHwwfHw%3D&w=1000&q=80", mongo)
    # collection.remove({})


    return 'Seeded succesfuly'

