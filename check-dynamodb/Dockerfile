FROM public.ecr.aws/lambda/python:3.12

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./main.py ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]
