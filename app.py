from flask import *
import json
from collections import OrderedDict
import jwt
import datetime
from datetime import datetime as dt_datetime 
from datetime import datetime as posttime
import uuid
import boto3
import pymysql
from dotenv import load_dotenv
import os
import mysql.connector
from flask_socketio import SocketIO, emit, join_room, leave_room
from uuid import UUID


load_dotenv()


secret_key = os.getenv("app.secret_key")
s3 = boto3.client("s3", aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
CloudFrontDomainName = os.getenv("CFDDomainName")


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = secret_key  # Use your secret key here

socketio = SocketIO(app)  # Initialize Flask-SocketIO


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/application")
def application():
    return render_template("application.html")

@app.route("/favorite")
def favorite():
    return render_template("favorite.html")

@app.route("/mypost")
def mypost():
    return render_template("mypost.html")

@app.route("/membership")
def membership():
    return render_template("membership.html")

@app.route("/schedule")
def schedule():
    return render_template("schedule.html")

@app.route("/message")
def message():
    return render_template("message.html")

@app.route('/api/user', methods=["POST"])
def signup():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )
    # 從name中抓取位置獲取資料
    signupName = request.form["signupName"]
    signupEmail = request.form["signupEmail"]
    signupPassword = request.form["signupPwd"]
    singupMemberIcon = "https://d202sf5j86ciff.cloudfront.net/fa4f6b4b-91ac-46c5-8068-b48e61b0426d.jpg"

    cursor = con.cursor()

    cursor.execute("SELECT * FROM membership WHERE memberEmail = %s", (signupEmail,))
    existing_user = cursor.fetchone()

    if existing_user:
        con.close()
        signup_error_response = {"error": True, "message": "The email address is already in use!"}
        return jsonify(signup_error_response), 400
    try:
        cursor.execute("INSERT INTO membership (memberId, memberEmail, memberPwd, memberIcon) VALUES (%s, %s, %s, %s)",
                       (signupName, signupEmail, signupPassword, singupMemberIcon))
        con.commit()
        con.close()
        signup_success_response = {"ok": True, "message": "Your registration was successful"}
        return jsonify(signup_success_response), 200
    except Exception as e:
        con.close()
        signup_error_response = {"error": True, "message": "Registration failure"}
        return jsonify(signup_error_response), 500

