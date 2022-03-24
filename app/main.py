from flask import Flask, request,jsonify
import face_recognition as fr
from pymongo import MongoClient
import numpy as np
from datetime import datetime
import pytz


def get_database():
    #get url of database from mongoDB
    CONNECTION_URL = "<MONGODB_URL>"
    #connect to client
    client = MongoClient(CONNECTION_URL)
    #return database referance by defining its name
    return client['users']
    
def getEncodings():
    dbname=get_database()
    collection_name = dbname["encodings"]
    items=collection_name.find({"category":"encodings"})
    for i in items:
        i.pop("category")
        i.pop("_id")
        known_images=list(i.keys())
        values=list(i.values())
        encodings=[]
        for v in values:
            encodings.append(np.array(v))
        return known_images,encodings


def update_face(imgName,addImg):
    addImage=fr.load_image_file(addImg)
    try:
        image_encoding=list(fr.face_encodings(addImage)[0])
    except IndexError as e:
        return "nil"
    pair={imgName:image_encoding}
    dbname=get_database()
    collection_name = dbname["encodings"]
    items=collection_name.update_one({"category":"encodings"},{'$set':pair})
    return "true"


def compare_faces(textImg):

    known_images,encodings=getEncodings()
    test = fr.load_image_file(textImg)

    try:
        test_encoding = fr.face_encodings(test)[0]
    except IndexError as e:
        return "nil"
    
    # Compare faces 
    results = fr.compare_faces(encodings, test_encoding)    
    print(results)
    if(True in results):
        i=results.index(True)
        return known_images[i].split(".")[0]
    return "nil"

def update_attendance(id,status):
    db= get_database()
    collName=db["logs_new"]
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    date1=now.strftime("%d/%m/%Y")
    time1=now.strftime("%H:%M:%S")
    data={"id":id,"status":status,"date":date1,"time":time1}
    ret =collName.insert_one(data)
    return "1"

app = Flask(__name__)

@app.route('/face_match', methods=['POST'])
def face_match():
    if request.method == 'POST':
        if ('file1' in request.files):  
            file1 = request.files.get('file1')    
            print("I got Image")                 
            ret = compare_faces(file1)  
            if ret!="nil":
                id=ret
                status=file1.filename
                update_attendance(id,status)
            print (ret)  
            return jsonify({"status":ret,"flag":ret=="nil"}) 
        return "Not Handled"

@app.route('/add_face',methods=['POST'])
def add_face():
    if request.method == 'POST':
       if ('file1' in request.files):  
           file1=request.files.get('file1')
           imgName=file1.filename.split(".")[0]
           ret = update_face(imgName,file1)

           return jsonify({"status":ret})

@app.route('/',methods=['GET'])
def hello_world():
    return '<h1>Home Page</h1>'



# if __name__ == "__main__":
# 	app.run(debug=True,port=5001,host="0.0.0.0")
