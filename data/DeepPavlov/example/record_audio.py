from io import BytesIO

import sounddevice as sd
from scipy.io.wavfile import write

sr = 16000
duration = 10

print('Recording...')
myrecording = sd.rec(duration*sr, samplerate=sr, channels=1)
sd.wait()
print('done')

voice = BytesIO()
write(voice, sr, myrecording)

with open("kek.waw", 'wb') as out: ## Open temporary file as bytes
    out.write(voice.read())
