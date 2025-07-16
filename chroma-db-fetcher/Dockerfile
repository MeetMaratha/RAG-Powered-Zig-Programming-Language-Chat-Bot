FROM public.ecr.aws/lambda/python:3.12

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./chroma_db_config.py ${LAMBDA_TASK_ROOT}

CMD [ "chroma_db_config.handler" ]
