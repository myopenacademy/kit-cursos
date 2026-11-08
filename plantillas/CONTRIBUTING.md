# Cómo contribuir a [RELLENAR: título del curso]

Gracias por querer mejorar el curso. Toda ayuda cuenta: una errata, una explicación más clara, un ejemplo mejor o un ejercicio nuevo.

## Antes de empezar

- El curso cumple el **[formato de los cursos de MyOpenAcademy](https://github.com/myopenacademy/kit-cursos/blob/main/FORMATO.md)**. Léelo antes de proponer cambios de estructura.
- Escribe en **español de España**, tuteando, para alguien que empieza desde cero en el tema.

## Cómo proponer un cambio

1. **Erratas y mejoras pequeñas:** abre directamente una *pull request*.
2. **Cambios grandes** (un módulo nuevo, dividir o mover módulos, cambiar el temario): abre antes una *issue* para hablarlo.
3. En la *pull request*, explica qué cambias y por qué.

## Lo que se comprueba

- **El formato:** desde la raíz del curso, con el kit en la carpeta hermana `../kit-cursos/`:

  ```bash
  python3 ../kit-cursos/herramientas/formato_academia.py
  ```

- **El código:** todo programa del texto está en `codigo/`, es idéntico al del módulo y se ha ejecutado de verdad, con su salida real.
- **Las versiones** y los datos que caducan se comprueban en la documentación oficial y se fechan en el texto.

## Reglas que no se pueden saltar

- **No cambies los identificadores de `curso.json`**: el progreso de los alumnos va unido a ellos. Cambiar un título se hace en su `titulo`, conservando el `id`.
- **Títulos en texto plano**, sin formato Markdown.
- Si renombras o mueves un fichero, actualiza su ruta en `curso.json` y los enlaces que apuntan a él (también los de otros cursos).

## Licencia de lo que aportes

Al contribuir aceptas que tu aportación se publique con las licencias del curso: CC BY-SA 4.0 para el texto y MIT para el código ([`LICENSE`](LICENSE)).
