package es.contador;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

public class ContadorApp extends Application {
    private int veces;

    @Override
    public void start(Stage stage) {
        Label etiqueta = new Label("Pulsaciones: 0");
        Button boton = new Button("Suma uno");
        boton.setId("suma");
        boton.setOnAction(evento -> {
            veces++;
            etiqueta.setText("Pulsaciones: " + veces);
            System.out.println("Pulsado " + veces + " veces");
        });
        VBox raiz = new VBox(10, etiqueta, boton);
        raiz.setAlignment(Pos.CENTER);
        raiz.setPadding(new Insets(16));
        stage.setTitle("Contador");
        stage.setScene(new Scene(raiz, 240, 120));
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
