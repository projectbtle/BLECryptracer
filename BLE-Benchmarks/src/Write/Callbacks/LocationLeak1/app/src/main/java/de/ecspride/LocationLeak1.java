package de.ecspride;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;

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
 * @testcase_name LocationLeak1
 * @version 0.1
 * @author Secure Software Engineering Group (SSE), European Center for Security and Privacy by Design (EC SPRIDE) 
 * @author_mail siegfried.rasthofer@cased.de
 * 
 * @description This example contains a location information leakage in the onResume() callback method.
 *  The data source is placed into the onLocationChanged() callback method, especially the parameter "loc".
 * @dataflow onLocationChanged: source -> latitude, longtitude; onResume: latitude -> sink, longtitude -> sink 
 * @number_of_leaks 2
 * @challenges the analysis must be able to emulate the Android activity lifecycle correctly,
 *  integrate the callback method onLocationChanged and detect the callback methods as source.
 */
public class LocationLeak1 extends Activity {
	private byte[] bytesToWrite = new byte[0];
	private BluetoothGattCharacteristic mBluetoothGattCharacteristic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_location_leak1);
        
        LocationManager locationManager = (LocationManager) 
        getSystemService(Context.LOCATION_SERVICE);
        
        LocationListener locationListener = new MyLocationListener();  
        locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000, 10, locationListener);            
    }

    @Override
    protected void onResume (){
    	super.onResume();

		mBluetoothGattCharacteristic.setValue(bytesToWrite); // sink
    }
    
    private class MyLocationListener implements LocationListener {  
		  @Override  
		  public void onLocationChanged(Location loc) {  //source
			  String charValue = "This is a test....";
			  String toWrite = charValue.toString();
			  SecretKey secret = generateKey("*****");

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
		  }  

		  @Override  
		  public void onProviderDisabled(String provider) {}  

		  @Override  
		  public void onProviderEnabled(String provider) { }  

		  @Override  
		  public void onStatusChanged(String provider, int status, Bundle extras) {}

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
}
