import argparse
import json
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

from config import PipelineConfig
from schema import EventMessage
from utils import setup_logging, parse_message


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", default="DirectRunner")
    known_args, pipeline_args = parser.parse_known_args(argv)
    setup_logging()

    config = PipelineConfig()
    options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=options) as p:
        messages = (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(
                subscription=f"projects/{config.project_id}/subscriptions/{config.subscription}"
            )
            | "Decode" >> beam.Map(lambda m: m.decode("utf-8"))
            | "ParseJSON" >> beam.Map(json.loads)
        )

        validated = messages | "Validate" >> beam.Map(parse_message)
        valid = validated | "FilterValid" >> beam.Filter(lambda m: m["valid"])
        invalid = validated | "FilterInvalid" >> beam.Filter(lambda m: not m["valid"])

        (
            valid
            | "ExtractPayload" >> beam.Map(lambda m: m["data"].model_dump())
            | "Window1Min" >> beam.WindowInto(beam.window.FixedWindows(60))
            | "WriteBigQuery" >> beam.io.WriteToBigQuery(
                table=f"{config.project_id}:{config.dataset}.{config.table}",
                schema=config.bq_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )

        (
            invalid
            | "FormatDLQ" >> beam.Map(lambda m: json.dumps(m).encode("utf-8"))
            | "WriteDLQ" >> beam.io.WriteToPubSub(
                topic=f"projects/{config.project_id}/topics/{config.topic_dlq}"
            )
        )


if __name__ == "__main__":
    run()
