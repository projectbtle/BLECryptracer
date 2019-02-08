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
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidParameterSpecException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class MyApplication extends Application {
	
	ComponentCallbacks2 callbacks = new ComponentCallbacks2() {

		byte[] bytesToWrite = new byte[0];
		private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
		
		@Override
		public void onLowMemory() {
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
		public void onConfigurationChanged(Configuration newConfig) {
			mBluetoothGattCharacteristic.setValue(bytesToWrite); // sink  //sink, leak
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
