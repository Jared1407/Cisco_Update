from flask import Flask, render_template, request
import MkV

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def manage_devices():
    if request.method == 'POST':
        data = []
        try:
            device_list = request.form['device_list']
            tftp_ip = request.form.get('tftp_ip')  # Use get method to handle missing field
            cfg_file = request.form.get('cfg_file')  # Use get method to handle missing field
            selection = request.form['selection']

            data = MkV.main(device_list, tftp_ip, cfg_file, selection)

            #Parse data, If we find 'False' in the data, we know something went wrong
            for key, value in data:
                if 'False' in value:
                    return render_template('index.html', error='Connection Failed')

            return render_template('index.html')
        except Exception as e:
            return render_template('index.html', error=e)
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