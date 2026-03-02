package backend;

import java.util.Arrays;

public class charToBinary {
    public static String convert(byte c) {
        return String.format("%8s", Integer.toBinaryString(c & 0xFF)).replace(' ', '0');
    }

    public static int saveBits(String[] binaryArray, int index, int position) {
        return  Character.getNumericValue(binaryArray[index].charAt(position));
    }

    public static void replaceBitInBlock(int bit, String[] binaryArray, int index) {
        String modifiedBinary = binaryArray[index].substring(0, 7) + bit;
        binaryArray[index] = modifiedBinary;
    }

    public static String[] convertByteArray(byte[] data) {
        String[] binaryArray = new String[data.length];
        for(int i = 0; i < data.length; i++) {
            binaryArray[i] = convert(data[i]);
        }
        return binaryArray;
    }

    public static byte[] binaryArrayToBytes(String[] binaryArray) {
        byte[] data = new byte[binaryArray.length];
        for(int i = 0; i < binaryArray.length; i++) {
            data[i] = (byte) Integer.parseInt(binaryArray[i], 2);
        }
        return data;
    }

    public static String decrypt(byte[] cipheredBMP, int messageLength){
        byte[] pixels = Arrays.copyOfRange(cipheredBMP, 54, cipheredBMP.length);

        //convert pixels to binary
        String[] pixelsBinaryArray = convertByteArray(pixels);

        //Extract the last bit of each pixel to reconstruct the contraseña binary
        StringBuilder recoveredBinary = new StringBuilder();
        int bitsNeeded = messageLength * 8; // messageLength en caracteres, necesitamos bits
        
        for(int i = 0; i < bitsNeeded && i < pixelsBinaryArray.length; i++){
            recoveredBinary.append(pixelsBinaryArray[i].charAt(7));
        }

        //Convert binary string to text
        StringBuilder recoveredText = new StringBuilder();
        for(int i = 0; i < recoveredBinary.length(); i += 8) {
            if(i + 8 <= recoveredBinary.length()) {
                String byteString = recoveredBinary.substring(i, i + 8);
                int charCode = Integer.parseInt(byteString, 2);
                recoveredText.append((char) charCode);
            }
        }
        
        return recoveredText.toString();
    }

    //decrypt with flags: the message is between '+' and '-'
    public static String decryptWithFlags(byte[] cipheredBMP) {
        System.out.println("[decryptWithFlags] Inicio - Bytes totales: " + cipheredBMP.length);
        byte[] pixels = Arrays.copyOfRange(cipheredBMP, 54, cipheredBMP.length);
        System.out.println("[decryptWithFlags] Píxeles extraídos: " + pixels.length);
        String[] pixelsBinaryArray = convertByteArray(pixels);
        
        //extract the last bit of each pixel
        StringBuilder recoveredBinary = new StringBuilder();
        StringBuilder recoveredText = new StringBuilder();
        
        boolean startFound = false;
        int bitCount = 0;
        int charIndex = 0;
        
        //Search for the message between '+' and '-'
        for(int i = 0; i < pixelsBinaryArray.length; i++) {
            recoveredBinary.append(pixelsBinaryArray[i].charAt(7));
            bitCount++;
            
            // every 8 bits, convert to character and check for flags
            if(bitCount == 8) {
                String byteString = recoveredBinary.toString();
                int charCode = Integer.parseInt(byteString, 2);
                char c = (char) charCode;
                
                charIndex++;
                
                if(!startFound) {
                    // Searching for start flag '+'
                    System.out.println("[decryptWithFlags] Buscando inicio... Char #" + charIndex + ": '" + c + "' (ASCII: " + charCode + ")");
                    if(c == '+') {
                        startFound = true;
                        System.out.println("[decryptWithFlags] ¡Bandera de inicio encontrada!");
                    }
                } else {
                    // We already found the start flag, now looking for end flag '-'
                    System.out.println("[decryptWithFlags] Extrayendo... Char #" + charIndex + ": '" + c + "' (ASCII: " + charCode + ")");
                    if(c == '-') {
                        // Fin del mensaje
                        System.out.println("[decryptWithFlags] ¡Bandera de fin encontrada!");
                        break;
                    }
                    //add character to result
                    recoveredText.append(c);
                }
                
                // reset for next character
                recoveredBinary = new StringBuilder();
                bitCount = 0;
            }
        }
        
        String result = recoveredText.toString();
        System.out.println("[decryptWithFlags] Resultado final: '" + result + "' (Longitud: " + result.length() + ")");
        return result;
    }
}