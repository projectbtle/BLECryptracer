"""
    Copyright (C) 2018 projectbtle@tutanota.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from worker_getvalue import WorkerGetvalue
from multiprocessing import Process, JoinableQueue, active_children
import sys
import os
import fnmatch

#apk_folder = "/mnt/sda1/apps_gatt/"
apk_folder = "../test/"
extension = "apk"

NUMBER_OF_PROCESSES = 3

error_output = "crypto_analysis_getvalue_error.txt"
fo_err = open(error_output,'a',0)

def main():    
    #Keep track of the number of processes we create.
    num_processes = 0
    
    #Check whether output file already exists.
    # If it does, then append to the existing file.
    # If not, create new and initialise with headers.
    file_exists = False
    output_file = "crypto_analysis_getvalue_output.csv"
    try:
        fo_output_file = open(output_file, 'r')
        fo_output_file.close()
        file_exists = True
    except:
        print "Output file does not yet exist. Creating and initialising with column headers."
        
    fo_output_file = open(output_file, 'a', 0)
    if file_exists != True:
        fo_output_file.write("FILENAME,PACKAGE,GETVALUE,CRYPTO_USE,CRYPTO_IN_GETVALUE,CONFIDENCE_LEVEL_GETVALUE,LOCATION_GETVALUE,LOCATION_CRYPTO_GETVALUE,NUM_BLE_METHODS,ALL_BLE_METHODS,TIME_TAKEN_GETVALUE\n")
    
    #List all files in app directory.
    matches = []
    for root, dirnames, filenames in os.walk(apk_folder):
        for filename in fnmatch.filter(filenames, '*' + extension):
            matches.append(os.path.join(root, filename))

    if matches == []:
        print "No APK files found."
        sys.exit(0)
    
    #if num_apks == 0:
    num_apks = len(matches)
    
    #Remove already checked apps from list.
    checked_apks = []
    try:
        checked_file = "crypto_analysis_getvalue_checked.txt"
        fo_checked = open(checked_file,'r')
        checked_apks = fo_checked.read().splitlines()
        fo_checked.close()
    except Exception as e:
        print "List of checked files cannot be opened. Possibly it doesn't exist."

    for checked_apk in checked_apks:
        try:
            matches.remove(checked_apk)
        except Exception as e:
            print "Unable to remove apk.", str(e)
        
    if matches == []:
        print "All APK files checked."
        sys.exit(0)

    #Free up memory
    checked_apks = None
    initial_matches = None   

    length_apk_list = len(matches)/NUMBER_OF_PROCESSES
    length_apk_list = int(length_apk_list)
    print "Total number of APKs:", len(matches), "\nNumber of APKs per thread:", length_apk_list 

    #Create queues for sending jobs to worker threads and receiving results from them.
    process_send_queue = JoinableQueue()
    process_receive_queue = JoinableQueue()    
    
    process_list = []
    
    #Create worker processes.
    for i in range(0, NUMBER_OF_PROCESSES):
        worker_gvalue = WorkerGetvalue()
        worker = Process(target=worker_gvalue.main, args=(process_send_queue,process_receive_queue,num_processes))
        worker.start()
        process_list.append(worker)
        num_processes+=1
    
    #Send jobs to worker processes.
    for match in matches:
        process_send_queue.put(str(match))
        
    fo_checked = open(checked_file,'a',0)
    completed_apk_count = 0
    
    while True:
        #Get and process information sent by worker process.
        result = process_receive_queue.get()
        process_receive_queue.task_done()
        analysed_file = result.split(",")[0]
        fo_checked.write(analysed_file+"\n")
        if result.split(",")[2] == "Error":
            write_string = result.split("err_div")[0]
            err_string = result.split("err_div")[1]
            fo_output_file.write(write_string)
            fo_err.write(analysed_file+","+err_string)
        else:
            fo_output_file.write(result)
        print "\n  Finished analysing", analysed_file
        
        #Check if any processes have become zombies.
        if len(active_children()) < NUMBER_OF_PROCESSES:
            for p in process_list:
                if not p.is_alive():
                    process_list.remove(p)
                    #Create a new process in its place.        
                    worker_gvalue = WorkerGetvalue()
                    replacement_worker = Process(target=worker_gvalue.main, args=(process_send_queue,process_receive_queue,num_processes))
                    replacement_worker.start()
                    process_list.append(replacement_worker)
                    num_processes+=1
          
        #Check if all APKs have been analysed.
        completed_apk_count+=1
        if completed_apk_count == len(matches):
            break
            
    print "All done"
    # Tell child processes to stop
    for i in range(NUMBER_OF_PROCESSES):
        process_send_queue.put('STOP')
    
    
#=====================================================#  
if __name__ == "__main__":
    main()
