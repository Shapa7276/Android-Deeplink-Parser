# Android-Deeplink-Parser

## This Script can be used to Parse the AndroidManifest.xml and Strings.xml to List the all deeplinks of the android application 


![Alt Text](https://github.com/Shapa7276/Android-Deeplink-Parser/blob/main/Animation.gif)

# Example 

```Java
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
fbconnect://test
lol://lol
word://
```

# Installation
```
Download Jadx from https://github.com/skylot/jadx
git clone https://github.com/Shapa7276/Android-Deeplink-Parser.git
Update the path of jadx in "deeplinkparser.py" on line number 160
Run below command with apk file as input 
python3 deeplinkparser.py facebook.apk
```

# Reference 
* https://developer.android.com/training/app-links/deep-linking
