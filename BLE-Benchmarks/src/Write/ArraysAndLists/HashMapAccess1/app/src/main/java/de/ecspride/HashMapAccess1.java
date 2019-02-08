package de.ecspride;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidParameterSpecException;
import java.util.HashMap;
import java.util.Map;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

/**
 * @testcase_name HashMapAccess1
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail steven.arzt@cased.de
 * 
 * @description A hash map is filled with both tainted and untainted data. The untainted
 * 	data is then read out and sent via SMS.
 * @dataflow -
 * @number_of_leaks 0
 * @challenges the analysis must distinguish between different hash map entries to recognize that the tainted
 *  data does not get leaked. 
 */
public class HashMapAccess1 extends Activity {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_hash_map_access1);

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

		Map<String, byte[]> hashMap = new HashMap<String, byte[]>();
		hashMap.put("tainted", bytesToWrite); //source
		hashMap.put("untainted", new byte[0]);

		mBluetoothGattCharacteristic.setValue(hashMap.get("untainted")); //sink, no leak
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
