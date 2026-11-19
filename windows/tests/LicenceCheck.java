// The phone's side of the unlock-code scheme, lifted from the Android app's Licence.kt, so the claim
// that one code works on both can be checked rather than asserted. test_licence.py runs this when a JDK
// is present and skips it when there is not one; it is not part of the shipped app.
//
// Usage: java LicenceCheck <folder> <email>
//   reads   from_python.code  - a code made in Python, verified here with Java's own ECDSA
//   writes  from_java.code    - a code made here, for Python to verify
//   writes  public.key        - the throwaway public key both sides check against
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;
import java.util.Base64;
import java.util.Locale;

public class LicenceCheck {
    static final String PREFIX = "GJ1";
    static final String B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

    static String normalize(String email) { return email.trim().toLowerCase(Locale.ROOT); }
    static byte[] message(String email) { return (PREFIX + "|" + normalize(email)).getBytes(java.nio.charset.StandardCharsets.UTF_8); }

    static byte[] decode(String code) {
        String s = code.toUpperCase(Locale.ROOT).replaceAll("[^A-Z0-9]", "");
        if (s.startsWith(PREFIX)) s = s.substring(PREFIX.length());
        long buf = 0; int bits = 0;
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        for (char c : s.toCharArray()) {
            int i = B32.indexOf(c);
            if (i < 0) return null;
            buf = (buf << 5) | i; bits += 5;
            if (bits >= 8) { bits -= 8; out.write((int) ((buf >> bits) & 0xFF)); }
        }
        byte[] raw = out.toByteArray();
        return raw.length == 64 ? raw : null;
    }

    static String encode(byte[] sig) {
        StringBuilder sb = new StringBuilder(); long buf = 0; int bits = 0;
        for (byte b : sig) {
            buf = (buf << 8) | (b & 0xFF); bits += 8;
            while (bits >= 5) { bits -= 5; sb.append(B32.charAt((int) ((buf >> bits) & 31))); }
        }
        if (bits > 0) sb.append(B32.charAt((int) ((buf << (5 - bits)) & 31)));
        StringBuilder out = new StringBuilder(PREFIX + "-");
        for (int i = 0; i < sb.length(); i += 5) out.append(sb, i, Math.min(i + 5, sb.length())).append('-');
        return out.substring(0, out.length() - 1);
    }

    static byte[] toDer(byte[] raw) {
        byte[] r = asInt(java.util.Arrays.copyOfRange(raw, 0, 32));
        byte[] s = asInt(java.util.Arrays.copyOfRange(raw, 32, 64));
        byte[] body = new byte[r.length + s.length];
        System.arraycopy(r, 0, body, 0, r.length);
        System.arraycopy(s, 0, body, r.length, s.length);
        byte[] der = new byte[2 + body.length];
        der[0] = 0x30; der[1] = (byte) body.length;
        System.arraycopy(body, 0, der, 2, body.length);
        return der;
    }

    static byte[] asInt(byte[] b) {
        int i = 0;
        while (i < b.length - 1 && b[i] == 0) i++;
        byte[] v = java.util.Arrays.copyOfRange(b, i, b.length);
        if ((v[0] & 0x80) != 0) { byte[] p = new byte[v.length + 1]; System.arraycopy(v, 0, p, 1, v.length); v = p; }
        byte[] out = new byte[2 + v.length];
        out[0] = 0x02; out[1] = (byte) v.length;
        System.arraycopy(v, 0, out, 2, v.length);
        return out;
    }

    static byte[] rawFromDer(byte[] der) throws Exception {
        // minimal DER reader for SEQUENCE { INTEGER r, INTEGER s }
        int i = 2;
        byte[] raw = new byte[64];
        for (int half = 0; half < 2; half++) {
            int len = der[i + 1];
            int from = i + 2, skip = 0;
            while (skip < len - 1 && der[from + skip] == 0) skip++;
            int size = len - skip;
            System.arraycopy(der, from + skip, raw, half * 32 + (32 - size), size);
            i += 2 + len;
        }
        return raw;
    }

    static boolean verify(String email, String code, PublicKey key) throws Exception {
        byte[] raw = decode(code);
        if (raw == null) return false;
        Signature sig = Signature.getInstance("SHA256withECDSA");
        sig.initVerify(key);
        sig.update(message(email));
        return sig.verify(toDer(raw));
    }

    public static void main(String[] a) throws Exception {
        Path dir = Paths.get(a[0]);
        String email = a[1];

        byte[] pub = Base64.getDecoder().decode(Files.readString(dir.resolve("public.key")).trim());
        PublicKey key = KeyFactory.getInstance("EC").generatePublic(new X509EncodedKeySpec(pub));

        String fromPython = Files.readString(dir.resolve("from_python.code")).trim();
        System.out.println("PHONE ACCEPTS THE DESKTOP CODE: " + verify(email, fromPython, key));
        System.out.println("PHONE REJECTS IT FOR ANOTHER EMAIL: " + !verify("someone.else@example.test", fromPython, key));

        byte[] priv = Base64.getDecoder().decode(Files.readString(dir.resolve("private.key")).trim());
        PrivateKey signing = KeyFactory.getInstance("EC").generatePrivate(new PKCS8EncodedKeySpec(priv));
        Signature sig = Signature.getInstance("SHA256withECDSA");
        sig.initSign(signing);
        sig.update(message(email));
        Files.writeString(dir.resolve("from_java.code"), encode(rawFromDer(sig.sign())));
        System.out.println("WROTE from_java.code");
    }
}
