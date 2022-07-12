FROM node:17-alpine as frontend

WORKDIR /frontend
ADD frontend/package.json frontend/yarn.lock ./
RUN yarn install
ADD frontend ./
RUN yarn run build

FROM sourcehub-base:latest as backend

WORKDIR ${HOME_DIR}/backend

ADD pyproject.toml poetry.lock build-constraints.txt ./

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    PIP_CONSTRAINT=build-constraints.txt \
    CFLAGS="-mavx -DWARN(a)=(a)" \
    poetry install && \
    playwright install-deps && \
    playwright install chromium

RUN echo ". ${HOME_DIR}/backend/venv/bin/activate" >> ~/.bashrc

ADD backend ./

COPY --from=frontend /frontend/build/ ${HOME_DIR}/frontend/build

ENV PYTHONPATH="${HOME_DIR}"

CMD ["/bin/bash"]