from flask import Flask, render_template, request
import MkV

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def manage_devices():
    #Only move on when the "Submit" button is pressed:
    if request.method == 'POST':
        device_list = request.form['device_list']
        tftp_ip = request.form.get('tftp_ip')  # Use get method to handle missing field
        cfg_file = request.form.get('cfg_file')  # Use get method to handle missing field
        selection = request.form['selection']

        MkV.main(device_list, tftp_ip, cfg_file, selection)

        return 'Devices managed successfully'
    else:
        return render_template('index.html')
    
@app.route('/edit_database', methods=['GET', 'POST'])
def edit_database():
    if request.method == 'POST':
        new_database = request.form['new_database']  # Get the edited JSON data from the form
        with open('cisco_database.json', 'w') as f:
            f.write(new_database)  # Write the updated JSON data to the file
        #return 'Database updated successfully'

    with open('cisco_database.json', 'r') as f:
        current_database = f.read()

    return render_template('edit_database.html', current_database=current_database)


if __name__ == '__main__':
    app.run(debug=True)