package es.tienda;

public class Precio {
    public static double conIva(double precio) {
        return Math.round(precio * 1.21 * 100) / 100.0;
    }
}
