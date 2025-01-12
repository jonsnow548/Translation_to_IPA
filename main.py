from flask import Flask, render_template, request, redirect, url_for
import pronouncing
import csv
import os

app = Flask(__name__)

# Dicționar ARPAbet -> IPA pentru simboluri
arpabet_to_ipa = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AX": "ə", "AY": "aɪ", "B": "b", "CH": "ʧ",
    "D": "d", "DH": "ð", "EH": "ɛ", "ER": "ɜr", "EY": "eɪ", "F": "f", "G": "g", "HH": "h", "IH": "ɪ",
    "IY": "i", "JH": "ʤ", "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ", "OW": "oʊ", "OY": "ɔɪ",
    "P": "p", "R": "r", "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "UH": "ʊ", "UW": "u", "V": "v", "W": "w",
    "Y": "j", "Z": "z", "ZH": "ʒ"
}

# Function to convert a word into IPA using the pronouncing library
def get_ipa_transcription(word):
    # Obține transcrierea ARPAbet pentru cuvântul dat
    phones = pronouncing.phones_for_word(word)

    if phones:
        # Preia prima transcriere ARPAbet
        arpabet_transcription = phones[0]

        # Elimină numerele de accent (ex. 'AO1' -> 'AO')
        arpabet_transcription = " ".join([phone[:-1] if phone[-1].isdigit() else phone for phone in arpabet_transcription.split()])

        # Convertește ARPAbet în IPA
        ipa_transcription = []
        for symbol in arpabet_transcription.split():
            ipa_transcription.append(arpabet_to_ipa.get(symbol, symbol))  # Folosește simbolul ARPAbet dacă nu există conversie

        return " ".join(ipa_transcription)
    else:
        return "IPA transcription not found."

# Function to save transcriptions to a CSV file
def save_transcriptions_to_csv(words, transcriptions, filename='ipa_transcriptions.csv'):
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Word', 'IPA Transcription'])  # Add header if file doesn't exist
        for word, transcription in zip(words, transcriptions):
            writer.writerow([word, transcription])

# Function to read words from an uploaded file
def read_words_from_file(file):
    words = file.read().decode('utf-8').splitlines()
    return [word.strip() for word in words if word.strip().isalpha()]

# Homepage route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'single_word' in request.form:  # Single word transcription
            word = request.form.get('word').strip()
            if word.isalpha():
                ipa_transcription = get_ipa_transcription(word)
                save_transcriptions_to_csv([word], [ipa_transcription])
                return render_template('index.html', single_result=(word, ipa_transcription))
            else:
                error = "Please enter a valid English word (letters only)."
                return render_template('index.html', error=error)

        elif 'file_upload' in request.form:  # File upload transcription
            uploaded_file = request.files.get('file')
            if uploaded_file and uploaded_file.filename.endswith('.txt'):
                words = read_words_from_file(uploaded_file)
                transcriptions = [get_ipa_transcription(word) for word in words]
                save_transcriptions_to_csv(words, transcriptions)
                results = zip(words, transcriptions)
                return render_template('index.html', file_results=results)
            else:
                error = "Please upload a valid .txt file with one word per line."
                return render_template('index.html', error=error)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
