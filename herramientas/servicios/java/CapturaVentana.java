import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.ButtonBase;
import javafx.scene.control.SelectionModel;
import javafx.scene.control.TextInputControl;
import javafx.scene.image.PixelReader;
import javafx.scene.image.WritableImage;
import javafx.stage.Stage;
import javafx.stage.Window;

/**
 * Lanzador de los programas de JavaFX para verificar_codigo.py y generar_modulo.py (no se publica en los
 * módulos).
 *
 * <p>Sale de herramientas/CapturaVentana.java del curso de Java (la primera edición), sin cambios: en el kit lo usa
 * lenguajes/java.py, que lo compila dentro de la terminal (en la imagen de Java, /opt/kit-java/CapturaVentana.java).
 *
 * <p>Arranca la aplicación con su {@code main} (que llama a {@code launch}; si no tiene, con {@code Application.launch}),
 * así que se ejecutan su init, start y stop como al ejecutarla. Espera
 * a que se muestre su ventana, hace las acciones de {@code acciones.txt} si las hay, guarda la imagen de la
 * ventana si se pide y cierra la aplicación. Así, un programa con ventanas termina solo y se puede comprobar
 * sin pantalla, con {@code -Dglass.platform=headless} (JavaFX 26 o posterior).
 *
 * <p>Uso: {@code java -Dglass.platform=headless --module-path <JavaFX> --add-modules javafx.controls
 * -cp <este fichero compilado y el programa> [-Dcaptura.fichero=captura.png] [-Dcaptura.acciones=acciones.txt]
 * CapturaVentana paquete.ClaseApp [argumentos]}
 *
 * <p>Las acciones, una por línea ({@code #} empieza un comentario): {@code escribir #id texto} (el texto de un
 * campo), {@code pulsar #id} (un botón, una casilla...), {@code elegir #id n} (la opción n, desde 0, de una
 * lista, una tabla o un desplegable), {@code responder Texto} (el botón con ese texto, como el «Aceptar» de un
 * diálogo) y {@code esperar ms} (a que termine una tarea en segundo plano). Cada acción se hace sobre la ventana
 * que está delante: si una abre un diálogo y espera a que se cierre ({@code showAndWait}), las siguientes se
 * hacen sobre el diálogo. La imagen es la de la ventana que está delante al final. Termina con código 0 si todo
 * va bien, 1 si la aplicación falla y 2 si no se muestra ninguna ventana o una acción no se puede hacer.
 */
public class CapturaVentana {
    private static final long ESPERA_VENTANA = 20;          // segundos, como mucho, hasta que se muestre

    public static void main(String[] args) throws Exception {
        @SuppressWarnings("unchecked")
        Class<? extends Application> app = (Class<? extends Application>) Class.forName(args[0]);
        String fichero = System.getProperty("captura.fichero");
        String acciones = System.getProperty("captura.acciones");
        Thread guion = Thread.ofPlatform().daemon().start(() -> {
            try {
                esperarVentana();
                List<AtomicReference<Exception>> pendientes = new ArrayList<>();
                if (acciones != null) {
                    for (String linea : Files.readAllLines(Path.of(acciones))) {
                        String accion = linea.strip();
                        if (accion.isEmpty() || accion.startsWith("#")) {
                            continue;
                        }
                        if (accion.startsWith("esperar ")) {
                            Thread.sleep(Long.parseLong(accion.substring("esperar ".length()).strip()));
                            continue;
                        }
                        pendientes.add(hacerSobreLaDeDelante(accion));
                    }
                }
                Thread.sleep(300);                         // lo que las acciones dejan para después (runLater)
                for (AtomicReference<Exception> fallo : pendientes) {
                    if (fallo.get() != null) {
                        throw fallo.get();
                    }
                }
                if (fichero != null) {
                    WritableImage imagen = enHiloFx(() -> delante().getScene().snapshot(null));
                    guardar(imagen, new File(fichero));
                }
            } catch (Exception e) {
                System.err.println("CapturaVentana: " + e.getMessage());
                Runtime.getRuntime().halt(2);
            }
            Platform.exit();
        });
        String[] argumentos = List.of(args).subList(1, args.length).toArray(String[]::new);
        Method main;
        try {
            main = app.getMethod("main", String[].class);
        } catch (NoSuchMethodException e) {
            main = null;
        }
        if (main != null) {
            try {
                main.invoke(null, (Object) argumentos);
            } catch (java.lang.reflect.InvocationTargetException e) {
                throw e.getCause() instanceof Exception causa ? causa : e;
            }
        } else {
            Application.launch(app, argumentos);
        }
        guion.join(TimeUnit.SECONDS.toMillis(5));
    }

    // La primera ventana (Stage) que se muestra: la principal
    private static Stage esperarVentana() throws Exception {
        long limite = System.nanoTime() + TimeUnit.SECONDS.toNanos(ESPERA_VENTANA);
        while (System.nanoTime() < limite) {
            Thread.sleep(100);
            Stage ventana = enHiloFx(() -> Window.getWindows().stream()
                    .filter(w -> w instanceof Stage && w.isShowing()).map(w -> (Stage) w).findFirst().orElse(null));
            if (ventana != null && ventana.getScene() != null) {
                Thread.sleep(300);                          // la primera disposición y los runLater de start
                return ventana;
            }
        }
        throw new IllegalStateException("la aplicación no muestra ninguna ventana en " + ESPERA_VENTANA + " s");
    }

    // La ventana que está delante: la última que se ha mostrado y sigue abierta (un diálogo, si hay uno)
    private static Window delante() {
        List<Window> abiertas = Window.getWindows().stream().filter(Window::isShowing).toList();
        return abiertas.getLast();
    }