@app.route('/api/user/auth', methods=["PUT"])
def signin():
    try:
        con = pymysql.connect(        
            host=os.getenv("host"),
            port=3306,
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        signinEmail = request.form["signinEmail"]
        signinPassword = request.form["signinPwd"]
        cursor = con.cursor()

        cursor.execute("SELECT * FROM membership WHERE memberEmail = %s AND memberPwd =%s" , (signinEmail, signinPassword))
        signinMembership = cursor.fetchall()
        for signinRow in signinMembership:
            if signinRow[2] == signinEmail and signinRow[3] == signinPassword:
                user_info = {
                   "id": signinRow[0],
                   "name": signinRow[1],
                   "email": signinRow[2]
                }
                expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                secret_key = os.getenv("app.secret_key")
                token = jwt.encode({"data": user_info, "exp": expiration_time}, secret_key, algorithm="HS256")
                return jsonify({"token": token})
        return jsonify({"error":True, "message":"Incorrect username or password"}), 400 
    except Exception as e:
        signin_error_response = {
        "error": True,
        "message": "請按照情境提供對應的錯誤訊息"
        }
        return jsonify(signin_error_response), 500 

def authenticate_token(f):
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        secret_key = os.getenv("app.secret_key")
        if token is None:
            return jsonify(data=None)
        
        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            return jsonify(data=None)
        
        jwt_token = token_parts[1]
        
        try:
            decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
            token_user_info = decode_token.get("data", None)
            if token_user_info is None:
                return jsonify(data=None)
            return jsonify(data=token_user_info)
        except jwt.ExpiredSignatureError:
            return jsonify(data=None), 400
        except jwt.InvalidTokenError as e:
            return jsonify(data=None), 400
    return decorated

@app.route("/api/user/auth", methods=["GET"])
@authenticate_token
def user_auth(current_user):
    return jsonify(data=current_user)

@app.route("/api/jobPost", methods=["GET"])
def getJobPost():
    try:
        con = pymysql.connect(
            host=os.getenv("host"),
            port=3306,
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )

        keyword = request.args.get('keyword')
        postcode = request.args.get('postalCode')
        cursor = con.cursor()

        if keyword:
            query = "SELECT * FROM jobs WHERE ( title LIKE %s ) ORDER BY postTime DESC"
            cursor.execute(query, ('%' + keyword + '%',))

        elif postcode:
            query = "SELECT * FROM jobs WHERE zipcode = %s ORDER BY postTime DESC"
            cursor.execute(query, (postcode,))

        else:
            query = "SELECT * FROM jobs ORDER BY postTime DESC"
            cursor.execute(query)

        result = cursor.fetchall()

        job_posts = []
        for row in result:
            job_post = {
            'post_id':row[1],
            'job_title': row[3],
            'job_description': row[4],
            'job_date':row[5],
            'job_start_time':row[6],
            'job_end_time':row[7],
            'job_zipcode':row[8],
            'job_city':row[9],
            'job_location':row[10],
            'job_salary':row[11],
            'job_others':row[12],
            'number_of_job_positions':row[13],
            'post_time':row[14],
            'pay_date':row[15],
            'pay_method':row[16]
            }

            email = row[2]
            if email:
                query = "SELECT * FROM membership WHERE memberEmail = %s"
                cursor.execute(query, (email,))
                memberID = cursor.fetchone()

                if memberID:
                    job_post['memberID'] = memberID[1]
                    job_post["memberIcon"] = memberID[4]

            job_posts.append(job_post)

        cursor.close()
        con.close()

        return jsonify(job_posts)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/jobPost', methods=["POST"])
def updateJobPost():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )
    jobTitle = request.form["jobTitle"]
    jobDetail = request.form["jobDetail"]
    jobDate = request.form["jobDate"]
    jobStartTime = request.form["jobStartTime"]
    jobEndTime = request.form["jobEndTime"]
    jobZipcode = request.form["zipcode"]
    jobCounty = request.form["county"]
    jobCity = request.form["district"]
    jobLocation = request.form["jobLocation"]
    jobSalary = request.form["jobSalary"]
    jobOthers = request.form["jobOthers"]
    payDates = request.form["payDate"]
    paymentMethod = request.form["paymentMethod"]
    numberOfJobPositions = request.form["numberOfJobPositions"]
    # Format to get only the year, month, and day
    current_time = posttime.now()
    formatted_date = current_time.strftime("%Y-%m-%d")
    postTime = formatted_date 
    postId = str(uuid.uuid4())
    jobcityName = jobCounty + jobCity

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:
        if not token or not token.startswith("Bearer "):
            raise InvalidTokenError("Invalid or missing token")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']
        cursor.execute("SELECT * FROM jobs WHERE memberEmail = %s AND title = %s AND detail = %s AND jobDate = %s AND start_time = %s AND end_time = %s AND zipcode = %s AND city = %s AND location = %s AND salary = %s AND jobOthers = %s AND numberOfJobPositions = %s AND postTime = %s AND payDates = %s AND paymentMethod = %s",
               (user_email, jobTitle, jobDetail, jobDate, jobStartTime, jobEndTime, jobZipcode, jobcityName, jobLocation, jobSalary, jobOthers, numberOfJobPositions, postTime, payDates, paymentMethod))

        existing_record = cursor.fetchone()
        print(existing_record)

        if existing_record:
            # If the record already exists, you can handle it accordingly
            response_data = {"error": True, "message": "The position has been posted!", "token": token}
        else:
    # Insert the job post into the database
            cursor.execute("INSERT INTO jobs (memberEmail, title, detail, jobDate, start_time, end_time, zipcode, city, location, salary, jobOthers, numberOfJobPositions, postTime, payDates, paymentMethod, postId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s, %s, %s, %s, %s)",
                (user_email, jobTitle, jobDetail, jobDate, jobStartTime, jobEndTime, jobZipcode, jobcityName, jobLocation, jobSalary, jobOthers, numberOfJobPositions, postTime, payDates, paymentMethod, postId))
            con.commit()
            con.close()

            response_data = {"ok": True, "message": "Posted successfully!", "token": token}

        return jsonify(response_data), 200

    except Exception as e:
        con.rollback()
        con.close()
        erro_response_data = {"error": True, "message": "Failed to post the positon!", "token": token}
        return jsonify({erro_response_data}), 500

