package edu.mit.to_components_share_memory;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.telephony.TelephonyManager;
import edu.mit.to_components_share_memory.R;

public class AnotherActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        byte[] characteristicValue = mBluetoothGattCharacteristic.getValue();
        Singleton.v().s = characteristicValue;
    }
}
