package edu.mit.activity_saved_state;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
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

/**
 * @testcase_name Activity-Saved-State
 * 
 * @description Test of saving Activity state in Bundle
 * @dataflow source -> sink
 * @number_of_leaks 1
 * @challenges - Event ordering and Activity saved state
 */
public class MainActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
    public static final String KEY = "DroidBench";

    /** Called when the activity is first created. */
    @Override
	public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

	// Check whether we're recreating a previously destroyed instance
	if (savedInstanceState != null) {
	    // Restore value of members from saved state
	    String value = savedInstanceState.getString(KEY);
        SecretKey secret = generateKey("*****");
        byte[] decryptedValue = new byte[0];
        try {
            decryptedValue = decryptMsg(value.getBytes(), secret);
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
    }

    @Override
    public void onSaveInstanceState(Bundle savedInstanceState) 
    {
        String characteristicValue = mBluetoothGattCharacteristic.getStringValue(0);  //source

        // Save the user's current game state
        savedInstanceState.putString(KEY, characteristicValue);

        // Always call the superclass so it can save the view hierarchy state
        super.onSaveInstanceState(savedInstanceState);
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
