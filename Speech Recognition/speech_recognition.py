from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.lang import Builder
import numpy as np
from scipy.io import wavfile
import soundfile as sf
import librosa
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer

class SpeechRecognitionApp(App):
    def recognize_speech(self, instance):
        file_name = self.file_chooser.selection and self.file_chooser.selection[0] or None

        if not file_name:
            self.result_label.text = "Please select a file."
            return

        try:
            input_audio, _ = librosa.load(file_name, sr=16000)

            tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
            input_values = tokenizer(input_audio, return_tensors="pt").input_values

            model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

            logits = model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = tokenizer.batch_decode(predicted_ids)[0]

            # Update the label with the recognized speech
            self.result_label.text = "Recognized speech:\n" + transcription  # Add "\n" for newline
        except Exception as e:
            self.result_label.text = f"Error: {e}"

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Add file chooser for selecting the audio file
        self.file_chooser = FileChooserIconView()
        self.file_chooser.path = "/Users"  # Set the initial path to the user's home directory
        self.file_chooser.filters = ["*.wav", "*.mp3"]  # Filter to only show WAV and MP3 files
        layout.add_widget(self.file_chooser)

        # Add button for triggering speech recognition
        button = Button(text='Recognize Speech')
        button.bind(on_press=self.recognize_speech)
        layout.add_widget(button)


# Add label to display recognized speech
        self.result_label = Label(text='Speech recognition result will appear here', halign='left', valign='top',
                                  size_hint_y=None, height=100)  # Adjust height for multiple lines
        self.result_label.bind(size=self.result_label.setter('text_size'))  # Enable text wrapping
        layout.add_widget(self.result_label)

        return layout

if _name_ == '_main_':
    SpeechRecognitionApp().run()
