package de.ecspride;

import android.app.Activity;
import android.app.Fragment;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.telephony.SmsManager;

public class ExampleFragment extends Fragment {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	private static byte[] bytesToWrite = null;
	
	@Override
	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);
        mBluetoothGattCharacteristic.setValue(bytesToWrite); //sink, leak
	}
	  
	  
	@Override
	public void onAttach(Activity activity) {
		super.onAttach(activity);
        bytesToWrite = MainActivity.bytesToWrite;
	}
}
