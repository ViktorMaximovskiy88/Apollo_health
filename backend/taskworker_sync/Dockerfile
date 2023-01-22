FROM public.ecr.aws/bitnami/python:3.10.3

WORKDIR ${LAMBDA_TASK_ROOT}

COPY main.py requirements.txt ${LAMBDA_TASK_ROOT}
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

RUN curl -LO https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && chmod +x aws-lambda-rie
ENTRYPOINT [ "./aws-lambda-rie", "python", "-m", "awslambdaric" ]

CMD [ "main.handler" ]