FROM nvcr.io/nvidia/cuda:11.3.0-devel-ubuntu20.04

USER root

RUN apt-get update

RUN apt-get install -y libopenblas-dev libx11-6 libgl1-mesa-glx

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y software-properties-common nvidia-container-toolkit python3.9 python3.9-dev python3-pip git-all

RUN mkdir -p /home/app

RUN mkdir -p /home/app/data /home/app/eval_output 

COPY . /home/app

WORKDIR /home/app

RUN pip install -r requirements.txt

ENV TORCH_CUDA_ARCH_LIST="7.5"

RUN bash dependencies.sh

RUN wandb disabled

RUN chmod u+rwx /home/app/docker-entrypoint.sh

CMD [ "/home/app/docker-entrypoint.sh" ]
