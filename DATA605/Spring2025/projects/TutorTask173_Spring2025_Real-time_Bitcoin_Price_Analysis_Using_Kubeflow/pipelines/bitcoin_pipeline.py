# bitcoin_pipeline.py

from kfp import dsl
from kubernetes import client as k8s_client

def bitcoin_price_pipeline():
    fetch_op = dsl.ContainerOp(
        name="Fetch Bitcoin Price",
        image="bitcoin-fetcher:v1",
        command=["python", "fetch_bitcoin_price.py"]
    )

    fetch_op.container.add_env_variable(k8s_client.V1EnvVar(name='DB_USER', value='postgres'))
    fetch_op.container.add_env_variable(k8s_client.V1EnvVar(name='DB_PASSWORD', value='testpass'))
    fetch_op.container.add_env_variable(k8s_client.V1EnvVar(name='DB_HOST', value='host.docker.internal'))
    fetch_op.container.add_env_variable(k8s_client.V1EnvVar(name='DB_PORT', value='5432'))
    fetch_op.container.add_env_variable(k8s_client.V1EnvVar(name='DB_NAME', value='bitcoin_db'))
    fetch_op.container.add_env_variable(k8s_client.V1EnvVar(name='COINGECKO_API_KEY', value='CG-KufNKPvFrCUCFUWHxW6yyXTM'))
