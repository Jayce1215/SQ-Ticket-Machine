import os
import openai
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key



# client = openai.OpenAI(
#         api_key=os.environ.get("OPENAI_API_KEY")
#     )

def generate_content(name, contactNum, location, modelNum, serialNum, issue, filename):
    # prompt = f"""
    # Customer Name: {name}
    # Contact Number: {contactNum}
    # Location: {location}
    # Model Number: {modelNum}
    # Serial Number: {serialNum}
    # Issue: {issue}
    # Uploaded File: {filename}

    # Please generate organized content describing dianosis with the model, the defect and action plan based on the above details. Do not metion the customer's info.
    # """
    # response = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt,
    #         }
    #     ],
    #     model="gpt-3.5-turbo",
    # )
    # content = response.choices[0].message.content

    return name, contactNum, location, modelNum, serialNum, issue, filename



@app.route('/')
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
    return render_template('step2.html', name=name, contactNum=contactNum, location=location, modelNum=modelNum, serialNum=serialNum, issue=issue)

@app.route('/step3', methods=['POST'])
def step3():
    name = request.form['name']
    contactNum = request.form['contactNum']
    location = request.form['location']
    modelNum = request.form['modelNum']
    serialNum = request.form['serialNum']
    issue = request.form['issue']
    
   
    file = request.files.get('file')
    filename = None
    if file and file.filename != '':
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return render_template('step3.html', name=name, contactNum=contactNum, location=location, modelNum=modelNum, serialNum=serialNum, issue=issue, filename=filename)


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
    
    content = generate_content(name, contactNum, location, modelNum, serialNum, issue, filename)
    
    return render_template('confirm.html', content=content, name=name, contactNum=contactNum, location=location, modelNum=modelNum, serialNum=serialNum, issue=issue, filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)