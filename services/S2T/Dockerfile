FROM python:3.6.9

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

# RUN echo "Downloading BERT"
# RUN rm -rf requirements.txt
# RUN wget https://raw.githubusercontent.com/vlomme/Bert-Russian-punctuation/master/bert_punctuation.py
# RUN wget https://raw.githubusercontent.com/vlomme/Bert-Russian-punctuation/master/vocab.txt
# RUN wget https://raw.githubusercontent.com/vlomme/Bert-Russian-punctuation/master/requirements.txt

RUN python -m pip install -r requirements.txt
RUN python -m pip install gdown
RUN gdown https://drive.google.com/uc?id=190dLqhRjqgNJLKBqz0OxQ3TzxSm5Qbfx


RUN git clone -b cpu https://github.com/bart02/punctuation-restoration.git
RUN gdown https://drive.google.com/uc?id=1DVONLsJ7aywlIKv0jah6PreTRcUpyq2Q
RUN pip install -r punctuation-restoration/requirements.txt

RUN pip install torch==1.7.1+cpu torchvision==0.8.2+cpu torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html