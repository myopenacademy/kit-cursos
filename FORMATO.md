# Formato de los cursos de MyOpenAcademy

> **Versión del formato: 1, revisión 1.1** · la versión 1, aprobada por el autor el 8 de noviembre de 2026; la revisión 1.1, del 23 de noviembre de 2026.
> Forma parte del kit de cursos de MyOpenAcademy. Cómo se cambia: [apartado 15](#15-cambiar-este-formato).

Este documento dice **cómo tiene que ser un curso para que MyOpenAcademy lo pueda instalar**. Está escrito para cualquiera que quiera crear un curso, no solo para el autor.

## 1. La idea

MyOpenAcademy funciona como **un juego con DLC**: la academia es el juego y cada curso es una expansión que se instala, se actualiza sin perder el progreso y que cualquiera puede crear. Todo es gratis y de código abierto.

Para que eso funcione, la academia y los cursos solo comparten **este contrato**:

- **Manda la academia.** Este formato recoge lo que la academia necesita para instalar y mostrar un curso, y **todo curso lo cumple**. Si un curso necesita algo que la academia no sabe hacer, no se hace un apaño en el curso: primero se amplía la academia y este formato, y después lo usa el curso.
- **La academia no sabe nada de ningún curso concreto** y **un curso no sabe nada del código de la academia**. Cada uno tiene su repositorio, sus versiones y su ritmo.
- **Un curso se lee también sin la academia**, directamente en GitHub: todo es Markdown con enlaces que funcionan.
- **El formato tiene versión** (el campo `formato` de [`curso.json`](#3-cursojson-la-identidad-del-curso)). Solo se cambia desde el proyecto del kit, y la academia sigue sabiendo leer las versiones anteriores. Las ampliaciones compatibles no cambian la versión: son revisiones (apartado 15).

En lo que sigue, **«debe»** es obligatorio (la comprobación falla si no se cumple) y **«conviene»** es una recomendación (la comprobación avisa, pero no falla).

## 2. Estructura de un repositorio de curso

```
curso-xxx/
├── curso.json                ← identidad y estructura del curso (apartado 3)
├── README.md                 ← portada: qué es, a quién va, cómo usarlo, versiones, requisitos
├── LICENSE                   ← licencias (apartado 12)
├── .gitattributes            ← saltos de línea LF en todo el texto (apartado 7)
├── CONTRIBUTING.md           ← cómo proponer cambios
├── CHANGELOG.md              ← qué cambia en cada versión
├── 00-indice.md              ← índice completo; se genera desde curso.json
├── 99-chuleta-global.md      ← todas las chuletas; se genera
├── ROADMAP.md                ← ruta de aprendizaje del curso (conviene)
├── RUTA-MINIMA.md            ← ruta mínima, si el curso la tiene (opcional; se genera desde curso.json)
├── glosario.md               ← términos del curso (opcional; el común, en el curso inicial: apartado 9)
├── fase-01-nombre/
│   ├── 01-nombre.md          ← un fichero por módulo
│   ├── 02-nombre.md
│   ├── retos.md              ← retos opcionales de la fase (apartado 6)
│   ├── img/                  ← imágenes de la fase (si hay)
│   └── codigo/               ← código de la fase (apartado 7)
├── fase-02-nombre/
│   └── …
└── proyecto/                 ← etapas del proyecto, si el curso lo hace por etapas (apartado 8)
    ├── 01-nombre.md
    └── codigo/
```

- **Cada curso es su propio repositorio de Git.** Los cursos oficiales viven en la organización [`myopenacademy`](https://github.com/myopenacademy) de GitHub, con el nombre `curso-<nombre>` (`myopenacademy/curso-java`); la academia está en [`santi-cast/myopenacademy`](https://github.com/santi-cast/myopenacademy). Un curso de otra persona puede estar en cualquier cuenta: basta con que cumpla este formato.
- Carpetas y ficheros **numerados** para que aparezcan en orden, con nombres en **minúsculas, sin tildes, sin eñes y sin espacios** (guiones en su lugar).
- **El número y el nombre del fichero no son la identidad del módulo**: la identidad está en `curso.json`. Un fichero se puede renombrar o mover a otra fase; basta con actualizar su ruta en `curso.json`.
- Las herramientas internas de quien escribe el curso (verificación, generadores) no son parte del curso: no se instalan en la academia. Si el curso las guarda en su repositorio, van en `herramientas/`, que la academia ignora.

## 3. `curso.json`: la identidad del curso

Es la **fuente de verdad** de la estructura del curso: qué fases, módulos, ejercicios y etapas tiene, en qué orden, en qué fichero está cada uno y con qué identificador. La academia lo lee para instalar el curso; el índice, la chuleta global y los roadmaps del curso se generan a partir de él. Se edita a mano o con las herramientas del kit, y **el kit lo comprueba siempre**: cambiar el título de un ejercicio o añadir uno nuevo son cosas distintas, y solo quien escribe el curso sabe cuál de las dos ha hecho.

### 3.1. Ejemplo

```json
{
  "formato": 1,
  "tipo": "curso",
  "id": "java",
  "titulo": "Java de 0 a experto",
  "descripcion": "De no saber programar a trabajar con Java y Spring Boot.",
  "version": "2.0.0",
  "academia_minima": "1.1.0",
  "idioma": "es",
  "repositorio": "https://github.com/myopenacademy/curso-java",
  "conviene_saber_antes": ["inicial"],
  "partes": [
    {
      "id": "java.parte.lenguaje",
      "titulo": "El lenguaje Java",
      "fases": ["java.fase.fundamentos", "java.fase.poo"]
    }
  ],
  "fases": [
    {
      "id": "java.fase.poo",
      "carpeta": "fase-03-poo",
      "titulo": "Programación orientada a objetos",
      "retos": "fase-03-poo/retos.md",
      "modulos": [
        {
          "id": "java.polimorfismo",
          "fichero": "fase-03-poo/04-polimorfismo.md",
          "titulo": "Polimorfismo",
          "ejercicios": [
            { "id": "java.polimorfismo.compila", "titulo": "¿Compila? ¿Qué pasa al ejecutar?" },
            { "id": "java.polimorfismo.parking", "titulo": "Las tarifas del parking" }
          ]
        }
      ]
    }
  ],
  "proyecto": {
    "tipo": "etapas",
    "titulo": "Mi Biblioteca",
    "etapas": [
      { "id": "java.etapa.consola", "fichero": "proyecto/01-version-consola.md", "titulo": "Versión de consola" }
    ]
  },
  "ruta_minima": {
    "modulos": ["java.polimorfismo"],
    "etapas": ["java.etapa.consola"],
    "plantilla": "RUTA-MINIMA.plantilla.md"
  },
  "equivalencias": []
}
```

### 3.2. Campos

| Campo | Qué es |
|---|---|
| `formato` | Versión de este documento que cumple el curso. Hoy, `1`. Las revisiones (1.1, 1.2…) no van aquí: son ampliaciones compatibles que no lo cambian (apartado 15). |
| `tipo` | Tipo de paquete. Hoy solo existe `"curso"`; el campo está para poder añadir otros en el futuro. |
| `id` | Identificador del curso: corto, en minúsculas (`inicial`, `java`, `sql`). Es el prefijo de todos los demás identificadores. No cambia nunca. |
| `titulo`, `descripcion` | Lo que muestra la academia en el catálogo. |
| `version` | Versión del curso (apartado 11). Coincide con la etiqueta de Git que se instala. |
| `academia_minima` | Opcional (desde la revisión 1.1). La versión mínima de MyOpenAcademy que necesita el curso, con la misma forma `MAYOR.MENOR.PARCHE` que `version` (apartado 11.1; por ejemplo, `"1.1.0"`). La academia lo lee y rechaza el curso si pide una versión mayor que la suya, comparando MAYOR, MENOR y PARCHE como números y en ese orden (`1.10.0` es mayor que `1.9.0`). Sin el campo, el curso vale para cualquier academia. Una academia 1.0.0 no conoce el campo y lo ignora (como todos los que no conoce; comprobado el 23 de noviembre de 2026), así que un curso que necesita la 1.1.0 lo dice también en su `README.md`. |
| `idioma` | Idioma del contenido (`es`). |
| `repositorio` | Dirección del repositorio en GitHub. La usan los enlaces entre cursos y el botón «Mejorar esta lección». |
| `conviene_saber_antes` | Cursos que se recomienda haber hecho antes (sus `id`). Son recomendaciones: nada se bloquea. |
| `partes` | Opcional. Tramos con nombre del curso, cada uno con la lista ordenada de sus fases. Sirven para orientarse y como piezas de los roadmaps. Si hay partes, cada fase está exactamente en una. Desde la revisión 1.1, además: cada parte tiene al menos una fase, sus fases van **seguidas y en el orden del curso** (un tramo), y las partes van una tras otra en ese mismo orden. Por ejemplo, A: [f1, f2] y B: [f3] vale; A: [f3, f1] (desordenada) o A: [f1, f3] con B: [f2] (no seguida), no. |
| `fases` | Las fases en orden. Cada una con su `id`, su `carpeta`, su `titulo` (el mismo de `00-indice.md`), sus `modulos` en orden y, si tiene retos, la ruta de su `retos.md`. Si los retos aún no están escritos, la fase lleva ya su ruta prevista y `"retos_disponibles": false`: se comprueba que la ruta es `<carpeta>/retos.md`, pero no que exista, y la academia no los muestra hasta que estén disponibles. |
| `modulos` | Cada módulo con su `id`, su `fichero`, su `titulo` (el mismo del encabezado del fichero) y sus `ejercicios` en orden. Un módulo todavía sin escribir lleva `"disponible": false`; conviene que lleve ya su `fichero` previsto (así los nombres quedan cerrados antes de escribir). De ese fichero se comprueba la forma de la ruta y que está en la carpeta de su fase, pero no que exista, y la academia no lo muestra hasta que el módulo esté disponible. |
| `ejercicios` | Cada ejercicio con su `id` y su `titulo`: el texto exacto que sigue a «Ejercicio N · » en el módulo (apartado 5.4). |
| `proyecto` | El proyecto para el portfolio del alumno (apartado 8). |
| `equivalencias` | Qué fue de los identificadores que ya no existen (apartado 11.2). |
| `ruta_minima` | Opcional (desde la revisión 1.1). La ruta mínima del curso, de la que sale `RUTA-MINIMA.md`. Un objeto con `modulos` (los `id` de sus módulos, en orden: al menos uno y sin repetir), `etapas` (opcional: los `id` de las etapas del proyecto que entran) y `plantilla` (opcional: un `.md` de la raíz del curso con su texto propio y estos huecos: `{{resumen}}`, `{{modulos}}`, que es obligatorio, `{{proyecto}}` y `{{consultas}}`; cualquier otro es un error). `RUTA-MINIMA.md` se genera desde aquí con `generar_ruta_minima.py` del kit y no se edita a mano; sin plantilla, el kit usa un texto genérico. La academia 1.0.0 ignora este campo sin error (comprobado el 23 de noviembre de 2026) y no instala la plantilla. |
| `transicion` | Opcional. Reglas de este formato que el curso todavía no cumple y que, mientras tanto, la comprobación trata como avisos y no como errores. Solo para cursos escritos antes de este formato. Hoy solo admite `"preguntas-de-repaso"` (el curso de Java lleva `"transicion": ["preguntas-de-repaso"]` mientras las añade). |

**Los títulos son texto plano.** Los del curso, las fases, los módulos, los ejercicios y los retos, tanto en `curso.json` como en sus encabezados, **no deben llevar formato Markdown**: ni negrita ni cursiva, ni código entre comillas invertidas, ni enlaces, ni HTML. La academia los muestra tal cual en menús, listas y seguimiento. Los nombres de órdenes, ficheros o código se escriben sin más: «Lee la salida de java -version», «Merge o rebase».

### 3.3. Identificadores

- **Forma:** el `id` del curso, un punto y un nombre: `java.polimorfismo`, `java.fase.poo`, `java.etapa.consola`, `java.parte.lenguaje`. Los ejercicios cuelgan de su módulo: `java.polimorfismo.parking`. Solo letras minúsculas sin tildes, cifras, guiones y puntos.
- **Sin números de posición.** El identificador no dice en qué fase ni en qué orden está el módulo, así que moverlo o renumerarlo no lo cambia.
- **Permanentes.** Una vez publicado, un identificador **no cambia ni se reutiliza nunca**: el progreso de los usuarios va unido a él. Cambiar el título de un módulo o de un ejercicio es cambiar su `titulo`, conservando el `id`.
- **Únicos** dentro del curso; con el prefijo del curso, también en toda la academia. Por eso **el `id` del curso tiene que ser único en la academia**: la academia no instala un curso cuyo `id` ya usa otro curso instalado. Quien cree un curso por su cuenta conviene que elija un `id` que no se confunda con los oficiales (por ejemplo, `ana-fotografia` mejor que `fotografia`).
- **Cómo se eligen la primera vez:** del nombre del fichero sin número para los módulos (`04-polimorfismo.md` → `java.polimorfismo`) y del título para los ejercicios (`Las tarifas del parking` → `java.polimorfismo.las-tarifas-del-parking`), en minúsculas, sin tildes y con guiones. Las herramientas del kit los proponen así. Después ya no cambian aunque cambie el fichero o el título.

## 4. Ficheros especiales

- **`README.md`**: portada del curso. Qué es, a quién va dirigido, qué conviene saber antes, cómo usarlo (en orden o por libre), versiones de las herramientas, requisitos de software y licencia.
- **`LICENSE`**, **`CONTRIBUTING.md`** y **`CHANGELOG.md`**: obligatorios (apartados 11 y 12).
- **`00-indice.md`**: el índice completo, con un encabezado `## Fase NN — Título` por fase y enlaces a todos los módulos, con su nivel y su tiempo. Se genera desde `curso.json`; no se edita a mano.
- **`99-chuleta-global.md`**: la sección «Chuleta» de todos los módulos, reunida. Se genera.
- **`ROADMAP.md`** (conviene) y **`RUTA-MINIMA.md`** (opcional): la ruta de aprendizaje del propio curso y, si la hay, la ruta mínima. `RUTA-MINIMA.md` se genera desde `ruta_minima` de `curso.json` (apartado 3.2) con `generar_ruta_minima.py` del kit; no se edita a mano. Si `curso.json` tiene `ruta_minima` y falta `RUTA-MINIMA.md`, la comprobación avisa.

## 5. El módulo

### 5.1. Plantilla

Todos los módulos siguen **exactamente** esta estructura, para que el lector sepa siempre dónde buscar y la academia pueda leerlos:

```markdown
# 03.04 Polimorfismo

> **Versiones:** Java 25
> **Conviene saber antes:** [03.03 Herencia](03-herencia.md)
> **Tiempo estimado:** 5 horas
> **Nivel:** Intermedio · Núcleo

## Qué aprenderás

## 1. Teoría

## 2. Ejemplos de código

## 3. Errores típicos

## 4. Buenas prácticas

## 5. Ejercicios prácticos resueltos

## 6. Chuleta

## 7. Preguntas de repaso

---
⬅️ [Anterior: …](…) · 📚 [Índice](../00-indice.md) · ➡️ [Siguiente: …](…)
```

- El **título** es `# NN.NN Título`, con el mismo título que `curso.json`. El número es solo para orientarse.
- Las secciones van **en este orden y con estos nombres exactos**.
- **Se numeran** los subapartados de Teoría, Ejemplos de código, Errores típicos y Buenas prácticas, con el número de su sección: `### 1.1.`, `### 2.3.`…
- **No se numeran** los de Qué aprenderás, Ejercicios prácticos resueltos (se agrupan por niveles: `### 🟢 Básico`…, apartado 5.4), Chuleta (es de consulta rápida, no se lee en orden) y Preguntas de repaso.

### 5.2. Cabecera

Las líneas de la cita del principio son los **datos del módulo** que lee la academia:

| Línea | Obligatoria | Qué lleva |
|---|---|---|
| `**Versiones:**` | No | Las versiones de las herramientas que usa el módulo, si aplican. |
| `**Conviene saber antes:**` | Sí | Enlaces a los módulos que se recomienda haber estudiado, de este curso o de otro (apartado 10.2), separados por ` · `, sin más texto. Para precisar una sección, se enlaza a ella con su ancla: `[00.01 Qué es programar, 1.7](01-que-es-programar.md#17-el-bytecode)`. Si no hace falta nada, `Nada`. Son recomendaciones: nada se bloquea. |
| `**Tiempo estimado:**` | Sí | Horas de estudio, incluidos los ejercicios: `5 horas`, `1 hora`, `1,5 horas`. |
| `**Nivel:**` | Sí | `Básico`, `Intermedio` o `Avanzado`, seguido de ` · ` y `Núcleo` (imprescindible) o `Ampliación` (para profundizar más adelante). |

### 5.3. «Qué aprenderás»

Lista de objetivos concretos del módulo. Es lo primero que ve quien entra suelto a un módulo: con esto y con «Conviene saber antes» decide si el módulo es para él.

### 5.4. «Ejercicios prácticos resueltos»

```markdown
## 5. Ejercicios prácticos resueltos

### 🟢 Básico

#### Ejercicio 1 · Las tarifas del parking

Enunciado…

<details>
<summary>Pista 1</summary>

…

</details>

<details>
<summary>Ver solución</summary>

Razonamiento, código, salida y explicación…

</details>
```

- Los ejercicios se agrupan en cuatro niveles, en este orden y con estos encabezados: `### 🟢 Básico`, `### 🟡 Intermedio`, `### 🔴 Avanzado` y `### 🏆 Caso real`.
- Cada ejercicio es `#### Ejercicio N · Título`. El **título** (lo que sigue a «Ejercicio N · ») debe coincidir **exactamente** con el `titulo` de ese ejercicio en `curso.json`, y en el mismo orden. Es texto plano, sin formato Markdown (apartado 3.2). N es solo la posición: no identifica al ejercicio.
- **Pistas** (conviene): cero, una o varias, cada una en su `<details>` con `<summary>Pista N</summary>`, **antes** de la solución.
- **Solución** (obligatoria): un `<details>` con `<summary>Ver solución</summary>`, **después** de las pistas. Completa, comentada y explicada.
- Deja una línea en blanco después de `<summary>…</summary>` y antes de `</details>`, para que el Markdown de dentro se vea bien en GitHub.

### 5.5. «Preguntas de repaso»

```markdown
## 7. Preguntas de repaso

1. ¿Qué diferencia hay entre el tipo de la variable y el tipo del objeto?

   <details>
   <summary>Ver respuesta</summary>

   El tipo de la variable decide qué métodos se pueden llamar… Lo tienes en [1.2. El tipo de la variable y el tipo del objeto](#12-el-tipo-de-la-variable-y-el-tipo-del-objeto).

   </details>

2. …
```

- Una lista numerada de preguntas de autoevaluación, cada una con su respuesta en `<details>` con `<summary>Ver respuesta</summary>`.
- Conviene que cada respuesta **enlace al apartado del módulo** donde se explica.
- Sin nota ni seguimiento: son para que el alumno compruebe si lo ha entendido.
- **Obligatorias** en los cursos nuevos. En los cursos que ya estaban escritos antes de este formato (el de Java), la comprobación **solo avisa** mientras se añaden poco a poco, si el curso lo declara en el campo `transicion` de `curso.json`.

## 6. Los retos de cada fase

Al final de cada fase, un fichero **`retos.md`** con retos **opcionales** para afianzar lo aprendido. Mezclan lo de varios módulos de la fase. **No tienen seguimiento** (la academia no guarda si se han hecho) y **no bloquean nada**.

```markdown
# Retos de la fase 03 — Programación orientada a objetos

> **Conviene saber antes:** los módulos de la fase.
> **Tiempo estimado:** 4 horas

Introducción: qué se practica y cómo abordarlos…

## Reto 1 · El inventario de una ferretería

Enunciado…

<details>
<summary>Pista 1</summary>

…

</details>

<details>
<summary>Ver solución</summary>

…

</details>
```

- El fichero se llama siempre `retos.md` (queda el último de la fase al ordenar) y su ruta se declara en `curso.json`, en el campo `retos` de la fase.
- Cada reto es `## Reto N · Título`, con el título en texto plano (apartado 3.2) y con pistas y solución como los ejercicios (apartado 5.4).
- Su código va en `codigo/retos/reto-NN-nombre/` de la fase y se verifica como el resto.
- No es un módulo: no tiene identificador ni aparece en `modulos`. La academia lo muestra al final de su fase como extra opcional.
- Conviene que **cada fase tenga sus retos**; la comprobación avisa si faltan o si siguen con `"retos_disponibles": false`. **Excepción:** una fase cuyo único módulo es el proyecto final (`"proyecto": {"tipo": "modulo"}`) no necesita retos, porque el proyecto ya lo es; si no los tiene, no se avisa.

## 7. El código

- Cada fase tiene una carpeta `codigo/` con una subcarpeta por módulo, con el **mismo nombre que su fichero** sin `.md`. Dentro, `ejemplos/` y `ejercicios/`.
- **Una carpeta por ejemplo o solución**, nombrada con el número de su apartado y una descripción: `ejemplos/2.1-upcasting/`, `ejercicios/ej02-tarifas-parking/`.
- Solo llevan carpeta los programas **completos**; los fragmentos se quedan en el texto.
- En el módulo, debajo de cada programa completo, el enlace a su carpeta:
  `📁 **Código:** [`codigo/04-polimorfismo/ejemplos/2.1-upcasting/`](codigo/04-polimorfismo/ejemplos/2.1-upcasting/)`
- El bloque del módulo y el fichero de `codigo/` deben ser **idénticos**.
- **Nombres reservados** junto a la solución de cada ejercicio, para la corrección automática futura: `partida/` (código de partida que se da al alumno) y `pruebas/` (pruebas que comprueban su solución). Hoy no los usa nadie, pero no se pueden usar para otra cosa.
- La academia ofrece cada carpeta enlazada como descarga en ZIP.
- **Proyectos de Maven y Gradle** (revisión 1.1, decisión del autor del 23 de noviembre de 2026): cuando el destino de un enlace «📁 Código» está dentro de un proyecto de Maven o Gradle, el ZIP que entrega la academia es el del **proyecto entero**, no el de la carpeta enlazada. El proyecto es el **más exterior dentro de `codigo/`**: la carpeta del `pom.xml` sin otro `pom.xml` por encima, o la carpeta con `settings.gradle` o `settings.gradle.kts`; si en la misma ruta hay de los dos tipos, el más exterior de todos. **Un proyecto de Gradle sin `settings.gradle` ni `settings.gradle.kts`** en la ruta (Gradle lo construye como un proyecto de un solo módulo; comprobado con Gradle 9.8.2 el 24 de noviembre de 2026) es la carpeta de su `build.gradle` o `build.gradle.kts` más exterior, y cuenta igual para el más exterior de todos; si en la ruta hay algún `settings.gradle*`, los `build.gradle*` no cuentan. Nunca se sale de `codigo/`, y `codigo/` misma no cuenta como proyecto. La `codigo/` que cuenta es **solo la que marca este formato**: la que cuelga directamente de una fase (`fase-NN-*/codigo/`) o de `proyecto/` (`proyecto/codigo/`); una carpeta llamada `codigo` más abajo (un paquete de Java, por ejemplo) es un nombre cualquiera y no corta la búsqueda. En un **multimódulo** (como `ej07-multimodulo` del módulo 01.05 del curso de Java), el ZIP es el de la raíz que agrupa a los módulos, aunque el enlace lleve a uno de ellos. El enlace sigue apuntando a la carpeta del fichero, para leerlo en GitHub, y su texto dice esa misma carpeta: si el texto y el destino son carpetas distintas, la comprobación avisa.
  - Ejemplo: `📁 **Código:** [`codigo/05-maven/ejercicios/ej07-multimodulo/bookshop-model/src/main/java/com/bookshop/model/`](codigo/05-maven/ejercicios/ej07-multimodulo/bookshop-model/src/main/java/com/bookshop/model/)` lleva al fichero en GitHub, y su ZIP es el de `codigo/05-maven/ejercicios/ej07-multimodulo/` entero.
  - Mezclados: con un `pom.xml` en `codigo/02-x/ejemplos/2.1-tienda/` y un `settings.gradle.kts` en `codigo/02-x/ejemplos/` (Maven dentro de Gradle), el ZIP es el de `ejemplos/`; al revés (Gradle dentro de Maven), el de la carpeta del `pom.xml`. El kit lo verifica igual: copia ese proyecto a la terminal, pero construye el programa con la herramienta de su módulo (su `pom.xml` o `build.gradle*` más cercano).
  - Sin settings: con `codigo/03-x/ejemplos/2.1-inventario/build.gradle.kts` y ningún `settings.gradle*` en la ruta, el ZIP es el de `2.1-inventario/`; si encima hay otro `build.gradle*` sin settings, el de esa carpeta, la más exterior.
  - Una academia 1.0.0 no lo aplica: da el ZIP de la carpeta enlazada.
- **Saltos de línea LF** en los ficheros de texto de `codigo/` (scripts y datos): con CRLF (los de Windows), bash falla (`$'\r': orden no encontrada`) y `grep`, `cut` o `read` ven un `\r` al final de cada línea. Conviene que el curso lleve en su raíz un `.gitattributes` con `* text=auto eol=lf`, como el de la plantilla del kit: así Git guarda LF y cualquier clon sale con LF, también en Windows con `core.autocrlf=true`. Un fichero con CRLF a propósito (para enseñar el error) se marca con `-text` en `.gitattributes`.
- **Lo que no viaja con Git:** un clon del curso (y la academia, que instala desde un commit) solo recibe lo que guarda Git. **Carpetas vacías**, no: si un ejemplo necesita una, conviene crearla dentro de la sesión (`mkdir`); un `.gitkeep` dentro también vale, pero `ls -a`, `find` y `du` lo muestran y un `rmdir` de esa carpeta fallaría. **Permisos**, solo si un fichero es ejecutable o no: un script que una sesión lanza con `./` debe estar guardado como ejecutable (`git update-index --chmod=+x`), salvo que la sesión haga su `chmod`; y cualquier otro permiso (un fichero de solo lectura) se pone con `chmod` dentro de la sesión.
- **Carpetas ocultas** (las que empiezan por punto), como `.github/`: van en la carpeta del ejemplo como cualquier otra, salvo `.git`, que nunca va en `codigo/` (los repositorios se crean dentro de la sesión); la terminal del kit las copia y el kit las comprueba. Un `.md` que empieza por una **cabecera YAML entre `---`** (como una plantilla de *issue* de GitHub en `.github/ISSUE_TEMPLATE/`) debe cerrarla con otra `---`, y la cabecera debe ser YAML válido con claves y valores; el resto se comprueba como Markdown. Una carpeta `.git` (o un submódulo) dentro de `codigo/` es un error: Git no guarda su contenido, así que no llega a un clon ni a la academia.
- **Ficheros `.env`:** en `codigo/`, solo **`.env.example`** (así, en minúsculas), con valores de ejemplo que se vean falsos (`cambia-esto`, `escribe-aqui-la-clave`, vacío…). La academia lo admite y **excluye cualquier otro** `.env` (`.env`, `.env.local`, `.env.production`…), así que un `.env` real en `codigo/` es un error: además de no llegar al alumno, puede llevar secretos. Si un ejemplo necesita el `.env`, se crea en la sesión (`cp .env.example .env`). Un valor de `.env.example` con pinta de secreto real (una clave de un servicio conocido, una clave privada, un JWT, una contraseña dentro de una URL, o una clave larga y aleatoria en una variable de secretos) da un aviso.
- **Sin `export-ignore`** en `.gitattributes` para nada de `codigo/`: `git archive` lo deja fuera, y la verificación de un commit (`verificar_codigo.py --commit`) ya no sería igual que un clon.

### 7.1. Ficheros de verificación y salidas en el texto

Le dicen al kit cómo comprobar un ejemplo o una solución. Salen del curso de Java original: los generales, en la primera tabla, y los propios de Java, en la segunda. Los de otros lenguajes y servicios de ese curso (bases de datos, páginas, modelos de IA) se añadirán cuando un curso los pida.

- **Los usa el kit para verificar**; la academia los trata como cualquier otro fichero de la carpeta.
- **Van también en el ZIP que descarga el alumno**, así que su texto debe entenderse sin el kit, y el `README.md` del curso explica en una línea qué son.
- **Un bloque del módulo puede enseñar un fichero de verificación** (revisión 1.1), como las peticiones de un `peticiones.txt` o lo que se teclea en un `entrada.txt`: el kit compara el bloque con él como con cualquier otro fichero de la carpeta (deben ser idénticos), pero no lo ejecuta. Como va en el ZIP, lo que el alumno ve en ese bloque también lo puede descargar.
- Solo se verifican los programas **completos** (los que tienen carpeta); los fragmentos que se quedan en el texto, no.

| Fichero, en la carpeta del ejemplo o la solución | Para qué |
|---|---|
| `entrada.txt` | Lo que se teclea: se pasa como entrada estándar al programa o al script. |
| `args.txt` | Los argumentos, en una línea, con comillas como en la terminal. |
| `termina-con-error.txt` | El programa o el script termina **a propósito** con un error (un código distinto de 0). Dentro, una línea que dice por qué. |
| `debe-fallar.txt` | El fichero de datos está mal **a propósito** (un JSON con una coma de más, un YAML mal sangrado…): el kit comprueba que falla, en vez de darlo por malo. Dentro, una línea que dice qué error tiene. Las imágenes SVG de la carpeta no cuentan: tienen que ser válidas siempre. |
| `separador.txt` | El separador de los CSV de la carpeta, en una sola línea (`;`, `\|` o la palabra `tabulador`). Si no está, la coma. Un `.tsv` va siempre con tabulador. |
| `codificacion.txt` | La codificación de los CSV de la carpeta cuando no están en UTF-8 a propósito (como los que exporta un programa antiguo), en una sola línea y con el nombre que entiende `iconv`: `WINDOWS-1252`, `ISO-8859-15`… El kit convierte el CSV desde esa codificación y lo comprueba como cualquier otro. Sin él, los CSV deben estar en UTF-8 **sin BOM** (un BOM es un error). |
| `servidor.json` | Las respuestas del **servidor HTTP local** al que pregunta `curl` en las sesiones y los scripts de la carpeta (ver «Peticiones HTTP» más abajo). |
| `salida-variable.txt` | Lo que cambia en cada ejecución (fechas, identificadores de commit, tiempos): una expresión regular de Python por línea (las vacías y las que empiezan por `#` no cuentan). Antes de comparar, lo que encaja se sustituye por `…` en la salida real y en la del texto, y el texto avisa de que la del alumno será distinta en esas partes. |
| `sesion.txt` (o `sesion-<nombre>.txt`) | Las órdenes de una sesión de terminal, una por línea, como se teclean; las líneas vacías y las que empiezan por `#` no se teclean. Cada una empieza desde cero, con los ficheros de la carpeta. |
| `sesion-1.txt`, `sesion-2.txt`… | **Sesiones encadenadas**: las de un ejemplo que el alumno hace una detrás de otra. Se teclean en ese orden en la misma terminal: cada una encuentra los ficheros (y los commits) como los dejó la anterior, pero arranca en una terminal nueva, en la carpeta del ejemplo, sin la carpeta actual ni las variables de la anterior (el alumno puede cerrarla entre una y otra; si una sesión necesita un `cd`, lo hace ella). Van de la 1 en adelante, sin saltos ni ceros delante, y conviven con las sueltas de la misma carpeta. |

**Los de Java** (desde la revisión 1.1). Son los del curso de Java original y los comprueba el ejecutor de Java del kit, desde el kit 1.1.0. En ellos también valen `entrada.txt`, `args.txt`, `termina-con-error.txt` y `salida-variable.txt` de la tabla anterior; `entrada.txt` y `args.txt` pueden ir también en la raíz de su módulo, y en un proyecto Maven, `salida-variable.txt`, junto al `pom.xml` (vale también para su «**Salida de las pruebas:**»; si hay uno en la carpeta del fichero, manda ese).

| Fichero | Para qué |
|---|---|
| `opciones-java.txt` | Opciones de la JVM para ejecutar el programa, en una línea y separadas por espacios, como en la terminal (`--enable-preview --source 25`, `--enable-native-access=ALL-UNNAMED`). Junto al programa o en la raíz de su módulo. |
| `solo-compilar.txt` | El programa **solo se compila**, no se ejecuta (una ventana que no se puede abrir sin pantalla, como un `JOptionPane`). Dentro, por qué. En un proyecto Maven va junto al `pom.xml` (en uno de Gradle, junto a su `build.gradle.kts` o `build.gradle`): el proyecto se construye (pruebas incluidas) y sus programas no se ejecutan (una aplicación de Spring Boot que se queda escuchando). Si el texto empieza por «Sin pruebas:» (revisión 1.1; por ejemplo, «Sin pruebas: su prueba usa Testcontainers, que necesita Docker»), el proyecto entero se construye **sin ejecutar sus pruebas**, aunque sí se compilan (`mvn package -DskipTests`; con Gradle, `gradle build testClasses -x test`). |
| `peticiones.txt` | Junto al `pom.xml` de una aplicación de **Spring Boot**: las órdenes `curl` a `http://localhost:8080`, una por línea (las que empiezan por `#` son comentarios). El kit arranca la aplicación en un puerto libre, lanza las órdenes con ese puerto, la para y compara la sesión con el bloque «**Con la aplicación arrancada:**», viendo el puerto como 8080, sin la cabecera `Date` ni las fechas y horas ISO. Sin ese bloque, la aplicación solo se construye. |
| `servidor.txt` | Los programas de Java que se arrancan antes y se paran al terminar, uno por línea y en orden: junto a un `pom.xml` con `peticiones.txt`, las **API simuladas** que usa la aplicación (`../api-externa/ApiDelTiempo.java`; tras la ruta de un proyecto de Spring Boot, sus opciones, como `--server.port=8082`); en la carpeta de una página que usa `fetch`, el servidor que la sirve, que solo se compila. Cada uno escribe en su primera línea «Escuchando en http://localhost:PUERTO/». El puerto de un proyecto de Spring Boot (`--server.port=` o `server.port=` de su `application*.properties`) es un número o `${VARIABLE:número}` (revisión 1.1). |
| `acciones.txt` | **JavaFX**: lo que se hace en la ventana antes de la captura, una acción por línea (`escribir #id texto`, `pulsar #id`, `elegir #id n`, `responder Texto`, `esperar ms`), siempre en la ventana de delante, también en un diálogo. |

**Conversiones.** Si una carpeta tiene ficheros de datos con el mismo nombre, el kit comprueba que dicen lo mismo:

- Un `.json` y un `.yaml`: deben cargar los mismos datos.
- Un `.csv` (o `.tsv`) y un `.json` (si no hay `.json`, no se compara):
  - El JSON es una **lista** en el nivel superior, con **un objeto por fila de datos** del CSV (la primera fila es la cabecera), **en el mismo orden**. El orden de las claves dentro de cada objeto no importa.
  - Cada objeto tiene **exactamente las claves de la cabecera** (ni una más ni una menos), y la cabecera no repite nombres.
  - Cada campo del CSV se compara según el tipo de su valor en el JSON: un **texto**, igual letra a letra, aunque parezca un número (`"08012"`); un **número**, el campo escrito como `-?(0|[1-9][0-9]*)(\.[0-9]+)?` y con el mismo valor (`12.50` es `12.5`; `08012` o `12,50` como número son un error); un **booleano**, `sí` o `true` para `true`, y `no` o `false` para `false`, exactamente así, en minúscula; **`null`**, el campo vacío (y un campo vacío solo vale como `null`, no como `""`); una **lista** o un **objeto**, error (un CSV no los tiene).
  - Cada error dice la línea del CSV, la fila y la clave.

**Peticiones HTTP (`curl`).** Nunca a internet: el kit verifica sin red. Si la carpeta de una sesión o un script tiene un `servidor.json`, el kit arranca antes un servidor HTTP en `localhost` que responde lo que dice ese fichero, y lo para después (para unas sesiones encadenadas, uno para toda la serie). El servidor no sabe nada de ninguna API: cada ejemplo describe la suya, en JSON:

```json
{
  "puerto": 8080,
  "rutas": [
    {"metodo": "GET", "ruta": "/libros/1", "estado": 200, "cuerpo": {"id": 1, "titulo": "Niebla"}},
    {"metodo": "POST", "ruta": "/libros", "estado": 201, "cabeceras": {"Location": "/libros/2"}, "cuerpo": {"id": 2}},
    {"metodo": "GET", "ruta": "/estado", "estado": 200, "cuerpo": "Todo en orden\n"}
  ]
}
```

- `"puerto"`: opcional; si no está, 8080 (entre 1024 y 65535). Escucha en `localhost` (`127.0.0.1` y `::1`).
- `"rutas"`: una o más, sin repetir el mismo método con la misma ruta. Cada una con:
  - `"metodo"`: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD` u `OPTIONS`, en mayúsculas.
  - `"ruta"`: empieza por `/`. Sin `?`, vale con cualquier consulta (`/libros` y `/libros?autor=x`); con `?`, solo con esa consulta exacta, y va antes que la que no la lleva.
  - `"estado"`: un código de estado de HTTP (200, 201, 404…).
  - `"cabeceras"` (opcional): nombre y valor, como texto; salen en ese orden. `Content-Length` no: la pone el servidor.
  - `"cuerpo"` (opcional): un **texto** se envía tal cual (con `Content-Type: text/plain; charset=utf-8` si las cabeceras no dicen otro); **cualquier otro valor** se envía como JSON con sangría de 2 espacios y un salto de línea al final (con `Content-Type: application/json` si no dicen otro). Sin cuerpo, la respuesta va vacía.
- **Lo que responde, siempre igual:** `HTTP/1.1` con su línea de estado (`HTTP/1.1 404 Not Found`), las cabeceras de la ruta, `Content-Type` si hay cuerpo y `Content-Length`. Nada más: ni `Date` ni `Server`, que cambiarían en cada ejecución o con la versión del kit (si un módulo quiere enseñarlas, las pone en `"cabeceras"` con un valor fijo). `HEAD` responde como `GET`, sin cuerpo. Una ruta que no existe da `404` con `{"error": "No existe la ruta /x"}`, y una que existe con otro método, `405` con la cabecera `Allow` y `{"error": "La ruta /x no admite PUT"}`. Lo que envía la petición (`curl -d`) se lee y no se usa: las respuestas son fijas, y un `POST` no guarda nada.
- El kit comprueba el `servidor.json` de cada carpeta enlazada (cada error, con su línea), aunque ninguna sesión lo use. **No se copia a la terminal** (un `ls` no lo enseña, como los `sesion*.txt`), pero va en el ZIP del alumno, que **no tiene ese servidor**: el módulo dice qué hacer en su equipo.
- **Para que la pantalla no cambie** con la versión de `curl` (la terminal del kit trae la de Ubuntu 26.04, la 8.18.0 a 16 de noviembre de 2026; Git Bash y macOS traen la suya): `-i` para ver la línea de estado y las cabeceras, `-s` para quitar la barra de progreso (sale con tiempos en cuanto la respuesta va a un fichero, con `-o`, o a una tubería) y `-w` para escoger lo que se ve (`-w '%{http_code}\n'`). **`-v` no** en una sesión verificada: lo que escribe cambia de una versión a otra (enséñalo como fragmento, sin verificar). Un cuerpo de texto debe terminar en salto de línea: si no, el indicador `$ ` sale pegado a él.
- El puerto del servidor está ocupado mientras dura la sesión: no lo uses para otra cosa en una sesión verificada.

Lo que se compara se escribe en el módulo **justo después del programa y de su enlace «📁 Código»**, con estas líneas exactas, cada una seguida de un bloque ` ```text `:

| En el texto | Qué es |
|---|---|
| `**Salida:**` | La salida estándar real del programa o del script. |
| `**Salida de error:**` | Su salida de error, en los que llevan `termina-con-error.txt`. |
| ``**En tu terminal** (`sesion.txt`):`` | La pantalla de la sesión: cada orden de `sesion.txt` tecleada tras el indicador `$ ` en una carpeta con los ficheros de la del ejemplo (sin los `sesion*.txt`, que son del kit), y lo que contesta. Una sesión encadenada, con su nombre: ``**En tu terminal** (`sesion-2.txt`):``. |

En los cursos de Java (desde la revisión 1.1), además:

| En el texto | Qué es |
|---|---|
| `**Sesión en la terminal:**` | En lugar de «**Salida:**», la pantalla de un programa que lee del teclado: lo que escribe y cada línea de `entrada.txt`, como si la tecleara el alumno. |
| `**Salida de las pruebas:**` | Tras una clase de pruebas de un proyecto Maven: el resumen de las pruebas, sin los tiempos ni las trazas. |
| `**Con la aplicación arrancada:**` | Tras la clase principal de una aplicación de Spring Boot con `peticiones.txt`: cada orden con `$ ` y su respuesta. |
| `**La ventana:**` | Tras el programa de JavaFX o Swing (y su «**Salida:**», si la hay), una imagen `![…](….png)` (no un bloque ` ```text `): la ventana dibujada sin pantalla (después de las acciones de `acciones.txt`, si las hay), idéntica byte a byte. |

## 8. El proyecto para el portfolio del alumno

Todo curso **debe** tener un proyecto con el que el alumno termine teniendo algo que enseñar, aunque sea pequeño. Se declara en `curso.json`, en el campo `proyecto`, de una de estas dos formas:

- **Por etapas** (`"tipo": "etapas"`): un proyecto que crece a lo largo del curso, en la carpeta `proyecto/`, con un fichero por etapa y su código en `proyecto/codigo/`. Cada etapa tiene su `id`, su `fichero` y su `titulo`. Las etapas no son módulos: la academia las muestra en su propia sección, con su propio seguimiento.
- **Como un módulo final** (`"tipo": "modulo"`, con `"modulo": "inicial.primer-repositorio"`): un módulo del curso que es el proyecto. Es el caso del curso inicial.

## 9. El glosario

- **El glosario común** es el `glosario.md` de la raíz del **curso inicial**: los términos que comparten todos los cursos se definen allí una vez, y los demás cursos enlazan a esa definición en vez de volver a explicarla.
- **Cualquier curso puede tener además su propio `glosario.md`**, en su raíz, con los términos que son solo suyos (el de Java, los de Java). No repite los del glosario común: enlaza a ellos.
- En los dos, un encabezado `## Letra` por letra y un `### Término` por término, en orden alfabético (la ñ, entre la n y la o), y cada término una sola vez.
- Para enlazar a un término desde otro curso se usa un enlace entre cursos (apartado 10.2): `https://github.com/myopenacademy/curso-inicial/blob/main/glosario.md#api`.

## 10. Enlaces, imágenes y diagramas

### 10.1. Dentro del mismo curso

- Enlaces **relativos**, para que funcionen en cualquier editor y en GitHub: `[03.03 Herencia](03-herencia.md)`, `[el índice](../00-indice.md)`, `[1.2](#12-el-tipo-de-la-variable-y-el-tipo-del-objeto)`.
- Las anclas son las que genera GitHub a partir del encabezado.
- Todo enlace debe llevar a un fichero o carpeta que exista y, si tiene ancla, a un encabezado que exista.

### 10.2. A otro curso

- Con la **dirección completa de GitHub** del fichero, en la rama `main`:
  `[Git: fundamentos](https://github.com/myopenacademy/curso-inicial/blob/main/fase-05-git-y-github/01-git-fundamentos.md#qué-es-un-commit)`
- **Funciona en GitHub tal cual.** El kit la traduce a la carpeta hermana del curso (`../curso-inicial/`) y comprueba que el fichero y el ancla existen. La academia la convierte en un enlace a la lección si ese curso está instalado; si no, deja el enlace a GitHub.
- Se puede enlazar a **cualquier curso**: hacia atrás (lo que conviene saber antes) y hacia delante (por ejemplo, el curso inicial dice qué curso enseña cada pieza de una aplicación). Si la carpeta hermana del curso enlazado no está en la máquina de quien escribe, la comprobación avisa de que no ha podido revisar ese enlace.

### 10.3. Imágenes

- Solo imágenes **PNG, JPG o SVG** guardadas en el propio curso (en la carpeta `img/` de la fase), con enlace relativo y **texto alternativo** que describa la imagen: `![Diagrama de la herencia de Empleado](img/herencia.svg)`.
- Nada de imágenes de otras webs ni incrustadas (`data:`).
- Los SVG, legibles con fondo claro y oscuro.

### 10.4. Diagramas Mermaid

- En bloques ` ```mermaid `, que GitHub y la academia dibujan.
- Sin negrita ni cursiva en las etiquetas, y solo las entidades `&quot;`, `&lt;`, `&gt;` y `&amp;`.
- Sin directivas, *frontmatter*, interacciones, imágenes ni estilos con `url()` o `@import`: la academia muestra esos diagramas como código.
- Conviene acompañar los diagramas importantes de una frase que diga lo mismo en texto, para quien no pueda verlos.

### 10.5. HTML

**Primero Markdown; HTML solo cuando Markdown no llega**: los `<details>` y `<summary>` que pide este formato, y lo que no se puede escribir en Markdown, como código dentro de un `<summary>` (`<summary>Ver <code>Employee</code></summary>`, porque ahí el Markdown no se interpreta), teclas (`<kbd>Ctrl</kbd>`) o un salto de línea dentro de una celda de tabla (`<br>`). Las tablas, la negrita, el tachado (`~~texto~~`), los enlaces y las imágenes se escriben en Markdown.

La academia trata el HTML así:

- **Se admite tal cual**, sin atributos: `details`, `summary`, `code`, `kbd`, `br`, `sup`, `sub`, `em`, `strong`, `del`, `p`, `blockquote`, `hr`, `pre`, los encabezados (`h1` a `h6`), las listas (`ul`, `ol`, `li`) y las tablas (`table`, `thead`, `tbody`, `tr`, `th`, `td`). Los únicos atributos admitidos son `align` en `th` y `td`, `start` en `ol` y `class="language-…"` en `code`. **`<details open>` no se admite**: las soluciones y las pistas empiezan siempre plegadas.
- **Formato sin efecto** (`span`, `div`, `u`, `b`, `i`, `s`, `mark`, `small`, `center`, `section`…) y enlaces escritos en HTML (`<a>`): la academia quita la etiqueta al instalar y deja su texto. Es un **aviso**.
- **Cualquier otra etiqueta** (scripts, marcos, estilos, formularios, imágenes escritas en HTML…) y **cualquier otro atributo** (manejadores de eventos como `onclick`, `style`, `id`, `open`…) **hacen fallar la instalación**: es un **error**.

### 10.6. Listas de tareas

Las listas de tareas de Markdown (`- [ ] Pendiente`, `- [x] Hecho`), que dibuja GitHub, **de momento no se admiten** fuera de los bloques de código: la academia todavía no las dibuja (se vería `[ ]` como texto). Es un **aviso**. Dentro de un bloque de código (para enseñar cómo se escriben) o en los `.md` de `codigo/` se pueden usar. Cuando la academia las dibuje, se quitará el aviso.

### 10.7. Correos

Las direcciones de correo, **siempre en código** (`` `Ana García <ana@example.com>` ``). Entre `<` y `>` fuera de código, CommonMark y GitHub las convierten en un enlace `mailto:`, que la academia no admite. También un correo suelto (`ana@example.com`): GitHub lo enlaza, aunque la academia lo deja como texto (una dirección de SSH como `git@github.com:usuario/repo.git` no cuenta, pero va en código igualmente). Tampoco se usan enlaces `[texto](mailto:…)`. Es un **aviso**. Los correos de ejemplo usan dominios reservados para documentación (`example.com`).

## 11. Versiones del curso

### 11.1. Versión y registro de cambios

- La `version` de `curso.json` sigue el esquema `MAYOR.MENOR.PARCHE`: tres números con cifras de `0` a `9` separados por puntos, sin ceros a la izquierda (salvo el propio `0`) y nada más, ni delante ni detrás (ni espacios, ni saltos de línea, ni `v`, ni `-beta`). Valen `1.0.0`, `0.9.0` y `1.10.0`; no valen `1.0`, `01.0.0`, `1.0.0-beta`, `v1.0.0` ni `1.0.0.0`. La misma forma tienen `academia_minima` (apartado 3.2) y el `desde` de las equivalencias (11.2). La expresión regular exacta es `^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$`, aplicada a todo el texto, sin admitir un salto de línea final (en Python, `re.fullmatch()`, como el kit; en Java, `String.matches()` o `Pattern.matcher(…).matches()`, no `find()`; en JavaScript, `test()` sin el modificador `m`), y solo con cifras ASCII (revisión 1.1; antes no se decía).
  - **PARCHE** (`2.0.1`): erratas y mejoras de texto o de código, sin cambiar la estructura.
  - **MENOR** (`2.1.0`): contenido nuevo (módulos, ejercicios, retos, etapas) sin quitar ni cambiar identificadores.
  - **MAYOR** (`3.0.0`): cambios de estructura con equivalencias, o una edición nueva del curso.
- Cada versión publicada se **etiqueta en Git** con su número (`v2.1.0`), y esa etiqueta es lo que se instala en la academia.
- `CHANGELOG.md` dice qué cambia en cada versión, de la más nueva a la más antigua.

### 11.2. Equivalencias

Cuando un identificador publicado deja de existir, `curso.json` dice qué fue de él, para que la academia traslade el progreso de los usuarios:

```json
"equivalencias": [
  { "desde": "2.0.0", "antes": "java.colecciones", "ahora": ["java.listas", "java.mapas"] },
  { "desde": "2.0.0", "antes": "java.applets", "ahora": [], "motivo": "Tecnología retirada" }
]
```

- **Dividir** un módulo: `ahora` lleva los nuevos. **Unir** varios: una entrada por cada uno, con el mismo destino. **Retirar**: `ahora` vacío y un `motivo`.
- Las equivalencias no se borran nunca: alguien puede actualizar desde una versión muy antigua.
- Cambiar el título, el fichero, la fase o el orden **no** necesita equivalencia: el identificador no cambia.

## 12. Licencias

Salvo que el curso diga otra cosa en su `LICENSE`, los cursos de MyOpenAcademy usan:

- **CC BY-SA 4.0** para el texto: cualquiera puede usarlo y adaptarlo citando la autoría, y lo que publique a partir de él lo comparte con la misma licencia.
- **MIT** para el código (`codigo/`, `proyecto/codigo/`).

## 13. Comprobación

La comprobación del kit (`formato_academia.py`) revisa que un curso cumple este formato **antes de instalarlo**. Cada error dice el fichero, la línea y qué falta (por ejemplo, «`fase-03-poo/04-polimorfismo.md:1165`: falta la solución del ejercicio 4»). Comprueba:

- `curso.json`: campos (también `ruta_minima` y los huecos de su plantilla, y que `academia_minima` sea `MAYOR.MENOR.PARCHE`), identificadores (forma, unicidad, que no desaparezca ninguno publicado sin equivalencia; para saberlo compara con la última versión etiquetada) y que cada fichero declarado existe (salvo el previsto de un módulo o unos retos no disponibles) y cada fichero de módulo está declarado.
- Títulos en texto plano: los del curso, las fases, los módulos, los ejercicios y los retos (apartado 3.2).
- Cada módulo: título, cabecera, secciones en orden, ejercicios con sus títulos iguales a `curso.json`, solución de cada ejercicio, preguntas de repaso.
- Retos, etapas, glosario y proyecto.
- Enlaces del mismo curso y entre cursos (con sus anclas), imágenes, diagramas y HTML.
- Que el texto de cada «📁 **Código:**» y su destino sean la misma carpeta (apartado 7), con un aviso.
- Listas de tareas fuera de los bloques de código (apartado 10.6), con un aviso.
- Correos fuera del código (entre `<` y `>` o sueltos) y enlaces `mailto:` (apartado 10.7), con un aviso.
- Ficheros obligatorios.
- Lo de `codigo/` que no viaja con Git (apartado 7), con avisos: un fichero de texto con CRLF en lo que guarda Git (o en el disco, si el curso no está en Git) o que no saldría con LF en un clon; carpetas vacías; scripts que una sesión lanza con `./` sin permiso de ejecución en Git; y permisos del disco que un clon no tendría.
- Un repositorio de Git dentro de `codigo/` (una carpeta `.git` o un submódulo), con un error (apartado 7).
- Los `.env` de `codigo/` (apartado 7): un `.env` real (cualquiera salvo `.env.example`) que Git guarda es un error, y uno que Git ignora, un aviso; en `.env.example`, un aviso por cada valor con pinta de secreto real, con la línea y la variable (nunca el valor).

El código lo comprueba otra herramienta del kit, `verificar_codigo.py`. Para cerrar una fase o publicar una versión, se verifica **el commit, como lo recibe el alumno** (`verificar_codigo.py --commit`, o `--commit v1.0.0` para una etiqueta), no el disco de quien escribe.

**Errores** (no se instala) frente a **avisos** (se instala, pero conviene corregirlo): lo que este documento dice con «debe» es un error, y lo que dice con «conviene», un aviso.

## 14. Lo que vive en la academia, no en los cursos

Para que los cursos no dependan unos de otros, algunas cosas son de la academia:

- **Roadmaps entre cursos** (por ejemplo, «Backend con Java: inicial → Java → SQL → Git a fondo»): ficheros de datos en el repositorio de la academia, que nombran cursos, partes, fases o módulos por su identificador. Los roadmaps de dentro de un curso siguen en el curso (`ROADMAP.md`).
- **La lista de cursos instalados** y su versión.

**Los cursos de ejemplo**, en cambio, viven en **el kit**, que es quien los comprueba (`herramientas/pruebas/cursos/`): `bueno`, un curso pequeño que cumple este formato y sirve de modelo para crear uno nuevo, y `ejemplo-destino`, al que enlaza `bueno` como a otro curso (con su propio glosario y un proyecto de tipo `"modulo"`). La academia guarda una copia sacada de un commit fijo del kit para sus pruebas y su demo, y la renueva cuando hace falta.

## 15. Cambiar este formato

- Se cambia **solo desde el proyecto del kit** (`Cursos/kit-cursos/`), nunca desde un curso ni desde la academia por su cuenta.
- **Un cambio incompatible sube la versión del formato** (el campo `formato`): uno con el que la academia ya no podría instalar un curso o lo entendería mal. Se anota qué cursos hay que poner al día y la academia sigue sabiendo leer las versiones anteriores.
- **Una ampliación compatible es una revisión** (1.1, 1.2…): un campo nuevo opcional o un fichero de verificación nuevo. Los cursos siguen con `"formato": 1` y la revisión se apunta en el registro de cambios de abajo. La academia ignora los campos que no conoce (comprobado con la academia 1.0.0 el 23 de noviembre de 2026), así que un curso que usa una revisión se sigue instalando en una academia anterior.
- **Registro de cambios** (de la más nueva a la más antigua):
  - Revisión 1.1 (kit 1.1.0, 23 y 24 de noviembre de 2026): campos opcionales `ruta_minima` y `academia_minima` de `curso.json` (la academia rechaza un curso que pide una versión mayor que la suya; la 1.0.0 lo ignora) (apartados 3.2 y 13), la forma exacta de `MAYOR.MENOR.PARCHE` (sin ceros a la izquierda, solo cifras ASCII y nada más; apartado 11.1), ficheros de verificación de Java (con «Sin pruebas:» al principio de un `solo-compilar.txt` de un proyecto, se construye sin ejecutar sus pruebas; y el `salida-variable.txt` del `pom.xml` vale también para la «**Salida de las pruebas:**»), y un bloque puede enseñar un fichero de verificación, que el kit compara como cualquier otro y va en el ZIP (apartado 7.1); el ZIP de un enlace «📁 Código» dentro de un proyecto de Maven o Gradle es el del proyecto más exterior dentro de `codigo/` (un Gradle sin `settings.gradle*`, la carpeta de su `build.gradle*` más exterior), y el texto y el destino del enlace, la misma carpeta (apartados 7 y 13; una academia 1.0.0 da el ZIP de la carpeta enlazada); y las partes, cada una un tramo de fases seguidas y en orden, sin partes vacías (apartado 3.2; ningún curso publicado tenía partes, y la academia las comprobará igual al instalar).
- **Las versiones cuentan desde la primera publicación.** Hasta que se publique el primer curso, los ajustes se hacen dentro de la versión 1 y se anotan aquí:
  - 8 de noviembre de 2026: un módulo con `"disponible": false` puede llevar su `fichero` previsto, y una fase sus `retos` previstos con `"retos_disponibles": false` (apartado 3.2); ficheros de verificación `debe-fallar.txt` y `separador.txt`, y después todos los del curso de Java con las salidas en el texto (apartado 7.1); títulos del curso, las fases, los módulos, los ejercicios y los retos en texto plano (apartado 3.2); una fase que solo contiene el proyecto final no necesita retos (apartado 6); qué subapartados se numeran (apartado 5.1); «Conviene saber antes», solo enlaces, con ancla para precisar la sección (apartado 5.2); el HTML que admite de verdad la academia, y `<details open>` no (apartado 10.5); 9 de noviembre de 2026: los cursos de ejemplo viven en el kit y la academia guarda una copia (apartado 14), y cualquier curso puede tener su propio glosario además del común del curso inicial (apartado 9); saltos de línea LF en `codigo/` y `.gitattributes` con `* text=auto eol=lf` (apartados 2, 7 y 13); lo que no viaja con Git (carpetas vacías y permisos), sin `export-ignore` en `codigo/`, y verificar el commit para cerrar una fase (apartados 7 y 13); sesiones encadenadas, `sesion-1.txt`, `sesion-2.txt`… (apartado 7.1); `codificacion.txt`, CSV en UTF-8 sin BOM, `.tsv` con tabulador y la comparación de un CSV con su JSON (apartado 7.1); listas de tareas, de momento no (apartado 10.6); 16 de noviembre de 2026: servidor HTTP local para `curl`, con las rutas de cada ejemplo en su `servidor.json` (apartado 7.1), y en `codigo/` solo `.env.example`, sin secretos reales (apartados 7 y 13); los correos, siempre en código y sin enlaces `mailto:` (apartados 10.7 y 13), y el ejemplo de «puerto en uso» sin Python (apartado 7.1); carpetas ocultas como `.github/` en `codigo/`, nunca `.git`, y la cabecera YAML entre `---` de un `.md` (apartados 7 y 13). **A poner al día:** el curso de Java, al adaptarlo, tiene 88 títulos de ejercicio con formato (comillas invertidas o cursiva).
- **La versión 1 se cierra al publicar el kit** (versión 1.0.0, con el pack base 1.0). Desde entonces, cada cambio de este formato sube su versión o, si es compatible, su revisión (arriba).
- Si un curso necesita algo nuevo, primero se amplía la academia y este formato, y después lo usa el curso.
