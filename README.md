# Conference speech2text

![Data scheme](https://habrastorage.org/webt/g5/e2/my/g5e2myra8yluuzxi2ii3vt-8jdu.png)

User-service communication

## Usage

1. Install and check requirements
2. `git clone https://github.com/Dan1lD/conference_speech2text && cd conference_speech2text`
    1. (optional, if you want to make your server public) Set your nginx configuration (host) in file *services/Web/nginx/nginx.conf*. Specify your `server_name` (google nginx configuration).
3. `docker-compose build`
4. `docker-compose up`
5. Open in your web-browser `http://127.0.0.1` (or `http://` + `server_name` if you did *2.1 step*). It is web-site for end users.

### Requirements
Software:
- Docker
- nvidia-docker
- docker-compose
- nvidia drivers
- CUDA

Hardware:
- Nvidia videocard
- 20 GB RAM
- 30 GB of free memory on ROM

## Services description
### Web-site
The website provides a graphical interface for wav file transcription and management. It runs on python Django backend, and javascript + HTML + CSS frontend.

#### Avaliable features:
- Voice transcription from uploaded `wav` file
- Search records by keywords
- `wav` files uploading by user
- Files storing: voice record(`wav`) and transcription(`txt`)

#### Screenshots
![main menu](https://habrastorage.org/webt/km/f3/bt/kmf3btjtvcqsyxqkl3rwdkb6oay.png)

Main menu. There user can upload his `wav` file to transcript. At the top right we can open menu with main pages and search records by keywords in the local searcher.

![record cards](https://habrastorage.org/webt/d5/ek/su/d5eksu8vogptbtmudt9coyzfm1e.png)

Record cards. This a list of cards for uploaded voice records. User can open full transcription by clicking on card. Every card shows word cloud of keywords, title of record, few first words from transcription, upload date and time, links for download `wav` and `txt` files, button to delete the record.

![record transcription](https://habrastorage.org/webt/vx/mp/kv/vxmpkveow9ewrmljj5tamzpmtne.png)

Record transcription. There user can see full transcription, uploaded file name and same items as in record card. It is possible to edit recognized text.

<img src="https://habrastorage.org/webt/j2/oe/aj/j2oeajvsnlaqsf6-z0hoihi8trq.jpeg" style="height: 600px;"/>

Mobile site view. Our site supports mobile users.

#### Stack used:
- python
    - django
    - matplotlib
    - wordcloud
- javascript
    - bootstrap
    - jquery
    - modernizr
- HTML
- CSS

### Voice-text convertion
We perform voice(`wav`) to text convertion using open source speech recognition toolkit ["VOSK"](https://alphacephei.com/vosk/). For code look at *services/S2T/app/app.py*.

### Puntuation adding
We put punctuation marks to the converted text using modified ["Neuro-comma"](https://github.com/sviperm/neuro-comma) model. For code look at *services/S2T/app/app.py*.

![Transformer Models](https://github.com/sviperm/neuro-comma/raw/master/readme/model-architecture.png)

A Transformer architecture based language model.

### Keywords extracting
We exctact keywords from converted text for quick navigation between records. 

Exctracting performs in 4 steps:
1. We bring words in the text to their infinitives to avoid repetions of different forms of word in keywords by applying an open source conversational AI framework [DeepPavlov](https://deeppavlov.ai/)
2. Calculate embeddings of words using [sentence-transformers](https://github.com/UKPLab/sentence-transformers) framework
3. Select the most popular words in terms of number of embedding similar word pairs
4. Leave only unique instanses of word.
