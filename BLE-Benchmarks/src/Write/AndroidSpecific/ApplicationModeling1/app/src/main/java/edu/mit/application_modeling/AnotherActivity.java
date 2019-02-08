package edu.mit.application_modeling;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.util.Log;

public class AnotherActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mBluetoothGattCharacteristic.setValue(((MyApplication)getApplication()).bytesToWrite); //Sink
    }
}
