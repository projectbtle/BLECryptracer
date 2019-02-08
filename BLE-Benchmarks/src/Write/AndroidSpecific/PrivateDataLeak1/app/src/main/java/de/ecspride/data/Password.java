package de.ecspride.data;

public class Password {
	private byte[] password;
	
	public Password(byte[] password){
		this.password = password;
	}

	public byte[] getPassword() {
		return password;
	}

	public void setPassword(byte[] password) {
		this.password = password;
	}
}
