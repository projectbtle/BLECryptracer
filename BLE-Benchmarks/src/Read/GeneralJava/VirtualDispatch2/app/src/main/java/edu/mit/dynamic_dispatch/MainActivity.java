package edu.mit.dynamic_dispatch;

import android.app.Activity;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Bundle;
import android.telephony.SmsManager;
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
 * @testcase_name Dynamic-Dispatch
 * 
 * @description Testing dispatching of overiding methods
 * @dataflow source -> sink
 * @number_of_leaks 1
 * @challenges The analysis tool has to be able to differentiate the base and the derived class objects
 */
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

      
        Test test1 = new Test();
        Test test2 = new Test();
        A b = new B();
        A c = new C();

        SmsManager smsmanager = SmsManager.getDefault();

         //sink, leak
        SecretKey secret = generateKey("*****");
        byte[] decryptedValue = new byte[0];
        try {
            decryptedValue = decryptMsg( test1.method(b).getBytes(), secret);
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }

        //sink, no leak
        secret = generateKey("*****");
        decryptedValue = new byte[0];
        try {
            decryptedValue = decryptMsg(test2.method(c).getBytes(), secret);
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

class Test {
    public String method(A a) {        
        return a.f();  // uses the context insensitive pta for call targets
    }
}

class A {
    public String f() {
        return "untainted";
    }
}

class B extends A {
    private static BluetoothGattCharacteristic mBluetoothGattCharacteristic;
    public String f() {
        return mBluetoothGattCharacteristic.getStringValue(0);  //source
    }
}

class C extends A {
    public String f() {
        return "not tainted";
    }
}
