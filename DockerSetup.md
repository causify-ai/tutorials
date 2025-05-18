# 🐳 Docker Setup Guide: Real-Time Bitcoin Price Dashboard

This section provides complete instructions to **build and run** the project using Docker.

---

## 📦 Step 1: Build the Docker Image

From your project root (where your Dockerfile is located), run:

```bash
docker build -t bitcoin-dashboard .
```

### ✅ Expected Output (truncated):
```
[+] Building 5.0s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load metadata for python:3.11
 => [1/5] FROM python:3.11
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt .
 => [4/5] RUN pip install -r requirements.txt
 => [5/5] COPY . .
 => => naming to docker.io/library/bitcoin-dashboard:latest
```

---

## 🚀 Step 2: Run the Docker Container

```bash
docker run -d -p 8000:8000 --name bitcoin-dashboard-container bitcoin-dashboard
```

### ✅ Expected Output:
```
<container-id>
```

Then visit your dashboard in your browser:  
📍 [http://localhost:8000/dashboard](http://localhost:8000/dashboard)

---

## 🧪 Verify It's Working

You should see in terminal via `docker logs bitcoin-dashboard-container`:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

You’ll also see log entries when accessing routes:

```
INFO:     172.17.0.1:54732 - "GET /dashboard HTTP/1.1" 200 OK
```

## 📂 Files Required in Project Root

Make sure these files exist before building the image:

```
.
├── Dockerfile
├── requirements.txt
├── bitcoin_5yr_history.csv
├── app/
│   └── main.py
```
