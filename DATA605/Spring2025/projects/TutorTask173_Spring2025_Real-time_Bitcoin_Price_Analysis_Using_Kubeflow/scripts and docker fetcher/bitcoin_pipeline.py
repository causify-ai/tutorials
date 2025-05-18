# bitcoin_pipeline.py

import kfp
from kfp import dsl

@dsl.pipeline(
    name="Bitcoin Price Fetch Pipeline",
    description="Fetch Bitcoin price and save to DB + CSV using a Docker container"
)
def bitcoin_pipeline():
    dsl.ContainerOp(
        name="Fetch Bitcoin Price",
        image="antodelinxavier/bitcoin-project-fetcher:v1",  # Replace with full image if pushed to DockerHub
        command=["python", "fetch_bitcoin_price.py"]
    )
