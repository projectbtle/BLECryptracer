package de.ecspride;

import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;

public class LooperThread extends Thread {
	
	public static Handler handler = new Handler() {
        private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
        public void handleMessage(Message msg) {
      	  if (msg.obj != null && msg.obj instanceof byte[])
              mBluetoothGattCharacteristic.setValue((byte[]) msg.obj); // sink
        }
	};
	public boolean ready = false;
	
	public void run() {
		Looper.prepare();
		ready = true;
		Looper.loop();
	}
	
}
