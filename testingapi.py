import json
import subprocess
from flask import Flask,render_template,redirect,url_for,jsonify

username = str(subprocess.check_output("uname -a",shell=True)) # Get the the username of the computer reading from the client computer 
Getusername = username.split("-")[0].split(" ")[1]  #Get the username
HOME_PATH = "/home/"+str(Getusername)+"/Automaticsoftware/"

app = Flask(__name__) 
@app.route("/components") 
def index(): 
     jsonfile = open(HOME_PATH+"e_components.json",'r')
     data = json.load(jsonfile)    
     return jsonify(data)
if __name__ == '__main__': 
          
       app.run(debug=True,host='0.0.0.0',port=8000)
