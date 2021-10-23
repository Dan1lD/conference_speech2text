import io
import itertools
import os
from collections import Counter

import numpy as np
import sklearn
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

stemmer = SnowballStemmer("russian") 
os.environ["KERAS_BACKEND"] = "tensorflow"

        
with io.open("/data/key_extractor/stop_words_russian.txt", "r", encoding="utf-8") as file:
     stop_words = file.read()


def max_sum_sim(doc_embedding, word_embeddings, words, candidates, top_n=10, nr_candidates=20):
    # Calculate distances and extract keywords
    distances = cosine_similarity(doc_embedding, word_embeddings)
    distances_candidates = cosine_similarity(word_embeddings, 
                                            word_embeddings)


    # Get top_n words as candidates based on cosine similarity
    words_idx = list(distances.argsort()[0][-nr_candidates:])
    words_vals = [candidates[index] for index in words_idx]
    distances_candidates = distances_candidates[np.ix_(words_idx, words_idx)]
    
    # print(distances_candidates)

    # Calculate the combination of words that are the least similar to each other
    min_sim = np.inf
    candidate = None
    for combination in itertools.combinations(range(len(words_idx)), top_n):
        sim = sum([distances_candidates[i][j] for i in combination for j in combination if i != j])
        if sim < min_sim:
            candidate = combination
            min_sim = sim

    return [words_vals[idx] for idx in candidate]


def create_keywords(sentence_transformer_model, doc, n_gram_range=(1, 1), top_n=20):
    candidates = list((set(doc.strip().lower().replace('\n', ' ').split(' ')) - set([''])) - set(stop_words))
    # Model1:   paraphrase-xlm-r-multilingual-v1
    # Model2:   distilbert-base-nli-mean-tokens
    doc_embedding = sentence_transformer_model.encode([doc]) 
    candidate_embeddings = sentence_transformer_model.encode(candidates)
    distances = cosine_similarity(doc_embedding, candidate_embeddings)
    keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]

    keywords = max_sum_sim(doc_embedding, candidate_embeddings, keywords, candidates)
    stemmed_keywords = [stemmer.stem(word) for word in keywords]

    del_idx = []
    for i in range(len(stemmed_keywords)):
        for j in range(i):
            if stemmed_keywords[i] == stemmed_keywords[j]:
                del_idx.append(i)
    new_keywords = []
    for i, kw in enumerate(keywords):
        if i not in del_idx:
            new_keywords.append(kw)

    return new_keywords
