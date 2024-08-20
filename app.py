import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from demo.product import product_data
import uuid
import base64
import json
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import pandas as pd
from datetime import datetime
from sqlalchemy import func



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

# Initialize Flask-Admin
admin = Admin(app, name='Admin', template_mode='bootstrap3')


# Define a model for storing user information
# Unique_id should be replaced with a ticket number
class UserInfo(db.Model):
    __tablename__ = 'user_info'

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
    appointment_date = db.Column(db.DateTime, nullable = False)   # Ensure this line exists

    def __repr__(self):
        return f'<UserInfo {self.name}>'

# Define a model for slot
class ChatSlot(db.Model):
    __tablename__ = 'chat_slots'

    slot_id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    nickname = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    updated_on = db.Column(db.DateTime, nullable=True)  # Allow NULL
    updated_by = db.Column(db.String(100), nullable=True)  # Allow NULL
    warehouse_id = db.Column(db.String(50), nullable=False)
    zone = db.Column(db.String(10), nullable=False)
    from_dtime = db.Column(db.DateTime, nullable=False)
    to_dtime = db.Column(db.DateTime, nullable=False)
    slot = db.Column(db.Integer, nullable=False)
    product_category = db.Column(db.String(50), nullable=True)

    def __init__(self, nickname, slot_id, created_on, created_by, updated_on, updated_by, warehouse_id, zone, from_dtime, to_dtime, slot, product_category):
        self.nickname = nickname
        self.slot_id = slot_id
        self.created_on = created_on
        self.created_by = created_by
        self.updated_on = updated_on
        self.updated_by = updated_by
        self.warehouse_id = warehouse_id
        self.zone = zone
        self.from_dtime = from_dtime
        self.to_dtime = to_dtime
        self.slot = slot
        self.product_category = product_category


    def __repr__(self):
        return f'<ChatSlot {self.slot_id}>'
    

# Add the slots to the database
csv_file_path='chatslot_LA.csv'
def add_chat_slots_from_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)
    
    with app.app_context():  # Ensure the app context is active
        for index, row in df.iterrows():  # Corrected: iterrows returns index and row
            existing_slot = ChatSlot.query.filter_by(slot_id=row['SLOTID']).first()
            if existing_slot:
                print(f"Slot ID {row['SLOTID']} already exists in the database. Skipping...")
                continue
            # Convert dates to strings if they're not already
            created_on_str = str(row['CREATEDON']) if not pd.isna(row['CREATEDON']) else None
            updated_on_str = str(row['UPDATEDON']) if not pd.isna(row['UPDATEDON']) else None
            from_dtime_str = str(row['FROMDTIME']) if not pd.isna(row['FROMDTIME']) else None
            to_dtime_str = str(row['TODTIME']) if not pd.isna(row['TODTIME']) else None

            # Parse the dates only if they're not None
            created_on = datetime.strptime(created_on_str, '%Y-%m-%d %H:%M:%S.%f') if created_on_str else None
            updated_on = datetime.strptime(updated_on_str, '%Y-%m-%d %H:%M:%S.%f') if updated_on_str else None
            from_dtime = datetime.strptime(from_dtime_str, '%Y-%m-%d %H:%M:%S.%f') if from_dtime_str else None
            to_dtime = datetime.strptime(to_dtime_str, '%Y-%m-%d %H:%M:%S.%f') if to_dtime_str else None

            chat_slot = ChatSlot(
                nickname=row['NICKNAME'],
                slot_id=row['SLOTID'],
                created_on=created_on,
                created_by=row['CREATEDBY'],
                updated_on=updated_on,
                updated_by=row['UPDATEDBY'],
                warehouse_id=row['WAREHOUSEID'],
                zone=row['ZONE'],
                from_dtime=from_dtime,
                to_dtime=to_dtime,
                slot=row['SLOT'],
                product_category=row['PRODUCTCATEGORY']
            )
            db.session.add(chat_slot)
            db.session.commit()

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

    return render_template('schedule/step2.html', name=name, contactNum=contactNum, address=address,  city=city, state=state, zipcode=zipcode, email=email, product_data=product_data)


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

        # Check if a record with the same key fields already exists
    existing_user = UserInfo.query.filter_by(
            name=name,
            contactNum=contactNum,
            serialNum=serialNum,
        ).first()
    logging.debug(name, contactNum, serialNum)
    logging.debug(existing_user)

    if existing_user:
            unique_id = existing_user.unique_id
    else:
            unique_id = str(uuid.uuid4())

    today = datetime.today().date()

    # Query the available dates where slot > 0
    available_dates = ChatSlot.query.filter(
        ChatSlot.slot > 0, 
        ChatSlot.zone == "E",
        func.date(ChatSlot.from_dtime) >= today
        ).all()
    
    # Extract the dates
    available_dates = [slot.from_dtime.strftime('%Y-%m-%d') for slot in available_dates]


    # Define paths
    base_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
    issues_path = os.path.join(base_path, 'Issues')
    bos_path = os.path.join(base_path, 'BOS')

    # Ensure directories exist
    os.makedirs(issues_path, exist_ok=True)
    os.makedirs(bos_path, exist_ok=True)

    # Handle BOS image
    img_bos = request.files.get('img_bos')  # Use parentheses () instead of square brackets []
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
            # Secure the filename
            issue_filename = secure_filename(img_issue.filename)
            
            # Create the full file path
            issue_file_path = os.path.join(issues_path, issue_filename)
            
            # Save the file to the specified path
            img_issue.save(issue_file_path)
            
            # Append the path to the list
            img_issues_paths.append(issue_file_path)
            logging.debug(f"Saved img_issue_{i} at: {issue_file_path}")
        else:
            # Append None or an empty string if no file was uploaded
            img_issues_paths.append(None)
            logging.debug(f"No file uploaded for img_issue_{i}")
    

    return render_template('schedule/step3.html', name=name, issue=issue, contactNum=contactNum,
                           address=address, modelNum=modelNum, serialNum=serialNum, img_issues_paths=img_issues_paths,
                           img_bos_path=img_bos_path, warrantyStatus=warrantyStatus, city=city, state=state,
                           zipcode=zipcode, email=email,unique_id=unique_id, available_dates=available_dates)


