package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

/**
 * @testcase_name FieldSensitivity1
 * @version 0.2
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail siegfried.rasthofer@cased.de
 * 
 * @description An object has two fields, one of them gets a tainted value, the other one is sent to a sink.
 * @dataflow -
 * @number_of_leaks 0
 * @challenges the analysis must be able to distinguish between different fields of an object.
 */
public class FieldSensitivity1 extends Activity {
	private Datacontainer d1;
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_field_sensitivity1);
        
        d1 = setTaint(d1);
		sendTaint();
    }

	private Datacontainer setTaint(Datacontainer data){
		data = new Datacontainer();
		data.setDescription(new byte[0]);
        byte[] characteristicValue = mBluetoothGattCharacteristic.getValue();
		data.setSecret(characteristicValue); //source
		return data;
	}
	
	private void sendTaint(){
        SecretKey secret = generateKey("*****");
        byte[] decryptedValue = new byte[0];
        try {
            decryptedValue = decryptMsg(d1.getDescription(), secret);
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
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
