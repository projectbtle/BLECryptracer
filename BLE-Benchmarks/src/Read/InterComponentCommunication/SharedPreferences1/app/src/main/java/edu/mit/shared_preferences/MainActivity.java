package edu.mit.shared_preferences;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.telephony.TelephonyManager;

/**
 * @testcase_name SharedPreferences
 * 
 * @description Test modeling of SharedPreferences
 * @dataflow source -> sink
 * @number_of_leaks 1
 * @challenges - Modeling of SharedPreferences
 */
public class MainActivity extends Activity {    
    public static final String PREFS_NAME = "MyPrefsFile";
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        String charValue = mBluetoothGattCharacteristic.getStringValue(0);
        
        SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
        SharedPreferences.Editor editor = settings.edit();
        editor.putString("imei", charValue);
        
        // Commit the edits!
        editor.commit();
    }
        
}
