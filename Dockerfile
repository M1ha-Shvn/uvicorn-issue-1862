ARG PYTHON_VER=3.8.10

# Dependency installation
FROM python:${PYTHON_VER}-slim  AS build_stage

ARG APP_PATH=.
ARG APP_REQUIREMENTS_FILE=requirements.txt

ENV APP_UID ${APP_UID:-1000}
ENV APP_GID ${APP_GID:-1000}
ENV APP_NAME ${APP_NAME:-"app"}


COPY ${APP_PATH}/requirements.txt /tmp/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
  set -eu && \
  python3 -m pip install --user --no-cache-dir --no-warn-script-location --upgrade pip setuptools wheel  && \
  python3 -m pip install --user --no-cache-dir --no-warn-script-location --upgrade --requirement /tmp/requirements.txt


FROM python:${PYTHON_VER}-slim  AS image_stage

ARG APP_PATH=.

ENV APP_UID ${APP_UID:-1000}
ENV APP_GID ${APP_GID:-1000}
ENV APP_NAME ${APP_NAME:-"app"}

# Configure utf-8 locales to make sure Python correctly handles unicode filenames
# Configure pip local path to copy data from pip_stage
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUSERBASE=/${APP_NAME}/pip PATH=/${APP_NAME}/pip/bin:$PATH

RUN set -eu && \
  apt-get update && \
  groupadd --gid "${APP_GID}" "${APP_NAME}" && \
  useradd --uid ${APP_UID} --gid ${APP_GID} --create-home --shell /bin/bash -d /${APP_NAME} ${APP_NAME} && \
  mkdir -p /${APP_NAME}/pip /${APP_NAME}/src /${APP_NAME}/static /${APP_NAME}/run && \
  chmod 755 /${APP_NAME} /${APP_NAME}/pip && \
  chown -R ${APP_UID}:${APP_GID} /${APP_NAME}

USER ${APP_UID}
WORKDIR /${APP_NAME}/src

COPY --chown=${APP_UID}:${APP_GID} ${APP_PATH} /${APP_NAME}/src
COPY --chown=${APP_UID}:${APP_GID} --from=build_stage /root/.local /${APP_NAME}/pip

CMD ["uvicorn", "--host", "0.0.0.0", "-port", "8000"]
