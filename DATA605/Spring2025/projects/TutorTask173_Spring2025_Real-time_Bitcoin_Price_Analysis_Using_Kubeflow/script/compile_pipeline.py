from kfp.compiler import Compiler
from bitcoin_pipeline import bitcoin_pipeline

Compiler().compile(bitcoin_pipeline, 'bitcoin_pipeline.yaml')
