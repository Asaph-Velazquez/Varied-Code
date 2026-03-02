package backend;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.concurrent.Worker;
import javafx.scene.Scene;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import javafx.stage.Stage;
import netscape.javascript.JSObject;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Arrays;

public class App extends Application {

    private WebEngine webEngine;
    private Stage primaryStage;

    @Override
    public void start(Stage stage) {
        this.primaryStage = stage;
        WebView webView = new WebView();
        webEngine = webView.getEngine();
        webEngine.setJavaScriptEnabled(true);

        InputStream htmlStream = getClass().getResourceAsStream("/static/index.html");
        if (htmlStream == null) htmlStream = getClass().getResourceAsStream("/interface.html");
        if (htmlStream != null) {
            try {
                webEngine.loadContent(new String(htmlStream.readAllBytes()));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        webEngine.getLoadWorker().stateProperty().addListener((obs, oldState, newState) -> {
            if (newState == Worker.State.SUCCEEDED)
                ((JSObject) webEngine.executeScript("window")).setMember("javaConnector", new JavaConnector());
        });

        stage.setTitle("Introduction to Cryptography");
        stage.setScene(new Scene(webView, 1500, 800));
        stage.show();
    }

    public class JavaConnector {

        public void loadTextFile(String base64Content, String fileName) {
            try {
                String content = new String(java.util.Base64.getDecoder().decode(base64Content), "UTF-8");
                runScript("document.getElementById('secretMessage').value = '" + escape(content) + "';");
            } catch (Exception e) {
                showAlert("Error al cargar archivo: " + e.getMessage());
            }
        }

        public void encrypt(String message, String base64BmpData, String bmpFileName) {
            try {
                if (base64BmpData == null || base64BmpData.isEmpty()) { showAlert("No se proporcionó datos del archivo BMP"); return; }
                if (message == null || message.trim().isEmpty()) { showAlert("El mensaje no puede estar vacío"); return; }

                message = message.trim();
                String messageWithFlags = "+" + message + "-";

                byte[] bmpBytes = java.util.Base64.getDecoder().decode(base64BmpData);
                int availablePixels = bmpBytes.length - 54;

                if (messageWithFlags.length() * 8 > availablePixels) {
                    showAlert("Error: El mensaje es muy largo para esta imagen.\n" +
                              "Capacidad: " + (availablePixels / 8 - 2) + " caracteres\n" +
                              "Mensaje: " + message.length() + " caracteres");
                    return;
                }

                byte[] header = Arrays.copyOfRange(bmpBytes, 0, 54);
                byte[] pixels = Arrays.copyOfRange(bmpBytes, 54, bmpBytes.length);

                StringBuilder msgBin = new StringBuilder();
                for (char c : messageWithFlags.toCharArray())
                    msgBin.append(charToBinary.convert((byte) c)).append(" ");

                String[] msgBinArr = msgBin.toString().split(" ");
                String[] pixBinArr = charToBinary.convertByteArray(pixels);

                int pixelIndex = 0;
                for (String charBinary : msgBinArr) {
                    if (charBinary.isEmpty()) continue;
                    for (int j = 0; j < charBinary.length() && pixelIndex < pixBinArr.length; j++)
                        charToBinary.replaceBitInBlock(Character.getNumericValue(charBinary.charAt(j)), pixBinArr, pixelIndex++);
                }

                byte[] modifiedPixels = charToBinary.binaryArrayToBytes(pixBinArr);
                byte[] encryptedBmp = new byte[header.length + modifiedPixels.length];
                System.arraycopy(header, 0, encryptedBmp, 0, header.length);
                System.arraycopy(modifiedPixels, 0, encryptedBmp, header.length, modifiedPixels.length);

                String encryptedFileName = "Cifrado_" + new File(bmpFileName).getName();
                File cipheredDir = new File("src/main/ciphered");
                if (!cipheredDir.exists()) cipheredDir.mkdirs();
                File outputFile = new File(cipheredDir, encryptedFileName);
                Files.write(outputFile.toPath(), encryptedBmp);

                String savedPath = outputFile.getAbsolutePath();
                Platform.runLater(() -> showSuccess("Cifrado exitoso",
                    "Mensaje cifrado correctamente.\nArchivo guardado como: " + encryptedFileName + "\nRuta: " + savedPath));

            } catch (Exception e) {
                showAlert("Error al cifrar: " + e.getMessage());
            }
        }

        public void decrypt(String base64BmpData, String bmpFileName) {
            try {
                if (base64BmpData == null || base64BmpData.isEmpty()) { showAlert("No se proporcionó ningún archivo BMP"); return; }

                String decryptedMessage = charToBinary.decryptWithFlags(java.util.Base64.getDecoder().decode(base64BmpData));

                if (decryptedMessage.isEmpty()) {
                    showAlert("No se encontró ningún mensaje cifrado en la imagen.\nAsegúrate de que la imagen fue cifrada con este programa.");
                    return;
                }

                showSuccess("✓ Descifrado exitoso",
                    "Mensaje recuperado:\n\n\"" + decryptedMessage + "\"\n\n" +
                    "Longitud: " + decryptedMessage.length() + " caracteres\n(Extraído automáticamente usando banderas)");

            } catch (Exception e) {
                showAlert("Error al descifrar: " + e.getMessage());
            }
        }

        private void runScript(String js) {
            Platform.runLater(() -> webEngine.executeScript(js));
        }

        private void showAlert(String message) {
            runScript("alert('" + escape(message) + "');");
        }

        private void showSuccess(String title, String content) {
            Platform.runLater(() -> {
                try {
                    webEngine.executeScript("showResult('" + escape(title) + "', '" + escape(content) + "');");
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }

        private String escape(String text) {
            return text.replace("\\", "\\\\").replace("'", "\\'")
                       .replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r");
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
