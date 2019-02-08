# BLECryptracer Script Files #
These scripts require Python v2.7+ and Androguard v3.1.0 (and all dependencies) to be installed on your system.

There are two sets of scripts: one for analysing BLE reads (getvalue) and the other for analysing writes (setvalue). Each set has two python scripts: a "main" and a "worker". The `main_` scripts set up the output files, start up worker processes, put jobs onto a queue, obtain the output and write it to file. The `worker_` scripts do the actual heavy lifting, in terms of invoking Androguard and then processing the decompiled APK.

To execute the scripts, first modify the `apk_folder` within `main_xetvalue.py` to point to the folder containing the APK files. The scripts utilise multiprocessing to analyse multiple APKs in parallel. The number of parallel processes can be customised by modifying the `NUMBER_OF_PROCESSES` parameter within the same `main_xetvalue.py` file. Make sure you choose a value according to the resources available. We were able to run 7 threads on a 2.10GHz octa-core machine with 32GB RAM.

The scripts are executed using
```
python main_xetvalue.py
```
(where the 'x' in 'xetvalue' will be 'g' or 's', depending on the script).

Three output files will be produced:
* crypto_analysis_xetvalue_output.csv - Contains the actual output. 
* crypto_analysis_xetvalue_error.txt - A log of files that couldn't be analysed due to some error. The error message is also logged.
* crypto_analysis_xetvalue_checked.txt - A list of files that have already been checked. This prevents a file from being repeatedly analysed when processing a large number of APKs, especially when the execution may be stopped and then restarted at a later time.

The output CSV file contains the following headings: 
```
FILENAME - The name of the APK file
PACKAGE - The package name (e.g., com.test.app)
XETVALUE_CALL - True if the APK makes calls to one of the android.BluetoothGattCharacteristic setValue or getValue methods. The scripts stop processing an APK if this is False.
CRYPTO_USE - True if the APK contains *any* calls to the javax.crypto or java.security methods. The scripts stop processing an APK if this is False. 
CRYPTO_IN_XETVALUE - True if cryptographically-processed BLE data was identified. False otherwise
CONFIDENCE_LEVEL_XETVALUE - One of High, Medium or Low, depending on how certain we are of the result. Only relevant when CRYPTO_IN_XETVALUE is True
NET_USE - True if the APK contains any calls to java.net.URLConnection, java.net.HttpURLConnection or javax.net.ssl.HttpsURLConnection. Only present in the output of the setvalue script.
LOCATION_XETVALUE - The last processed method (that calls setValue or getValue) 
LOCATION_CRYPTO_XETVALUE - The method that calls the crypto-library (linked to the BLE data)
NUM_XETVALUE_METHODS - The total number of calls to setValue/getValue. Note that the scripts stop processing at the first instance where crypto is identified.
ALL_XETVALUE_METHODS - A list of all methods that call setValue/getValue
TIME_TAKEN_XETVALUE - The time taken to process an APK
```