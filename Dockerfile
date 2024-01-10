# Dockerfile to create mask3d image as non-root user

FROM nvcr.io/nvidia/cuda:11.3.0-devel-ubuntu20.04

# To not cache the packages
RUN echo "[install]\ncompile = no\n\n[global]\nno-cache-dir = True" > /etc/pip.conf

# Set timezone to not be imteractive the python installation
ENV TZ=Europe/Madrid

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set non-root user as user
ARG USER_ID
ARG GROUP_ID

RUN apt-get update && \
    apt-get install -y sudo && \
    addgroup --gid $GROUP_ID user && \
    adduser --uid $USER_ID --gid $GROUP_ID --disabled-password --gecos "Default user" user && \
    echo 'user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

USER user

# Install necesary libraries
RUN sudo apt-get install --no-install-recommends -y libopenblas-dev libx11-6 libgl1-mesa-glx

# Install Python and git
RUN sudo apt-get install -y python3.9 python3.9-dev python3-pip git-all

RUN sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*

ENV PATH=/home/user/.local/bin:$PATH

# Create mask3D app and output folders
RUN mkdir -p /home/user/app

RUN mkdir -p /home/user/app/data /home/user/app/eval_output/instance_evaluation_docker_0/decoder_-1

# Change Workdirectory to mask3D app
WORKDIR /home/user/app

# Copy files into the container and set the appropriate permissions
COPY --chown=user:user . /home/user/app
RUN chmod -R ug+rwx /home/user/app

# Install necesary requeriments and dependencies
RUN pip3 install -r requirements.txt

RUN pip3 install --upgrade pip

ENV TORCH_CUDA_ARCH_LIST=export TORCH_CUDA_ARCH_LIST="6.0 6.1 6.2 7.0 7.2 7.5 8.0 8.6"

RUN sudo chmod -R a+rwx /usr

RUN bash dependencies.sh

# Disable wandb
ENV WANDB_MODE=disabled

# Default entrypoint
CMD [ "python3", "-u", "-m", "utils.demo", "--scene", "scene0001_00", "--exp_name", "docker", "--checkpoint", "scannet_best" ]
