#!/bin/bash

#  conda install -c anaconda numpy==1.18.1

# python main.py

# python /home/user/data/dataset_to_librispeech.py

python /home/user/install/fairseq/train.py /home/user/data --save-dir /home/user/data/model --max-epoch 80 --task speech_recognition --arch vggtransformer_2 --optimizer adadelta --lr 1.0 --adadelta-eps 1e-8 --adadelta-rho 0.95 --clip-norm 10.0  --max-tokens 5000 --log-format json --log-interval 1 --criterion cross_entropy_acc --user-dir /home/user/install/fairseq/examples/speech_recognition/