# Selfie App

A playful local web app designed to turn a simple camera capture into an exaggerated compliment experience.

## Why It’s Memorable

`selfie_app` is not just a file uploader. The project leans into social theater: take a photo, capture attention, and present it in a playful, over-the-top way that feels more like a joke product than a utility.

## What It Does

- serves a browser UI for local media capture
- accepts uploads through a Flask backend
- stores captured files locally
- supports a presentation flow meant to feel fun, dramatic, and shareable

## Project Structure

```text
selfie_app/
|-- server.py
|-- index.html
|-- requirements.txt
|-- uploads/
`-- README.md
```

## Requirements

- Python 3.8+

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Locally

```bash
python server.py
```

Then open:

- `http://127.0.0.1:5000`
- or `http://<your-local-ip>:5000` on the same network

## How It Works

- `server.py` runs the Flask app and handles uploads
- the browser UI captures user media and sends it to the backend
- uploaded files are stored in `uploads/`
- the experience is shaped more like a playful impression-maker than a plain form submission tool

## Tone Of The Project

This repo works best when treated as a cheeky photo-based novelty experience rather than a serious productivity app.
