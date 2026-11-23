import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicReference;
import javax.imageio.ImageIO;
import javax.swing.JComponent;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JViewport;
import javax.swing.SwingUtilities;

/**
 * Lanzador de los programas de Swing para verificar_codigo.py y generar_modulo.py (no se publica en los módulos).
 *
 * <p>Sale de herramientas/CapturaSwing.java del curso de Java (la primera edición), sin cambios: en el kit lo usa
 * lenguajes/java.py, que lo compila dentro de la terminal (en la imagen de Java, /opt/kit-java/CapturaSwing.java).
 *
 * <p>Sin pantalla no se puede crear un {@code JFrame} (da {@code HeadlessException}), pero sí su contenido. Por
 * convención, los programas de Swing del curso construyen el contenido de su ventana en un método
 * {@code public static JPanel content()} (y su {@code main} lo pone en un {@code JFrame}). Este lanzador llama a
 * ese método en el hilo de eventos de Swing (el EDT), dispone el panel con su tamaño preferido (como hace
 * {@code pack()}) y, si se pide, lo pinta en un PNG. El {@code main} del programa no se ejecuta.
 *
 * <p>Uso: {@code java -Djava.awt.headless=true -cp <este fichero compilado y el programa>
 * [-Dcaptura.fichero=captura.png] CapturaSwing paquete.Clase}
 *
 * <p>Termina con código 0 si todo va bien y 1 si el programa falla (con su traza).
 */
public class CapturaSwing {

    public static void main(String[] args) throws Exception {
        Method content = Class.forName(args[0]).getMethod("content");
        String fichero = System.getProperty("captura.fichero");
        AtomicReference<Exception> fallo = new AtomicReference<>();
        SwingUtilities.invokeAndWait(() -> {
            try {
                JComponent panel = (JComponent) content.invoke(null);
                Dimension size = panel.getPreferredSize();
                panel.setSize(size);
                disponer(panel);
                if (fichero != null) {
                    BufferedImage imagen = new BufferedImage(size.width, size.height, BufferedImage.TYPE_INT_ARGB);
                    Graphics2D g = imagen.createGraphics();
                    panel.paint(g);
                    g.dispose();
                    ImageIO.write(imagen, "png", new File(fichero));
                }
            } catch (InvocationTargetException e) {
                fallo.set(e.getCause() instanceof Exception causa ? causa : e);
            } catch (Exception e) {
                fallo.set(e);
            }
        });
        if (fallo.get() != null) {
            throw fallo.get();
        }
        System.exit(0);
    }

    // Sin ventana, nadie dispone los componentes: se hace a mano, de fuera adentro, como haría validate(). Y lo
    // que hace una JTable al mostrarse (addNotify): poner su fila de cabeceras en su JScrollPane
    private static void disponer(Component componente) {
        if (componente instanceof JTable tabla && tabla.getParent() instanceof JViewport vista
                && vista.getParent() instanceof JScrollPane desplazable && desplazable.getColumnHeader() == null
                && tabla.getTableHeader() != null) {
            desplazable.setColumnHeaderView(tabla.getTableHeader());
            desplazable.doLayout();
            disponer(desplazable.getColumnHeader());
        }
        if (componente instanceof Container contenedor) {
            contenedor.doLayout();
            for (Component hijo : contenedor.getComponents()) {
                disponer(hijo);
            }
        }
    }
}
