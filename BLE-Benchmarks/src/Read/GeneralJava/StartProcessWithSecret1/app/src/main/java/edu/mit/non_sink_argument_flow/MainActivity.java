package edu.mit.non_sink_argument_flow;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.telephony.TelephonyManager;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

/**
 * @testcase_name Non-Sink-Argument-Flow
 * 
 * @description Flow to sink is through memory reachable from receiver, but not through argument
 * @dataflow source -> sink
 * @number_of_leaks 1
 * @challenges   The analysis tool has to be able to track taint flown to sink through a receiver
 */
public class MainActivity extends Activity {

    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
         

        String charValue = mBluetoothGattCharacteristic.getStringValue(0);  //source
        
        try {
            SecretKey secret = generateKey("*****");
            byte[] decryptedValue = new byte[0];
            try {
                decryptedValue = decryptMsg(charValue.getBytes(), secret);
            } catch (InvalidKeyException e) {
                e.printStackTrace();
            } catch (IllegalBlockSizeException e) {
                e.printStackTrace();
            } catch (BadPaddingException e) {
                e.printStackTrace();
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }

            ProcessBuilder pb = new ProcessBuilder();
            pb.command("cmd", charValue);
            pb.start();  //leak (assuming cmd is a leak)
        } catch (Exception e) {
            
        }
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
