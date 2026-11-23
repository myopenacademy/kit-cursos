import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class Hora {
    public static void main(String[] args) {
        String hora = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
        System.out.println("Son las " + hora);
    }
}
