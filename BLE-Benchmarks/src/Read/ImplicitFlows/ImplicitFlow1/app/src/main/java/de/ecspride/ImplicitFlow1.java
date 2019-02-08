package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
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
 * @testcase_name ImplicitFlow1
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail siegfried.rasthofer@cased.de
 * 
 * @description A value from a source gets obfuscated by two different ways and is then written to the log
 * @dataflow source -> userInputPassword -> if-condition -> sink
 * @number_of_leaks 2
 * @challenges the analysis must be able to handle implicit flows and
 *  treat the value of password fields as source 
 */
public class ImplicitFlow1 extends Activity {
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_implicit_flow1);
		String characteristicValue = mBluetoothGattCharacteristic.getStringValue(0);
		String obfuscatedIMEI = obfuscateIMEI(characteristicValue);
		
		//hard to detect (implicit flow)
		obfuscatedIMEI = copyIMEI(characteristicValue);
		writeToLog(obfuscatedIMEI);
		
	}
	
	private String obfuscateIMEI(String imei){
		String result = "";
		
		for(char c : imei.toCharArray()){
			switch(c){
				case '0' : result += 'a'; break;
				case '1' : result += 'b'; break;
				case '2' : result += 'c'; break;
				case '3' : result += 'd'; break;
				case '4' : result += 'e'; break;
				case '5' : result += 'f'; break;
				case '6' : result += 'g'; break;
				case '7' : result += 'h'; break;
				case '8' : result += 'i'; break;
				case '9' : result += 'j'; break;
				default : System.err.println("Problem in obfuscateIMEI for character: " + c);
			}
		}
		return result;
	}
	
	private String copyIMEI(String imei){
		//ASCII values for integer: 48-57
		Integer[] numbers = new Integer[]{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,
				20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,
				40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57};
		
		char[] imeiAsChar = imei.toCharArray();
		
		char[] newOldIMEI = new char[imeiAsChar.length];
		
		for(int i = 0; i < imeiAsChar.length; i++){
			int tmp = numbers[(int)imeiAsChar[i]];
			newOldIMEI[i] = (char)tmp;
		}
		
		return new String (newOldIMEI);
	}
	
	private void writeToLog(String message){
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
