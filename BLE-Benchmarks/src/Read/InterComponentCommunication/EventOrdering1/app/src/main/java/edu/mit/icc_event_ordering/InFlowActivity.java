package edu.mit.icc_event_ordering;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.telephony.TelephonyManager;
import android.util.Log;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class InFlowActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
    private static final String PREFS_NAME = "prefs";

    @Override
	protected void onCreate(Bundle savedInstanceState) {
	    super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		// Restore preferences
		SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
		String characteristicValue = settings.getString("imei", "");

        SecretKey secret = generateKey("*****");
        byte[] decryptedValue = new byte[0];
        try {
            decryptedValue = decryptMsg(characteristicValue.getBytes(), secret);
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        } //sink, leak of imei if a foreign app launches this activity before OutFlowActivity
		writePreferences();
	}

    private void writePreferences() {
	TelephonyManager telephonyManager = (TelephonyManager) getSystemService(TELEPHONY_SERVICE);
	String imei = mBluetoothGattCharacteristic.getStringValue(0);  //source
	
	SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
	SharedPreferences.Editor editor = settings.edit();
	editor.putString("imei", imei);
	
	// Commit the edits!
	editor.commit();
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
