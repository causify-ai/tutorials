# Altair.example.py

## Overview

This file is the entry-point for launching the FastAPI application locally.

## Code Structure

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("Altair_API:app", host="127.0.0.1", port=8080, reload=True)
```

## Usage

### Local:
```bash
python3 Altair.example.py
```

### Docker:
```bash
docker run -it -p 8080:8080 altair-dashboard
```

## Architecture Role

It boots the `Altair_API.app` module using `uvicorn`. Intended for local development and quick testing.
