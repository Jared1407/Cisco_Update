from flask import Flask, render_template, request
import MkV

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def manage_devices():
    if request.method == 'POST':
        device_list = request.form['device_list']
        tftp_ip = request.form.get('tftp_ip')  # Use get method to handle missing field
        cfg_file = request.form.get('cfg_file')  # Use get method to handle missing field
        selection = request.form['selection']

        MkV.main(device_list, tftp_ip, cfg_file, selection)

        return 'Devices managed successfully'
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')