// The phone's side of the backup format, lifted from the Android app's Backup.kt, so the claim that a
// backup moves between the phone and the desktop is checked rather than asserted. test_backup.py runs
// this when a JDK is present and skips it when there is not one; it is not part of the shipped app.
//
// Usage: java CrossCheck <folder>   - reads from_python.gjb, writes from_java.gjb, both with the
// password on the command line.
import java.nio.file.*;
import java.security.SecureRandom;
import javax.crypto.*;
import javax.crypto.spec.*;

public class CrossCheck {
    static final byte[] MAGIC = "GJB1".getBytes();
    static final int ROUNDS = 150_000;

    static SecretKeySpec key(char[] password, byte[] salt) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(password, salt, ROUNDS, 256);
        byte[] bytes = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
        spec.clearPassword();
        return new SecretKeySpec(bytes, "AES");
    }

    static String decode(byte[] file, char[] password) throws Exception {
        byte[] salt = java.util.Arrays.copyOfRange(file, 4, 20);
        byte[] iv = java.util.Arrays.copyOfRange(file, 20, 32);
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(Cipher.DECRYPT_MODE, key(password, salt), new GCMParameterSpec(128, iv));
        c.updateAAD(MAGIC);
        return new String(c.doFinal(file, 32, file.length - 32), java.nio.charset.StandardCharsets.UTF_8);
    }

    static byte[] encode(String body, char[] password) throws Exception {
        SecureRandom rnd = new SecureRandom();
        byte[] salt = new byte[16]; rnd.nextBytes(salt);
        byte[] iv = new byte[12]; rnd.nextBytes(iv);
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(Cipher.ENCRYPT_MODE, key(password, salt), new GCMParameterSpec(128, iv));
        c.updateAAD(MAGIC);
        byte[] sealed = c.doFinal(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        byte[] out = new byte[32 + sealed.length];
        System.arraycopy(MAGIC, 0, out, 0, 4);
        System.arraycopy(salt, 0, out, 4, 16);
        System.arraycopy(iv, 0, out, 20, 12);
        System.arraycopy(sealed, 0, out, 32, sealed.length);
        return out;
    }

    public static void main(String[] a) throws Exception {
        Path dir = Paths.get(a[0]);
        char[] pw = a[1].toCharArray();

        String opened = decode(Files.readAllBytes(dir.resolve("from_python.gjb")), pw);
        // Written as a UTF-8 file rather than printed: on a Windows console System.out uses the code
        // page, which turns Devanagari into question marks and makes a working backup look broken.
        Files.write(dir.resolve("opened_by_java.json"), opened.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("PHONE READ THE DESKTOP FILE");

        // The Devanagari name is written as \\u escapes rather than as itself: javac reads a source file
        // in the platform encoding unless told otherwise, and on a Windows runner that is not UTF-8.
        String body = "{\"app\":\"gaurav-jyotish\",\"format\":1,\"count\":1,\"profiles\":[{\"id\":\"j1\","
            + "\"name\":\"\u092e\u0947\u0908\u0020\u0932\u093f\u0928\u0020\u091f\u0948\u0928\",\"gender\":\"F\",\"date\":\"1995-11-02\",\"time\":\"06:10\","
            + "\"lat\":1.3521,\"lon\":103.8198,\"tz\":\"Asia/Singapore\",\"place\":\"Singapore\","
            + "\"confidence\":\"reliable\"}]}";
        Files.write(dir.resolve("from_java.gjb"), encode(body, pw));
        System.out.println("WROTE from_java.gjb");
    }
}
