import sqlite3
import numpy as np # linear algebra
import pandas as pd  ##
import math
from datetime import datetime
import time
import json
import requests
import ast
from flask import Response
from flask import Flask, jsonify
from flask import request, send_from_directory
from flask import render_template, redirect, url_for
from flask_cors import CORS
import logging
import uuid

#ssh -i /Users/dimosanagnostopoulos/Downloads/newkeypairproject.pem ec2-user@ec2-52-91-51-228.compute-1.amazonaws.com
#scp -i /Users/dimosanagnostopoulos/Downloads/newkeypairproject.pem routes.py ec2-user@ec2-52-91-51-228.compute-1.amazonaws.com:/home/ec2-user/movierama/.
#scp -i /Users/dimosanagnostopoulos/Downloads/newkeypairproject.pem -r /Users/dimosanagnostopoulos/Desktop/movierama_frontend/movierama/dist ec2-user@ec2-52-91-51-228.compute-1.amazonaws.com:/home/ec2-user/movierama/

# put server's host name to dist vue axios link before scping dist to server
#cur.execute("CREATE TABLE MOVIES(Title TEXT, Description TEXT, User TEXT, Date_of_pub TEXT, Likes INTEGER, Hates INTEGER,Like_Users TEXT,Hate_Users TEXT)")