@app.route('/schedule/confirm/<unique_id>', methods=['POST'])
def schedule_confirm(unique_id):
    error_message_availability = None
    error_message_user = None
    user_info = UserInfo.query.filter_by(unique_id=unique_id).first()
    print(unique_id)
    
    # Check if a record already exists
    if user_info is not None:
            today = datetime.today().date()
            available_dates = ChatSlot.query.filter(
            ChatSlot.slot > 0, 
            ChatSlot.zone == "E",
            func.date(ChatSlot.from_dtime) >= today
            ).all()
            available_dates = [slot.from_dtime.strftime('%Y-%m-%d') for slot in available_dates]
            error_message_user = f"Your ticket({unique_id}) already exists. Please reschedule using the ticket number."
            return render_template('schedule/step3.html', name=user_info.name, contactNum=user_info.contactNum, address=user_info.address, modelNum=user_info.modelNum, 
                            serialNum=user_info.serialNum, img_bos_path=user_info.img_bos, img_issues_paths=user_info.img_issues.split(","), warrantyStatus=user_info.warrantyStatus, 
                            city=user_info.city, state=user_info.state, zipcode=user_info.zipcode, email=user_info.email, issue=user_info.issue, selected_date=user_info.appointment_date, 
                            product_type=user_info.product_type, product_category=user_info.product_category, unique_id=unique_id, error_message_user=error_message_user, available_dates=available_dates)
    else:
        try:
            # Collect form data
            selected_date = datetime.strptime(request.form['datepicker'] + " 00:00:00", '%Y-%m-%d %H:%M:%S')
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
            img_bos_path = request.form['img_bos_path']
            img_issues_paths = request.form.getlist('img_issues_paths')
            unique_id = request.form['unique_id']
            
        
            chat_slot = ChatSlot.query.filter(
                    ChatSlot.zone == 'E',
                    func.date(ChatSlot.from_dtime) <= selected_date.date(),
                    func.date(ChatSlot.to_dtime) >= selected_date.date(),
                ).first()

                # Check if the slot is available
            if chat_slot is None or chat_slot.slot <= 0:
                    error_message_availability = "The selected slot is no longer available. Please go back and choose another date."
                    return render_template('schedule/step3.html', name=name ,unique_id=unique_id , error_message_availability=error_message_availability)
            else:
                    # Proceed with the confirmation process if the slot is available
                    chat_slot.slot -= 1
                    chat_slot.updated_on = datetime.now()

                    # Save the data to the database
                    user_info = UserInfo(
                        appointment_date=selected_date,
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
                        img_issues=",".join(img_issues_paths),
                    )

                    db.session.add(user_info)
                    db.session.commit()
                
                    return render_template('schedule/confirm.html', name=name, contactNum=contactNum, address=address, modelNum=modelNum, 
                                    serialNum=serialNum, img_bos_path=img_bos_path, img_issues_paths=img_issues_paths, warrantyStatus=warrantyStatus, 
                                    city=city, state=state, zipcode=zipcode, email=email, issue=issue, selected_date=selected_date, 
                                    product_type=product_type, product_category=product_category, unique_id=unique_id)
        except Exception as e:
            logging.error(f'Error during confirmation: {e}')
            return f'An error occurred during the file upload process.{unique_id}'

@app.route('/uploads/<unique_id>/<path:filename>')
def uploads(unique_id,filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], unique_id), filename)

