from transformers import pipeline
import transformers
import librosa 
import torch
import iPython
from transformers import Wav2Vec2Vec2ForCTC, Wav2Vec2Tokenizer
import numpy as np

tokenizer= Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")


