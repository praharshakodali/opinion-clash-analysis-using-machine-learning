# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 16:51:40 2020

@author: suma sree
"""
import numpy as np
from pymongo import MongoClient
from random import randint
from flask import flash,Flask,jsonify,render_template,request,redirect,session
import pickle
import os
import bcrypt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
client = MongoClient('mongodb+srv://relationshipsite:relationshipsite@cluster0.hqrc3.mongodb.net/userdata?retryWrites=true&w=majority')
db=client.userdata
result=0
uname=''
fname=''
lname=''
hashed_pwd=''
suggestions=['Spend more time together']
p=['Promising','Unpromising']
output=0
app=Flask(__name__,template_folder='templates')
model=pickle.load(open('model.pkl','rb'))
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('/')
@app.route('/signup')
def signup():
    return render_template('signup.html')
@app.route('/testsignup')
def testsignup():
    firstname=request.args.get('firstname')
    lastname=request.args.get('lastname')
    global fname
    fname=firstname
    global lname
    lname=lastname
    username=(request.args.get('username'))
    password=(request.args.get('password')).encode('utf-8')
    global hashed_pwd
    hashed_pwd=bcrypt.hashpw(password, bcrypt.gensalt(10))
    if len(password)<8:
        return render_template('signup.html',check="password must be atleast 8 characters long..")
    else:
        data={'fname':firstname,'lname':lastname,'uname':username,'pwd':hashed_pwd}
        search=db.signupdata.find_one({'uname':username})
        if search is None:
            db.signupdata.insert_one(data)
            return render_template('login.html')
        else:
            return render_template('signup.html',check="username already exists..")
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/testlogin')
def testlogin():
    username=(request.args.get('username'))
    password=(request.args.get('password')).encode('utf-8')
    global uname
    uname=username
    search=db.signupdata.find_one({'uname':username})
    if search is None:
        return render_template('signup.html',check="user doesn't exist, please create an account")
    else:
        data=db.signupdata.find_one({'uname':username},{'pwd':1,'_id':0})
        hashed_pwd=data.get("pwd")
        if bcrypt.checkpw(password, hashed_pwd):
            session['logged_in'] = True
            if(len(fname)==0):
                return render_template('dashboard.html',welcome="hello "+username)
            else:
                return render_template('dashboard.html',welcome="hello "+fname)
        else:
            return render_template('login.html',check='incorrect password..')
    
@app.route('/predict',methods=["post"])
def predict():
    int_features=[(x) for x in request.form.values()]
    int_features=np.array(int_features)
    int_features = int_features[0::2] 
    int_features=list(map(int,int_features))
    final_features=[np.array(int_features)]
    if(int_features[0]<=3):
        suggestions.append('Almost like magic, apology has the power to repair harm, mend relationships, soothe wounds and heal broken hearts. Try forgiving :)')

    if(int_features[7]<=3):
        suggestions.append('A vacation gives you a chance to rediscover one another. Getting away from all of the daily hassles and spending time together in a different place can strip down barriers and help you to rediscover the foundations of what made you a couple at the start of your marriage.')

    if(int_features[12]<=3):
        suggestions.append('Try to find a common interest and spend time on it . It would help start conversations , understand your partner and enjoy the time you spend with them .')

    if(int_features[20]<=3):
        suggestions.append('Know what your patner wants in life and be willing to help each other get there.')

    if(int_features[6]>=3):
        suggestions.append('Effective communication allows good thoughts and feelings to flow between a couple. With the right skills, bickering, hurt feelings and resentment will go way down.')

    if(int_features[32]>=3):
        suggestions.append('Try avoiding use of negative statements about personality of your partner')

    if(int_features[35]>=3):
        suggestions.append('Control your anger and avoid humilation during argument')
    prediction=model.predict(final_features)
    output=round(prediction[0],2)
    global result
    result=output
    db.signupdata.update_one({'uname':uname},{'$set':{'inputs':int_features,'suggestions':suggestions}})
    return render_template('check.html')

@app.route('/form-example', methods=['GET', 'POST'])
def form_example():
   name=request.args.get('name')
   sid_obj = SentimentIntensityAnalyzer()  
   sentiment_dict = sid_obj.polarity_scores(name) 
   if sentiment_dict['compound'] >= 0.05 : 
       s="you are doing great!!keep enjoying your relationship"
   elif sentiment_dict['compound'] <= - 0.05 : 
       s="Your relationship needs effort.It takes lot of effort to make it worth..We are here to help you"
   else : 
       s="Things look good in your relationship!"
   print(s)
   global result
   if(result==0):
       result=10
   else:
       result=5
   db.signupdata.update_one({'uname':uname},{'$set':{'text':s,'result':result}})
   return render_template('final.html',foo=suggestions,res=result,data=s)
@app.route('/verify',methods=['GET','POST'])
def verify():
    return render_template('index.html')
@app.route('/report',methods=['GET','POST'])
def report():
    data=db.signupdata.find_one({'uname':uname},{'_id':0})
    text=data.get("text")
    result=data.get("result")
    suggestions=data.get("suggestions")
    if(suggestions is None):
        return render_template('index.html',data="answer these questions to view report")
    else:
        return render_template('final.html',foo=suggestions,data=text,res=result)
                              
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run()
    
    
