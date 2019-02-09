from worker_setvalue import WorkerSetvalue
from multiprocessing import Process, JoinableQueue, active_children
import sys
import os
import fnmatch

#apk_folder = "/mnt/sda1/apps_gatt/"
apk_folder = "../test/"
extension = "apk"

# Number of (multiprocessing) processes.
NUMBER_OF_PROCESSES = 2

error_output = "crypto_analysis_setvalue_error.txt"
fo_err = open(error_output, 'a', 0)


def main():
    # Keep track of the number of processes we create.
    num_processes = 0

    # Check whether output file already exists.
    # If it does, then append to existing file.
    # If it doesn't, then create a new file and initialise with headers.
    file_exists = False
    output_file = "crypto_analysis_setvalue_output.csv"
    try:
        fo_output_file = open(output_file, 'r')
        fo_output_file.close()
        file_exists = True
    except:
        print "Output file does not yet exist. Creating and initialising with column headers."

    fo_output_file = open(output_file, 'a', 0)
    if file_exists != True:
        fo_output_file.write(
            "FILENAME,PACKAGE,SETVALUE_CALL,CRYPTO_USE,CRYPTO_IN_SETVALUE,CONFIDENCE_LEVEL_SETVALUE,NET_USE,LOCATION_SETVALUE,LOCATION_CRYPTO_SETVALUE,NUM_SETVALUE_METHODS,ALL_SETVALUE_METHODS,TIME_TAKEN_SETVALUE,NOTES\n")

    # Enumerate all files in app directory.
    matches = []
    for root, dirnames, filenames in os.walk(apk_folder):
        for filename in fnmatch.filter(filenames, '*' + extension):
            matches.append(os.path.join(root, filename))

    if matches == []:
        print "No APK files found."
        sys.exit(0)

    # Remove already checked apps from list.
    checked_apks = []
    try:
        checked_file = "crypto_analysis_setvalue_checked.txt"
        fo_checked = open(checked_file, 'r')
        checked_apks = fo_checked.read().splitlines()
        fo_checked.close()
    except Exception as e:
        print "No existing list of checked files."

    for checked_apk in checked_apks:
        try:
            matches.remove(checked_apk)
        except Exception as e:
            print "Unable to remove apk from list:", str(e)

    if matches == []:
        print "All APK files checked."
        sys.exit(0)

    length_apk_list = len(matches)/NUMBER_OF_PROCESSES
    length_apk_list = int(length_apk_list)
    print "Total number of APKs:", len(
        matches), "\nApproximate number of APKs per thread:", length_apk_list

    # Free up memory
    checked_apks = None
    initial_matches = None

    # Create two process queues: one for sending data to, and one for receiving data from, worker process.
    process_send_queue = JoinableQueue()
    process_receive_queue = JoinableQueue()

    # List for keeping track of processes.
    process_list = []
    # Create worker processes.
    for i in range(0, NUMBER_OF_PROCESSES):
        worker_svalue = WorkerSetvalue()
        worker = Process(target=worker_svalue.main, args=(
            process_send_queue, process_receive_queue, num_processes))
        worker.start()
        process_list.append(worker)
        num_processes += 1

    # Send work to worker process.
    for match in matches:
        process_send_queue.put(str(match))

    fo_checked = open(checked_file, 'a', 0)
    completed_apk_count = 0

    while True:
        # Get information sent by worker process.
        result = process_receive_queue.get()
        process_receive_queue.task_done()
        # Analyse the output string.
        analysed_file = result.split(",")[0]
        fo_checked.write(analysed_file+"\n")
        if result.split(",")[2] == "Error":
            write_string = result.split("err_div")[0]
            err_string = result.split("err_div")[1]
            fo_output_file.write(write_string)
            # Log the error to a separate file.
            fo_err.write(analysed_file+","+err_string)
        else:
            fo_output_file.write(result)
        print "\n  Finished analysing", analysed_file

        # Check if any processes have become zombies.
        # Actually, this should not be necessary.
        if len(active_children()) < NUMBER_OF_PROCESSES:
            for p in process_list:
                if not p.is_alive():
                    process_list.remove(p)
                    # Create a new process in its place.
                    worker_svalue = WorkerSetvalue()
                    replacement_worker = Process(target=worker_svalue.main, args=(
                        process_send_queue, process_receive_queue, num_processes))
                    replacement_worker.start()
                    process_list.append(replacement_worker)
                    num_processes += 1

        # Check if all APKs have been analysed.
        completed_apk_count += 1
        if completed_apk_count == len(matches):
            break

    print "All done."

    # Tell child processes to stop
    for i in range(NUMBER_OF_PROCESSES):
        process_send_queue.put('STOP')


#=====================================================#
if __name__ == "__main__":
    main()