@app.route("/api/jobPost/<postId>")
def get_job_post(postId):
    try:
        con = pymysql.connect(        
            host=os.getenv("host"),
            port=3306,
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )

        cursor = con.cursor()

        query = "SELECT * FROM jobs WHERE postId = %s"
        cursor.execute(query, (postId,))
        data = cursor.fetchall()

        if len(data) == 0:
            error_response = {
                "error": True,
                "message": "No job post found with the provided postId"
            }
            return json.dumps(error_response, ensure_ascii=False).encode('utf8'), 404  # Use 404 for resource not found

        row = data[0]
        job_data = {
            'postId': row[1],  
            'job_title': row[3],
            'job_description': row[4],
            'job_date':row[5],
            'job_start_time':row[6],
            'job_end_time':row[7],
            'job_zipcode':row[8],
            'job_city':row[9],
            'job_location':row[10],
            'job_salary':row[11],
            'job_others':row[12],
            'number_of_job_positions':row[13],
            'pay_date':row[15],
            'pay_method':row[16],
        }

        email = row[2]  # Replace 'email' with the actual column name in your jobs table
        if email:
            query = "SELECT * FROM membership WHERE memberEmail = %s"
            cursor.execute(query, (email,))
            memberID = cursor.fetchone()

            if memberID:
                job_data['memberID'] = memberID[1]
                job_data["memberIcon"] = memberID[4]

        response = {"data": job_data}
        return json.dumps(response, ensure_ascii=False).encode('utf8')


    except Exception as e:
        error_response = {
            "error": True,
            "message": str(e)  # Provide details about the error
        }
        return json.dumps(error_response, ensure_ascii=False).encode('utf8'), 500
    finally:
        cursor.close()
        con.close()

@app.route("/api/applicant/<postId>")
def getapplicant(postId):
    try:
        con = pymysql.connect(
            host=os.getenv("host"),
            port=3306,
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )

        cursor = con.cursor()

        query = "SELECT * FROM applications WHERE postId = %s"
        cursor.execute(query, (postId,))
        data = cursor.fetchall()

        result_data = []

        for row in data:
            current_job_data = {
                'postId': row[1],
                'applicantEmail': row[2],
                'positionStatus': row[3]
            }

            email = row[2]
            if email:
                query = "SELECT * FROM membership WHERE memberEmail = %s"
                cursor.execute(query, (email,))
                member_data = cursor.fetchall()

                if member_data:
                    # Assuming 'member_data' contains only one row
                    current_job_data['memberId'] = member_data[0][1]
                    current_job_data['memberIcon'] = member_data[0][4]

            result_data.append(current_job_data)

        response = {"data": result_data}
        return json.dumps(response, ensure_ascii=False).encode('utf8')

    except Exception as e:
        error_response = {
            "error": True,
            "message": str(e)  # Provide details about the error
        }
        return json.dumps(error_response, ensure_ascii=False).encode('utf8'), 500
    finally:
        cursor.close()
        con.close()


@app.route("/api/jobPost/<postId>", methods=["POST"])
def savePosition(postId):
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']
        post_id = postId

        # Check if the post with the same postId already exists
        cursor.execute("SELECT * FROM saveposition WHERE memberEmail = %s AND postId = %s", (user_email, post_id))
        existing_record = cursor.fetchone()

        if existing_record:
            # If the record already exists, you can handle it accordingly
            response_data = {"ok": True, "message": "This position has been saved!", "token": token}
        else:
            # Insert the job post into the database
            cursor.execute("INSERT INTO saveposition (memberEmail, postId) VALUES (%s, %s)", (user_email, post_id))
            con.commit()
            response_data = {"ok": True, "message": "Saved successfully", "token": token}

        con.close()

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": "Failed to save the positon!", "token": token}
        return jsonify(error_response_data), 500


@app.route("/api/jobPost/<postId>", methods=["DELETE"])
def cancelSavePosition(postId):
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:
        if not token or not token.startswith("Bearer "):
            raise InvalidTokenError("Invalid or missing token")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        # Use postId directly as a UUID
        post_id = UUID(postId)

        # Check if the post with the same postId already exists
        cursor.execute("SELECT * FROM saveposition WHERE memberEmail = %s AND postId = %s", (user_email, post_id))
        existing_record = cursor.fetchone()

        if existing_record:
            delete_saveposition_query = "DELETE FROM saveposition WHERE memberEmail = %s AND postId = %s"
            cursor.execute(delete_saveposition_query, (user_email, post_id))
            con.commit()
            response_data = {"ok": True, "message": "Unsave the position!", "token": token}
        else:
            response_data = {"ok": True, "message": "Error", "token": token}

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        error_response_data = {"error": True, "message": "Failed to unsave the positon!", "token": token}
        return jsonify(error_response_data), 500
    finally:
        con.close()



