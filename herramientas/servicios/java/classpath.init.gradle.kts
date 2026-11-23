// Script de inicialización que usa lenguajes/java.py del kit (sale de herramientas/ del curso de Java): añade a cada
// proyecto Java una tarea que imprime su classpath de ejecución (clases compiladas, recursos y dependencias).
// Del kit: con -PkitPreparar (solo en «verificar_codigo.py --preparar-java»), las pruebas que fallan no paran la
// construcción, como -Dmaven.test.failure.ignore=true en Maven: así se descarga todo lo que usan aunque fallen a
// propósito. Al verificar no se pasa, y Gradle se comporta como siempre.
allprojects {
    plugins.withId("java") {
        tasks.register("printRuntimeClasspath") {
            val classpath = project.extensions.getByType<SourceSetContainer>()["main"].runtimeClasspath
            doLast {
                println(classpath.files.joinToString(File.pathSeparator))
            }
        }
        if (project.hasProperty("kitPreparar")) {
            tasks.withType<Test>().configureEach {
                ignoreFailures = true
            }
        }
    }
}
