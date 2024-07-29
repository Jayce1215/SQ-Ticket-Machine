import os
import openai
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from demo.product import product_data
import uuid
import base64
import json
import logging
from flask_sqlalchemy import SQLAlchemy


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='demo/templates', static_folder='demo/static')
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder where images will be saved
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')



#configure the database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a model for storing user information
# Unique_id should be replaced with a ticket number
class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(36), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contactNum = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    modelNum = db.Column(db.String(50), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    product_category = db.Column(db.String(50), nullable=False)
    serialNum = db.Column(db.String(50), nullable=False)
    issue = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    warrantyStatus = db.Column(db.String(20), nullable=False)
    img_bos = db.Column(db.String(200), nullable=True)
    img_issues = db.Column(db.Text, nullable=True)


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/schedule/step1')
def schedule_step1():
    return render_template('schedule/step1.html')

@app.route('/schedule/step2', methods=['POST'])
def schedule_step2():
    name = request.form['name']
    contactNum = request.form['contactNum']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zipcode']
    email = request.form['email']

    return render_template('schedule/step2.html', name=name, contactNum=contactNum, address=address,  city=city, state=state, zipcode=zipcode, email=email)


@app.route('/schedule/step3', methods=['POST'])
def schedule_step3():
    name = request.form['name']
    contactNum = request.form['contactNum']
    address = request.form['address']
    modelNum = request.form['modelNum']
    serialNum = request.form['serialNum']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zipcode']
    email = request.form['email']
    issue = request.form['issue']
    warrantyStatus = request.form['warrantyStatus']
    unique_id = str(uuid.uuid4())

    # Define paths
    base_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
    issues_path = os.path.join(base_path, 'Issues')
    bos_path = os.path.join(base_path, 'BOS')

    # Ensure directories exist
    os.makedirs(issues_path, exist_ok=True)
    os.makedirs(bos_path, exist_ok=True)

    # Handle BOS image
    img_bos = request.files.get('img_bos')
    img_bos_path = None
    if img_bos and img_bos.filename:
        bos_filename = secure_filename(img_bos.filename)
        img_bos_path = os.path.join(bos_path, bos_filename)
        img_bos.save(img_bos_path)

    # Handle issue images
    img_issues_paths = []
    for i in range(1, 5):
        img_issue = request.files.get(f'img_issue_{i}')
        if img_issue and img_issue.filename:
            issue_filename = secure_filename(img_issue.filename)
            issue_file_path = os.path.join(issues_path, issue_filename)
            img_issue.save(issue_file_path)
            img_issues_paths.append(issue_file_path)
    

    return render_template('schedule/step3.html', name=name, issue=issue, contactNum=contactNum,
                           address=address, modelNum=modelNum, serialNum=serialNum, img_bos=img_bos_path,
                           img_issues=img_issues_paths, warrantyStatus=warrantyStatus, city=city, state=state,
                           zipcode=zipcode, email=email,unique_id=unique_id)


@app.route('/schedule/confirm', methods=['GET','POST'])
def schedule_confirm():
    try:
        # Collect form data
        date = request.form['date']
        name = request.form['name']
        contactNum = request.form['contactNum']
        address = request.form['address']
        modelNum = request.form['modelNum']
        product_type = product_data.get(modelNum, ("Unknown", "Unknown"))[0]
        product_category = product_data.get(modelNum, ("Unknown", "Unknown"))[1]
        serialNum = request.form['serialNum']
        issue = request.form['issue']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        email = request.form['email']
        warrantyStatus = request.form['warrantyStatus']
        img_bos_path = request.form['img_bos']
        img_issues_paths = request.form.getlist('img_issues')
        unique_id = request.form['unique_id']


        # Save the data to the database
        user_info = UserInfo(
            unique_id=unique_id,
            name=name,
            contactNum=contactNum,
            address=address,
            modelNum=modelNum,
            product_type=product_type,
            product_category=product_category,
            serialNum=serialNum,
            issue=issue,
            city=city,
            state=state,
            zipcode=zipcode,
            email=email,
            warrantyStatus=warrantyStatus,
            img_bos=img_bos_path,
            img_issues=",".join(img_issues_paths)
        )

        db.session.add(user_info)
        db.session.commit()

        return render_template('schedule/confirm.html', name=name, contactNum=contactNum, address=address, modelNum=modelNum, 
                               serialNum=serialNum, img_bos=img_bos_path, img_issues=img_issues_paths, warrantyStatus=warrantyStatus, 
                               city=city, state=state, zipcode=zipcode, email=email, issue=issue, date=date, 
                               product_type=product_type, product_category=product_category, unique_id=unique_id)
    except Exception as e:
        logging.error(f'Error during confirmation: {e}')
        logging.debug(f"Received img_bos_path: {img_bos_path}")
        logging.debug(f"Received img_issues_paths: {img_issues_paths}")
        logging.debug(f"Received unique_id: {unique_id}")

        return "An error occurred during the file upload process."

@app.route('/uploads/<unique_id>/<filename>')
def uploads(unique_id,filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], unique_id), filename)

@app.route('/reschedule/step1')
def reschedule_step1():
    return render_template('reschedule/step1.html')

@app.route('/reschedule/step2', methods=['POST'])
def reschedule_step2():
    return render_template('reschedule/step2.html')

@app.route('/reschedule/confirm', methods=['POST'])
def reschedule_confirm():
    return render_template('reschedule/confirm.html')

@app.route('/cancel/step1')
def cancel_step1():
    return render_template('cancel/step1.html')

@app.route('/cancel/step2',methods=['POST'])
def cancel_step2():
    return render_template('cancel/step2.html')

@app.route('/cancel/confirm',methods=['POST'])
def cancel_confirm():
    return render_template('cancel/confirm.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure that all database tables are created
    app.run(port=8000, debug=True)



 # Schedule / confirm -> Find the date in Slot and Update to minus 1. if Sloct == 0, then show error message + update time stamp
        # Reschedule / Step 2 -> Find the date in ticket number and update the date in Slot to minus 1, the old date in slot to plus 1. if Sloct == 0, then show error message + update time stamp 
        # Cancel / Step 2 -> Find the date in ticket number and update the date in Slot to plus 1. + update time stamp