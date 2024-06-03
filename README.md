# Patient Medical History Summarisation &#129658;

## Description

Doctors are time poor and often do not have time to study large volumes of patient medical records. Our 
aim with this project is to produce a more relevant and efficient method of reading summaries of patient's 
medical notes with the help of Natural Language Processing (NLP) techniques.

This website allows healthcare professionals to search for a patient's medical history. It will show 
them a "Patient History" and a "Radiology History" longitudinal timeline view of a patient's history 
alongside notes summarised using Hugging Face transformers' BioGPT and BART text models.

## Usage

1. Import preprocessing/discharge.csv and preprocessing/radiology.csv into a PostgreSQL database.
2. Run patient_history/app.py

## Features

- Patient Number Search Bar
- Patient Details Summary
- Patient History timeline and summarised discharge section notes
- Radiology History timeline and summarised radiology notes

## Credits

- Alexander Authors
- Ovylia Lie
- Pei Ying Chong
- Zhi Ning Ku (Freya)
