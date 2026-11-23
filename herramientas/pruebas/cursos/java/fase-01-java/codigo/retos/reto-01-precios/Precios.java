public class Precios {
    public static void main(String[] args) {
        double[] precios = {10.0, 2.5};
        double total = 0;
        for (double precio : precios) {
            total += precio;
        }
        System.out.printf("Total: %.2f €%n", total);
    }
}
