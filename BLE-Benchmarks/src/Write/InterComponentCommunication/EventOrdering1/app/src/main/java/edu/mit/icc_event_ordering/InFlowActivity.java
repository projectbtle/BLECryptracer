package edu.mit.icc_event_ordering;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.SharedPreferences;
import android.os.Bundle;
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

public class InFlowActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
    private static final String PREFS_NAME = "prefs";

    @Override
	protected void onCreate(Bundle savedInstanceState) {
	    super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		// Restore preferences
		SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
		String bytesToWrite = settings.getString("imei", "");

        mBluetoothGattCharacteristic.setValue(bytesToWrite);  //sink, leak of imei if a foreign app launches this activity before OutFlowActivity

		writePreferences();
	}

    private void writePreferences() {
        String charValue = "This is a test....";
        String toWrite = charValue.toString();
        SecretKey secret = generateKey("*****");
        byte[] bytesToWrite = new byte[0];
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
        }

        SharedPreferences settings = getSharedPreferences(PREFS_NAME, 0);
        SharedPreferences.Editor editor = settings.edit();
        editor.putString("imei", bytesToWrite.toString());

        // Commit the edits!
        editor.commit();
    }



	// Both methods taken from here: https://stackoverflow.com/questions/40123319/easy-way-to-encrypt-decrypt-string-in-android
	public static SecretKey generateKey(String password)
	{
		SecretKeySpec secret;
		return secret = new SecretKeySpec(password.getBytes(), "AES");
	}

	public static byte[] encryptMsg(String message, SecretKey secret)
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
