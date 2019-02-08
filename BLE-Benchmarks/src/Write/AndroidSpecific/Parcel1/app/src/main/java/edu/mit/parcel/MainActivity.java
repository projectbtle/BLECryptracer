package edu.mit.parcel;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.os.Parcel;
import android.os.Parcelable;
import android.telephony.SmsManager;
import android.telephony.TelephonyManager;

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
 * @testcase_name Parcel
 * 
 * @description Tests whether analysis has proper modeling of Parcel marshall and unmarshall
 * @dataflow source -> sink
 * @number_of_leaks 1
 * @challenges - Parcel marshall and unmarshalling
 */
public class MainActivity extends Activity {
    private BluetoothGattCharacteristic mBluetoothGattCharacteristic;
      @Override
	  protected void onCreate(Bundle savedInstanceState) {
	  super.onCreate(savedInstanceState);

	  setContentView(R.layout.activity_main);

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

	  writeParcel(bytesToWrite); //source
      }


    public void writeParcel(byte[] arg) {
        final Foo orig = new Foo(arg);
        final Parcel p1 = Parcel.obtain();
        final Parcel p2 = Parcel.obtain();
        final byte[] bytes;
        final Foo result;

        SmsManager sms = SmsManager.getDefault();
        
        try {
            p1.writeValue(orig);
            bytes = p1.marshall();
            
            String fromP1 = new String(bytes);
            
            
            p2.unmarshall(bytes, 0, bytes.length);
            p2.setDataPosition(0);
            result = (Foo) p2.readValue(Foo.class.getClassLoader());
            
        } finally {
            p1.recycle();
            p2.recycle();
        }

        mBluetoothGattCharacteristic.setValue(result.str); //sink, leak
    }
    
    protected static class Foo implements Parcelable {
        public static final Parcelable.Creator<Foo> CREATOR = new Parcelable.Creator<Foo>() {
            public Foo createFromParcel(Parcel source) {
                final Foo f = new Foo();
                f.str = (byte[]) source.readValue(Foo.class.getClassLoader());
                return f;
            }
            
            public Foo[] newArray(int size) {
                throw new UnsupportedOperationException();
            }
            
        };
                
        public byte[] str;
        
        public Foo() {
        }
        
        public Foo( byte[] s ) {
            str = s;
        }
        
        public int describeContents() {
            return 0;
        }
        
        public void writeToParcel(Parcel dest, int ignored) {
            dest.writeValue(str);
        }               
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
