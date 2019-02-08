package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;
import android.view.View;
import android.widget.Toast;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

/**
 * @testcase_name Button4
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail steven.arzut@cased.de
 * 
 * @description The sink is called after the user clicks a button. The button
 *  handler is defined via XML using an include directive.
 * @dataflow OnCreate: source -> imei; sendMessage: imei -> sink
 * @number_of_leaks 1
 * @challenges the analysis must analyze the layout xml file and correctly handle include directives
 */
public class Button4 extends Activity {

    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
    byte[] characteristicValue;
	
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_button1);

        characteristicValue = mBluetoothGattCharacteristic.getValue();//source
    }

    public void sendMessage(View view){
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