    // Hace la acción en el hilo de JavaFX sobre la ventana de delante y espera a que termine... salvo que abra
    // un diálogo que espera al usuario (showAndWait): entonces sigue, y la acción terminará al cerrarlo. Lo que
    // devuelve es el fallo de la acción, si lo hay (cuando termine)
    private static AtomicReference<Exception> hacerSobreLaDeDelante(String accion) throws Exception {
        Window antes = enHiloFx(CapturaVentana::delante);
        AtomicReference<Exception> fallo = new AtomicReference<>();
        CountDownLatch hecho = new CountDownLatch(1);
        Platform.runLater(() -> {
            try {
                hacer(antes.getScene(), accion);
            } catch (Exception e) {
                fallo.set(e);
            } finally {
                hecho.countDown();
            }
        });
        long limite = System.nanoTime() + TimeUnit.SECONDS.toNanos(ESPERA_VENTANA);
        while (!hecho.await(50, TimeUnit.MILLISECONDS)) {
            if (enHiloFx(CapturaVentana::delante) != antes) {
                Thread.sleep(300);                         // el diálogo, ya dibujado
                return fallo;                              // ha abierto otra ventana: las acciones siguientes, en ella
            }
            if (System.nanoTime() > limite) {
                throw new IllegalStateException("«" + accion + "» no termina en " + ESPERA_VENTANA + " s");
            }
        }
        if (fallo.get() != null) {
            throw fallo.get();
        }
        return fallo;
    }

    private interface Tarea<T> {
        T hacer() throws Exception;
    }

    // Ejecuta la tarea en el hilo de JavaFX y espera su resultado (o su excepción)
    private static <T> T enHiloFx(Tarea<T> tarea) throws Exception {
        AtomicReference<T> resultado = new AtomicReference<>();
        AtomicReference<Exception> fallo = new AtomicReference<>();
        CountDownLatch hecho = new CountDownLatch(1);
        Platform.runLater(() -> {
            try {
                resultado.set(tarea.hacer());
            } catch (Exception e) {
                fallo.set(e);
            } finally {
                hecho.countDown();
            }
        });
        if (!hecho.await(ESPERA_VENTANA, TimeUnit.SECONDS)) {
            throw new IllegalStateException("el hilo de JavaFX no responde (¿un diálogo que espera al usuario?)");
        }
        if (fallo.get() != null) {
            throw fallo.get();
        }
        return resultado.get();
    }

    private static Void hacer(Scene escena, String accion) throws Exception {
        if (accion.startsWith("responder ")) {
            String texto = accion.substring("responder ".length()).strip();
            ButtonBase boton = botonConTexto(escena.getRoot(), texto);
            if (boton == null) {
                throw new IllegalArgumentException("«" + accion + "»: no hay ningún botón «" + texto + "» en la ventana de delante");
            }
            boton.fire();
            return null;
        }
        String[] partes = accion.split("\\s+", 3);
        Node nodo = partes.length > 1 ? escena.lookup(partes[1]) : null;
        if (nodo == null) {
            throw new IllegalArgumentException("«" + accion + "»: no hay ningún nodo " + (partes.length > 1 ? partes[1] : ""));
        }
        switch (partes[0]) {
            case "escribir" -> {
                if (!(nodo instanceof TextInputControl campo)) {
                    throw new IllegalArgumentException("«" + accion + "»: " + partes[1] + " no es un campo de texto");
                }
                campo.requestFocus();
                campo.setText(partes.length > 2 ? partes[2] : "");
            }
            case "pulsar" -> {
                if (!(nodo instanceof ButtonBase boton)) {
                    throw new IllegalArgumentException("«" + accion + "»: " + partes[1] + " no se puede pulsar");
                }
                boton.fire();
            }
            case "elegir" -> {
                // ListView, TableView, ComboBox, ChoiceBox...: todos tienen getSelectionModel(), con un SelectionModel
                // (su clase concreta es interna de JavaFX: se usa el tipo público)
                Method seleccion = nodo.getClass().getMethod("getSelectionModel");
                if (!(seleccion.invoke(nodo) instanceof SelectionModel<?> modelo)) {
                    throw new IllegalArgumentException("«" + accion + "»: " + partes[1] + " no tiene opciones que elegir");
                }
                modelo.select(Integer.parseInt(partes[2]));
            }
            default -> throw new IllegalArgumentException("«" + accion + "»: acción desconocida (escribir, pulsar, elegir, responder o esperar)");
        }
        return null;
    }

    // El primer botón del árbol con ese texto (los de un diálogo no tienen id)
    private static ButtonBase botonConTexto(Node nodo, String texto) {
        if (nodo instanceof ButtonBase boton && texto.equals(boton.getText())) {
            return boton;
        }
        if (nodo instanceof Parent padre) {
            for (Node hijo : padre.getChildrenUnmodifiable()) {
                ButtonBase encontrado = botonConTexto(hijo, texto);
                if (encontrado != null) {
                    return encontrado;
                }
            }
        }
        return null;
    }

    // La imagen de JavaFX, píxel a píxel, a un PNG (sin javafx.swing)
    private static void guardar(WritableImage imagen, File fichero) throws IOException {
        int ancho = (int) imagen.getWidth(), alto = (int) imagen.getHeight();
        BufferedImage png = new BufferedImage(ancho, alto, BufferedImage.TYPE_INT_ARGB);
        PixelReader pixeles = imagen.getPixelReader();
        for (int y = 0; y < alto; y++) {
            for (int x = 0; x < ancho; x++) {
                png.setRGB(x, y, pixeles.getArgb(x, y));
            }
        }
        javax.imageio.ImageIO.write(png, "png", fichero);
    }
}
