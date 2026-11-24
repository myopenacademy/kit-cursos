# 01.01 Programas de Java

> **Versiones:** Java 25 (Temurin 25.0.4.1)
> **Conviene saber antes:** [el índice](../00-indice.md)
> **Tiempo estimado:** 1 hora
> **Nivel:** Básico · Núcleo

## Qué aprenderás

- Cómo se ejecuta un programa de Java de un solo fichero.
- Cómo lee argumentos, opciones y lo que tecleas.

## 1. Teoría

### 1.1. Un programa de un solo fichero

Un programa de un solo fichero se ejecuta con `java Fichero.java`, sin compilarlo antes.

## 2. Ejemplos de código

### 2.1. Un saludo con argumentos

```java
public class Saludo {
    public static void main(String[] args) {
        System.out.println("Hola, " + String.join(" ", args) + ".");
        System.out.printf("Tienes %d argumentos y %.2f euros.%n", args.length, 1234.5);
    }
}
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.1-saludo/`](codigo/01-programas/ejemplos/2.1-saludo/)

**Salida:**

```text
Hola, Ana de la Fuente.
Tienes 2 argumentos y 1234,50 euros.
```

### 2.2. Preguntar al usuario

```java
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
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.2-preguntar/`](codigo/01-programas/ejemplos/2.2-preguntar/)

**Sesión en la terminal:**

```text
¿Cómo te llamas? Ana
¿Cuántos libros tienes? 7
Ana tiene 7 libros.
```

### 2.3. Una opción de la JVM

```java
public class Propiedad {
    public static void main(String[] args) {
        System.out.println("Tienda: " + System.getProperty("tienda.nombre"));
    }
}
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.3-opciones/`](codigo/01-programas/ejemplos/2.3-opciones/)

**Salida:**

```text
Tienda: La Librería
```

### 2.4. Un programa que termina con un error

```java
public class Media {
    public static void main(String[] args) {
        System.out.println("Calculando la media...");
        System.err.println("Error: no hay notas para hacer la media.");
        System.exit(1);
    }
}
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.4-error/`](codigo/01-programas/ejemplos/2.4-error/)

**Salida:**

```text
Calculando la media...
```

**Salida de error:**

```text
Error: no hay notas para hacer la media.
```

### 2.5. La hora

```java
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class Hora {
    public static void main(String[] args) {
        String hora = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
        System.out.println("Son las " + hora);
    }
}
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.5-hora/`](codigo/01-programas/ejemplos/2.5-hora/)

**Salida:**

```text
Son las 10:30:00
```

Tu hora será otra.

### 2.6. Una ventana de aviso

```java
import javax.swing.JOptionPane;

public class Aviso {
    public static void main(String[] args) {
        JOptionPane.showMessageDialog(null, "Tu pedido está en camino.");
    }
}
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.6-ventana/`](codigo/01-programas/ejemplos/2.6-ventana/)

### 2.7. Un programa con paquetes

El producto, en su paquete:

```java
package es.tienda.modelo;

public record Producto(String nombre, double precio) {
}
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.7-paquetes/src/es/tienda/modelo/`](codigo/01-programas/ejemplos/2.7-paquetes/src/es/tienda/modelo/)

Y el programa, en otro paquete, que lo usa:

```java
package es.tienda.app;

import es.tienda.modelo.Producto;

public class Main {
    public static void main(String[] args) {
        Producto lapiz = new Producto("Lápiz", 0.5);
        System.out.println(lapiz.nombre() + ": " + lapiz.precio() + " €");
    }
}
```

📁 **Código:** [`codigo/01-programas/ejemplos/2.7-paquetes/src/es/tienda/app/`](codigo/01-programas/ejemplos/2.7-paquetes/src/es/tienda/app/)

**Salida:**

```text
Lápiz: 0.5 €
```

Se ejecuta con `java Main.java` desde su carpeta: Java busca las demás clases desde la raíz de las fuentes (`src/`).

## 3. Errores típicos

### 3.1. El nombre del fichero

El fichero se llama como su clase pública.

## 4. Buenas prácticas

- Pon nombres claros a las clases.

## 5. Ejercicios prácticos resueltos

### 🟢 Básico

#### Ejercicio 1 · La tabla del 3

Escribe las tres primeras líneas de la tabla de multiplicar del 3.

<details>
<summary>Pista 1</summary>

Usa un bucle `for`.

</details>

<details>
<summary>Ver solución</summary>

```java
public class Tabla {
    public static void main(String[] args) {
        for (int i = 1; i <= 3; i++) {
            System.out.println("3 x " + i + " = " + (3 * i));
        }
    }
}
```

📁 **Código:** [`codigo/01-programas/ejercicios/ej01-tabla/`](codigo/01-programas/ejercicios/ej01-tabla/)

**Salida:**

```text
3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
```

</details>

### 🟡 Intermedio

Este módulo no tiene ejercicios intermedios todavía.

### 🔴 Avanzado

Este módulo no tiene ejercicios avanzados todavía.

### 🏆 Caso real

Tampoco tiene caso real.

## 6. Chuleta

### Ejecutar

| Qué | Orden |
|---|---|
| Un programa | `java Fichero.java` |

## 7. Preguntas de repaso

1. ¿Con qué orden se ejecuta un programa de un solo fichero?

   <details>
   <summary>Ver respuesta</summary>

   Con `java Fichero.java`. Lo tienes en [1.1. Un programa de un solo fichero](#11-un-programa-de-un-solo-fichero).

   </details>

---
⬅️ [Índice](../00-indice.md) · 📚 [Índice](../00-indice.md) · ➡️ [Siguiente: Un proyecto de Maven](02-maven.md)
