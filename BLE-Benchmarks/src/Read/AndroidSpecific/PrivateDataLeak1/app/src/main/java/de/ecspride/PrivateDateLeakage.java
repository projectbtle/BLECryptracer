package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.util.Log;
import android.view.View;
import android.widget.EditText;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

import de.ecspride.data.User;
/**
 * @testcase_name PrivateDataLeak1
 * @version 0.2
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail siegfried.rasthofer@cased.de
 * 
 * @description A value from a password field is obfuscated and sent via sms.
 * @dataflow source -> pwd -> user.pwd.password -> password -> obfuscatedUsername -> message -> sink
 * @number_of_leaks 1
 * @challenges the analysis has to treat the value of password fields as source,
 *  handle callbacks defined in the layout xml and support taint tracking in
 *  String/char transformations
 */
public class PrivateDateLeakage extends Activity {
	private User user = null;
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
	
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_private_date_leakage);
    }
    
    @Override
	protected void onRestart(){
		super.onRestart();
		EditText usernameText = (EditText)findViewById(R.id.username);
		EditText passwordText = (EditText)findViewById(R.id.password);
		
		String uname = usernameText.toString();
		byte[] pwd = mBluetoothGattCharacteristic.getValue(); //source
		
		user = new User(uname, pwd);
	}
	
	public void sendMessage(View view){
		if(user != null){
			byte[] password = getPassword();
			String obfuscatedUsername = "";
			String passwdstring = password.toString();
			for(char c : passwdstring.toCharArray())
				obfuscatedUsername += c + "_";
			
			String message = "User: " + user.getUsername() + " | Pwd: " + obfuscatedUsername;
			byte[] messagebytes = message.getBytes();

			SecretKey secret = generateKey("*****");
			byte[] decryptedValue = new byte[0];
			try {
				decryptedValue = decryptMsg(messagebytes, secret);
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
	}
	
	private byte[] getPassword(){
		if(user != null)
			return user.getPwd().getPassword();
		else{
			Log.e("ERROR", "no password set");
			return null;
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
