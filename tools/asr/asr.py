from whisper_punctuator import punctuator
import whisper

model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
wav_file = '/home/p76111652/Linux_DATA/synthesis/corpus/22k/tools/asr/38_5866_20170916205917.wav'
audio = whisper.load_audio(wav_file)
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")
# decode the audio
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)

punctuator = punctuator.Punctuator(language="zh", punctuations=",.?", initial_prompt="Hello, everyone.")
punctuated_text = punctuator.punctuate(
    wav_file,
    "打電話給"
)
print(punctuated_text) # -> "And do you know what the answer to this question now is? The answer is no. It is not possible to buy a cell phone that doesn't do too much. So"