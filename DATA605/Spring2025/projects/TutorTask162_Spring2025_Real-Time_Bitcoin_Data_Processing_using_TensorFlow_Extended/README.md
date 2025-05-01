# Bitcoin Price Forecasting Pipeline using TFX

This project builds a real-time machine learning pipeline using TensorFlow Extended (TFX) to forecast Bitcoin prices. The pipeline handles end-to-end data ingestion, validation, transformation, model training, and deployment.

---

## Steps Followed

1. **Project Structure Setup**
   - Created a directory `tfx_pipeline_output/bitcoin_price_pipeline` to store pipeline artifacts.
   - Chose a modular structure to separate pipeline definition (`pipeline.py`), transformation logic (`transform.py`), and model logic (`trainer.py`) for maintainability.

2. **Data Ingestion**
   - Used `CsvExampleGen` to read raw Bitcoin price data from the `/data` folder.

3. **Statistics and Schema Generation**
   - Employed `StatisticsGen` and `SchemaGen` to compute feature statistics and automatically infer the data schema so that we do an early detection of feature distribution and data type mismatches. 

4. **Example Validation**
   - Integrated `ExampleValidator` to check for schema violations or missing/invalid entries in the dataset.

5. **Data Transformation**
   - Defined a `preprocessing_fn` in `transform.py` to normalize the `price` feature using `tft.scale_to_z_score`.
   I am normalizing here so that it will be beneficiail during training LSTM model to forecast bitcoin price. 

6. **Model Training**
   - Developed a simple regression model using Keras in `trainer.py` with a dense neural network architecture.
   - The pipeline trains on the `normalized_price` feature and predicts the same as output.

7. **Pipeline Execution**
   - Created `tf_pipeline.py` to define all pipeline components and their connections.

---

## Docker Setup 

### How It Was Set Up:
1. Created a `Dockerfile` based on `tensorflow/tfx` base image.
2. Added application files into `/app/tutorial_template`.
3. Used `docker-compose.yml` to simplify build and run steps.

### To build and run:
```bash
docker build -t bitcoin-tfx-pipeline .
docker-compose up
```

---

## Status
As of now, following are completed:
- Data ingestion
- Validation
- Transformations
- Trainer is integrated and runs end-to-end 

---

## Next Steps

- Implement a more sophisticated LSTM model for time series.
- Add a Pusher component to serve the trained model via a REST API.


