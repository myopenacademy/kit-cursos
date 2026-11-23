public class Saludo {
    public static void main(String[] args) {
        System.out.println("Hola, " + String.join(" ", args) + ".");
        System.out.printf("Tienes %d argumentos y %.2f euros.%n", args.length, 1234.5);
    }
}
