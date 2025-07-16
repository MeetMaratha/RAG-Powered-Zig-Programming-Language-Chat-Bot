FROM public.ecr.aws/lambda/python:3.12

# Install essential utilities (including xargs)
RUN dnf install -y findutils tar lshw && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Install Ollama (now has xargs available)
RUN curl -fsSL https://ollama.com/install.sh | sh

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./main.py ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]
