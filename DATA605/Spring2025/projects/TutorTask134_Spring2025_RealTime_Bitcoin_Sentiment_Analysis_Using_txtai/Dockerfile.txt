FROM jupyter/scipy-notebook:python-3.10

# Upgrade pip first so it gets access to pre-built wheels
RUN pip install --upgrade pip

# Install tokenizers FIRST using binary only so it avoids Rust build
RUN pip install "tokenizers==0.12.1" --only-binary=tokenizers

# Install the rest (transformers and txtai depend on tokenizers)
RUN pip install numpy==1.26.4 \
    transformers==4.21.2 \
    txtai==3.3.0

