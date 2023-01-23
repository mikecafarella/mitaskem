FROM python:3.10
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

# Copy src code in and start API
COPY . /MITASKEM
WORKDIR /MITASKEM
RUN pip install -r requirements.txt
WORKDIR /MITASKEM/api
CMD ["uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]