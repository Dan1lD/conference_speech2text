FROM nvidia/cuda:10.2-base-ubuntu18.04

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    ffmpeg \
    # sentencepiece \
    libx11-6 \
    build-essential \
    pkg-config \
    cmake \
    make \
    libgoogle-perftools-dev \
 && rm -rf /var/lib/apt/lists/*


# Create a working directory
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user

USER user

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN chmod 777 /home/user

# Install Miniconda and Python 3.8
ENV CONDA_AUTO_UPDATE_CONDA=false
ENV PATH=/home/user/miniconda/bin:$PATH
RUN curl -sLo ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-py38_4.8.2-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh \
 && conda install -y python==3.8.1 \
 && conda clean -ya

# CUDA 10.2-specific steps
RUN conda install -y -c pytorch torchaudio \
    cudatoolkit=10.2 \
    "pytorch=1.5.0=py3.8_cuda10.2.89_cudnn7.6.5_0" \
    "torchvision=0.6.0=py38_cu102" \
&& conda clean -ya

RUN conda install pip

RUN mkdir /home/user/install
WORKDIR /home/user/install

RUN echo "Installing fairseq"
RUN git clone https://github.com/pytorch/fairseq /home/user/install/fairseq
WORKDIR /home/user/install/fairseq
RUN python -m pip install install --editable ./


RUN echo "Installing sentencepiece"
WORKDIR /home/user/install/
RUN git clone https://github.com/google/sentencepiece.git 
RUN mkdir sentencepiece/build
WORKDIR /home/user/install/sentencepiece/build
RUN cmake ..
RUN make -j $(nproc)

USER root
RUN make install
RUN ldconfig -v
USER user



# RUN echo "Installing NVIDIA's apex library"
# RUN git clone https://github.com/NVIDIA/apex /home/user/install/apex

# WORKDIR /home/user/install/apex
# RUN python -m pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" \
#   --global-option="--deprecated_fused_adam" --global-option="--xentropy" \
#   --global-option="--fast_multiheasd_attn" ./

WORKDIR /home/user/
COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt
RUN pip install --upgrade numpy
WORKDIR /app/
