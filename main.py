import stable_whisper
import torch

cuda = torch.cuda.is_available()

if cuda:
    print("CUDA is available.")
else:
    print("CUDA not available.")


print("Loading model.")
model = stable_whisper.load_model('medium')
print("Loaded model.")


no_speech_threshold = 0.7
compression_ratio_threshold = 1.7
beam_size = 4
best_of = 3
temperature = 0.0

results = model.transcribe(
    'test.mkv', language='fr', verbose=False,
    condition_on_previous_text=False,
    no_speech_threshold=no_speech_threshold,
    compression_ratio_threshold=compression_ratio_threshold,
    beam_size=beam_size,
    best_of=best_of,
    temperature=temperature
)

stable_whisper.results_to_sentence_srt(results, 'audio.srt')
