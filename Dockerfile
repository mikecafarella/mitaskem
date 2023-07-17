FROM python:3.10
EXPOSE 8000 

# General Environment Setup
RUN apt-get update && apt-get install -y \
    git \
    graphviz \
    libgraphviz-dev \
    pkg-config

# Automates clone and install
RUN mkdir /automates
RUN git clone https://github.com/ml4ai/automates.git ./automates
WORKDIR /automates
RUN pip install -e .

WORKDIR /
# local KG
# get mira KG
RUN curl -o epi_2023-07-07_nodes.tsv.gz https://askem-mira.s3.amazonaws.com/dkg/epi/build/2023-07-07/nodes.tsv.gz
RUN gunzip epi_2023-07-07_nodes.tsv

# Copy src code in and start API
COPY . /
ENV PYTHONPATH "${PYTHONPATH}:/src"
RUN pip install -r requirements.txt



WORKDIR /api


CMD ["uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
