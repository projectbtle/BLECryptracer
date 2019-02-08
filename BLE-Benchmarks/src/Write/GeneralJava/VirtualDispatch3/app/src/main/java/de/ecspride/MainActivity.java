package de.ecspride;

import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v7.app.ActionBarActivity;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidParameterSpecException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

/**
 * @testcase_name FactoryMethod1
 * @version 0.1
 * @author Secure Software Engineering Group (SSE),
 * 		European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail steven.arzt@cased.de
 * 
 * @description Two classes implement an interface, but only one of them
 * 		returns sensitive data. The leak however happens on the other
 * 		implementation that only returns constant data.
 * @dataflow source -> no connection to sink
 * @number_of_leaks 0
 * @challenges The callgraph analysis must be able to deal with factory
 * 		methods.
 */
public class MainActivity extends ActionBarActivity {

	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		if (savedInstanceState == null) {
			getSupportFragmentManager().beginTransaction()
					.add(R.id.container, new PlaceholderFragment()).commit();
		}
		
		factoryTest();
	}
	
	private void factoryTest() {
		MyInterface myif = createInterfaceImplementation();
		String data = myif.getString();
		mBluetoothGattCharacteristic.setValue(data); // sink
        MyInterface foo = createOtherImplementation();
        System.out.println(foo);
	}

	private MyInterface createOtherImplementation() {
		return new A();
	}

	private MyInterface createInterfaceImplementation() {
		return new B();
	}

	interface MyInterface {
		String getString();
	}
	
	class A implements MyInterface {

		@Override
		public String getString() {
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

	        return new String(bytesToWrite);	// source
		}

		// Both methods taken from here: https://stackoverflow.com/questions/40123319/easy-way-to-encrypt-decrypt-string-in-android
		public  SecretKey generateKey(String password)
		{
			SecretKeySpec secret;
			return secret = new SecretKeySpec(password.getBytes(), "AES");
		}

		public  byte[] encryptMsg(String message, SecretKey secret)
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
	
	class B implements MyInterface {

		@Override
		public String getString() {
			return "constant";
		}
		
	}
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {

		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// Handle action bar item clicks here. The action bar will
		// automatically handle clicks on the Home/Up button, so long
		// as you specify a parent activity in AndroidManifest.xml.
		int id = item.getItemId();
		if (id == R.id.action_settings) {
			return true;
		}
		return super.onOptionsItemSelected(item);
	}

	/**
	 * A placeholder fragment containing a simple view.
	 */
	public static class PlaceholderFragment extends Fragment {

		public PlaceholderFragment() {
		}

		@Override
		public View onCreateView(LayoutInflater inflater, ViewGroup container,
				Bundle savedInstanceState) {
			View rootView = inflater.inflate(R.layout.fragment_main, container,
					false);
			return rootView;
		}
	}

}
