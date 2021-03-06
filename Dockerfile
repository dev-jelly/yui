FROM python:3.8

MAINTAINER item4 <item4@localhost>

RUN apt-get update -q \
    && apt-get install --no-install-recommends -y \
    build-essential\
    libffi-dev\
    libxml2-dev\
    libxslt-dev\
    tzdata\
    postgresql\
    postgresql-contrib\
    curl\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip setuptools wheel

ENV HOME="/home/kazuto"

RUN groupadd --gid 1007 kirigaya && useradd --create-home --uid 1007 --gid 1007 kazuto && mkdir -p $HOME/yui/data && chown -R kazuto:kirigaya $HOME/yui
USER kazuto

ENV PATH="${HOME}/.poetry/bin:${PATH}"
ENV TZ="Asia/Seoul"

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
RUN cp -r "${HOME}/.poetry/lib/poetry/_vendor/py3.7" "${HOME}/.poetry/lib/poetry/_vendor/py3.8"

COPY --chown=kazuto:kirigaya ./pyproject.toml ./poetry.lock ${HOME}/yui/

WORKDIR ${HOME}/yui/

RUN poetry install --no-dev

COPY --chown=kazuto:kirigaya . ${HOME}/yui/
CMD ["yui", "run"]

VOLUME ${HOME}/yui/data
