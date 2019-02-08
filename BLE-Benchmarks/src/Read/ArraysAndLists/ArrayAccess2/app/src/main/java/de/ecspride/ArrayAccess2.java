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
 * @testcase_name ArrayAccess2
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail siegfried.rasthofer@cased.de
 * 
 * @description an array is created which is filled with untainted and tainted (deviceId source) data.
 *   The untainted data of a calculated array position is retrieved and sent via sms.
 * @dataflow -
 * @number_of_leaks 0
 * @challenges the analysis must distinguish between different array positions and has to evaluate the function to recognize that the tainted
 *  data does not get leaked. 
 */
public class ArrayAccess2 extends Activity {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_array_access2);
        
        byte[][] array = new byte[10][];
		byte[] characteristicValue = mBluetoothGattCharacteristic.getValue(); //source
		array[5] = characteristicValue;
		array[4] = new byte[0];

		SecretKey secret = generateKey("*****");
		byte[] decryptedValue = new byte[0];
		try {
			decryptedValue = decryptMsg(array[calculateIndex()], secret);
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
	
	private int calculateIndex(){
		int index = 1;
		index++;
		index *= 5;
		index = index%10;
		index += 4;
		
		return index;
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
