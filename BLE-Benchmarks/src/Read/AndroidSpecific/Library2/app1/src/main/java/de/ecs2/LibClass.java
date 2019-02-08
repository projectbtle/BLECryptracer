package de.ecs2;

import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;


/**
 * THIS IS NOT A TEST CASE ON ITS OWN. IT IS A PART OF LIBRARY2.
 * @author Steven Arzt
 */
public class LibClass {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

	public byte[] getIMEI(Context context) {
		return mBluetoothGattCharacteristic.getValue(); //source
	}
	
}
