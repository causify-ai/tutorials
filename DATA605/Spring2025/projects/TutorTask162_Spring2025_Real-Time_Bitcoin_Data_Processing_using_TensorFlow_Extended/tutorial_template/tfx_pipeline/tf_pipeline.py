import os
import shutil
from absl import logging
from tfx.orchestration import pipeline
from tfx.orchestration.beam.beam_dag_runner import BeamDagRunner
from tfx.components import (
    CsvExampleGen, StatisticsGen, SchemaGen, ExampleValidator, Transform, 
    Trainer, Pusher
)
from tfx.proto import trainer_pb2, pusher_pb2, example_gen_pb2
from tfx.orchestration.metadata import sqlite_metadata_connection_config

_pipeline_name = 'bitcoin_price_pipeline'
_pipeline_root = os.path.join(os.getcwd(), 'tfx_pipeline_output', _pipeline_name)
_data_root = os.path.join(os.getcwd(), 'data', 'bitcoin')
_module_file_transform = os.path.join(os.getcwd(), 'transform.py')
_module_file_trainer = os.path.join(os.getcwd(), 'trainer.py')
_serving_model_dir = os.path.join(_pipeline_root, 'serving_model')

def create_pipeline():
    output_config = example_gen_pb2.Output(
        split_config=example_gen_pb2.SplitConfig(splits=[
            example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=8),
            example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=2),
        ])
    )

    example_gen = CsvExampleGen(input_base=_data_root, output_config=output_config)
    statistics_gen = StatisticsGen(examples=example_gen.outputs['examples'])
    schema_gen = SchemaGen(statistics=statistics_gen.outputs['statistics'], infer_feature_shape=True)
    example_validator = ExampleValidator(
        statistics=statistics_gen.outputs['statistics'],
        schema=schema_gen.outputs['schema']
    )
    transform = Transform(
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        module_file=_module_file_transform,
        force_tf_compat_v1=False
    )
    trainer = Trainer(
        module_file=_module_file_trainer,
        examples=transform.outputs['transformed_examples'],
        transform_graph=transform.outputs['transform_graph'],
        schema=schema_gen.outputs['schema'],
        train_args=trainer_pb2.TrainArgs(num_steps=100),
        eval_args=trainer_pb2.EvalArgs(num_steps=50)
    )
    pusher = Pusher(
        model=trainer.outputs['model'],
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(base_directory=_serving_model_dir)
        )
    )

    return pipeline.Pipeline(
        pipeline_name=_pipeline_name,
        pipeline_root=_pipeline_root,
        components=[
            example_gen,
            statistics_gen,
            schema_gen,
            example_validator,
            transform,
            trainer,
            pusher,
        ],
        enable_cache=False,
        metadata_connection_config=sqlite_metadata_connection_config(
            os.path.join(_pipeline_root, 'metadata.sqlite')
        ),
        beam_pipeline_args=[
            '--direct_running_mode=multi_processing',
            '--direct_num_workers=0',
        ]
    )

def run_pipeline():
    """
    Run the complete TFX pipeline.
    This function is called by realtime_update.py for automated retraining.
    
    Returns:
        bool: True if pipeline executed successfully, False otherwise
    """
    try:
        logging.set_verbosity(logging.INFO)
        
        # Ensure data directory exists
        os.makedirs(_data_root, exist_ok=True)
        
        # Check if data file exists, if not fetch it
        data_file = os.path.join(_data_root, 'bitcoin_prices.csv')
        if not os.path.exists(data_file):
            from tf_bitcoin_utils import fetch_bitcoin_prices
            print("Fetching Bitcoin data for pipeline...")
            data = fetch_bitcoin_prices(days=30)
            data.to_csv(data_file, index=False)
            print(f"Saved data to {data_file}")
        
        # Create and run the pipeline
        pipeline_obj = create_pipeline()
        BeamDagRunner().run(pipeline_obj)
        
        print("Pipeline executed successfully!")
        return True
        
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        logging.error(f"Pipeline execution failed: {e}")
        return False

if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    os.makedirs(_data_root, exist_ok=True)

    # Remove previous pipeline output for a clean run when running manually
    if os.path.exists(_pipeline_root):
        print(f"Removing previous pipeline output at {_pipeline_root}")
        shutil.rmtree(_pipeline_root)

    # Ensure we have data
    data_file = os.path.join(_data_root, 'bitcoin_prices.csv')
    if not os.path.exists(data_file):
        from tf_bitcoin_utils import fetch_bitcoin_prices
        print("Fetching initial Bitcoin data...")
        data = fetch_bitcoin_prices(days=30)
        data.to_csv(data_file, index=False)
        print(f"Saved data to {data_file}")

    # Run the pipeline
    success = run_pipeline()
    if success:
        print("Pipeline completed successfully!")
    else:
        print("Pipeline failed!")
        exit(1)