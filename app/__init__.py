import os

from flask import Flask, render_template, request, flash, redirect, url_for, json, session, make_response
import requests
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
# recaptcha = ReCaptcha(app=app)
app.config['SECRET_KEY'] = 'Srihari@1209'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'spsr'

app.config['RECAPTCHA_ENABLED '] = True
app.config['RECAPTCHA_SITE_KEY'] = '6LcSZ6QeAAAAAHdmSmKbAK1mnIJgUZ7xOqN1ZVB8'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcSZ6QeAAAAAF9iEGqQaV_q1-k8nSd8589BBQHu'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "static/assets/"

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# recaptcha = ReCaptcha()
# recaptcha.init_app(app)
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        print("Welcome")
        appliedpost = request.form['JobAppliedFor']
        name = request.form['name']
        gender = request.form['gender']
        fathername = request.form['fatherName']
        DOB = request.form['DOB']
        # datetime_object = datetime.strptime(DOB)
        datetime_object = datetime.fromisoformat(DOB)
        age = ((datetime.today() - datetime_object).days / 365)
        print(age)
        birthplace = request.form['placeOfBirth']
        email = request.form['email']
        message1 = request.form['message1']
        message2 = request.form['message2']
        phone = request.form['phone']
        print(phone)
        caste = request.form['caste']
        # print(caste)
        # casteCert = request.form['casteCert']
        # profilePic = request.form['profilePic']
        # VisuallyImpaired = request.form['VisuallyImpaired']
        # HearingImpaired = request.form['HearingImpaired']
        # OrthopedicallyHandicapped = request.form['OrthopedicallyHandicapped']
        # MentalIllness = request.form['MentalIllness']
        # print("welcome1")
        deformity = request.form.getlist('deformity')
        # print(deformity)
        DisabilityPer = request.form['DisabilityPer']
        # print(DisabilityPer)
        motherTongue = request.form['Mother_Tongue']
        # print(motherTongue)
        general_qualification = request.form['general_qualification']
        # print(general_qualification)
        technical_qualification = request.form['technical_qualification']
        # print(technical_qualification)
        Address_1 = request.form['Address_1']
        print(Address_1)
        Passed_class_1 = request.form['Passed_class_1']
        print(Passed_class_1)
        Percentage_1 = request.form['Percentage_1']
        print(Percentage_1)
        uploadCert = request.files['cert_1']
        casteCert = request.files['casteCert']
        profilePic = request.files['profilePic']
        files = [uploadCert, casteCert, profilePic]
        print(files)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        folder = cursor.execute('select max(id) from spsr.applications;')
        target = "static/uploads/{}".format(str(folder))
        path = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                extension = str(filename.split("."))
                extension = str(extension[1])
                print(filename)
                #source = app.config['UPLOAD_FOLDER'] + "/tmp" + filename
                #destination = app.config['UPLOAD_FOLDER'] + "/" + name + datetime.datetime.now() + "." + extension
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], "tmp", filename))
                #user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(folder + 1))
                os.mkdir(target, exists_ok=True)
                file.save(os.path.join(target, filename))
                path.append(os.path.join(target, filename))
                print("os.path.join(app.config['UPLOAD_FOLDER']", filename)
        fields = (
            appliedpost, name, gender, fathername, DOB, age, birthplace, message1, message2, email, caste,
            path[0], path[1], deformity, DisabilityPer, motherTongue, general_qualification, technical_qualification,
            Address_1, Passed_class_1, Percentage_1, path[2])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('"INSERT INTO spsr.applications values(%s,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,'
                       '%s,%s,%d,%s)"',
                       fields)
        return render_template('home.html')
        print("Welcome")
    return render_template('generic.html', sitekey=app.config['RECAPTCHA_SITE_KEY'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        username = request.form['name']
        password = request.form['password']
        captcha_response = request.form['g-recaptcha-response']
        if is_human(captcha_response):
            status = "Detail submitted successfully."
        else:
            status = "Sorry ! Please Check Im not a robot."
        flash(status)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE name = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            msg = 'Logged in successfully !'
        else:
            msg = 'Incorrect username / password !'
        res = make_response(render_template('home.html', msg=msg))
        res.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
        return res
    else:
        msg = 'Incorrect submit !'
    return render_template('login.html', sitekey=app.config['RECAPTCHA_SITE_KEY'], msg=msg)


@app.route('/admin')
def admin():
    return render_template('home.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return 'Logout'


def is_human(captcha_response):
    """ Validating recaptcha response from google server
            Returns True captcha test passed for submitted form else returns False."""
    payload = {'response': captcha_response, 'secret': app.config['RECAPTCHA_PRIVATE_KEY']}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