@app.route('/reschedule/step1')
def reschedule_step1():
    return render_template('reschedule/step1.html')

@app.route('/reschedule/step2', methods=['POST'])
def reschedule_step2():
    ticketNum = request.form['ticketNum']
    name = request.form['name']
    contactNum = request.form['contactNum']

    user = UserInfo.query.filter_by(unique_id=ticketNum , name=name , contactNum = contactNum ).first()    
    today = datetime.today().date()

    # Query the available dates where slot > 0
    available_dates = ChatSlot.query.filter(
        ChatSlot.slot > 0, 
        ChatSlot.zone == "E",
        func.date(ChatSlot.from_dtime) >= today
        ).all()

    # Extract the dates
    available_dates = [slot.from_dtime.strftime('%Y-%m-%d') for slot in available_dates]

    if user == None :
        return render_template('reschedule/step1.html', error_message="Schedule not found",ticketNum=ticketNum, name=name, contactNum=contactNum)
    else:
        user_appointment_date = user.appointment_date
        unique_id = user.unique_id
        return render_template('reschedule/step2.html', unique_id=unique_id ,ticketNum=ticketNum, name=name, contactNum=contactNum, appointment_date = user_appointment_date, available_dates=available_dates)

@app.route('/reschedule/confirm/<unique_id>', methods=['POST'])
def reschedule_confirm(unique_id):
    selected_date = datetime.strptime(request.form['datepicker'] + " 00:00:00", '%Y-%m-%d %H:%M:%S')
    name = request.form['name']

    chat_slot = ChatSlot.query.filter(
            ChatSlot.zone == 'E',
            func.date(ChatSlot.from_dtime) <= selected_date.date(),
            func.date(ChatSlot.to_dtime) >= selected_date.date(),
        ).first()
    
    # Check if the slot is available
    if chat_slot is None or chat_slot.slot <= 0:
        error_message_availability = "No available slot found for the selected date. Please go back and choose another date."
        return render_template('reschedule/step2.html', unique_id=unique_id, error_message_availability=error_message_availability , name=name)

    else:
        # update new slot with -1
        chat_slot.slot -= 1
        chat_slot.updated_on = datetime.now()
        
        # update the original slot with +1
        original_date = UserInfo.query.filter_by(unique_id=unique_id).first().appointment_date
        ChatSlot.query.filter(
            ChatSlot.zone == 'E',
            func.date(ChatSlot.from_dtime) <= original_date.date(),
            func.date(ChatSlot.to_dtime) >= original_date.date(),
        ).update({'slot': ChatSlot.slot + 1})

        # update the user info with the new date
        UserInfo.query.filter_by(unique_id=unique_id).update({'appointment_date': selected_date})
        
                                                              
        db.session.commit()
        
    return render_template('reschedule/confirm.html', selected_date=selected_date, original_date=original_date, unique_id=unique_id , name=name)

@app.route('/cancel/step1')
def cancel_step1():
    return render_template('cancel/step1.html')

@app.route('/cancel/step2',methods=['POST'])
def cancel_step2():
    ticketNum = request.form['ticketNum']
    name = request.form['name']
    contactNum = request.form['contactNum']

    user = UserInfo.query.filter_by(unique_id=ticketNum , name=name , contactNum = contactNum ).first()    

    if user == None :
        return render_template('cancel/step1.html', error_message="Ticket not found",ticketNum=ticketNum, name=name, contactNum=contactNum)
    else:
        user_appointment_date = user.appointment_date
        unique_id = user.unique_id
        return render_template('cancel/step2.html', unique_id=unique_id , appointment_date = user_appointment_date)

@app.route('/cancel/confirm/<unique_id>',methods=['POST'])
def cancel_confirm(unique_id):
    name = request.form['name']
    user = UserInfo.query.filter_by(unique_id=unique_id).first()
    appointment_date = user.appointment_date

    # update the original slot with +1
    ChatSlot.query.filter(
            ChatSlot.zone == 'E',
            func.date(ChatSlot.from_dtime) <= appointment_date.date(),
            func.date(ChatSlot.to_dtime) >= appointment_date.date(),
        ).update({'slot': ChatSlot.slot + 1, 'updated_on': datetime.now()})

    db.session.delete(user)
    db.session.commit()

    return render_template('cancel/confirm.html', unique_id=unique_id, name=name) 


admin.add_view(ModelView(UserInfo, db.session))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure that all database tables are created
        add_chat_slots_from_csv('chatslot_LA.csv')
    app.run(port=8000, debug=True)


# 1. time issue 2. 

# Reschedule / Step 2 -> Find the date in ticket number and update the date in Slot to minus 1, the old date in slot to plus 1. if Sloct == 0, then show error message + update time stamp 
# Cancel / Step 2 -> Find the date in ticket number and update the date in Slot to plus 1. + update time stamp