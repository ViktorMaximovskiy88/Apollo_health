FROM python:3.10.3-bullseye as builder

ENV APP_DIR=/app
WORKDIR ${APP_DIR}

RUN curl -LO https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && chmod +x aws-lambda-rie
RUN  pip install --target ${APP_DIR} awslambdaric

COPY ./backend/taskworker_sync/requirements.txt ${APP_DIR}
RUN  pip install -r requirements.txt --target "${APP_DIR}"

COPY ./backend/taskworker_sync/main.py ${APP_DIR}

FROM python:3.10.3-slim-bullseye as release

ENV APP_DIR=/app
WORKDIR ${APP_DIR}

COPY --from=builder /app /app

ENTRYPOINT [ "/app/aws-lambda-rie", "python", "-m", "awslambdaric" ]
CMD [ "main.handler" ]