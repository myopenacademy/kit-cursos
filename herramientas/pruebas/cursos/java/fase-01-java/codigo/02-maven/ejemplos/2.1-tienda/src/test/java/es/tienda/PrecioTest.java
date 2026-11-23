package es.tienda;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class PrecioTest {
    @Test
    void sumaElIva() {
        assertEquals(24.2, Precio.conIva(20.0));
    }

    @Test
    void redondeaALosCentimos() {
        assertEquals(1.21, Precio.conIva(0.999));
    }
}
