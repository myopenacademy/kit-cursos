package es.precios;

import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

@RestController
@RequestMapping("/api")
public class PrecioController {
    private final RestClient cambio = RestClient.create("http://localhost:8090");

    public record Precio(int id, String nombre, double euros) {
    }

    public record EnDolares(String nombre, double dolares) {
    }

    @GetMapping("/precios/{id}")
    public Precio uno(@PathVariable int id) {
        if (id != 1) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "No existe el precio " + id);
        }
        return new Precio(1, "Cuaderno", 2.5);
    }

    @DeleteMapping("/precios/{id}")
    public ResponseEntity<Void> borrar(@PathVariable int id) {
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/precios")
    public ResponseEntity<Precio> crear(@RequestBody Precio precio) {
        URI donde = ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}").buildAndExpand(precio.id()).toUri();
        return ResponseEntity.created(donde).body(precio);
    }

    @GetMapping("/precios/{id}/dolares")
    public EnDolares enDolares(@PathVariable int id) {
        Precio precio = uno(id);
        Map<?, ?> tipo = cambio.get().uri("/cambio").retrieve().body(Map.class);
        double dolares = precio.euros() * ((Number) tipo.get("dolar")).doubleValue();
        return new EnDolares(precio.nombre(), dolares);
    }

    @GetMapping("/saludo")
    public String saludo(@RequestParam String nombre) {
        return "Hola, " + nombre + "\n";
    }

    @GetMapping("/tienda")
    public String tienda() throws IOException {
        return Files.readString(Path.of("tienda.txt"));
    }
}
