from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import pyodbc
from werkzeug.security import generate_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\AtharvaK\\Desktop\\EC 530\\uploads'

# Set a secret key for session management
app.secret_key = '0123456789'

# Database connection details
server = 'ATHARVA'
database = 'HMS'
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};DATABASE={database};Trusted_Connection=yes;'
)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form['role']

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute("SELECT * FROM Users WHERE Email = ?", (email,))
            if cursor.fetchone():
                flash('Email already exists.', 'error')
                return redirect(url_for('add_user'))

            # Insert the user
            cursor.execute("INSERT INTO Users (Name, Email, Password) VALUES (?, ?, ?);", (name, email, password))
            user_id = cursor.execute("SELECT SCOPE_IDENTITY();").fetchone()[0]

            # Link the user to their role
            cursor.execute("INSERT INTO UserRoles (UserId, RoleId) VALUES (?, ?)", (user_id, role_id))
            conn.commit()

            flash('User added successfully.', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('add_user'))
    return render_template('add_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # Directly using the plaintext password

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Direct comparison of plaintext passwords (not recommended for production)
        cursor.execute("""
        SELECT u.UserId, u.Name, r.RoleName 
        FROM Users u
        JOIN UserRoles ur ON u.UserId = ur.UserId
        JOIN Roles r ON ur.RoleId = r.RoleId
        WHERE u.Email = ? AND u.Password = ?""", (email, password))
        user_info = cursor.fetchone()
        
        if user_info:
            # Store user information and roles in session
            session['user_id'] = user_info.UserId
            session['user_name'] = user_info.Name
            session['user_role'] = user_info.RoleName

            cursor.close()
            conn.close()

            # Redirect based on role
            if user_info.RoleName == 'Patient':
                return redirect(url_for('patient_home'))
            elif user_info.RoleName in ['Doctor', 'Nurse']:
                return redirect(url_for('mp_home'))
            elif user_info.RoleName == 'Admin':
                return redirect(url_for('admin_home'))
            # Add more role checks as needed
        else:
            cursor.close()
            conn.close()
            flash('Invalid login credentials. Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')


# Placeholder routes for demonstration
@app.route('/patient_home')
def patient_home():
    patient_name = session.get('user_name', 'Guest')
    return render_template('patient_home.html', patient_name=patient_name)

@app.route('/mp_home')
def mp_home():
    mp_name = session.get('user_name', 'Guest')
    return render_template('mp_home.html', mp_name=mp_name)

@app.route('/admin_home')
def admin_home():
    # admin_name = session.get('user_name', 'Guest')
    return render_template('admin_home.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/view_measurements')
def view_measurements():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT Type, Value, Timestamp FROM Measurements WHERE UserId = ?", (user_id,))
    measurements = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('view_measurements.html', measurements=measurements)

@app.route('/browse_patients')
def browse_patients():
    if session.get('user_role') not in ['Doctor', 'Nurse']:
        flash("Unauthorized access.", "error")
        return "Unauthorized", 403
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT UserId, Name FROM Users WHERE UserId IN (SELECT UserId FROM UserRoles WHERE RoleId = (SELECT RoleId FROM Roles WHERE RoleName = 'Patient'))")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('browse_patients.html', patients=patients)

@app.route('/write_message', methods=['GET', 'POST'])
def write_message():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    sender_id = session['user_id']
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    user_id = session['user_id']

    if request.method == 'POST':
        message_content = request.form['message']
        recipient_id = request.form['recipient_id']  # Assuming you have a way to select the recipient
        
        cursor.execute("INSERT INTO Messages (SenderId, RecipientId, Content, Timestamp) VALUES (?, ?, ?, GETDATE())", (sender_id, recipient_id, message_content))
        conn.commit()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('write_message'))
    
    cursor.execute("""
        SELECT DISTINCT u.UserId, u.Name
        FROM Appointments a
        JOIN Users u ON a.DoctorId = u.UserId
        WHERE a.PatientId = ?
        """, (user_id,))
    doctors = cursor.fetchall()

    cursor.execute("""
            SELECT m.MessageId, m.Content, m.Timestamp, u.Name AS SenderName
            FROM Messages m
            JOIN Users u ON m.SenderId = u.UserId
            WHERE m.RecipientId = ?
            ORDER BY m.Timestamp DESC
            """, (user_id,))
    messages = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('write_message.html', messages=messages, doctors=doctors)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_media', methods=['GET', 'POST'])
