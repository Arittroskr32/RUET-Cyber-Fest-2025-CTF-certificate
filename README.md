# CTFd Certificate Generator - Pure Python

Simple certificate generator that integrates with CTFd using session cookies. **Zero JavaScript**, pure server-side Python Flask application.

## Setup

```bash
# Install dependencies
pip3 install Flask requests

# Set environment variables
export CTFD_URL=http://localhost:8000
export CERTIFICATE_PORT=5001

# Run
python3 app.py
```

## How It Works

1. User logs into CTFd
2. User visits certificate generator (different port)
3. Generator reads CTFd session cookie
4. Fetches user data from CTFd API
5. Renders certificate with user's data
6. User can customize display name only
7. Print to PDF or save directly from browser

## Files

- `app.py` - Main Flask application
- `templates/certificate.html` - Certificate template (server-side rendered)
- `.env.example` - Configuration template
- `requirements.txt` - Python dependencies

## Configuration

Set these environment variables:

```bash
CTFD_URL=http://your-ctfd-server:8000
CERTIFICATE_PORT=5001
SECRET_KEY=your-random-secret-key
HASH_SALT=your-random-salt
```

## Usage

```bash
python3 app.py
```

Users access at `http://your-server:5001` after logging into CTFd.

## Features

- ✅ Pure Python - No JavaScript
- ✅ Session-based auth via CTFd cookies
- ✅ Auto-fetches rank, points, challenges from CTFd
- ✅ User can only change display name
- ✅ Print to PDF via browser
- ✅ No changes needed to CTFd infrastructure
