import os
from absl import logging
from tfx.orchestration import pipeline
from tfx.orchestration.beam.beam_dag_runner import BeamDagRunner
from tfx.components import CsvExampleGen, StatisticsGen, SchemaGen, ExampleValidator, Transform, Trainer, Pusher
from tfx.proto import trainer_pb2, pusher_pb2
from tfx.orchestration.metadata import sqlite_metadata_connection_config

_pipeline_name = 'bitcoin_price_pipeline'
_pipeline_root = os.path.join(os.getcwd(), 'tfx_pipeline_output', _pipeline_name)
_data_root = os.path.join(os.getcwd(), 'data')  # <-- CSV files should be here
_module_file_transform = os.path.join(os.getcwd(), 'transform.py')
_module_file_trainer = os.path.join(os.getcwd(), 'trainer.py')
_serving_model_dir = os.path.join(_pipeline_root, 'serving_model')

def create_pipeline():
    example_gen = CsvExampleGen(input_base=_data_root)

    statistics_gen = StatisticsGen(examples=example_gen.outputs['examples'])
    schema_gen = SchemaGen(statistics=statistics_gen.outputs['statistics'], infer_feature_shape=True)
    example_validator = ExampleValidator(statistics=statistics_gen.outputs['statistics'], schema=schema_gen.outputs['schema'])

    transform = Transform(
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        module_file=_module_file_transform)

    trainer = Trainer(
        module_file=_module_file_trainer,
        examples=transform.outputs['transformed_examples'],
        transform_graph=transform.outputs['transform_graph'],
        schema=schema_gen.outputs['schema'],
        train_args=trainer_pb2.TrainArgs(num_steps=100),
        eval_args=trainer_pb2.EvalArgs(num_steps=50))

    pusher = Pusher(
        model=trainer.outputs['model'],
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(base_directory=_serving_model_dir)))

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
        enable_cache=True,
        metadata_connection_config=sqlite_metadata_connection_config(
            os.path.join(_pipeline_root, 'metadata.db')),
        beam_pipeline_args=[
            '--direct_running_mode=multi_processing',
            '--direct_num_workers=0',
        ])

if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    BeamDagRunner().run(create_pipeline())
