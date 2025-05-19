# docker_data605_style/Dockerfile

# 1) pick your Python base
FROM python:3.8-slim

# 2) set working dir
WORKDIR /app

# 3) install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) copy your app code (one level up)
COPY ../streamlit_btc_app.py    ./streamlit_btc_app.py
COPY ../rasa_utils.py           ./rasa_utils.py

# 5) expose Streamlit port
EXPOSE 8501

# 6) run Streamlit
CMD ["streamlit","run","streamlit_btc_app.py",\
     "--server.address=0.0.0.0",\
     "--server.port=8501",\
     "--server.enableXsrfProtection=false"]
