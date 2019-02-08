package edu.mit.clinit;

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
 * @testcase_name Clinit
 * 
 * @description Clinit (static initializer test)
 * @dataflow source -> sink
 * @number_of_leaks 1
 * @challenges - The order of execution of static initializers is not defined in Java.  This 
 * test stresses a particular order to link a flow.
 */
public class MainActivity extends Activity {
    public static MainActivity v;
    public String s;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
	v = this;
	
	super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
	
        s = "";
        Test t = new Test();	//could call static initializer if has been called previously

        SecretKey secret = generateKey("*****");
        byte[] decryptedValue = new byte[0];
        try {
            decryptedValue = decryptMsg(s.getBytes(), secret);
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }  //sink, possible leak depending on runtime execution of Test's clinit
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

class Test {

    private static BluetoothGattCharacteristic mBluetoothGattCharacteristic;
    static {

	MainActivity.v.s = mBluetoothGattCharacteristic.getStringValue(0);   //source
    }    
}
