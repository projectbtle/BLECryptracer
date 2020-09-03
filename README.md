# BLECryptracer #

BLECryptracer is a tool for analysing Android applications (APK files), to identify the presence of cryptographically-processed BLE data. It consists of custom Python scripts, which utilise [Androguard](https://github.com/androguard/androguard). Separate scripts have been developed for analysing BLE reads and writes.

This repository consists of three folders:
1. "BLECryptracer" - Contains the Python scripts (which invoke Androguard) and instructions on how to use them.
2. "Amandroid Tests" - Contains custom source-sink files used for executing [Amandroid](http://pag.arguslab.org/argus-saf), to run comparison tests. 
3. "BLE Benchmarks" - Contains sample Android applications, based on the DroidBench benchmarking suite, for testing our tools.

An additional folder "Test Dataset" contains lists of the (SHA256 hashes of) applications used in the first phase of our research. It also contains the SHA256 hashes of applications that were identified as having cryptographically-processed BLE data with High confidence.

Further details about the code, as well as information about BLE data security in the presence of co-located Android apps, can be found in our [paper](https://www.usenix.org/system/files/sec19-sivakumaran_0.pdf) (presented at the 28th USENIX Security Symposium, August 2019).
