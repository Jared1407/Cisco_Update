from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
import os
import MkV
import json

app = Flask(__name__)
# A secret key is required to use the flash messaging system
app.secret_key = os.urandom(24) 

@app.route('/', methods=['GET', 'POST'])
def manage_devices():
    '''This function takes fields from the user and submits them to the main app MkV.py'''
    if request.method == 'POST':
        if request.form.get('Submit') == 'Submit':
            try:
                device_list = request.form['device_list']
                tftp_ip = request.form.get('tftp_ip', '') # Use get with default
                cfg_file = request.form.get('cfg_file', '') # Use get with default
                selection = request.form['selection']

                # Basic validation
                if not device_list:
                    flash('Device List File Name is required.', 'warning')
                    return redirect(url_for('manage_devices'))
                if selection == '1' and not tftp_ip:
                    flash('TFTP IP Address is required for an IOS Update.', 'warning')
                    return redirect(url_for('manage_devices'))
                if selection == '2' and not cfg_file:
                    flash('Config File is required for Config from File.', 'warning')
                    return redirect(url_for('manage_devices'))

                data = MkV.main(device_list, tftp_ip, cfg_file, selection)

                # Parse data, if we find 'False' in the data, something went wrong
                has_error = False
                for key, value in data.items():
                    if 'False' in str(value):
                        flash(f"Error on device {key}: {value}", 'danger')
                        has_error = True
                
                if not has_error:
                    flash('Actions completed successfully on all devices!', 'success')
                
                return redirect(url_for('manage_devices'))

            except Exception as e:
                flash(f"An error occurred: {e}", 'danger')
                return redirect(url_for('manage_devices'))

        elif request.form.get('Submit') == 'Edit Database':
            return redirect(url_for('edit_database'))
    
    return render_template('index.html')

@app.route('/edit_database', methods=['GET', 'POST'])
def edit_database():
    '''This function will edit the database and link to the upload screen'''
    database_path = 'cisco_database.json'
    if request.method == 'POST':
        submit_action = request.form.get('Submit')
        if submit_action == "Update Database":
            new_database_content = request.form['new_database']
            try:
                # Validate that the input is valid JSON
                json.loads(new_database_content)
                with open(database_path, 'w', encoding='utf-8') as f:
                    f.write(new_database_content)
                flash('Database updated successfully!', 'success')
            except json.JSONDecodeError:
                flash('Invalid JSON format. Please check your syntax.', 'danger')
            return redirect(url_for('edit_database'))

        elif submit_action == "Link to Cisco Database":
            return redirect('https://software.cisco.com/download/home')
        
        elif submit_action == "Upload Images":
            return redirect(url_for('upload_images'))

    with open(database_path, 'r', encoding='utf-8') as f:
        current_database = f.read()
    return render_template('edit_database.html', current_database=current_database)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'bin', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# It's a good practice to create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    '''A simple function to limit file extensions'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_images():
    '''In this function we upload files for new Cisco images'''
    if request.method == 'POST':
        submit_action = request.form.get('Submit')
        if submit_action == "Upload":
            if 'file' not in request.files:
                flash('No file part in the request.', 'danger')
                return redirect(request.url)
            
            file = request.files['file']

            if file.filename == '':
                flash('No file selected.', 'warning')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash(f'File "{filename}" uploaded successfully!', 'success')
                return redirect(url_for('upload_images'))
            else:
                flash('File type not allowed. Please upload .bin or .txt files.', 'danger')
                return redirect(request.url)

        elif submit_action == "Back to Database":
            return redirect(url_for('edit_database'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)