package backend;
import java.io.*;

public class MyFile {
    public String name;
    public String path;

    // Constructor
    public MyFile(String name, String path) {
        this.name = name;
        this.path = path;
    }

    //void constructor
    public MyFile() {
        this.name = "";
        this.name = "";    
    }

    //method to read the content of a file and return it as a string
    public String read() throws IOException{
        StringBuilder content = new StringBuilder();
        try(BufferedReader br = new BufferedReader(new java.io.FileReader(path))){
        String line;
        while((line = br.readLine()) != null){
            content.append(line).append("\n");            
        }
    }
        return content.toString();
    }

    //method to read the content of a file and return it as a byte array
    public byte[] readBinary() throws IOException{
          try(FileInputStream fis = new FileInputStream(path)){
            return fis.readAllBytes();
        }
    }

    public void write(String content){
        try(BufferedWriter bw = new BufferedWriter(new java.io.FileWriter(path))){
            bw.write(content);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void writeBinary(byte[] contenBytes) throws IOException{
        try{
            FileOutputStream fos = new FileOutputStream(path);
            for(Byte b : contenBytes){
                fos.write(b);
            }
            fos.close();
        }catch(Exception e){
            e.printStackTrace();
        }
    }   

    public String CharToBinary() throws IOException{
        String content = read();
        StringBuilder binaryContent = new StringBuilder();
        for(char c : content.toCharArray()){
            binaryContent.append(charToBinary.convert((byte) c)).append(" ");
        }
        return binaryContent.toString();
    }

    //method to create a file with binary content for the future creation of the descifrado file
    public void CreateFile(String name, String Path, String content) throws IOException{
        this.name = name;
        this.path = Path + "/" + name;
        File file = new File(this.path);
        if(file.createNewFile()){
            System.out.println("Archivo creado: " + file.getName());
        } else {
            System.out.println("El archivo ya existe.");
        }
        write(content);
    }

    //method overloading for CreateFile for binary content in the BMP file
    public void CreateFile(String name, String Path, byte[] content) throws IOException{
        this.name = name;
        this.path = Path + "/" + name;
        File file = new File(this.path);
        if(file.createNewFile()){
            System.out.println("\nArchivo creado: " + file.getName());
        } else {
            System.out.println("\nEl archivo ya existe.");
        }
        writeBinary(content);
    }
}
