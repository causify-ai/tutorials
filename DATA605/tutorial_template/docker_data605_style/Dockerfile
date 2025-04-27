# Use official Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required Python libraries
RUN pip install --upgrade pip
RUN pip install sqlalchemy requests pandas matplotlib seaborn notebook jupyter_contrib_nbextensions

# Copy jupyter extension script
COPY install_jupyter_extensions.sh /app/install_jupyter_extensions.sh

# Make it executable and run it
RUN chmod +x /app/install_jupyter_extensions.sh
RUN /app/install_jupyter_extensions.sh

# Expose Jupyter notebook port
EXPOSE 8888

# Start with bash shell
CMD ["bash"]

