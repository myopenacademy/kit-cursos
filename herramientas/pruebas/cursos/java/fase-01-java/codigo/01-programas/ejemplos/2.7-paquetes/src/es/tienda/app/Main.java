package es.tienda.app;

import es.tienda.modelo.Producto;

public class Main {
    public static void main(String[] args) {
        Producto lapiz = new Producto("Lápiz", 0.5);
        System.out.println(lapiz.nombre() + ": " + lapiz.precio() + " €");
    }
}