@app.route("/api/jobApply/<postId>", methods=["POST"])
def jobApply(postId):
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']
        post_id = postId


        # Check if the post with the same postId already exists
        cursor.execute("SELECT * FROM applications WHERE applicantEmail = %s AND postId = %s", (user_email, post_id))
        existing_record = cursor.fetchone()

        if existing_record:
            # If the record already exists, you can handle it accordingly
            response_data = {"ok": True, "message": "You have already applied this position! ", "token": token}
        else:
            # Insert the job post into the database
            cursor.execute("INSERT INTO applications (applicantEmail, postId, positionStatus) VALUES (%s, %s, %s)", (user_email, post_id, 1))
            con.commit()
            response_data = {"ok": True, "message": "You have applied successfully!", "token": token}

        con.close()

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": "Failed to apply the position! ", "token": token}
        return jsonify(error_response_data), 500


@app.route("/api/createMessage/<postId>", methods=["POST"])
def createMessage(postId):
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        senderEmail = token_user_info['email']
        post_id = postId

        cursor.execute("SELECT * FROM jobs WHERE postId = %s", (post_id))
        postInformation = cursor.fetchone()
        receiverEmail = postInformation[2]

        cursor.execute("SELECT * FROM message WHERE senderEmail = %s AND receiverEmail = %s", (senderEmail, receiverEmail))
        existingSender = cursor.fetchone()

        cursor.execute("SELECT * FROM message WHERE senderEmail = %s AND receiverEmail = %s", (receiverEmail, senderEmail))
        existingReceiver = cursor.fetchone()


        if existingSender or existingReceiver:
            # If the record already exists, you can handle it accordingly
            response_data = {"ok": True, "message": "The message has already existed!", "token": token}
        else:
            roomId = str(uuid.uuid4())
            cursor.execute("INSERT INTO message (senderEmail, receiverEmail, roomId) VALUES (%s, %s, %s)", (senderEmail, receiverEmail, roomId))
            con.commit()
            response_data = {"ok": True, "message": "Successfully sent the message.", "token": token}

        con.close()

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": "應徵職缺失敗", "token": token}
        return jsonify(error_response_data), 500

@app.route("/api/confirmPosition/<postId>/<applicationEmail>", methods=["POST"])
def confirmPosition(postId, applicationEmail):
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        # Validate the JWT token
        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")
        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])

        # Get user information from the decoded token
        token_user_info = decode_token.get("data", None)
        post_id = UUID(postId)
        print(post_id)
        application_email = applicationEmail
        print(application_email)

        # Update the position status in the database
        cursor.execute("UPDATE applications SET positionStatus = %s WHERE applicantEmail = %s AND postId = %s", (2, application_email, post_id))
        response_data = {"ok": True, "message": "Your changes have been successfully saved!", "token": token}
        con.commit()  # Commit the changes to the database
        con.close()

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": f"Failed to save tour changes: {str(e)}", "token": token}
        return jsonify(error_response_data), 500

@app.route("/api/cancelConfirmPosition/<postId>/<applicationEmail>", methods=["POST"])
def cancelConfirmPosition(postId, applicationEmail):
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        # Validate the JWT token
        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")
        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])

        # Get user information from the decoded token
        token_user_info = decode_token.get("data", None)
        post_id = UUID(postId)
        print(post_id)
        application_email = applicationEmail
        print(application_email)

        # Update the position status in the database
        cursor.execute("UPDATE applications SET positionStatus = %s WHERE applicantEmail = %s AND postId = %s", (1, application_email, post_id))
        response_data = {"ok": True, "message": "Your changes have been successfully saved!", "token": token}
        con.commit()  # Commit the changes to the database
        con.close()

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": f"Failed to save tour changes: {str(e)}", "token": token}
        return jsonify(error_response_data), 500

@app.route("/api/declinePosition/<postId>/<applicationEmail>", methods=["POST"])
def declinePosition(postId, applicationEmail):
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        # Validate the JWT token
        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")
        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])

        # Get user information from the decoded token
        token_user_info = decode_token.get("data", None)
        post_id = UUID(postId)
        print(post_id)
        application_email = applicationEmail
        print(application_email)

        # Update the position status in the database
        cursor.execute("UPDATE applications SET positionStatus = %s WHERE applicantEmail = %s AND postId = %s", (3, application_email, post_id))
        response_data = {"ok": True, "message": "Your changes have been successfully saved!", "token": token}
        con.commit()  # Commit the changes to the database
        con.close()

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": f"Failed to save tour changes: {str(e)}", "token": token}
        return jsonify(error_response_data), 500

