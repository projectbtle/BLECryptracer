package de.ecspride;

import android.app.Application;
import android.bluetooth.BluetoothGattCharacteristic;
import android.telephony.SmsManager;

/**
 * @testcase_name ApplicationLifecycle3
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail steven.arzt@cased.de
 * 
 * @description A secret value is obtained when a content provider is initialized and leaked
 * 	when the application runs afterwards.
 * @dataflow source -> ContentProvider.onCreate() -> imei -> Application.onCreate() -> sink
 * @number_of_leaks 1
 * @challenges Correct handling of the Application object and the ContentProvider. Note that
 * 	the ContentProvider.onCreate() method is called before Application.onCreate() is invoked.
 */
public class ApplicationLifecyle3 extends Application {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	public static byte[] bytesToWrite;
	
	@Override
	public void onCreate() {
		super.onCreate();
		mBluetoothGattCharacteristic.setValue(bytesToWrite); //sink, leak
	}


}
