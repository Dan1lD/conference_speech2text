import json
from typing import List

from fuzzywuzzy import process

# with open('/app/dragndrop/data.json', 'r') as read_file:
#     data = json.load(read_file)


def f(s: str, l: List[str]):
    a = process.extractOne(s, l)
    return a[1] > 90


def link(text):
    ttt = set()
    k = data.keys()
    t = list(map(lambda x: x.strip(".,\"\':;()"), text.split()))
    i = 0
    while i < len(t):
        if f(t[i].lower().strip('.,\"\':;()'), k):
            start = i
            end = i + 1
            while end < len(t) and f(" ".join(t[start:end]).lower().strip('.,\"\':;()'), k):
                end += 1
            end -= 1
            term = " ".join(t[start:end])
            if process.extractOne(term.lower().strip('.,\"\':;()'), k)[1] > 90:
                if term not in ttt:
                    text = text.split(term)
                    text = ("<a href=\"" + data[process.extractOne(term.lower().strip('.,\"\':;()'), k)[0]] + "\">" + term + "</a>").join(text)
                    ttt.add(term)

            i = end
        i += 1
    return text
