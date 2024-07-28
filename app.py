import os
import openai
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from demo.product import product_data
import uuid
import base64
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='demo/templates', static_folder='demo/static')
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')


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

    def convert_to_base64(file):
        file_content = file.read()
        mime_type = file.mimetype
        base64_image = base64.b64encode(file_content).decode('utf-8')
        return f"data:{mime_type};base64,{base64_image}"

    img_issues = []
    for i in range(1, 5):
        file = request.files.get(f'img_issue_{i}')
        if file and file.filename:
            base64_image = convert_to_base64(file)
            img_issues.append(base64_image)
            logging.info(f'Encoded Issue Image {i}: {base64_image[:30]}...')  # Log first 30 chars for brevity

    img_bos = request.files.get('img_bos')
    if img_bos and img_bos.filename:
        img_bos = convert_to_base64(img_bos)
        logging.info(f'Encoded BOS Image: {img_bos[:30]}...')  # Log first 30 chars for brevity


    return render_template('schedule/step3.html', name=name, issue=issue, contactNum=contactNum,
                           address=address, modelNum=modelNum, serialNum=serialNum, img_bos=img_bos,
                           img_issues=img_issues, warrantyStatus=warrantyStatus, city=city, state=state,
                           zipcode=zipcode, email=email)


@app.route('/schedule/confirm', methods=['POST'])
def schedule_confirm():
    try:
        # Should be replaced with a real ticket number
        unique_id = str(uuid.uuid4())
        base_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
        os.makedirs(base_path, exist_ok=True)

        issues_path = os.path.join(base_path, 'Issues')
        bos_path = os.path.join(base_path, 'BOS')
        os.makedirs(issues_path, exist_ok=True)
        os.makedirs(bos_path, exist_ok=True)
        
        img_bos = request.files.get('img_bos')
        bos_file_path = None
        if img_bos and img_bos.strip():  # Check if img_bos has a value before proceeding
            filename = 'bos.jpg'
            bos_file_path = os.path.join(bos_path, filename)
            with open(bos_file_path, "wb") as fh:
                fh.write(base64.b64decode(img_bos.split(",", 1)[1]))
            img_bos = url_for('uploaded_file', filename=f'{unique_id}/BOS/{filename}')
            logging.info(f'Saved BOS Image {filename} at {bos_file_path}')


        img_issues = []
        for i in range(1, 5):
            base64_str = request.form.get(f'img_issue_{i}')
            if base64_str:
                filename = f'issue_{i}.jpg'
                file_path = os.path.join(issues_path, filename)
                with open(file_path, "wb") as fh:
                    fh.write(base64.b64decode(base64_str.split(",")[1]))
                img_issues.append(url_for('uploaded_file', filename=f'{unique_id}/Issues/{filename}'))
                logging.info(f'Saved Issue Image {filename} at {file_path}')

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

        return render_template('schedule/confirm.html', name=name, contactNum=contactNum, address=address, modelNum=modelNum, 
                               serialNum=serialNum, img_bos=img_bos, img_issues=img_issues, warrantyStatus=warrantyStatus, 
                               city=city, state=state, zipcode=zipcode, email=email, issue=issue, date=date, 
                               product_type=product_type, product_category=product_category, unique_id=unique_id)
    except Exception as e:
        logging.error(f'Error during confirmation: {e}')
        return "An error occurred during the file upload process."


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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

@app.route('/cancel/step1',methods=['POST'])
def cancel_confirm():
    return render_template('cancel/confirm.html')

if __name__ == '__main__':
    app.run(port = 8000,debug=True)

