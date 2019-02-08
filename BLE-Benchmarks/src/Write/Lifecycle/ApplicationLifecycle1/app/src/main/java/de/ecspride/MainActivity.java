package de.ecspride;

import de.ecspride.applicationlifecycle1.R;
import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.telephony.SmsManager;

public class MainActivity extends Activity {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
	}

	public void onResume() {
        super.onResume();
		mBluetoothGattCharacteristic.setValue(ApplicationLifecyle1.bytesToWrite); //sink, leak
    }
}
