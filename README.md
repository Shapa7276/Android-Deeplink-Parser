# Android-Deeplink-Parser

## This Script to Parse the APK file to List the all deeplinks of the android application 

```
usage: deeplinkparser.py [-h] -a APK [-f] [-o OUTPUT]

Android APK Deeplink Scanner

options:
  -h, --help           show this help message and exit
  -a, --apk APK        Path to the APK file to analyze
  -f, --force          Force rescan even if results already exist
  -o, --output OUTPUT  Custom output directory for results (default: scan_results)

Examples:
  python script.py -a path/to/app.apk
  python script.py --apk app.apk
  python script.py -a app.apk --force  # Force rescan even if results exist
```
# Output saved in html format 
![Alt Text](html_report.png)

![Alt Text](Animation.gif)


# Example 

```XML
     <activity android:theme="@style/Theme.lolSplashBackground" android:name="com.lol.test.LaunchActivity" android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.VIEW"/>
                <category android:name="android.intent.category.DEFAULT"/>
                <category android:name="android.intent.category.BROWSABLE"/>
                <data android:scheme="@string/application_data_scheme" android:host="@string/application_data_host"/>
                <data android:scheme="@string/application_scheme" android:host="@string/application_data_host"/>
            </intent-filter>
            <intent-filter>
                <data android:scheme="@string/lol_schema" android:host="@string/lol_host"/>
                <action android:name="android.intent.action.VIEW"/>
                <category android:name="android.intent.category.DEFAULT"/>
                <category android:name="android.intent.category.BROWSABLE"/>
            </intent-filter>

```

# Output 
 AndroidManifest.xml and Strings.xml  will parsed and all deeplink will  be resulted as shown below 
 
```bash
------------------------------------com.lol.test.LaunchActivity----------------------------------------------

https://example.lol.com/test
lol://lol
word://
```

# Installation
```
Install the apktool 
sudo apt-get install apktool
git clone https://github.com/Shapa7276/Android-Deeplink-Parser.git
Run below command with apk file as input 
python3 deeplinkparser.py -a facebook.apk
```

# Reference 
* https://developer.android.com/training/app-links/deep-linking
