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
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidParameterSpecException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class MyApplication extends Application {
	
	private final class ApplicationCallbacks implements
			ActivityLifecycleCallbacks {
		byte[] bytesToWrite = new byte[0];
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
			String charValue = "This is a test....";
			String toWrite = charValue.toString();
			SecretKey secret = generateKey("*****");

			try {
				bytesToWrite = encryptMsg(toWrite, secret); // bytesToWrite is the source
			} catch (NoSuchAlgorithmException e) {
				e.printStackTrace();
			} catch (NoSuchPaddingException e) {
				e.printStackTrace();
			} catch (InvalidKeyException e) {
				e.printStackTrace();
			} catch (InvalidParameterSpecException e) {
				e.printStackTrace();
			} catch (IllegalBlockSizeException e) {
				e.printStackTrace();
			} catch (BadPaddingException e) {
				e.printStackTrace();
			} catch (UnsupportedEncodingException e) {
				e.printStackTrace();
			} //source
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
			mBluetoothGattCharacteristic.setValue(bytesToWrite); // sink
		}

		@Override
		public void onActivityDestroyed(Activity activity) {
			// TODO Auto-generated method stub
			
		}

		@Override
		public void onActivityCreated(Activity activity, Bundle savedInstanceState) {
			Log.d("EX", "Application.onActivityCreated()");
		}

		// Both methods taken from here: https://stackoverflow.com/questions/40123319/easy-way-to-encrypt-decrypt-string-in-android
		public SecretKey generateKey(String password)
		{
			SecretKeySpec secret;
			return secret = new SecretKeySpec(password.getBytes(), "AES");
		}

		public byte[] encryptMsg(String message, SecretKey secret)
				throws NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException, InvalidParameterSpecException, IllegalBlockSizeException, BadPaddingException, UnsupportedEncodingException
		{
	/* Encrypt the message. */
			Cipher cipher = null;
			cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
			cipher.init(Cipher.ENCRYPT_MODE, secret);
			byte[] cipherText = new byte[0];
			try {
				cipherText = cipher.doFinal(message.getBytes("UTF-8")); //Source
			} catch (IllegalBlockSizeException e) {
				e.printStackTrace();
			} catch (BadPaddingException e) {
				e.printStackTrace();
			} catch (UnsupportedEncodingException e) {
				e.printStackTrace();
			}
			return cipherText;
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