@app.route("/api/cancelDeclinePosition/<postId>/<applicationEmail>", methods=["POST"])
def cancelDeclinePosition(postId, applicationEmail):
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        # Validate the JWT token
        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")
        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])

        # Get user information from the decoded token
        token_user_info = decode_token.get("data", None)
        post_id = UUID(postId)
        print(post_id)
        application_email = applicationEmail
        print(application_email)

        # Update the position status in the database
        cursor.execute("UPDATE applications SET positionStatus = %s WHERE applicantEmail = %s AND postId = %s", (1, application_email, post_id))
        response_data = {"ok": True, "message": "Your changes have been successfully saved!", "token": token}
        con.commit()  # Commit the changes to the database
        con.close()

        return jsonify(response_data), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": f"Failed to save tour changes: {str(e)}", "token": token}
        return jsonify(error_response_data), 500
    
@app.route("/api/saveposition")
def loadingFav():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        # Retrieve all saved post IDs for the user
        cursor.execute("SELECT postId FROM saveposition WHERE memberEmail = %s", (user_email,))
        saved_post_ids = [row[0] for row in cursor.fetchall()]

        # Fetch job details for each saved post ID
        myfavJob = []
        for post_id in saved_post_ids:
    
            cursor.execute("SELECT * FROM jobs WHERE postId = %s", (post_id,))
            save_details = cursor.fetchone()
            if save_details:
                save_post = {
                'post_id':save_details[1],
                'job_title': save_details[3],
                'job_description': save_details[4],
                'job_date':save_details[5],
                'job_start_time':save_details[6],
                'job_end_time':save_details[7],
                'job_zipcode':save_details[8],
                'job_city':save_details[9],
                'job_location':save_details[10],
                'job_salary':save_details[11],
                'job_others':save_details[12],
                'number_of_job_positions':save_details[13],
                'post_time':save_details[14],
                'pay_date':save_details[15],
                'pay_method':save_details[16]
            }
            email = save_details[2],
            print(email)
            if email:
                query = "SELECT * FROM membership WHERE memberEmail = %s"
                cursor.execute(query, (email,))
                memberId = cursor.fetchone()
                print(memberId)

                if memberId:
                    save_post['memberId'] = memberId[1]
                    save_post["memberIcon"] = memberId[4]

            myfavJob.append(save_post)

        con.close()
        return jsonify(myfavJob), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": "Error", "token": token}
        return jsonify(error_response_data), 500

@app.route("/api/mypost")
def loadingMyPost():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        # Retrieve all saved post IDs for the user
        cursor.execute("SELECT postId FROM jobs WHERE memberEmail = %s", (user_email,))
        saved_post_ids = [row[0] for row in cursor.fetchall()]

        # Fetch job details for each saved post ID
        myPostJob = []
        for post_id in saved_post_ids:
    
            cursor.execute("SELECT * FROM jobs WHERE postId = %s", (post_id,))
            post_details = cursor.fetchone()
            if post_details:
                my_post = {
                'post_id':post_details[1],
                'job_title': post_details[3],
                'job_description': post_details[4],
                'job_date':post_details[5],
                'job_start_time':post_details[6],
                'job_end_time':post_details[7],
                'job_zipcode':post_details[8],
                'job_city':post_details[9],
                'job_location':post_details[10],
                'job_salary':post_details[11],
                'job_others':post_details[12],
                'number_of_job_positions':post_details[13],
                'post_time':post_details[14],
                'pay_date':post_details[15],
                'pay_method':post_details[16]
            }
            email = post_details[2],
            if email:
                query = "SELECT * FROM membership WHERE memberEmail = %s"
                cursor.execute(query, (email,))
                memberId = cursor.fetchone()

                if memberId:
                    my_post['memberId'] = memberId[1]
                    my_post["memberIcon"] = memberId[4]

            myPostJob.append(my_post)

        con.close()
        return jsonify(myPostJob), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": "Error", "token": token}
        return jsonify(error_response_data), 500

