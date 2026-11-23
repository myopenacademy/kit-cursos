# La terminal de Java del kit: la terminal del kit (servicios/terminal/Dockerfile) con el JDK, Maven y Gradle, para
# verificar el código de los cursos de Java (lenguajes/java.py). Se construye encima de la imagen kit-terminal (su
# nombre llega en BASE), así que todo lo demás es idéntico: Ubuntu 26.04.1 fijado por su huella, español, hora de
# Madrid, coreutils de GNU, Git 2.56.0 con su reloj y la persona «alumno».
#
# Las versiones son las del autor, instaladas con SDKMAN (decisión del 23 de noviembre de 2026), con la huella
# oficial de cada descarga comprobada ese día en su fuente:
#   - Temurin 25.0.4.1+1 (SDKMAN: 25.0.4.1+1-tem), de Eclipse Adoptium (api.adoptium.net y el .sha256.txt de su
#     versión en github.com/adoptium/temurin25-binaries; los dos dicen lo mismo). x64 y aarch64.
#     La más reciente el 23 de noviembre de 2026: 25.0.5.1+2 en la 25 (LTS); 27.0.1.1+4 de la última versión.
#   - Maven 3.10.0, de Apache (archive.apache.org, con su SHA-512 publicado).
#     La más reciente el 23 de noviembre de 2026: 3.10.2 (la 4.0.0 sigue en candidata: 4.0.0-rc-7).
#   - Gradle 9.8.2, de gradle.org (services.gradle.org/distributions, con su SHA-256 publicado).
#     La más reciente el 23 de noviembre de 2026: 9.9.2.
#   - Las letras DejaVu (fonts-dejavu-core) y fontconfig, fijadas: las ventanas de Swing y JavaFX que se dibujan
#     sin pantalla usan esas letras, y con otras la imagen cambiaría. Y Pango (libpangoft2-1.0-0, con sus
#     dependencias): JavaFX coloca el texto con él en Linux, y sin él ninguna ventana con texto arranca.
#
# SIN RED al verificar: Maven y Gradle trabajan sin conexión (-o, --offline) contra la caché de /opt/kit-java/cache,
# un volumen de Docker que llena «verificar_codigo.py --preparar-java» (la única vez que hay red). Fuera de la
# carpeta personal: una sesión que hace «ls -a» ve lo mismo que el alumno, y el kit no toca la caché al poner las
# fechas y los permisos de los ficheros copiados.
#
# Si se cambia algo, se cambia también la tabla de versiones de herramientas/README.md.
ARG BASE
FROM ${BASE} AS descargar

ARG TEMURIN_VERSION=25.0.4.1+1
ARG TEMURIN_SHA256_AMD64=dbb698396d478e7fa2b1e50f4103324b2a99b90569ee27c33f2261f9215cf41e
ARG TEMURIN_SHA256_ARM64=69df11a02cfa3ef7d7ca645e03edce6778ec090e100f6ae2b42097865730ac52
ARG MAVEN_VERSION=3.10.0
ARG MAVEN_SHA512=908b1501bfb420bf7c8affb855534a9c407fd6099367bfb9f2f2dcb8e9799102bffb84518cde74c679bd76870247c6528683abdd620581bffa90f95d92d175aa
ARG GRADLE_VERSION=9.8.2
ARG GRADLE_SHA256=21bd5da2de49b642904077f38c0efdc7778e92b3ed0889392dca61b97e389607

USER root
WORKDIR /descargas
# El JDK de la arquitectura de la máquina (amd64 o arm64), con la huella de esa descarga
RUN case "$(dpkg --print-architecture)" in \
        amd64) arquitectura=x64; huella="${TEMURIN_SHA256_AMD64}" ;; \
        arm64) arquitectura=aarch64; huella="${TEMURIN_SHA256_ARM64}" ;; \
        *) echo "Arquitectura sin JDK en el kit: $(dpkg --print-architecture)" >&2; exit 1 ;; \
    esac \
    && etiqueta="jdk-$(echo "${TEMURIN_VERSION}" | sed 's/+/%2B/')" \
    && fichero="OpenJDK25U-jdk_${arquitectura}_linux_hotspot_$(echo "${TEMURIN_VERSION}" | tr + _).tar.gz" \
    && curl -fsSL "https://github.com/adoptium/temurin25-binaries/releases/download/${etiqueta}/${fichero}" -o jdk.tar.gz \
    && echo "${huella}  jdk.tar.gz" | sha256sum -c - \
    && mkdir /java && tar -xzf jdk.tar.gz -C /java --strip-components=1
