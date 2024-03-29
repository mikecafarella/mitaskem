FROM python:3.10
EXPOSE 8000
ARG COMMIT_SHA=unknown
ARG VERSION=0.0.1
ENV GIT_COMMIT_SHA=${COMMIT_SHA}
ENV APP_VERSION=${VERSION}
RUN echo "APP Version is $APP_VERSION"
RUN echo "GIT Commit is ${GIT_COMMIT_SHA}"

# General Environment Setup
RUN apt-get update && apt-get install -y \
    git \
    graphviz \
    libgraphviz-dev \
    pkg-config

# set up locale
RUN apt-get update && apt-get install -y locales locales-all
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_NUMERIC  en_US.UTF-8
#RUN dpkg-reconfigure locales

# Automates clone and install
RUN mkdir /automates
RUN git clone https://github.com/ml4ai/automates.git ./automates
WORKDIR /automates
RUN pip install -e .

# Copy src code in and start API
RUN mkdir /mitaskem
COPY . /mitaskem
WORKDIR /mitaskem 
RUN pip install -e .

CMD ["uvicorn", "mitaskem.api.server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