@app.route("/api/confirmApplication")
def confirmApplication():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT postId FROM applications WHERE applicantEmail = %s AND positionStatus = 2", (user_email,))
        saved_application = [row[0] for row in cursor.fetchall()]
        myApplication = []
        for post_id in saved_application:    
            cursor.execute("SELECT * FROM jobs WHERE postId = %s", (post_id,))
            post_details = cursor.fetchone()
            if post_details:
                my_post = {
                'post_id':post_details[1],
                'job_title': post_details[3],
                'job_description': post_details[4],
                'job_date':post_details[5],
                'job_start_time':post_details[6],
                'job_end_time':post_details[7],
                'job_zipcode':post_details[8],
                'job_city':post_details[9],
                'job_location':post_details[10],
                'job_salary':post_details[11],
                'job_others':post_details[12],
                'number_of_job_positions':post_details[13],
                'post_time':post_details[14],
                'pay_date':post_details[15],
                'pay_method':post_details[16]
            }
            email = post_details[2],
            if email:
                query = "SELECT * FROM membership WHERE memberEmail = %s"
                cursor.execute(query, (email,))
                memberId = cursor.fetchone()

                if memberId:
                    my_post['memberId'] = memberId[1]
                    my_post["memberIcon"] = memberId[4]

            myApplication.append(my_post)

        con.close()
        return jsonify(myApplication), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": "Error", "token": token}
        return jsonify(error_response_data), 500

@app.route("/api/toBeConfirmApplication")
def toBeConfirmApplication():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    token = request.headers.get("Authorization")

    try:
        if not token or not token.startswith("Bearer "):
            raise InvalidTokenError("Invalid or missing token")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT postId FROM applications WHERE applicantEmail = %s AND positionStatus = 1", (user_email,))
        saved_application = [row[0] for row in cursor.fetchall()]

        myApplication = []
        for post_id in saved_application:
    
            cursor.execute("SELECT * FROM jobs WHERE postId = %s", (post_id,))
            post_details = cursor.fetchone()
            if post_details:
                my_post = {
                'post_id':post_details[1],
                'job_title': post_details[3],
                'job_description': post_details[4],
                'job_date':post_details[5],
                'job_start_time':post_details[6],
                'job_end_time':post_details[7],
                'job_zipcode':post_details[8],
                'job_city':post_details[9],
                'job_location':post_details[10],
                'job_salary':post_details[11],
                'job_others':post_details[12],
                'number_of_job_positions':post_details[13],
                'post_time':post_details[14],
                'pay_date':post_details[15],
                'pay_method':post_details[16]
            }
            email = post_details[2],
            if email:
                query = "SELECT * FROM membership WHERE memberEmail = %s"
                cursor.execute(query, (email,))
                memberId = cursor.fetchone()

                if memberId:
                    my_post['memberId'] = memberId[1]
                    my_post["memberIcon"] = memberId[4]

            myApplication.append(my_post)

        con.close()
        return jsonify(myApplication), 200
    except Exception as e:
        con.rollback()
        con.close()
        error_response_data = {"error": True, "message": "Error", "token": token}
        return jsonify(error_response_data), 500


@app.route("/api/updatePwd", methods=["POST"])
def updatePwd():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    data = request.json
    previousPwd = data.get("previousPwd")
    newPwd = data.get("newPwd")

    try:
        token = request.headers.get("Authorization")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT memberPwd FROM membership WHERE memberEmail = %s", (user_email,))
        stored_password_tuple = cursor.fetchone()

        if stored_password_tuple:
            stored_password = stored_password_tuple[0]  # Extract password from the tuple

        if stored_password == previousPwd:
            # Previous password matches, proceed with updating the password
            cursor.execute("UPDATE membership SET memberPwd = %s WHERE memberEmail = %s", (newPwd, user_email))
            con.commit()
            con.close()
            update_success_response = {"ok": True, "message": "Your changes have been successfully saved!"}
            return jsonify(update_success_response), 200
        else:
            # Previous password does not match, return a 403 status
            con.close()
            error_response = {"error": True, "message": "Incorrect passwords!"}
            return jsonify(error_response), 400

    except jwt.ExpiredSignatureError:
        con.close()
        error_response = {"error": True, "message": "Token expired!"}
        return jsonify(error_response), 401

    except jwt.InvalidTokenError:
        con.close()
        error_response = {"error": True, "message": "Token is invalid."}
        return jsonify(error_response), 401

    except Exception as e:
        con.rollback()
        con.close()
        error_message = {"error": True, "message": "Failed to change the passwords."}
        return jsonify(error_message), 500

@app.route("/api/loadingMemberId")
def loadingMemberId():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()
    try:
        token = request.headers.get("Authorization")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT memberId FROM membership WHERE memberEmail = %s", (user_email,))
        originMemberId = cursor.fetchone()

        if originMemberId is not None:
            memberId = {"ok": True, "data": originMemberId}
            return jsonify(memberId), 200
        else:
            # Previous password does not match, return a 403 status
            con.close()
            error_response = {"error": True, "message": "We cannot find a mathching username！"}
            return jsonify(error_response), 400

    except jwt.ExpiredSignatureError:
        con.close()
        error_response = {"error": True, "message": "Token expired!"}
        return jsonify(error_response), 401

    except jwt.InvalidTokenError:
        con.close()
        error_response = {"error": True, "message": "Token is invaild."}
        return jsonify(error_response), 401

    except Exception as e:
        con.rollback()
        con.close()
        error_message = {"error": True, "message": "Failed to load the username."}
        return jsonify(error_message), 500

