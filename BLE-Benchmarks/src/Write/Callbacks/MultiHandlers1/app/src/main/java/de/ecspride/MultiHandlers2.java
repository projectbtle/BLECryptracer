package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;

/**
 * @testcase_name MultiHandlers1
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail steven.arzt@cased.de
 * 
 * @description This example two activities that share the same callback class. However, none
 * 	of them actually leaks the data
 * @dataflow onLocationChanged: source -> / 
 * @number_of_leaks 0
 * @challenges the analysis must be able to correctly associate callback handlers
 * 	with the respective activities
 */
public class MultiHandlers2 extends Activity implements IDataProvider {

	private byte[] bytesToWrite = new byte[0];
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_multi_handlers1);
		
        LocationListener locationListener = new MyLocationListener1(this);  
        LocationManager locationManager = (LocationManager) 
        		getSystemService(Context.LOCATION_SERVICE);
        locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000, 10, locationListener);
	}

	@Override
    protected void onResume (){
    	super.onResume();
		mBluetoothGattCharacteristic.setValue(bytesToWrite); // sink //sink, leak
    }

	@Override
	public void setData(byte[] data) {
	}
}
