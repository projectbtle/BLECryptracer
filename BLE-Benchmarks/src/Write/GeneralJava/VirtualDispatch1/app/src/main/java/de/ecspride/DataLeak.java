package de.ecspride;

import android.bluetooth.BluetoothGattCharacteristic;
import android.util.Log;

public class DataLeak extends NoDataLeak{
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

	public DataLeak(String data){
		super(data);
	}
	
	@Override
	public void logData(){
		mBluetoothGattCharacteristic.setValue(super.getData()); // sink

	}
}
