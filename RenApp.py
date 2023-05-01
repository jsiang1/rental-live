from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'rental'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/index", methods=['POST'])
def index():
    return render_template('index.html')

@app.route("/form", methods=['POST'])
def form():
    return render_template('form.html')

@app.route("/addren", methods=['POST'])
def AddEmp():
    c_name = request.form['c_name']
    c_ssm = request.form['c_ssm']
    email = request.form['email']
    mobile = request.form['mobile']
    cat = request.form['cat']
    ans = request.form['ans']
    ren_image_file = request.files['ren_image_file']

    insert_sql = "INSERT INTO rental VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if ren_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (c_name, c_ssm, email, mobile, cat, ans))
        db_conn.commit()
        # Uplaod image file in S3 #
        ren_image_file_name_in_s3 = "c-ssm-" + str(c_ssm) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=ren_image_file_name_in_s3, Body=ren_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                ren_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('index.html', name=c_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

