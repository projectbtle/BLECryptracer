package edu.mit.shared_preferences;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;


public class AnotherActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Restore preferences
       SharedPreferences settings = getSharedPreferences(MainActivity.PREFS_NAME, 0);
       String bytesToWrite = settings.getString("imei", "");
        mBluetoothGattCharacteristic.setValue(bytesToWrite); //sink, leak
    }
}
