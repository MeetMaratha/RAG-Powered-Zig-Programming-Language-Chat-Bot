FROM public.ecr.aws/lambda/python:3.12

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./chunker.py ${LAMBDA_TASK_ROOT}
COPY ./chunking_code ${LAMBDA_TASK_ROOT}/chunking_code


CMD [ "chunker.handler" ]
