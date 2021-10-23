FROM python:3.6

# Create a working directory
RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN wget https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/paraphrase-xlm-r-multilingual-v1.zip

RUN unzip -qq paraphrase-xlm-r-multilingual-v1.zip -d paraphrase-xlm-r-multilingual-v1

RUN apt-get update && apt-get install protobuf-compiler -y
RUN pip install sentence-transformers nltk scikit-learn Flask celery redis protobuf