def upload_media():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Add file path to database
            cursor.execute("INSERT INTO Media (UserId, FilePath, Timestamp) VALUES (?, ?, GETDATE())", (session['user_id'], os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            conn.commit()
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('upload_media'))
    
    cursor.execute("""  
            SELECT MediaId, FilePath, Timestamp
            FROM Media
            WHERE UserId = ?
            ORDER BY Timestamp DESC
            """, (session['user_id'],))
    media_files = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('upload_media.html', media_files=media_files)

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        appointment_date = request.form['date']
        appointment_time = request.form['time']
        doctor_id = request.form['doctor_id']  # Assuming the patient selects a doctor
        status = "Scheduled"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Appointments (PatientId, DoctorId, Date, Time, Status) VALUES (?, ?, ?, ?, ?)", (session['user_id'], doctor_id, appointment_date, appointment_time, status))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('book_appointment'))

    return render_template('book_appointment.html')

@app.route('/assign_device', methods=['GET', 'POST'])
def assign_device():
    if 'user_id' not in session or 'Doctor' not in session.get('user_role', []) and 'Nurse' not in session.get('user_role', []):
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        device_id = request.form['device_id']
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO PatientDevices (PatientId, DeviceId, AssignedDate) VALUES (?, ?, GETDATE())", (patient_id, device_id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Device assigned successfully!', 'success')
        return redirect(url_for('assign_device'))

    return render_template('assign_device.html')

@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session or 'Admin' not in session.get('user_roles', []):
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT UserId, Name, Email, IsActive FROM Users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/set_alerts', methods=['GET', 'POST'])
def set_alerts():
    if 'user_id' not in session or 'Doctor' not in session.get('user_role', []) and 'Nurse' not in session.get('user_role', []):
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        measurement_type = request.form['measurement_type']
        threshold_value = request.form['threshold_value']
        alert_message = request.form['alert_message']
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Alerts (PatientId, MeasurementType, ThresholdValue, AlertMessage) VALUES (?, ?, ?, ?)", (patient_id, measurement_type, threshold_value, alert_message))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Alert set successfully!', 'success')
        return redirect(url_for('set_alerts'))

    return render_template('set_alerts.html')

@app.route('/manage_appointments')
def manage_appointments():
    if 'user_id' not in session or 'Doctor' not in session.get('user_role', []) and 'Nurse' not in session.get('user_role', []):
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT AppointmentId, PatientId, Date, Time FROM Appointments WHERE DoctorId = ?", (session['user_id'],))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('manage_appointments.html', appointments=appointments)

@app.route('/update_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def update_appointment(appointment_id):
    if 'user_id' not in session:
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        if request.method == 'POST':
            new_date = request.form['date']
            new_time = request.form['time']
            cursor.execute("UPDATE Appointments SET Date = ?, Time = ? WHERE AppointmentId = ?", (new_date, new_time, appointment_id))
            conn.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('manage_appointments'))
        else:
            cursor.execute("SELECT AppointmentId, PatientId, Date, Time FROM Appointments WHERE AppointmentId = ?", (appointment_id,))
            appointment = cursor.fetchone()
            return render_template('update_appointment.html', appointment=appointment)
    finally:
        cursor.close()
        conn.close()


@app.route('/cancel_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:
        if request.method == 'POST':
            # Process the cancellation
            cursor.execute("DELETE FROM Appointments WHERE AppointmentId = ?", (appointment_id,))
            conn.commit()
            flash('Appointment canceled successfully!', 'success')
            return redirect(url_for('manage_appointments'))
        else:
            # Display the confirmation page
            cursor.execute("SELECT AppointmentId, PatientId, Date, Time FROM Appointments WHERE AppointmentId = ?", (appointment_id,))
            appointment = cursor.fetchone()
            if appointment:
                return render_template('cancel_appointment.html', appointment=appointment)
            else:
                flash("Appointment not found.", "error")
                return redirect(url_for('manage_appointments'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('manage_appointments'))
    finally:
        cursor.close()
        conn.close()



@app.route('/toggle_user_status/<int:user_id>', methods=['POST'])
def toggle_user_status(user_id):
    if 'user_id' not in session or session.get('user_role') != 'Admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    try:
        # Fetch the current status of the user
        cursor.execute("SELECT IsActive FROM Users WHERE UserId = ?", (user_id,))
        current_status = cursor.fetchone()
        if current_status:
            new_status = not current_status.IsActive
            cursor.execute("UPDATE Users SET IsActive = ? WHERE UserId = ?", (new_status, user_id))
            conn.commit()
            flash('User status updated successfully!', 'success')
        else:
            flash("User not found.", "error")
    except Exception as e:
        flash(f'Failed to toggle user status: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_manage_users'))


# Add this new route for serving the measurement entry form
@app.route('/enter_measurement', methods=['GET', 'POST'])
def enter_measurement():
    if 'user_id' not in session:
        flash("Please log in to enter measurements.", "error")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        measurement_type = request.form['type']
        measurement_value = request.form['value']
        user_id = session['user_id']
        
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Measurements (UserId, Type, Value) VALUES (?, ?, ?)", (user_id, measurement_type, measurement_value))
            conn.commit()
            flash('Measurement entered successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('patient_home'))
    else:
        # For a GET request, display the enter_measurement.html form
        return render_template('enter_measurement.html')

@app.route('/view_appointments')
def view_appointments():
    if 'user_id' not in session:
        flash("Please log in to view appointments.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT AppointmentId, Date, Time, Status FROM Appointments WHERE PatientId = ? ORDER BY Date, Time", (user_id,))
        appointments = cursor.fetchall()
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        appointments = []
    finally:
        cursor.close()
        conn.close()

    return render_template('view_appointments.html', appointments=appointments)

@app.route('/admin_manage_users')
def admin_manage_users():
    if 'user_id' not in session or 'Admin' not in session.get('user_role', []):
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserId, Name, Email, IsActive FROM Users ORDER BY Name")
        users = cursor.fetchall()
    except Exception as e:
        flash(f'An error occurred while fetching users: {str(e)}', 'error')
        users = []
    finally:
        cursor.close()
        conn.close()

    return render_template('manage_users.html', users=users)



@app.route('/manage_roles', methods=['GET', 'POST'])
def manage_roles():
    if 'user_id' not in session or session.get('user_role') != 'Admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        role_ids = request.form.getlist('role_id')
        # Insert or update role assignments in the database
        # Ensure to handle multiple roles assignment logic here

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT UserId, Name FROM Users ORDER BY Name")
        users = cursor.fetchall()
    except Exception as e:
        flash(f'Failed to fetch users: {str(e)}', 'error')
        users = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('manage_roles.html', users=users)


@app.route('/manage_devices', methods=['GET', 'POST'])
def manage_devices():
    # Check if user is logged in and is an admin
    if 'user_id' not in session or session.get('user_role') != 'Admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        device_name = request.form.get('device_name')  # Retrieve device name from the form
        if device_name:  # Check if device name was actually provided
            try:
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()
                # Insert the new device, assuming all new devices are enabled by default
                cursor.execute("INSERT INTO Devices (DeviceName, IsActive) VALUES (?, ?)", (device_name, True))
                conn.commit()
                flash('Device added successfully', 'success')
            except Exception as e:
                flash(f'Failed to add device: {e}', 'error')
            finally:
                cursor.close()
                conn.close()

    # Load and display devices, handling both GET and successful POST requests
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT DeviceId, DeviceName, IsActive FROM Devices")
        devices = cursor.fetchall()
    except Exception as e:
        flash(f'Failed to fetch devices: {e}', 'error')
        devices = []  # Ensure the template can handle an empty list if the database call fails
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('manage_devices'))




@app.route('/toggle_device_status/<int:device_id>', methods=['POST'])
def toggle_device_status(device_id):
    if 'user_id' not in session or session.get('user_role') != 'Admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT IsActive FROM Devices WHERE DeviceId = ?", (device_id,))
        current_status = cursor.fetchone()
        if current_status:
            new_status = not current_status[0]  # Correct assumption that IsActive is the first column
            cursor.execute("UPDATE Devices SET IsActive = ? WHERE DeviceId = ?", (new_status, device_id))
            conn.commit()
            flash('Device status updated successfully.', 'success')
        else:
            flash("Device not found.", "error")
    except Exception as e:
        flash(f'Failed to toggle device status: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('manage_devices'))





# Existing endpoint implementations (add_user, assign_role, toggle_device_maker, test_db_connection) go here...

if __name__ == '__main__':
    app.run(debug=True)