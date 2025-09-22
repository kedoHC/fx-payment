# FX Payment

A Flask application for foreign exchange payment processing.

## Installation

### 1. Create the virtual environment

```bash
python3 -m venv venv
```

### 2. Activate the virtual environment

**On macOS/Linux:**

```bash
source venv/bin/activate
```

**On Windows (Command Prompt or PowerShell):**

```cmd
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

## Project Structure

- `app.py` - Main Flask application
- `requirements.txt` - Project dependencies
- `venv/` - Python virtual environment

## Docker usage

```bash
docker build - fx-payment .
```

```bash
docker run -p 5005:5000 fx-payment
```

[Optional] Use for development process

```bash
docker run -p 5005:5000 -w /app -v "$(pwd):/app" fx-payment
```
