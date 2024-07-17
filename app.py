import os
import openai
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from dotenv import load_dotenv
from demo.product import product_data

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='demo/templates', static_folder='demo/static')
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')



def generate_content(name, contactNum, location, modelNum, serialNum, issue, filename):
    prompt = f"""
    Customer Name: {name}
    Contact Number: {contactNum}
    Location: {location}
    Model Number: {modelNum}
    Serial Number: {serialNum}
    Issue: {issue}
    Uploaded File: {filename}

     generate organized content describing dianosis with the model, the defect and action plan based on the above details. Do not metion the customer's info.
    """
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    content = response.choices[0].message.content

    return content

app.config['SECRET_KEY'] = os.urandom(24)

def generate_content(name, contactNum, location, modelNum, serialNum, issue, filename, warranty_status):
    product_type = product_data.get(modelNum, ("Unknown", "Unknown"))[0]
    product_category = product_data.get(modelNum, ("Unknown", "Unknown"))[1]
    return f"""name:{name}, contactNum:{contactNum}, location:{location}, modelNum:{modelNum}, serialNum:{serialNum}, issue:{issue}, filename:{filename}, product_type:{product_type}, product_category:{product_category}, warranty_status:{warranty_status}"""

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/step1')
def step1():
    return render_template('step1.html')

@app.route('/step2', methods=['POST'])
def step2():
    name = request.form['name']
    contactNum = request.form['contactNum']
    location = request.form['location']
    modelNum = request.form['modelNum']
    serialNum = request.form['serialNum']
    issue = request.form['issue']
    warranty_status = request.form['warrantyStatus']

    return render_template('step2.html', name=name, contactNum=contactNum, location=location, modelNum=modelNum, serialNum=serialNum, issue=issue, warranty_status=warranty_status)

@app.route('/step3', methods=['POST'])
def step3():
    name = request.form['name']
    contactNum = request.form['contactNum']
    location = request.form['location']
    modelNum = request.form['modelNum']
    serialNum = request.form['serialNum']
    issue = request.form['issue']
    warranty_status = request.form['warrantyStatus']

    file = request.files.get('file')
    filename = None
    if file and file.filename != '':
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template('step3.html', name=name, contactNum=contactNum, location=location, modelNum=modelNum, serialNum=serialNum, issue=issue, filename=filename, warranty_status=warranty_status)

@app.route('/confirm', methods=['POST'])
def confirm():
    date = request.form['date']
    name = request.form['name']
    contactNum = request.form['contactNum']
    location = request.form['location']
    modelNum = request.form['modelNum']
    serialNum = request.form['serialNum']
    issue = request.form['issue']
    filename = request.form['filename']
    warranty_status = request.form['warrantyStatus']

    # content = generate_content(name, contactNum, location, modelNum, serialNum, issue, filename,warranty_status)
    # content = generate_content(name, contactNum, location, modelNum, serialNum, issue, filename)
    content = 'generated content'
    
    return render_template('confirm.html', content=content, name=name, contactNum=contactNum, location=location, modelNum=modelNum, serialNum=serialNum, issue=issue, filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(port = 8000,debug=True)

