# Local speech trial

Native APK transaction installed espeak-ng, speech-dispatcher,
py3-speech-dispatcher and py3-onnxruntime, with APK-selected dependencies.
All 77 resolved changes were installations, with no removals or upgrades.
Installed bindings import successfully with host Python 3.14.

Selected voice: Kirra (narrator magdalena), speaker 3 in
[Data Craftsman's Australian LibriVox model](https://huggingface.co/DataCraftsmanAustralia/piper-en_AU-librivox-medium).
The model uses CPU ONNX Runtime and the model-specified eSpeak phonemizer;
it is not Alpine's unrelated mouse-configuration package named piper.

`tools/australian_speech.py` supplies a small development frontend, using two
inference threads. `alpine-say 'Your text'` plays a temporary WAV; `--output
file.wav` saves one. It defaults to Kirra. Other female speakers are bindi,
marlo, matilda, tully and willow via `--voice`. The Python `synthesize` function
is also callable. Models live under ~/.local/share/alpine-speech, with the
model card, upstream attribution and a pinned revision/hash receipt.

This frontend has a narrower phoneme/text path than the full Piper application;
unsupported phonemes fail explicitly. Formal audiobook accents, old literary
training text and variable source recording quality are model limitations.
No global Speech Dispatcher voice or desktop accessibility setting was changed.

Model attribution: en_AU-librivox-medium by Data Craftsman, CC BY 4.0. Fine-tuned
from en_GB-jenny_dioco-medium, derived from the Jenny TTS dataset by **Jenny
(Dioco)**. Training recordings were donated by LibriVox volunteers, including
magdalena for Kirra. Retain upstream ATTRIBUTION.md with the weights.
