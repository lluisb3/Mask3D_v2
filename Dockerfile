FROM ubuntu:20.04
COPY . /app
WORKDIR /app
CMD [ "install miniconda" ]

RUN apt update

RUN apt install libopenblas-dev

RUN export TORCH_CUDA_ARCH_LIST="6.0 6.1 6.2 7.0 7.2 7.5 8.0 8.6"

