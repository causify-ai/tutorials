# Use an official OpenJDK base image (required for Spark)
FROM openjdk:11-jdk

# Set working directory inside container
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Install Spark (choose Spark 3.4.1 to match your EMR)
RUN apt-get install -y wget && \
    wget https://archive.apache.org/dist/spark/spark-3.4.1/spark-3.4.1-bin-hadoop3.tgz && \
    tar -xvzf spark-3.4.1-bin-hadoop3.tgz && \
    mv spark-3.4.1-bin-hadoop3 /spark


# Add Spark to PATH
ENV SPARK_HOME=/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Copy your project files
COPY . /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Default command
CMD ["bash", "run_spark.sh"]
