FROM python:3.9-slim

# Set work directory inside container
WORKDIR /home/app

# Copy all local files into container
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir jupyter pandas matplotlib seaborn statsmodels requests

# Set default command to run Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]

