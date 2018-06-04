from flask import Flask, render_template, request, redirect, url_for, g
from pager import Pager
# import sqlite3
import datetime


STATIC_FOLDER = 'static'
APPNAME = 'AMOS East'

app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.update(APPNAME=APPNAME,)

@app.route('/')
def homepage():
    
    # TODO: change camera count to get database number
    camera_count = 10
    return render_template('home.html', camera_count=camera_count)
    
@app.route('/about')
def aboutpage():
    return render_template('about.html')

@app.route('/map')
def mappage():
    # implement google map api functionality here
    return render_template('map.html')
    
@app.route('/submitcam')
def sumbitcam():
    return render_template('submitcam.html')

@app.route('/moreinfo')
def moreinfo():
    return render_template('moreinfo.html')
    

if __name__ == '__main__':
    app.run(debug=True)
