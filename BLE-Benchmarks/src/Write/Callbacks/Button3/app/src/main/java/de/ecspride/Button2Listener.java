package de.ecspride;

import android.bluetooth.BluetoothGattCharacteristic;
import android.telephony.SmsManager;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;

public class Button2Listener implements OnClickListener {
	
	private final MainActivity act;
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	
	public Button2Listener(MainActivity parentActivity) {
		this.act = parentActivity;
	}

	@Override
	public void onClick(View arg0) {
		mBluetoothGattCharacteristic.setValue(act.bytesToWrite); // sink //sink, leak
	}

}
