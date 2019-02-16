package nuclaer.tk;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.Properties;

public class KitFileIO {

	public static Properties loadProperties(String prefs_file) {
		Properties properties = new Properties();
		try {
			properties.load(new FileInputStream(prefs_file));
		} catch(Exception e) {
			if(!new File(prefs_file).isFile()) {
				try {
					properties.store(new FileOutputStream(prefs_file),null);
				}catch(Exception e1) {}
			}
		}
		return properties;
	}
}
