package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.Menu;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

/**
 * @testcase_name BroadcastReceiverLifecycle1
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail Steven.Arzt@cased.de
 * 
 * @description The sensitive data is read in onCreate() and sent out in a dynamically registered
 *   broadcast receiver.
 * @dataflow source -> imei -> sink
 * @number_of_leaks 1
 * @challenges The analysis must be able to handle the dynamic registration of broadcast
 *   receivers
 */
public class MainActivity extends Activity {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

        byte[] characteristicValue = mBluetoothGattCharacteristic.getValue(); //source
		
		IntentFilter filter = new IntentFilter();
		filter.addAction("de.ecspride.MyAction");
		
		registerReceiver(new MyReceiver(characteristicValue), filter);
		
		Intent intent = new Intent();
		intent.setAction("de.ecspride.MyAction");
		sendBroadcast(intent);
	}
	
	private class MyReceiver extends BroadcastReceiver {
		
		private final byte[] deviceId;
		
		public MyReceiver(byte[] deviceId) {
			this.deviceId = deviceId;
		}

		@Override
		public void onReceive(Context context, Intent intent) {
            SecretKey secret = generateKey("*****");
            byte[] decryptedValue = new byte[0];
            try {
                decryptedValue = decryptMsg(deviceId, secret);
            } catch (InvalidKeyException e) {
                e.printStackTrace();
            } catch (IllegalBlockSizeException e) {
                e.printStackTrace();
            } catch (BadPaddingException e) {
                e.printStackTrace();
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
		}
		
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}



    // Both methods taken from here: https://stackoverflow.com/questions/40123319/easy-way-to-encrypt-decrypt-string-in-android
    public static SecretKey generateKey(String password)
    {
        SecretKeySpec secret;
        return secret = new SecretKeySpec(password.getBytes(), "AES");
    }

    public static byte[] decryptMsg(byte[] sourceBytes, SecretKey secret)
            throws InvalidKeyException, IllegalBlockSizeException, BadPaddingException, UnsupportedEncodingException {
        Cipher cipher = null;
        cipher.init(Cipher.DECRYPT_MODE, secret);
        byte[] decryptedBytes = cipher.doFinal(sourceBytes); //Sink
        return decryptedBytes;
    }

}
