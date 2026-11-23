# Retos de la fase 01 — Java

> **Conviene saber antes:** los módulos de la fase.
> **Tiempo estimado:** 1 hora

Un reto opcional para afianzar lo aprendido.

## Reto 1 · El total de una compra

Suma los precios de una compra y escribe el total con dos decimales.

<details>
<summary>Pista 1</summary>

Recorre los precios con un bucle `for`.

</details>

<details>
<summary>Ver solución</summary>

```java
public class Precios {
    public static void main(String[] args) {
        double[] precios = {10.0, 2.5};
        double total = 0;
        for (double precio : precios) {
            total += precio;
        }
        System.out.printf("Total: %.2f €%n", total);
    }
}
```

📁 **Código:** [`codigo/retos/reto-01-precios/`](codigo/retos/reto-01-precios/)

**Salida:**

```text
Total: 12,50 €
```

</details>
