# selfie_app

`selfie_app` is a Flask-based local web app for browser media capture and upload.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Use

```bash
python server.py
```

Open `http://127.0.0.1:5000` or the machine's local network IP in a browser.

## How It Works

- `server.py` serves the UI and accepts uploaded media
- uploaded files are stored in `uploads/`
