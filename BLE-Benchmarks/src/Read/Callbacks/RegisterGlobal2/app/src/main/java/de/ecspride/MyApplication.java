package de.ecspride;

import android.app.Application;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.ComponentCallbacks2;
import android.content.Context;
import android.content.res.Configuration;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class MyApplication extends Application {
	
	ComponentCallbacks2 callbacks = new ComponentCallbacks2() {

		byte[] characteristicValue;
		private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
		
		@Override
		public void onLowMemory() {
	        TelephonyManager telephonyManager = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
			characteristicValue = mBluetoothGattCharacteristic.getValue(); //source
		}
		
		@Override
		public void onConfigurationChanged(Configuration newConfig) {
			SecretKey secret = generateKey("*****");
			byte[] decryptedValue = new byte[0];
			try {
				decryptedValue = decryptMsg(characteristicValue, secret);
			} catch (InvalidKeyException e) {
				e.printStackTrace();
			} catch (IllegalBlockSizeException e) {
				e.printStackTrace();
			} catch (BadPaddingException e) {
				e.printStackTrace();
			} catch (UnsupportedEncodingException e) {
				e.printStackTrace();
			}  //sink, leak
		}
		
		@Override
		public void onTrimMemory(int level) {
			// TODO Auto-generated method stub
			
		}

		// Both methods taken from here: https://stackoverflow.com/questions/40123319/easy-way-to-encrypt-decrypt-string-in-android
		public SecretKey generateKey(String password)
		{
			SecretKeySpec secret;
			return secret = new SecretKeySpec(password.getBytes(), "AES");
		}

		public byte[] decryptMsg(byte[] sourceBytes, SecretKey secret)
				throws InvalidKeyException, IllegalBlockSizeException, BadPaddingException, UnsupportedEncodingException {
			Cipher cipher = null;
			cipher.init(Cipher.DECRYPT_MODE, secret);
			byte[] decryptedBytes = cipher.doFinal(sourceBytes); //Sink
			return decryptedBytes;
		}
	};
	
	@Override
	public void onCreate() {
		super.onCreate();
		this.registerComponentCallbacks(callbacks);
	}
	
	@Override
	public void onTerminate() {
		super.onTerminate();
		this.unregisterComponentCallbacks(callbacks);
	}

}
