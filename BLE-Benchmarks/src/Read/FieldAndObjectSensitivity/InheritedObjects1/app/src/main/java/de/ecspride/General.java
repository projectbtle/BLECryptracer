package de.ecspride;

import android.bluetooth.BluetoothGattCharacteristic;
import android.telephony.TelephonyManager;

public abstract class General {
	BluetoothGattCharacteristic man;
	public abstract byte[] getInfo();
}