@app.route("/api/updateMemberId", methods=["POST"])
def updateMemberId():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    data = request.json
    newId = data.get("newId")

    try:
        token = request.headers.get("Authorization")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT memberId FROM membership WHERE memberEmail = %s", (user_email,))
        existingMemberId = cursor.fetchone()


        if existingMemberId:
            cursor.execute("UPDATE membership SET memberId = %s WHERE memberEmail = %s", (newId, user_email))
            cursor.execute("UPDATE messageStorage SET username = %s WHERE senderEmail = %s", (newId, user_email))
            con.commit()
            con.close()
            update_success_response = {"ok": True, "message": "Your changes have been successfully saved!"}
            return jsonify(update_success_response), 200
    except jwt.ExpiredSignatureError:
        con.close()
        error_response = {"error": True, "message": "Token expired."}
        return jsonify(error_response), 401

    except jwt.InvalidTokenError:
        con.close()
        error_response = {"error": True, "message": "Token is invaild."}
        return jsonify(error_response), 401

    except Exception as e:
        con.rollback()
        con.close()
        error_message = {"error": True, "message": "Failed to update the username."}
        return jsonify(error_message), 500

@app.route("/api/updatememberIdPhoto", methods=["POST"])
def updatememberIdPhoto():

    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    file = request.files['memberPhotoFile']

    try:
        token = request.headers.get("Authorization")

        if not token or not token.startswith("Bearer "):
            raise InvalidTokenError("Invalid or missing token")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        new_filename = str(uuid.uuid4())
        secret_key = os.getenv("app.secret_key")
        file_extension = file.filename.rsplit('.', 1)[1]
        new_filename_with_extension = f"{new_filename}.{file_extension}"

        # Upload the file to S3 with the new filename
        s3.upload_fileobj(file, BUCKET_NAME, new_filename_with_extension)
        base_url = f'https://{CloudFrontDomainName}/'
        image_url = base_url + new_filename_with_extension

        cursor.execute("UPDATE membership SET memberIcon = %s WHERE memberEmail = %s", (image_url, user_email))
        con.commit()
        con.close()
        update_success_response = {"ok": True, "message": "Your changes have been successfully saved!"}
        return jsonify(update_success_response), 200
    except jwt.ExpiredSignatureError:
        con.close()
        error_response = {"error": True, "message": "Token expired."}
        return jsonify(error_response), 401

    except jwt.InvalidTokenError:
        con.close()
        error_response = {"error": True, "message": "Token is invalid."}
        return jsonify(error_response), 401

    except Exception as e:
        con.rollback()
        con.close()
        error_message = {"error": True, "message": "Failed to update the user icon."}
        return jsonify(error_message), 500


