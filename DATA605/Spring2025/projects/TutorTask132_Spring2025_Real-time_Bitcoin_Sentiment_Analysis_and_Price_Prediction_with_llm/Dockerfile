# Use official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all project files to the container
COPY . .

# Remove the .env file to avoid baking secrets into the image
RUN rm -f .env

# Upgrade pip and install project dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -i https://pypi.org/simple --timeout 100


# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
