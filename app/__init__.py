import os
import logging
from typing import Union
from flask import Flask, render_template, request, flash, redirect, url_for, json, session, make_response,Response,send_from_directory,send_file
import requests
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
import datetime
from pathlib import Path
from flask_recaptcha import ReCaptcha
import pandas
import random
from google.cloud import storage
import pdfkit

app = Flask(__name__)
# recaptcha = ReCaptcha(app=app)
app.config['SECRET_KEY'] = 'Srihari@1209'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'spsr'

app.config['RECAPTCHA_ENABLED '] = True
app.config['RECAPTCHA_SITE_KEY'] = '6Ld5cUYlAAAAAKl9KXXfTdtcPehMmPl-154NMdZq'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ld5cUYlAAAAAEKYZTZwxJbiGD2yvgKxSq0qV2tF'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}

app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "static/assets/"

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# recaptcha = ReCaptcha()
# recaptcha.init_app(app)
mysql = MySQL(app)
recaptcha = ReCaptcha(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        Dict = {}
        appliedpost = request.form['JobAppliedFor']
        name = request.form['name']
        gender = request.form['gender']
        fathername = request.form['fatherName']
        DOB = request.form['DOB']
        #datetime_object = datetime.strptime(DOB,'yyyy-mm-dd')
        datetime_object = datetime.datetime.strptime(DOB, "%Y-%m-%d").date()
        age = int(((datetime.date.today() - datetime_object).days / 365))
        birthplace = request.form['placeOfBirth']
        email = request.form['email']
        message1 = request.form['message1']
        message2 = request.form['message2']
        phone = request.form['phone']
        caste = request.form['caste']
        deformity = request.form.getlist('deformity')
        deformity1 = ""
        for ele in deformity:
            deformity1 = deformity1 + ele + "|"
        DisabilityPer = request.form['DisabilityPer']
        motherTongue = request.form['Mother_Tongue']
        general_qualification = request.form['general_qualification']
        technical_qualification = request.form['technical_qualification']
        Address_1 = request.form['Address_1']
        Passed_class_1 = request.form['Passed_class_1']
        Percentage_1 = request.form['Percentage_1']
        uploadCert = request.files['cert_1']
        casteCert = request.files['casteCert']
        profilePic = request.files['profilePic']
        files = [uploadCert, casteCert, profilePic]
        
        emp_reg_no = request.form['emp_reg_no']
        emp_reg_date = request.form['emp_reg_date']
        obt_marks = request.form['obt_marks']
        tot_marks = request.form['tot_marks']
        year_passed = request.form['year_passed']
        
        df = pandas.read_csv("master.csv")
        #count_1 = df.count()
        primary_key = 1000 + len(df.index)
        target = "static/uploads/{}".format(str(primary_key))
        path = []
        project_id = "nellore-342906"
        # Create a Cloud Storage client.
        gcs = storage.Client(project=project_id)
        # Get the bucket that the file will be uploaded to.
        bucket = gcs.get_bucket("nellore-flask")
        num = random.randint(0, 9)
        num = name + str(num) + "/"
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                extension = str(filename.split("."))
                extension = str(extension[1])
                blob = bucket.blob(num+filename)
                blob.upload_from_string(
                     file.read(), content_type=file.content_type
                    )
                blob.make_public()
                #Path(target).mkdir(parents=True, exist_ok=True)
                #file.save(os.path.join(target, filename))
                #path.append(os.path.join(target, filename))
                path.append(blob.public_url)
        fields = (
            appliedpost, name, gender, fathername, DOB, age, birthplace, message1, message2, email, phone, caste,
            path[0], path[1], deformity, DisabilityPer, motherTongue, general_qualification, technical_qualification,
            Address_1, Passed_class_1, Percentage_1, path[2])
        Dict["id"] = primary_key
        Dict["appliedpost"] = appliedpost
        Dict["name"] = name
        Dict["gender"] = gender
        Dict["fathername"] = fathername
        Dict["DOB"] = DOB
        Dict["age"] = age
        Dict["birthplace"] = birthplace
        Dict["perm_address"] = message1
        Dict["temp_address"] = message2
        Dict["email"] = email
        Dict["phone"] = phone
        Dict["caste"] = caste
        Dict["caste_cert"] = path[1]
        Dict["profile_pic"] = path[2]
        Dict["deformity"] = deformity1
        Dict["DisabilityPer"] = DisabilityPer
        Dict["motherTongue"] = motherTongue
        Dict["general_qualification"] = general_qualification
        Dict["technical_qualification"] = technical_qualification
        Dict["address_1"] = Address_1
        Dict["passed_class"] = Passed_class_1
        Dict["pass_percentage"] = Percentage_1
        Dict["education_cert"] = path[0]
        
        
        Dict["emp_reg_no"] = emp_reg_no
        Dict["emp_reg_date"] = emp_reg_date
        Dict["obt_marks"] = obt_marks
        Dict["tot_marks"] = tot_marks
        Dict["year_passed"] = year_passed
        data = pandas.DataFrame(Dict, index=[0])
        bucket.blob('master.csv').upload_from_string(data.to_csv(index=False, header=True, mode="a"), 'text/csv')
        data.to_csv("master.csv", index=True, header=False, mode="a")
        return render_template('application.html', request=Dict)
    return render_template('generic.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        username = request.form['name']
        password = request.form['password']
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
        res = make_response(render_template('admin.html', msg=msg))
        res.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
        return res
    else:
        msg = 'Incorrect submit !'
    return render_template('login.html', sitekey=app.config['RECAPTCHA_SITE_KEY'], msg=msg)


@app.route('/admin',methods=['GET', 'POST'])
def admin():
    return render_template('home.html')


@app.route('/logout',methods=['GET', 'POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return render_template('generic.html')


@app.errorhandler(500)
def server_error(e: Union[Exception, int]) -> str:
    logging.exception("An error occurred during a request.")
    return (
        """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(
            e
        ),
        500,
    )


@app.route('/download',methods=['GET', 'POST'])
def download():
    #config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    #out = render_template("application.html")
    # PDF options
    #options = {
    #    "orientation": "landscape",
    #    "page-size": "A4",
    #    "margin-top": "1.0cm",
    #    "margin-right": "1.0cm",
    #    "margin-bottom": "1.0cm",
    #    "margin-left": "1.0cm",
    #    "encoding": "UTF-8",
    #}
    # Build PDF from HTML
    #pdf = pdfkit.from_string(out, "out.pdf", options=options,configuration=config)
    # Download the PDF
    #return send_from_directory(filename="masters.csv")
    #return Response(pdf, mimetype="application/pdf")
    return send_file("master.csv")

@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large', 413

if __name__ == '__main__':
    app.run(host='0.0.0.0')
