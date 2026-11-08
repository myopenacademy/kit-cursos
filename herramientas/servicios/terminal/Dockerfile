# La terminal en la que el kit verifica los scripts y las sesiones de los cursos (verificar_codigo.py).
#
# Fija todo lo que cambia la salida de una orden, para que sea la misma en cualquier máquina:
#   - Ubuntu 26.04.1 LTS, por su huella (la de ubuntu:26.04 el 8 de noviembre de 2026).
#   - Git 2.56.0, la versión que enseña el curso inicial (Ubuntu 26.04 trae la 2.53.0), compilado del
#     código oficial (kernel.org, con su SHA-256 publicado) CON SUS TRADUCCIONES (gettext): sin ellas,
#     Git responde en inglés aunque el sistema esté en español. Sin la parte en Rust (NO_RUST), que en la 2.56
#     es opcional según su Makefile (obligatoria desde Git 3.0) y no cambia los mensajes.
#   - bash 3.2.57, la de macOS, compilada del código oficial de GNU (firma de Chet Ramey verificada el
#     8 de noviembre de 2026; aquí, su SHA-256), como /usr/local/bin/bash-3.2: los scripts se ejecutan
#     también con ella, con las mismas herramientas GNU, para que una diferencia sea solo del bash.
#   - El idioma español (es_ES.UTF-8) generado y la zona horaria de Madrid.
#   - El reloj de Git (git-reloj, en /usr/local/sbin/git, delante del de verdad): los commits de una sesión,
#     con fechas fijas que avanzan un minuto cada uno desde el 15 de enero de 2026 a las 10:00.
#
# Si se cambia algo, se cambia también la tabla de versiones de herramientas/README.md.
FROM ubuntu:26.04@sha256:6a06111c3b0a8600feadb270aec771dc239bf407b25625f93f44ab00e11f4d3c AS compilar

ARG GIT_VERSION=2.56.0
ARG GIT_SHA256=26c56c296b38c0695b26fa95f475f1d01704d2d38e73465ca30b0b2f5dc789d3
ARG BASH32_SHA256=3fa9daf85ebf35068f090ce51283ddeeb3c75eb5bc70b1a4a7cb05868bfe06a4

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates curl xz-utils make gcc libc6-dev gettext zlib1g-dev libcurl4-openssl-dev \
        libexpat1-dev libssl-dev bison \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN curl -fsSL "https://www.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.xz" -o git.tar.xz \
    && echo "${GIT_SHA256}  git.tar.xz" | sha256sum -c - \
    && tar -xf git.tar.xz \
    && make -C "git-${GIT_VERSION}" -j"$(nproc)" prefix=/usr/local sysconfdir=/etc NO_TCLTK=1 NO_PERL=1 NO_PYTHON=1 NO_RUST=1 all \
    && make -C "git-${GIT_VERSION}" prefix=/usr/local sysconfdir=/etc NO_TCLTK=1 NO_PERL=1 NO_PYTHON=1 NO_RUST=1 install \
    && test -f /usr/local/share/locale/es/LC_MESSAGES/git.mo

# bash 3.2 es de 2014: con el C de hoy hace falta pedirle a gcc el C de entonces y que no corte por avisos
RUN curl -fsSL "https://ftp.gnu.org/gnu/bash/bash-3.2.57.tar.gz" -o bash.tar.gz \
    && echo "${BASH32_SHA256}  bash.tar.gz" | sha256sum -c - \
    && tar -xf bash.tar.gz && cd bash-3.2.57 \
    && CC="gcc -std=gnu89 -fcommon -w" CFLAGS="-O2" ./configure --prefix=/opt/bash-3.2 --without-bash-malloc --disable-nls >/dev/null \
    && make -j"$(nproc)" >/dev/null && make install >/dev/null \
    && /opt/bash-3.2/bin/bash -c 'echo "$BASH_VERSION"' | grep -q '^3\.2\.57'


FROM ubuntu:26.04@sha256:6a06111c3b0a8600feadb270aec771dc239bf407b25625f93f44ab00e11f4d3c

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        locales tzdata ca-certificates libcurl4t64 libexpat1 zlib1g file less tree curl jq python3 \
    && sed -i 's/^# *es_ES.UTF-8 UTF-8/es_ES.UTF-8 UTF-8/' /etc/locale.gen && locale-gen \
    && ln -sf /usr/share/zoneinfo/Europe/Madrid /etc/localtime && echo Europe/Madrid > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY --from=compilar /usr/local /usr/local
COPY --from=compilar /opt/bash-3.2/bin/bash /usr/local/bin/bash-3.2
COPY --chmod=755 git-reloj /usr/local/sbin/git

# La persona de las sesiones, con su carpeta personal; la configuración de Git de todo el sistema le da un
# nombre y la rama main (una sesión que enseña «git config --global» la cambia en su ~/.gitconfig, como en
# cualquier equipo)
RUN useradd --create-home --shell /bin/bash alumno \
    && printf '[user]\n\tname = Ana García\n\temail = ana@example.com\n[init]\n\tdefaultBranch = main\n' > /etc/gitconfig

ENV LANG=es_ES.UTF-8 LC_ALL=es_ES.UTF-8 LANGUAGE=es_ES:es TZ=Europe/Madrid
USER alumno
WORKDIR /home/alumno
RUN git --version | grep -q 'git version 2.56.0'