RUN curl -fsSL "https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" -o maven.tar.gz \
    && echo "${MAVEN_SHA512}  maven.tar.gz" | sha512sum -c - \
    && mkdir /maven && tar -xzf maven.tar.gz -C /maven --strip-components=1
# Gradle se publica en ZIP: python3 (de la terminal) lo abre, y se devuelve el permiso de ejecución a bin/gradle
RUN curl -fsSL "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip" -o gradle.zip \
    && echo "${GRADLE_SHA256}  gradle.zip" | sha256sum -c - \
    && python3 -m zipfile -e gradle.zip /tmp/gradle && mv "/tmp/gradle/gradle-${GRADLE_VERSION}" /gradle \
    && chmod 755 /gradle/bin/gradle


FROM ${BASE}

USER root
# Las fuentes de Ubuntu por HTTPS (la imagen base las trae con http://)
RUN sed -i 's|http://|https://|g' /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        fonts-dejavu-core=2.37-8build1 fontconfig=2.17.1-3ubuntu1 libpangoft2-1.0-0=1.57.0-1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=descargar /java /opt/java
COPY --from=descargar /maven /opt/maven
COPY --from=descargar /gradle /opt/gradle
# Lo del kit: la tarea de Gradle que da el classpath, el programa que teclea entrada.txt en una terminal, el que
# arranca una aplicación de Spring Boot y le hace sus peticiones, y los lanzadores de las ventanas de JavaFX y Swing
COPY classpath.init.gradle.kts teclear.py aplicacion.py CapturaVentana.java CapturaSwing.java /opt/kit-java/

# La caché de Maven y Gradle (el volumen de --preparar-java), de «alumno»: un volumen nuevo copia este dueño
RUN mkdir -p /opt/kit-java/cache/m2/repository /opt/kit-java/cache/gradle \
    && chown -R alumno:alumno /opt/kit-java/cache \
    && printf '%s\n' '<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0">' \
        '  <localRepository>/opt/kit-java/cache/m2/repository</localRepository>' '</settings>' \
        > /opt/maven/conf/settings.xml

ENV JAVA_HOME=/opt/java GRADLE_USER_HOME=/opt/kit-java/cache/gradle
ENV PATH=/opt/java/bin:/opt/maven/bin:/opt/gradle/bin:$PATH

# La lista de lo instalado, como la de la terminal (verificar_codigo.py --versiones enseña la de la terminal). Gradle,
# con una carpeta suya de usar y tirar: lo que deja en la caché tiene que ser de «alumno»
RUN mkdir -p /usr/share/kit-java && { \
      echo "# Imagen de Java del kit, construida el $(date -u +%Y-%m-%dT%H:%MZ)"; \
      java -version 2>&1 | sed -n 2p; \
      mvn -v 2>/dev/null | head -1; \
      GRADLE_USER_HOME=/tmp/gradle-versiones gradle -v 2>/dev/null | grep '^Gradle'; \
      dpkg-query -W -f='${Package} ${Version}\n' fonts-dejavu-core fontconfig libpangoft2-1.0-0; \
    } > /usr/share/kit-java/versiones.txt && rm -rf /tmp/gradle-versiones

USER alumno
WORKDIR /home/alumno
RUN java -version 2>&1 | grep -q 'Temurin-25.0.4.1+1' \
    && mvn -v | grep -q 'Apache Maven 3.10.0' \
    && GRADLE_USER_HOME=/tmp/gradle-prueba gradle -v | grep -q '^Gradle 9.8.2' && rm -rf /tmp/gradle-prueba
