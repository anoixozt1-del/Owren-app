import pathlib, re

# ---- AndroidManifest ----
mf = pathlib.Path('android/app/src/main/AndroidManifest.xml')
m = mf.read_text(encoding='utf-8')
if 'POST_NOTIFICATIONS' not in m:
    perms = '''<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.VIBRATE"/>
    <uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" android:maxSdkVersion="32"/>
    <uses-permission android:name="android.permission.USE_EXACT_ALARM"/>
    '''
    receivers = '''
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED"/>
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                <action android:name="com.htc.intent.action.QUICKBOOT_POWERON"/>
            </intent-filter>
        </receiver>
    '''
    queries = '''<queries>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
    </queries>
    '''
    m = m.replace('<application', perms + queries + '<application', 1)
    m = re.sub(r'android:label="[^"]*"', 'android:label="Söz Ýatlatma"', m, count=1)
    m = m.replace('</application>', receivers + '</application>', 1)
    mf.write_text(m, encoding='utf-8')

# ---- Gradle (desugaring) ----
kts = pathlib.Path('android/app/build.gradle.kts')
groovy = pathlib.Path('android/app/build.gradle')
if kts.exists():
    g = kts.read_text(encoding='utf-8')
    if 'isCoreLibraryDesugaringEnabled' not in g:
        g = g.replace('compileOptions {', 'compileOptions {\n        isCoreLibraryDesugaringEnabled = true', 1)
        g += '\ndependencies {\n    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")\n}\n'
        kts.write_text(g, encoding='utf-8')
elif groovy.exists():
    g = groovy.read_text(encoding='utf-8')
    if 'coreLibraryDesugaringEnabled' not in g:
        g = g.replace('compileOptions {', 'compileOptions {\n        coreLibraryDesugaringEnabled true', 1)
        g += "\ndependencies {\n    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.4'\n}\n"
        groovy.write_text(g, encoding='utf-8')
# ---- Bildiriş kiçi nyşany (ak jaň) ----
d = pathlib.Path('android/app/src/main/res/drawable')
d.mkdir(parents=True, exist_ok=True)
(d / 'ic_stat.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF"
        android:pathData="M12,22c1.1,0 2,-0.9 2,-2h-4c0,1.1 0.89,2 2,2zM18,16v-5c0,-3.07 -1.64,-5.64 -4.5,-6.32V4c0,-0.83 -0.67,-1.5 -1.5,-1.5s-1.5,0.67 -1.5,1.5v0.68C7.63,5.36 6,7.92 6,11v5l-2,2v1h16v-1l-2,-2z"/>
</vector>
''', encoding='utf-8')
# ---- Diňe täze Android (10+) ----
for gf in (kts, groovy):
    if gf.exists():
        g = gf.read_text(encoding='utf-8')
        g = re.sub(r'minSdk(Version)?(\s*=\s*|\s+)flutter\.minSdkVersion',
                   lambda mm: 'minSdk%s%s29' % (mm.group(1) or '', mm.group(2)), g)
        gf.write_text(g, encoding='utf-8')

# ---- R8/proguard (bildirişler üçin) ----
pathlib.Path('android/app/proguard-rules.pro').write_text('''-keep class com.dexterous.flutterlocalnotifications.** { *; }
-keep class com.google.gson.** { *; }
-keepattributes Signature
-keepattributes *Annotation*
''', encoding='utf-8')
print('Patch OK')
