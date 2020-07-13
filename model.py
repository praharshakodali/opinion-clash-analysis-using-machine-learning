
import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

#importing packages 
import numpy as np 
import pandas as pd  
from sklearn.model_selection import train_test_split 
from sklearn.tree import DecisionTreeClassifier 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report, confusion_matrix
import pickle

#importing data 
divorce=pd.read_csv('divorce.csv',sep=';')

#number of rows and columns in our dataset
divorce.shape

#viewing data first 5 lines 
divorce.head()

#sepearting attributes from labels 
X = divorce.drop('Class', axis=1)
y = divorce.get('Class')

#create a train test split
X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=0)

#creating Classifier Object 
clf=DecisionTreeClassifier(max_depth=4)

#train the classifier and fit the estimator 
clf.fit(X_train,y_train)


pickle.dump(clf,open('model.pkl','wb'))
model=pickle.load(open('model.pkl','rb'))