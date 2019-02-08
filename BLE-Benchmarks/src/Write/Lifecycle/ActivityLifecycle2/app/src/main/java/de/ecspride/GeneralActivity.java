package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.telephony.SmsManager;

public class GeneralActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	protected static byte[] bytesToWrite = null;
    
	@Override
    public void onResume() {
        super.onResume();
        mBluetoothGattCharacteristic.setValue(bytesToWrite); //sink, leak

    }
}
