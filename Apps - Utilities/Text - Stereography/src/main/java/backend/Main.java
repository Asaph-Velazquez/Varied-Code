package backend;
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        MyFile contraseñaFile = new MyFile("Contraseña.txt", "src/main/resources/Contraseña.txt");
        MyFile floresFile = new MyFile("Flores.BMP", "src/main/resources/Flores.BMP");
        MyFile outputFile = new MyFile();

        try{
            String contraseñaContent = contraseñaFile.read().trim();
    
            // Convertir contraseña a binario
            StringBuilder contraseñaBinaryContent = new StringBuilder();
            for(char c : contraseñaContent.toCharArray()){
                contraseñaBinaryContent.append(charToBinary.convert((byte) c)).append(" ");
            }
            
            byte[] floresContentBytes = floresFile.readBinary();

            System.out.println("Contraseña: " + contraseñaContent);
            for(char a : contraseñaBinaryContent.toString().toCharArray()){
                System.out.println(a + " ");
            }

            for(Byte b : floresContentBytes){
                System.out.print(b + " ");
            }

            //Header and pixels
            byte header[] = Arrays.copyOfRange(floresContentBytes, 0, 54);
            byte pixels[] = Arrays.copyOfRange(floresContentBytes, 54, floresContentBytes.length); 

            //Contraseña to binary
            String[] contraseñaBinaryArray = contraseñaBinaryContent.toString().split(" "); 
            String[] pixelsBinaryArray = charToBinary.convertByteArray(pixels);

            //Embedding the contraseña binary into the pixels binary
            int pixelIndex = 0;
            for(int i = 0; i < contraseñaBinaryArray.length; i++){
                String charBinary = contraseñaBinaryArray[i];
                if(charBinary.isEmpty()) continue; // Skip empty strings from split
                
                // Insertar cada bit del carácter en un pixel diferente
                for(int j = 0; j < charBinary.length(); j++){
                    if(pixelIndex >= pixelsBinaryArray.length) break;
                    int bit = Character.getNumericValue(charBinary.charAt(j));
                    charToBinary.replaceBitInBlock(bit, pixelsBinaryArray, pixelIndex);
                    pixelIndex++;
                }
            }

            //Reconstructuion of the modified pixels
            byte[] modifiedPixel = charToBinary.binaryArrayToBytes(pixelsBinaryArray);
            byte[] cipheredContent =  new byte[header.length + modifiedPixel.length];
            System.arraycopy(header, 0, cipheredContent, 0, header.length);
            System.arraycopy(modifiedPixel, 0, cipheredContent, header.length, modifiedPixel.length);

            //Creation of the Cifrado File
            outputFile.CreateFile("Cifrado.BMP", "src/main/chiphered", cipheredContent);

            //Reading the Cifrado file to verify the content
            MyFile cifradoFile = new MyFile("Cifrado.BMP", "src/main/chiphered/Cifrado.BMP");
            byte[] cifradoContentBytes = cifradoFile.readBinary();
            System.out.println("\nContenido del archivo Cifrado.BMP: " + Arrays.toString(cifradoContentBytes));

            //Decryption of the message from the Cifrado file
            String decryptedMessage = charToBinary.decrypt(cifradoContentBytes, contraseñaContent.length());
            System.out.println("\nMensaje descifrado: " + decryptedMessage);
        }catch(Exception e){
            e.printStackTrace();
        }
    }
}