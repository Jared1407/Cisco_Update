# MkV.py

import netmiko
from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect
import os,sys,subprocess,re
from pprint import pprint
import json
import threading
import time
import getpass
import time

# Database of switch versions and images
with open("cisco_database.json", "r") as f:
    CiscoImage = json.load(f)

#Try to detect model
def get_model(connection):
    model = ''
    try:
        output = connection.send_command("show ver")
        for line in output.splitlines():
            if "cisco" in line.lower() and "processor" in line.lower():
                model = line.split(",")[0].split(" ")[1]
                print("Model Found: {}".format(model))
        #If model is not found using the above method, try to find it using the below method
        if model == '':
            output = connection.send_command('sh ver')
            matches = re.findall("Cisco\s+(.*?)\s\Wrevision", output)
            if matches:
                model = matches[0]
                print("Model Found: {}".format(model))
        #If model is not found using the above method, we failed to find the model
        if model == '':
            print('Model Recognition Failed')
        return model
    except Exception as e:
        print('Failed to get model: {}'.format(e))


def read_list(device_list):
    devices = {}
    with open(device_list) as list_file:
        for row in list_file:
            properties = row.strip().split(',')  # use , to delimit lines
            # Device file format: 192.168.0.12, hostname
            device = {
                'ipaddr': properties[0],
                'hostname': properties[1]
            }
            devices[device['ipaddr']] = device  # key for device is its IP in the dictionary

    print(devices)
    return devices


def connect_and_manage(device, user, password, device_type, tftp_ip, cfg_file, selection):
    cisco_device = {'device_type': device_type, 'host': device['ipaddr'], 'username': user, 'password': password}

    try:
        predict_guess = SSHDetect(**cisco_device)
        deviceType = predict_guess.autodetect()
        cisco_device['device_type'] = deviceType
        print(deviceType)
    except Exception:
        print("Identification failed")

    print("Attempting Connection")
    try:
        connection = ConnectHandler(**cisco_device)
        print('Success!!!')
    except Exception as e:
        print("Connection failed!!!" + str(e))
        exit()

    print('Searching for model...')
    model = get_model(connection)

    if selection == '1':
        # ... (remaining logic for selection 1)
        ### Lookup Model in Database ###
         ############################# Change way tftp works depending on found model type ####################################
        if model == 'CISCO2901/K9':
            try:
                file = CiscoImage[model]
                print("Corresponding Image: {}".format(file))
                
                
                #temp#
                output = connection.send_command('enable')
                ### Check if File is already uploaded ###
                output = connection.send_command('dir')
                #print('Dir Output: {}'.format(output))
                
                if '{}'.format(file) in output:
                    print('File already exists')
                else:
                    ### Copy from TFTP Server ###
                    try:
                        output = connection.send_command(
                            'copy tftp://{tftp_server_ip}/{file} flash0:{file}'.format(tftp_server_ip=tftp_ip, file=file),
                             expect_string=r'Destination filename')
                        print('Uploading...')
                        output += connection.send_command(
                            '\n',
                            expect_string=r'#',
                            delay_factor=6)
                        print('Upload Success!!!')
                    except Exception as e:
                        print('Upload Error: {}'.format(e))
            except:
                print('Lookup Failed')
        
        else :
            try:
                file = CiscoImage[model]
                print("Corresponding Image: {}".format(file))
                
                ### Check if File is already uploaded ###
                output = connection.send_command('show flash:')
                
                if '{}'.format(file) in output:
                    print('File already exists')
                else:
                    ### Copy from TFTP Server ###
                    try:
                        output = connection.send_command(
                            'copy tftp://{tftp_server_ip}/{file} flash:{file}'.format(tftp_server_ip=tftp_ip, file=file),
                            expect_string=r'Destination filename',
                            delay_factor=6)
                        print("Uploading....")
                        output += connection.send_command(
                            '\n',
                            expect_string=r'#',
                            delay_factor=10,
                            read_timeout=9999)
                        print('Upload Success!!!')
                    except Exception as e:
                        print('Upload Error: {}'.format(e))
            except:
                print('Lookup Failed')
    elif selection == '2':
        # ... (remaining logic for selection 2)
        output = connection.send_config_from_file(cfg_file)
        output += connection.save_config()
        print(output)
        print('WIP')

    connection.disconnect()


def main(device_list2, tftp_ip2, cfg_file2, selection):
    tftp_ip = '0.0.0.0'
    cfg_file = 'na.txt'

    tftp_ip = tftp_ip2  # Remove this line, as it's now passed as an argument
    cfg_file = cfg_file2  # Remove this line, as it's now passed as an argument

    password = 'password'
    user = 'jared'
    device_type = 'autodetect'
    device_list = device_list2
    
    devices = read_list(device_list)
    
    config_threads = []
    
    for ipaddr, device in devices.items(): # for each device create a new thread and send its credentials
        config_threads.append(threading.Thread(target=connect_and_manage, args=(device, user, password, device_type, tftp_ip, cfg_file, selection)))
    
    for thread in config_threads:
        print("started a thread")
        thread.start()
        
    for thread in config_threads:
        thread.join()
