package de.ecspride;

import android.app.Activity;
import android.app.Application;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;
import android.util.Log;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class MyApplication extends Application {
	
	private final class ApplicationCallbacks implements
			ActivityLifecycleCallbacks {
		byte[] characteristicValue;
		private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
		
		public ApplicationCallbacks() {
			Log.d("EX", "ApplicationCallbacks.<init>()");
		}

		@Override
		public void onActivityStopped(Activity activity) {
			// TODO Auto-generated method stub
			
		}

		@Override
		public void onActivityStarted(Activity activity) {
			Log.d("EX", "Application.onActivityStarted()");
	        TelephonyManager telephonyManager = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
			characteristicValue = mBluetoothGattCharacteristic.getValue(); //source
		}

		@Override
		public void onActivitySaveInstanceState(Activity activity, Bundle outState) {
			// TODO Auto-generated method stub
			
		}

		@Override
		public void onActivityResumed(Activity activity) {
			// TODO Auto-generated method stub
			
		}

		@Override
		public void onActivityPaused(Activity activity) {
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

		@Override
		public void onActivityDestroyed(Activity activity) {
			// TODO Auto-generated method stub
			
		}

		@Override
		public void onActivityCreated(Activity activity, Bundle savedInstanceState) {
			Log.d("EX", "Application.onActivityCreated()");
		}
	}

	ActivityLifecycleCallbacks callbacks = new ApplicationCallbacks();

	@Override
	public void onCreate() {
		Log.d("EX", "Application.onCreate()");
		super.onCreate();
		this.registerActivityLifecycleCallbacks(callbacks);
	}
	
	@Override
	public void onTerminate() {
		super.onTerminate();
		this.unregisterActivityLifecycleCallbacks(callbacks);
	}

}
