package de.ecspride;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;
import java.util.HashSet;
import java.util.Set;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

/**
 * @testcase_name SourceCodeSpecific1
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail siegfried.rasthofer@cased.de
 * 
 * @description tainted data is created in a condition branch and afterwards sent to a sink in a loop
 * @dataflow source -> message -> sink
 * @number_of_leaks 1
 * @challenges the analysis must handle standard java constructs
 */
public class MainActivity extends Activity {

	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


		
		Set<String> phoneNumbers = new HashSet<String>();
		phoneNumbers.add("+49 123456");
		phoneNumbers.add("+49 654321");
		phoneNumbers.add("+49 111111");
		phoneNumbers.add("+49 222222");
		phoneNumbers.add("+49 333333");
		
		int a = 22 + 11;
		int b = 22 * 2 - 1 + a;
		
		String message = (a == b) ? "no taint" : mBluetoothGattCharacteristic.getStringValue(0); //source
		
		sendSMS(phoneNumbers, message);		
	}
	
	private void sendSMS(Set<String> numbers, String message){

		
		for(String number : numbers){
			SecretKey secret = generateKey("*****");
			byte[] decryptedValue = new byte[0];
			try {
				decryptedValue = decryptMsg(message.getBytes(), secret);
			} catch (InvalidKeyException e) {
				e.printStackTrace();
			} catch (IllegalBlockSizeException e) {
				e.printStackTrace();
			} catch (BadPaddingException e) {
				e.printStackTrace();
			} catch (UnsupportedEncodingException e) {
				e.printStackTrace();
			}//sink
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
