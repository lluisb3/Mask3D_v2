FROM ubuntu:20.04
COPY . /app
WORKDIR /app
CMD [ "install miniconda" ]