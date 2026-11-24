# 01.02 Un proyecto de Maven

> **Versiones:** Java 25 · Maven 3.10.0 · JUnit 6.0.3
> **Conviene saber antes:** [Programas de Java](01-programas.md)
> **Tiempo estimado:** 1 hora
> **Nivel:** Básico · Núcleo

## Qué aprenderás

- Cómo se organiza un proyecto de Maven.
- Cómo se prueban sus clases con JUnit.

## 1. Teoría

### 1.1. El pom.xml

El `pom.xml` dice el nombre del proyecto y sus dependencias.

## 2. Ejemplos de código

### 2.1. Una tienda

El precio con IVA:

```java
package es.tienda;

public class Precio {
    public static double conIva(double precio) {
        return Math.round(precio * 1.21 * 100) / 100.0;
    }
}
```

📁 **Código:** [`codigo/02-maven/ejemplos/2.1-tienda/src/main/java/es/tienda/`](codigo/02-maven/ejemplos/2.1-tienda/src/main/java/es/tienda/)

Y el programa que lo usa:

```java
package es.tienda;

public class App {
    public static void main(String[] args) {
        System.out.printf("Un libro de %.2f € cuesta %.2f € con IVA.%n", 20.0, Precio.conIva(20.0));
    }
}
```

📁 **Código:** [`codigo/02-maven/ejemplos/2.1-tienda/src/main/java/es/tienda/`](codigo/02-maven/ejemplos/2.1-tienda/src/main/java/es/tienda/)

**Salida:**

```text
Un libro de 20,00 € cuesta 24,20 € con IVA.
```

Sus pruebas:

```java
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
```

📁 **Código:** [`codigo/02-maven/ejemplos/2.1-tienda/src/test/java/es/tienda/`](codigo/02-maven/ejemplos/2.1-tienda/src/test/java/es/tienda/)

**Salida de las pruebas:**

```text
[INFO] Running es.tienda.PrecioTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 -- in es.tienda.PrecioTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
```

El proyecto entero:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>es.tienda</groupId>
    <artifactId>tienda</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.release>25</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>6.0.3</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.6.0</version>
            </plugin>
        </plugins>
    </build>
</project>
```

📁 **Código:** [`codigo/02-maven/ejemplos/2.1-tienda/`](codigo/02-maven/ejemplos/2.1-tienda/)

## 3. Errores típicos

### 3.1. La carpeta de las pruebas

Las pruebas van en `src/test/java`, no en `src/main/java`.

## 4. Buenas prácticas

- Fija la versión de cada dependencia.

## 5. Ejercicios prácticos resueltos

### 🟢 Básico

#### Ejercicio 1 · La carpeta de una prueba

¿En qué carpeta va `PrecioTest.java`?

<details>
<summary>Pista 1</summary>

Mira el ejemplo 2.1.

</details>

<details>
<summary>Ver solución</summary>

En `src/test/java/es/tienda/`: lo explica [3.1](#31-la-carpeta-de-las-pruebas).

</details>

### 🟡 Intermedio

Este módulo no tiene ejercicios intermedios todavía.

### 🔴 Avanzado

Este módulo no tiene ejercicios avanzados todavía.

### 🏆 Caso real

Tampoco tiene caso real.

## 6. Chuleta

### Maven

| Qué | Orden |
|---|---|
| Construir | `mvn package` |

## 7. Preguntas de repaso

1. ¿Dónde van las pruebas?

   <details>
   <summary>Ver respuesta</summary>

   En `src/test/java`. Lo tienes en [3.1. La carpeta de las pruebas](#31-la-carpeta-de-las-pruebas).

   </details>

---
⬅️ [Anterior: Programas de Java](01-programas.md) · 📚 [Índice](../00-indice.md) · ➡️ [Siguiente: Un proyecto de Gradle](03-gradle.md)
