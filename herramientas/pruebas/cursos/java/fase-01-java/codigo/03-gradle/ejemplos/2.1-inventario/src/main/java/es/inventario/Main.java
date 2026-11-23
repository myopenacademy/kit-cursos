package es.inventario;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<String> productos = List.of("Lápiz", "Cuaderno", "Goma");
        System.out.println("Hay " + productos.size() + " productos: " + String.join(", ", productos) + ".");
    }
}
