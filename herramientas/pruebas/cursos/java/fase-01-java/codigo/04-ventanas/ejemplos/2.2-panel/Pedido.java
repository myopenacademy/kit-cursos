import java.awt.BorderLayout;
import java.awt.GridLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

public class Pedido {
    public static JPanel content() {
        JPanel campos = new JPanel(new GridLayout(2, 2, 6, 6));
        campos.add(new JLabel("Producto:"));
        campos.add(new JTextField("Cuaderno", 12));
        campos.add(new JLabel("Cantidad:"));
        campos.add(new JTextField("3", 12));
        JPanel panel = new JPanel(new BorderLayout(8, 8));
        panel.add(campos, BorderLayout.CENTER);
        panel.add(new JButton("Pedir"), BorderLayout.SOUTH);
        return panel;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame ventana = new JFrame("Pedido");
            ventana.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            ventana.setContentPane(content());
            ventana.pack();
            ventana.setVisible(true);
        });
    }
}
