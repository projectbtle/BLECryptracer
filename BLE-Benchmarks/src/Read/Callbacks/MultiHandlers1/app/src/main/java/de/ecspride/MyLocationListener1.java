package de.ecspride;

import android.bluetooth.BluetoothGattCharacteristic;
import android.location.Location;
import android.location.LocationListener;
import android.os.Bundle;

public class MyLocationListener1 implements LocationListener {

	private IDataProvider dataProvider;
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	
	public MyLocationListener1(IDataProvider provider) {
		this.dataProvider = provider;
	}
	
	@Override
	public void onLocationChanged(Location arg0) {
		byte[] characteristicValue = mBluetoothGattCharacteristic.getValue();
		dataProvider.setCharacteristicValue(characteristicValue);
	}

	@Override
	public void onProviderDisabled(String provider) {
		// TODO Auto-generated method stub

	}

	@Override
	public void onProviderEnabled(String provider) {
		// TODO Auto-generated method stub

	}

	@Override
	public void onStatusChanged(String provider, int status, Bundle extras) {
		// TODO Auto-generated method stub

	}

}
