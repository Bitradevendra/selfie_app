# selfie_app

`selfie_app` is a Flask-based local web application for browser media capture and upload.

## Overview

The app serves a browser UI, accepts captured media from the client, and stores uploaded files locally.

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

## Running The Project

```bash
python server.py
```

Open the app in a browser:

- `http://127.0.0.1:5000`
- `http://<your-local-ip>:5000`

## How It Works

- `server.py` runs the Flask server and upload endpoints
- the browser UI captures media and posts it back to the server
- uploaded files are stored in `uploads/`
