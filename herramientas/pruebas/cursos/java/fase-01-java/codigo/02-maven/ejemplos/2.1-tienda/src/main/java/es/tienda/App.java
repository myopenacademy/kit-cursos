package es.tienda;

public class App {
    public static void main(String[] args) {
        System.out.printf("Un libro de %.2f € cuesta %.2f € con IVA.%n", 20.0, Precio.conIva(20.0));
    }
}
