package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;

/**
 * @testcase_name LocationLeak3
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail steven.arzt@cased.de
 * 
 * @description This example contains a location information leakage in the onResume() callback method.
 *  The data source is placed into the onLocationChanged() callback method in a separate class
 *  which sets the data into a field of the activity. Activity and callback are decoupled using an
 *  interface.
 * @dataflow onLocationChanged: source -> data -> onResume -> sink 
 * @number_of_leaks 1
 * @challenges the analysis must be able to emulate the Android activity lifecycle correctly,
 *  integrate the callback method onLocationChanged, detect the callback methods as source
 *  and connect the callback class to the activity via the interface.
 */
public class LocationLeak3 extends Activity implements IDataProvider {

	private byte[] bytesToWrite = new byte[0];
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_multi_handlers1);
		
        LocationListener locationListener = new MyLocationListener(this);  
        LocationManager locationManager = (LocationManager) 
        		getSystemService(Context.LOCATION_SERVICE);
        locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000, 10, locationListener);
	}

	@Override
    protected void onResume (){
    	super.onResume();
		mBluetoothGattCharacteristic.setValue(bytesToWrite); // sink
    }

	@Override
	public void setData(byte[] data) {
		this.bytesToWrite = data;
	}
}