@app.route("/api/loadingMemberIcon")
def loadingMemberIcon():
    con = pymysql.connect(        
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()
    try:
        token = request.headers.get("Authorization")

        if not token or not token.startswith("Bearer "):
            raise InvalidTokenError("Invalid or missing token")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT memberIcon FROM membership WHERE memberEmail = %s", (user_email,))
        memberIcon = cursor.fetchone()

        if memberIcon is not None:
            memberIcon = {"ok": True, "data": memberIcon}
            return jsonify(memberIcon), 200
        else:
            # Previous password does not match, return a 403 status
            con.close()
            error_response = {"error": True, "message": "Does not find We cannot find a mathching user icon！"}
            return jsonify(error_response), 400

    except jwt.ExpiredSignatureError:
        con.close()
        error_response = {"error": True, "message": "Token expired."}
        return jsonify(error_response), 401

    except jwt.InvalidTokenError:
        con.close()
        error_response = {"error": True, "message": "Token is invalid."}
        return jsonify(error_response), 401

    except Exception as e:
        con.rollback()
        con.close()
        error_message = {"error": True, "message": "Failed to laod the user icon."}
        return jsonify(error_message), 500

@app.route("/api/loadingMessageBox")
def loadingMessageBox():
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    try:
        token = request.headers.get("Authorization")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT * FROM message WHERE senderEmail = %s OR receiverEmail = %s", (user_email, user_email))
        messages = cursor.fetchall()

        myMessageBox = []

        for message in messages:
            # Determine the correspondent's email (receiver or sender)
            correspondent_email = message[2] if message[1] == user_email else message[1]

            # Ensure unique roomId
            cursor.execute("SELECT DISTINCT roomId FROM message WHERE roomId = %s", (message[3],))
            unique_room_id = cursor.fetchone()

            if unique_room_id:
                # Fetch details from membership based on correspondent's email
                cursor.execute("SELECT * FROM membership WHERE memberEmail = %s", (correspondent_email,))
                correspondent_details = cursor.fetchone()

                if correspondent_details:
                    my_post = {
                        'memberId': correspondent_details[1],
                        'memberIcon': correspondent_details[4],
                        'receiverEmail': correspondent_email,
                        'roomId': unique_room_id[0],
                    }
                    myMessageBox.append(my_post)

        con.close()

        return jsonify({"data": myMessageBox}), 200

    except pymysql.Error as e:
        # Log the error details
        print(f"Database error: {e}")
        con.rollback()
        return jsonify({"error": True, "message": "Internal server error"}), 500

@app.route("/api/loadingMessageRoomId/<messageRoomId>")
def loadingMessageRoomId(messageRoomId):
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    try:
        token = request.headers.get("Authorization")

        jwt_token = token.split(" ")[1]
        secret_key = os.getenv("app.secret_key")

        decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        token_user_info = decode_token.get("data", None)
        user_email = token_user_info['email']

        cursor.execute("SELECT * FROM message WHERE roomId = %s", (messageRoomId,))
        messageInfo = cursor.fetchone()
        
        message_dict = {
            'senderEmail': messageInfo[1],
            'receiverEmail': messageInfo[2],
            'messageRoomId': messageInfo[3],
            'userEmail': user_email,  # Corrected variable name
        }
        print(message_dict)
        query = "SELECT memberId FROM membership WHERE memberEmail = %s"
        cursor.execute(query, (user_email))
        memberId = cursor.fetchone()

        if memberId:
            message_dict['memberId'] = memberId[0],
  
        con.close()

        return jsonify({"data": message_dict}), 200

    except pymysql.Error as e:
        # Log the error details
        print(f"Database error: {e}")
        con.rollback()
        return jsonify({"error": True, "message": "Internal server error"}), 500


@app.route("/api/loadingMessageContent/<messageRoomId>")
def loadingMessageContent(messageRoomId):
    con = pymysql.connect(
        host=os.getenv("host"),
        port=3306,
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = con.cursor()

    cursor.execute("SELECT * FROM messageStorage WHERE roomId = %s", (messageRoomId,))
    messageContent = cursor.fetchall()

    allMessageBox = []

    for message in messageContent:
        # Create a dictionary for each message
        messageBox = {
            "username": message[2],  # Assuming username is at index 1 in the result
            "message": message[3],    # Assuming message is at index 2 in the result
            # Add other fields as needed
        }
        allMessageBox.append(messageBox)

    con.close()

    return jsonify({"data": allMessageBox}), 200




# Dictionary to store user-to-room mapping
users = {}

@socketio.on("connect")
def handle_connect():
    print("Client connected!")

@socketio.on("user_join")
def handle_user_join(username):
    print(f"User {username} joined!")
    users[username] = request.sid

@socketio.on("join_room")
def handle_join_room(data):
    room_id = data.get("roomId")
    user_id = data.get("userId")

    # Join the specified room
    join_room(room_id)
    print(f"User {user_id} joined room {room_id}")



@socketio.on("leave_room")
def handle_leave_room(data):
    room_id = data.get("roomId")
    username = data.get("username")

    if room_id and username:
        # Leave the specified room
        leave_room(room_id)
        print(f"User {username} left room {room_id}")

@socketio.on('new_message')
def handle_new_message(message, roomId, username, userEmail):
    if message and roomId and username and userEmail:
        con = pymysql.connect(
            host=os.getenv("host"),
            port=3306,
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )

        cursor = con.cursor()
        cursor.execute("INSERT INTO messageStorage (roomId, username, message, senderEmail) VALUES (%s, %s, %s, %s)", (roomId, username, message ,userEmail))
        con.commit()
        print(f"New message in room {roomId} from {username}: {message}")

        socketio.emit('new_message', {'roomId': roomId, 'username': username, 'message': message}, room=roomId)
        response_data = {"ok": True, "message": "Successful."}
        return jsonify({"data": response_data}), 200

    else:
        print("Invalid data for new_message event")

if __name__ == "__main__":
    socketio.run(app)
