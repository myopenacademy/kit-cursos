# 01.03 Un proyecto de Gradle

> **Versiones:** Java 25 · Gradle 9.8.2
> **Conviene saber antes:** [Un proyecto de Maven](02-maven.md)
> **Tiempo estimado:** 1 hora
> **Nivel:** Básico · Ampliación

## Qué aprenderás

- Cómo se organiza un proyecto de Gradle.

## 1. Teoría

### 1.1. El build.gradle.kts

El `build.gradle.kts` dice cómo se construye el proyecto, en Kotlin.

## 2. Ejemplos de código

### 2.1. Un inventario

```java
package es.inventario;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<String> productos = List.of("Lápiz", "Cuaderno", "Goma");
        System.out.println("Hay " + productos.size() + " productos: " + String.join(", ", productos) + ".");
    }
}
```

📁 **Código:** [`codigo/03-gradle/ejemplos/2.1-inventario/`](codigo/03-gradle/ejemplos/2.1-inventario/src/main/java/es/inventario/)

**Salida:**

```text
Hay 3 productos: Lápiz, Cuaderno, Goma.
```

El proyecto:

```kotlin
plugins {
    java
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:6.0.3")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.withType<JavaCompile> {
    options.release = 25
    options.encoding = "UTF-8"
}

tasks.test {
    useJUnitPlatform()
}
```

📁 **Código:** [`codigo/03-gradle/ejemplos/2.1-inventario/`](codigo/03-gradle/ejemplos/2.1-inventario/)

## 3. Errores típicos

### 3.1. Las comillas

En Kotlin, los textos van entre comillas dobles.

## 4. Buenas prácticas

- Usa el mismo Gradle en todo el equipo.

## 5. Ejercicios prácticos resueltos

### 🟢 Básico

#### Ejercicio 1 · Las comillas de Kotlin

¿Qué comillas lleva el nombre de una dependencia en el `build.gradle.kts`?

<details>
<summary>Pista 1</summary>

Mira el ejemplo 2.1.

</details>

<details>
<summary>Ver solución</summary>

Las dobles: lo explica [3.1](#31-las-comillas).

</details>

### 🟡 Intermedio

Este módulo no tiene ejercicios intermedios todavía.

### 🔴 Avanzado

Este módulo no tiene ejercicios avanzados todavía.

### 🏆 Caso real

Tampoco tiene caso real.

## 6. Chuleta

### Gradle

| Qué | Orden |
|---|---|
| Construir | `gradle build` |

## 7. Preguntas de repaso

1. ¿En qué lenguaje se escribe el build.gradle.kts?

   <details>
   <summary>Ver respuesta</summary>

   En Kotlin. Lo tienes en [1.1. El build.gradle.kts](#11-el-buildgradlekts).

   </details>

---
⬅️ [Anterior: Un proyecto de Maven](02-maven.md) · 📚 [Índice](../00-indice.md) · ➡️ [Siguiente: Retos de la fase](retos.md)
