package edu.mit.icc_event_ordering;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

/*
 * This class is used to make sure that privacy detecting tools can distinguish the different components.
 */
public class IsolateActivity extends Activity 
{
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		super.onCreate(savedInstanceState);
		
		Intent i = getIntent();
		String bytesToWrite = i.getStringExtra("DroidBench");
		mBluetoothGattCharacteristic.setValue(bytesToWrite);
	}
	
}
