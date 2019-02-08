package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.view.Menu;

import de.ecs2.LibClass;

/**
 * @testcase_name Library2
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail steven.arzt@cased.de
 * 
 * @description The IMEI is read out inside a custom library and then leaked in the app.
 * @dataflow OnCreate: source -> imei -> sink
 * @number_of_leaks 1
 * @challenges The analysis must correctly handle custom libraries
 */
public class MainActivity extends Activity {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		
		LibClass lc = new LibClass();
		byte[] bytesToWrite = lc.getIMEI(this);

		mBluetoothGattCharacteristic.setValue(bytesToWrite);  //sink, leak
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}

}
