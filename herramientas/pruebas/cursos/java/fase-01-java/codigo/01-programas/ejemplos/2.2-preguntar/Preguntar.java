import java.util.Scanner;

public class Preguntar {
    public static void main(String[] args) {
        Scanner teclado = new Scanner(System.in);
        System.out.print("¿Cómo te llamas? ");
        String nombre = teclado.nextLine();
        System.out.print("¿Cuántos libros tienes? ");
        int libros = teclado.nextInt();
        System.out.println(nombre + " tiene " + libros + " libros.");
    }
}
