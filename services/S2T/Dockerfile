FROM python:3.9.7

# Install some basic utilities
# RUN apt-get update && apt-get install -y \
#     curl \
#     ca-certificates \
#     sudo \
#     git \
#     bzip2 \
#     ffmpeg \
#     # sentencepiece \
#     libx11-6 \
#     build-essential \
#     pkg-config \
#     cmake \
#     make \
#  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y ffmpeg

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /audio/wav 

COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt
RUN pip install --upgrade numpy

RUN echo "Downloading VOSK model"
RUN wget --no-check-certificate https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip
RUN unzip -qq vosk-model-ru-0.10.zip
RUN mv vosk-model-ru-0.10 model
RUN rm -rf vosk-model-ru-0.10.zip
RUN python -m pip install -r requirements.txt


RUN echo "Downloading BERT model for punctuation"
RUN git clone https://github.com/Dan1lD/neuro_comma.git
RUN wget https://github.com/sviperm/neuro-comma/releases/download/repunct-quant/repunct-model-new.zip
RUN unzip repunct-model-new.zip -d neuro_comma/models/
RUN rm -rf repunct-model-new.zip
RUN pip install -r neuro_comma/requirements.txt

RUN pip install torch==1.7.1+cpu torchvision==0.8.2+cpu torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html