FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Install Python packages
RUN pip install --upgrade pip
RUN pip install \
    jupyter \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    pymc \
    pytensor \
    arviz \
    tqdm

# Create a working directory
WORKDIR /workspace

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser"]
