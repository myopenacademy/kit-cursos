// Script de inicialización que usa lenguajes/java.py del kit (sale de herramientas/ del curso de Java): añade a cada
// proyecto Java una tarea que imprime su classpath de ejecución (clases compiladas, recursos y dependencias).
allprojects {
    plugins.withId("java") {
        tasks.register("printRuntimeClasspath") {
            val classpath = project.extensions.getByType<SourceSetContainer>()["main"].runtimeClasspath
            doLast {
                println(classpath.files.joinToString(File.pathSeparator))
            }
        }
    }
}
