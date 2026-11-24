# 01.05 Una aplicación de Spring Boot

> **Versiones:** Java 25 · Spring Boot 4.1.2
> **Conviene saber antes:** [Un proyecto de Maven](02-maven.md)
> **Tiempo estimado:** 1 hora
> **Nivel:** Intermedio · Ampliación

## Qué aprenderás

- Cómo se escribe una API con Spring Boot.
- Cómo se prueba con curl.

## 1. Teoría

### 1.1. Un controlador

Un `@RestController` responde a las peticiones HTTP.

## 2. Ejemplos de código

### 2.1. Los precios de una tienda

La aplicación:

```java
package es.precios;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class PreciosApplication {
    public static void main(String[] args) {
        SpringApplication.run(PreciosApplication.class, args);
    }
}
```

📁 **Código:** [`codigo/05-spring/ejemplos/2.1-precios/aplicacion/src/main/java/es/precios/`](codigo/05-spring/ejemplos/2.1-precios/aplicacion/src/main/java/es/precios/)

Su controlador, que pregunta los tipos de cambio a una API (en el ejemplo, una simulada en el puerto 8090):

```java
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
```

📁 **Código:** [`codigo/05-spring/ejemplos/2.1-precios/aplicacion/src/main/java/es/precios/`](codigo/05-spring/ejemplos/2.1-precios/aplicacion/src/main/java/es/precios/)

**Con la aplicación arrancada:**

```text
# Un precio
$ curl -i http://localhost:8080/api/precios/1
HTTP/1.1 200
Content-Type: application/json
Content-Length: 40

{"id":1,"nombre":"Cuaderno","euros":2.5}

# El mismo, en dólares: la aplicación pregunta a la API de cambio
$ curl -s http://localhost:8080/api/precios/1/dolares
{"nombre":"Cuaderno","dolares":2.75}

# Uno que no existe
$ curl -s http://localhost:8080/api/precios/99
{"timestamp":"2026-11-23T13:39:28.477Z","status":404,"error":"Not Found","path":"/api/precios/99"}

# Un método que esa ruta no admite
$ curl -s -i -X PUT http://localhost:8080/api/precios/1
HTTP/1.1 405
Allow: DELETE, GET
Content-Type: application/json
Transfer-Encoding: chunked

{"timestamp":"2026-11-23T13:39:28.494Z","status":405,"error":"Method Not Allowed","path":"/api/precios/1"}

# Uno nuevo
$ curl -s -i -H "Content-Type: application/json" -d '{"id": 2, "nombre": "Lápiz", "euros": 0.8}' http://localhost:8080/api/precios
HTTP/1.1 201
Location: http://localhost:8080/api/precios/2
Content-Type: application/json
Transfer-Encoding: chunked

{"id":2,"nombre":"Lápiz","euros":0.8}

# El nombre, en una variable
$ NOMBRE=$(curl -s http://localhost:8080/api/precios/1 | jq -r .nombre)

$ curl -s "http://localhost:8080/api/saludo?nombre=$NOMBRE"
Hola, Cuaderno

$ curl -s http://localhost:8080/api/precios/1 | jq -r .euros
2.5

# La tienda, antes y después de cambiar su fichero
$ curl -s http://localhost:8080/api/tienda
La Papelería

$ cp otra-tienda.txt tienda.txt

$ sleep 1

$ curl -s http://localhost:8080/api/tienda
La Papelería Nueva
```

Tus fechas y horas serán otras.

## 3. Errores típicos

### 3.1. El puerto ocupado

Si el 8080 está ocupado, la aplicación no arranca.

## 4. Buenas prácticas

- Prueba cada ruta con curl.

## 5. Ejercicios prácticos resueltos

### 🟢 Básico

#### Ejercicio 1 · El código 201

¿Qué código devuelve un POST que crea un precio?

<details>
<summary>Pista 1</summary>

Mira el ejemplo 2.1.

</details>

<details>
<summary>Ver solución</summary>

El 201 (Created), con la cabecera `Location`: lo enseña el ejemplo [2.1](#21-los-precios-de-una-tienda).

</details>

### 🟡 Intermedio

Este módulo no tiene ejercicios intermedios todavía.

### 🔴 Avanzado

Este módulo no tiene ejercicios avanzados todavía.

### 🏆 Caso real

Tampoco tiene caso real.

## 6. Chuleta

### Spring Boot

| Qué | Anotación |
|---|---|
| Un controlador | `@RestController` |

## 7. Preguntas de repaso

1. ¿Qué anotación tiene un controlador?

   <details>
   <summary>Ver respuesta</summary>

   `@RestController`. Lo tienes en [1.1. Un controlador](#11-un-controlador).

   </details>

---
⬅️ [Anterior: Ventanas](04-ventanas.md) · 📚 [Índice](../00-indice.md) · ➡️ [Siguiente: Retos de la fase](retos.md)