def days_hours(td):
    return [td.days, td.seconds//3600]


app = Flask(__name__, static_url_path='', static_folder='/home/ec2-user/movierama/dist/', template_folder='/home/ec2-user/movierama/dist')
cors = CORS(app)

@app.route("/", defaults={"path": ""})
@app.route("/<string:path>")
@app.route("/<path:path>")
def index(path):
    return app.send_static_file("index.html")



@app.route("/get_movies", methods=['POST']) 
def get_movies():
    try:
        content = request.get_json()
        user = content["user"].upper()
        sort = content["sort"]
        con = sqlite3.connect("movies.db")
        cur = con.cursor()
        if user != "":
            res = cur.execute("SELECT * FROM MOVIES where User = ?",[user]).fetchall()
        elif user == "":
            res = cur.execute("SELECT * FROM MOVIES").fetchall()
        res = pd.DataFrame(res,columns=["Title", "Description","User","Date_of_pub","Likes","Hates","Like_Users","Hate_Users"])
        if sort == "likes":
        	res = res.sort_values(by=["Likes"],ascending=False).reset_index().drop(columns=["index"])
        elif sort == "hates":
        	res = res.sort_values(by=["Hates"],ascending=False).reset_index().drop(columns=["index"])
        elif sort == "date":
        	res = res.sort_values(by=["Date_of_pub"],ascending=False).reset_index().drop(columns=["index"])
        con.commit()
        con.close()
        result = []
        for i in res.values.tolist():
            result.append({
            	"title":i[0],
            	"description":i[1],
            	"user":i[2],
            	"date": days_hours(datetime.now() - datetime.strptime(i[3], '%Y-%m-%d %H:%M:%S')),
            	"likes":i[4],
            	"hates":i[5],
            	"like_users":ast.literal_eval(i[6]),
            	"hate_users":ast.literal_eval(i[7])	
            	})
        response = {
            'success': True,
            'message': "",
            'data': result
        }
    except Exception as e:
        logging.exception("could not run anything")
        response = {
            'success': False,
            'message': str(e),
            'data': "error"        
        }
    return json.dumps(response)



@app.route("/insert_movie", methods=['POST']) 
def insert_movie():
    try:
        content = request.get_json()
        con = sqlite3.connect("movies.db")
        title = content["title"]
        description = content["description"]
        user = content["user"].upper()
        date_of_pub = str(datetime.now()).split(".")[0]
        cur = con.cursor()
        res = cur.execute("SELECT * FROM MOVIES").fetchall()
        res = pd.DataFrame(res,columns=["Title", "Description","User","Date_of_pub","Likes","Hates","Like_Users","Hate_Users"])
        res = res[res["Title"] == title].reset_index().drop(columns=["index"])
        if len(res) == 0:
            cur.execute("INSERT INTO MOVIES VALUES(?, ?, ?, ?, ?, ?, ?, ?)", [title,description,user,date_of_pub,0,0,"[]","[]"])
        con.commit()
        con.close()
        response = {
            'success': True,
            'message': "",
            'data': ""
        }
    except Exception as e:
        logging.exception("could not run anything")
        response = {
            'success': False,
            'message': str(e),
            'data': "error"        
        }
    return json.dumps(response)


@app.route("/opinion_movie", methods=['POST']) 
def opinion_movie():
    try:
        content = request.get_json()
        con = sqlite3.connect("movies.db")
        title = content["title"]
        opinion_user = content["opinion_user"].upper()
        opinion = content["opinion"]
        date_of_pub = "" # current time
        cur = con.cursor()
        res = cur.execute("SELECT * FROM MOVIES").fetchall()
        res = pd.DataFrame(res,columns=["Title", "Description","User","Date_of_pub","Likes","Hates","Like_Users","Hate_Users"])
        res = res[res["Title"] == title].reset_index().drop(columns=["index"])
        if res["User"].values.tolist()[0] != opinion_user:
            if opinion == "like":
                if opinion_user not in ast.literal_eval(res["Like_Users"].values.tolist()[0]):
                    existing_likes = res["Likes"].values.tolist()[0]
                    new_likes = existing_likes + 1
                    new_likes_users = ast.literal_eval(res["Like_Users"].values.tolist()[0])
                    new_likes_users.append(opinion_user)
                    cur.execute("update MOVIES set Likes = ? where Title = ?", [new_likes,title])
                    cur.execute("update MOVIES set Like_Users = ? where Title = ?", [str(new_likes_users),title])
                    if opinion_user in ast.literal_eval(res["Hate_Users"].values.tolist()[0]):
                        existing_hates = res["Hates"].values.tolist()[0]
                        new_hates = existing_hates - 1
                        new_hates_users = ast.literal_eval(res["Hate_Users"].values.tolist()[0])
                        new_hates_users.remove(opinion_user)
                        cur.execute("update MOVIES set Hates = ? where Title = ?", [new_hates,title])
                        cur.execute("update MOVIES set Hate_Users = ? where Title = ?", [str(new_hates_users),title])
                elif opinion_user in ast.literal_eval(res["Like_Users"].values.tolist()[0]):
                    existing_likes = res["Likes"].values.tolist()[0]
                    new_likes = existing_likes - 1
                    new_likes_users = ast.literal_eval(res["Like_Users"].values.tolist()[0])
                    new_likes_users.remove(opinion_user)
                    cur.execute("update MOVIES set Likes = ? where Title = ?", [new_likes,title])
                    cur.execute("update MOVIES set Like_Users = ? where Title = ?", [str(new_likes_users),title])
            elif opinion == "hate":
                if opinion_user not in ast.literal_eval(res["Hate_Users"].values.tolist()[0]):
                    existing_hates = res["Hates"].values.tolist()[0]
                    new_hates = existing_hates + 1
                    new_hates_users = ast.literal_eval(res["Hate_Users"].values.tolist()[0])
                    new_hates_users.append(opinion_user)
                    cur.execute("update MOVIES set Hates = ? where Title = ?", [new_hates,title])
                    cur.execute("update MOVIES set Hate_Users = ? where Title = ?", [str(new_hates_users),title])
                    if opinion_user in ast.literal_eval(res["Like_Users"].values.tolist()[0]):
                        existing_likes = res["Likes"].values.tolist()[0]
                        new_likes = existing_likes - 1
                        new_likes_users = ast.literal_eval(res["Like_Users"].values.tolist()[0])
                        new_likes_users.remove(opinion_user)
                        cur.execute("update MOVIES set Likes = ? where Title = ?", [new_likes,title])
                        cur.execute("update MOVIES set Like_Users = ? where Title = ?", [str(new_likes_users),title])
                elif opinion_user in ast.literal_eval(res["Hate_Users"].values.tolist()[0]):
                    existing_hates = res["Hates"].values.tolist()[0]
                    new_hates = existing_hates - 1
                    new_hates_users = ast.literal_eval(res["Hate_Users"].values.tolist()[0])
                    new_hates_users.remove(opinion_user)
                    cur.execute("update MOVIES set Hates = ? where Title = ?", [new_hates,title])
                    cur.execute("update MOVIES set Hate_Users = ? where Title = ?", [str(new_hates_users),title])
        con.commit()
        con.close()
        response = {
            'success': True,
            'message': "",
            'data': ""
        }
    except Exception as e:
        logging.exception("could not run anything")
        response = {
            'success': False,
            'message': str(e),
            'data': "error"        
        }
    return json.dumps(response)







if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002, use_reloader=False)




