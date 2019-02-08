# Amandroid Taint Analysis Files #

First install Amandroid on your system (we used v3.1.3). To do this, download the Jar file from the link provided on the [Argus](http://pag.arguslab.org/argus-saf) website, and then execute it against a folder containing at least one APK file as follows:
``` 
java -jar argus-saf_***-version-assembly.jar t <path-to-apks>
```

When this is executed for the first time, Amandroid files will be downloaded and installed on your system. You can then copy the sources and sinks file over to <home-directory>/.amandroid-stash/amandroid/taintAnalysis/sourceAndSinks/TaintSourcesAndSinks.txt (replacing the file that is already there). After this point, when you execute the above command again, Amandroid will use the custom source/sink file.