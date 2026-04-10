
import sys
import os
import json
import importlib
import time
import pytz
from obspy.core import UTCDateTime
from datetime import datetime, timedelta as td
from pytz import timezone
from dotenv import load_dotenv 
import subprocess


def uploadValueToGraphite(closest_period_line, psd_hour_tag, tries, ADM_EMAILS, GRAPHITE_URL, GRAPHITE_PORT):  
    # split, but keep also keep original arg for recirsive call
    #BK.BRK.00.HHZ
    # ['2023-04-04', '02:59:59', '0.020000', '-81']
    this_date = closest_period_line[0]
    time_str = closest_period_line[1]
    year = int(this_date.split('-')[0])
    month = int(this_date.split('-')[1])
    day = int(this_date.split('-')[2])
    hour = int(time_str.split(':')[0])
    minute = int(time_str.split(':')[1])
    second = int(time_str.split(':')[2])
    date_object_for_value = datetime(year, month, day, hour, minute, second)
    unix_epoch_time_utc = date_object_for_value.replace(tzinfo=pytz.utc).timestamp()
    # Cannot have a . in the middle of a Graphite address
    period = closest_period_line[2].split(".")[0] + '_' + closest_period_line[2].split(".")[1]
    value = closest_period_line[3]
    network = psd_hour_tag.split('.')[0]
    station = psd_hour_tag.split('.')[1]
    location = str(psd_hour_tag.split('.')[2])
    channel = psd_hour_tag.split('.')[3]
    add_data_to_graphite = "echo \"PSD." + network + "." + station + "." + channel + "." + location + "." + period + " " + str(value) + " " + str(unix_epoch_time_utc) + " \" | nc " + GRAPHITE_URL + " " + GRAPHITE_PORT
    print("Add status to graphite: ", add_data_to_graphite)
    if (tries < 3):
        try:
            send_graphite_file_process = subprocess.Popen([add_data_to_graphite], shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = send_graphite_file_process.communicate()
            exit_code=send_graphite_file_process.wait()
            if (exit_code == 0):
                return 0
            else:
                tries+=1
                uploadValueToGraphite(closest_period_line, psd_hour_tag, tries, ADM_EMAILS, GRAPHITE_URL, GRAPHITE_PORT)
            
        except:
            tries+=1
            uploadValueToGraphite(closest_period_line, psd_hour_tag, tries, ADM_EMAILS, GRAPHITE_URL, GRAPHITE_PORT)
    else:
        # write a datetime stamp for when wrong
        current_time = time.time()
        sendWarningEmail('writePSDGraphiteError', current_time, ADM_EMAILS)     
        # also set status to unknown
        return 'writeGraphiteError'


def sendWarningEmail(message, message_time, emails):
    print(f"WARNING (email disabled): {message} at {message_time} to {emails}")
    return "Dummy Error Subject"



def main(*args):
    """
    Name: ntk_autoPSD.py - a Python 3 script to extract specified PSD values at specified period spanning across
    multiple different time stamps

    INPUT: the variables in param/autoPSD.json
    OUTPUT: file in data/psdPr with json variables in the name

    Written by Sylvester Seo
    """

    # Load env variables for connection to graphite an error messages
    load_dotenv()
    ADM_EMAILS = os.getenv("ADM_EMAILS")
    GRAPHITE_URL = os.getenv("GRAPHITE_URL")
    GRAPHITE_PORT = os.getenv("GRAPHITE_PORT")

    # Modifying to make this run with optional command line arguments. Change args to cmd_args
    # to avoid collision with args from json params file
    if (len(args) == 3):
        cmd_args = args
        #print("Called by the cron job")
        print("starting ntk_autoPSD.py with the following args: ", cmd_args)
    else:
        cmd_args = []
        print("normal usage")

    #Import noise toolkit libraries
    ntk_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    param_path = os.path.join(ntk_directory, 'param')
    lib_path = os.path.join(ntk_directory, 'lib')
    sys.path.append(lib_path)
    sys.path.append(param_path)

    import fileLib as file_lib
    import msgLib as msg_lib
    import tsLib as ts_lib
    import utilsLib as utils_lib
    import shared

    #Declare variables
    DATE_INDEX = 0
    TIME_INDEX = 1
    PERIOD_INDEX = 2
    VALUE_INDEX = 3
    WHITE = "\033[1;37m"
    ENDC = '\033[0m'

    if (len(cmd_args) == 3):
        #Read JSON file input
        print(cmd_args[2])
        json_path = os.path.join(param_path, cmd_args[2])
        json_object = open('param/' + cmd_args[2])
        json_dict = json.load(json_object)
        param_dict = json_dict['psd_parameters']
        settings_dict = json_dict['psd_period_settings']
    else:
        #Read JSON file input
        json_path = os.path.join(param_path, 'autoPSD.json')
        json_object = open('param/autoPSD.json')
        json_dict = json.load(json_object)
        param_dict = json_dict['psd_parameters']
        settings_dict = json_dict['psd_period_settings']
    


    #Define required variables
    data_directory = shared.dataDirectory
    if(param_dict['directory'] != 'None'):
         data_directory = param_dict['directory']

    #Check for valid network and station combos
    current_instruction = 0
    for request_network in param_dict['net']:
        for request_station in param_dict['sta']:
            ##request_query = utils_lib.get_fedcatalog_url(request_network, request_station, param_dict['loc'], 
            ##                                        param_dict['chan'], param_dict['start'], param_dict['end'])
            #if (len(args) == 3):
            #    print("Called by the cron job")
            #    request_query = utils_lib.get_fedcatalog_url(request_network, request_station, param_dict['loc'], 
            #                                        param_dict['chan'], args[0], args[1])
            #    print(request_query)
            #else:
            #    request_query = utils_lib.get_fedcatalog_url(request_network, request_station, param_dict['loc'], 
            #                                        param_dict['chan'], param_dict['start'], param_dict['end'])
            #fedcatalog_url = f'{shared.fedcatalog_url}{request_query}'
            #try:
            #    utils_lib.read_url(fedcatalog_url)
            #except Exception as e:
            #    print("Error:", e)
            #    print("There was a problem with utils_lib.read_url for", fedcatalog_url)
            #    continue
            print("Iris Fedcatalog stuff commented out")
            print(f"[{current_instruction}] {request_network}.{request_station}.{param_dict['loc']}.{param_dict['chan']}")
            current_instruction += 1


            #Format argument into command text
            args = ""
            for arg in param_dict:
                #print("param_dict arg is ", param_dict)
                if (arg == 'net'):
                    args += " " + arg + "=" + request_network
                elif (arg == 'sta'):
                    args += " " + arg + "=" + request_station
                else:
                    if (arg == 'start'):
                        if (len(cmd_args) == 3):
                           args += " " + arg + "=" + str(cmd_args[0])
                        else:
                            args += " " + arg + "=" + param_dict[arg]
                    elif (arg == 'end'):
                        if (len(cmd_args) == 3):
                            args += " " + arg + "=" + str(cmd_args[1])
                        else:
                            args += " " + arg + "=" + param_dict[arg]
                    else:
                        args += " " + arg + "=" + param_dict[arg]

            #print("HERE IS ARGS!", args)

            #Call bin/ntk_computePSD.py
            print(f"{WHITE}***************** CALLING COMPUTE PSD *****************{ENDC}")
            #compute_command = "python bin/super_test.py" + args
            compute_command = sys.executable + " bin/ntk_computePSD.py" + args
            print(compute_command)
            os.system(compute_command)

            #Call bin/ntk_computePsdHour.py
            print(f"\n\n{WHITE}***************** CALLING EXTRACT PSD DAY *****************{ENDC}")
            compute_command = sys.executable + " bin/ntk_extractPsdDay.py" + args
            os.system(compute_command)

            print(f"\n\n{WHITE}***************** EXTRACTING PERIOD *****************{ENDC}")


            #Attempt to read from the extracted PSD File

            #Get the date values of extractPsdHour that we are going to read
            # Have to use renamed cmd_args to check length of args
            if (len(cmd_args) == 3):
                #print("Called by the cron job")
                start_date_time = cmd_args[0]
                #print("start date time is:", start_date_time)
            else:
                start_date_time = param_dict['start']

            start_date = start_date_time.split('T')[0]
            utc_start_date = UTCDateTime(start_date)
            #print("HERE IS UTC_START_DATE", utc_start_date)

            if (len(cmd_args) == 3):
                #print("Called by the cron job")
                end_date_time = cmd_args[1]
                #print("end date time is:", end_date_time)
            else:
                end_date_time = param_dict['end']

            end_date = end_date_time.split('T')[0]
            utc_end_date = UTCDateTime(end_date)

            #Set filepath to the extracted PSD hour file
            psd_hour_dir, psd_hour_tag = file_lib.get_dir(data_directory, shared.psdDirectory, 
                                        request_network, request_station, param_dict['loc'], param_dict['chan'])

            #Begin looping through each day requested
            utc_curr_date = utc_start_date
            lines = list()
            while(utc_curr_date <= utc_end_date):

                curr_date = str(utc_curr_date).split('T')[0]

                psd_hour_file = os.path.join(psd_hour_dir, f"{psd_hour_tag}.{curr_date}.{param_dict['window_length']}.{param_dict['xtype']}.txt")
                
                #print("psd_hour_file is:", psd_hour_file)
                
                #Begin reading the PSD hour file
                if(os.path.exists(psd_hour_file) and os.path.isfile(psd_hour_file)):
                    with open(psd_hour_file) as file:
                        for line in file:
                            lines.append(line.split())
                else:
                    print('Error occurred within ntk_extractPsdDay.py, skipping...')
                    utc_curr_date += 24 * 3600
                    continue

                #Increment the current date
                utc_curr_date += 24 * 3600

            for period in settings_dict['period_value']:
                #Now that data has been retrieved, find the closest period value
                output_data = list()
                min_dist = None
                closest_period_line = None
                prev_time = None
                for line in lines:
                    curr_time = line[DATE_INDEX] + "T" + line[TIME_INDEX]
                    curr_dist = abs(float(period) - float(line[PERIOD_INDEX]))
                    if(prev_time != curr_time):
                        if(not closest_period_line is None):
                            #print("psd_hour_dir, psd_hour_tag", psd_hour_dir, psd_hour_tag)
                            #print("closest period line is: ", closest_period_line)
                            tries = 0
                            uploadValueToGraphite(closest_period_line, psd_hour_tag, tries, ADM_EMAILS, GRAPHITE_URL, GRAPHITE_PORT)
                            output_data.append(closest_period_line)
                        prev_time = curr_time
                        min_dist = curr_dist
                        closest_period_line = line
                    else:
                        if(min_dist is None or min_dist >= curr_dist):
                            min_dist = curr_dist
                            closest_period_line = line
            
                #If output data has no lines, exit
                if(len(output_data) == 0):
                    print("No data found within the computed PSD files, skipping...")
                    continue

                #print("psd_hour_dir, psd_hour_tag", psd_hour_dir, psd_hour_tag)
                #print("closest period line is: ", closest_period_line)
                tries = 0
                uploadValueToGraphite(closest_period_line, psd_hour_tag, tries, ADM_EMAILS, GRAPHITE_URL, GRAPHITE_PORT)
                output_data.append(closest_period_line)

                #Input the data into destination file
                dest_dir, dest_tag = file_lib.get_dir(data_directory, 'psdPr', 
                                                request_network, request_station, param_dict['loc'], param_dict['chan'])

                file_lib.make_path(dest_dir)
                dest_tag = f'{dest_tag}.{period}'

                final_destination = os.path.join(dest_dir, dest_tag) + ".txt"

                #Check that the settings are not overwrite
                if not settings_dict['overwrite'] and os.path.exists(final_destination):
                    previous_lines = list()
                    with open(final_destination, 'r') as file:
                        for line in file:
                            previous_lines.append(line.split())
                    if len(previous_lines) > 0:
                        first_date = UTCDateTime(previous_lines[0][DATE_INDEX])
                        last_date = UTCDateTime(previous_lines[len(previous_lines) - 1][DATE_INDEX])
                        curr_first_date = UTCDateTime(output_data[0][DATE_INDEX])
                        curr_last_date = UTCDateTime(output_data[len(output_data) - 1][DATE_INDEX])
                        if curr_first_date < first_date:
                            output_data = output_data + previous_lines
                        elif curr_first_date > last_date:
                            output_data = previous_lines + output_data
                        else:
                            minIndex, maxIndex = len(previous_lines), 0
                            for index in range(len(previous_lines)):
                                date_at_index = UTCDateTime(previous_lines[index][DATE_INDEX])
                                if(curr_first_date <= date_at_index and minIndex > index):
                                    minIndex = index
                                if(curr_last_date >= date_at_index and maxIndex < index):
                                    maxIndex = index
                            output_data = previous_lines[:minIndex] + output_data + previous_lines[(maxIndex+1):]

            
                #Write to file
                output_lines = list()
                for data in output_data:
                    text = '  '.join(data[:VALUE_INDEX]) + '    ' + data[VALUE_INDEX]
                    output_lines.append(text)

                with open(final_destination, 'w') as file:
                    for output in output_lines:
                        file.write(f'{output}\n')
                    



            #Epilogue
            json_object.close()

    if(current_instruction == 0):
        code = msg_lib.error(f'Invalid input of networks and stations. Confirm that at least one of the network-station permutations have a valid FDSN station', 2)
        sys.exit(code)


if __name__ == "__main__":
    import sys
    if (len(sys.argv) == 4):
        time1 = sys.argv[1]
        time2 = sys.argv[2]
        file = sys.argv[3]
        main(time1, time2, file)
    elif (len(sys.argv) == 1):
        main()
    else:
        print("Wrong number of arguments. I don't know what to do")
        sys.exit(1)
    
