import os


class PipelineConfig:
    project_id = os.getenv("GCP_PROJECT_ID", "my-gcp-project")
    subscription = os.getenv("PUBSUB_SUBSCRIPTION", "data-events-dev-sub")
    topic_dlq = os.getenv("PUBSUB_DLQ_TOPIC", "data-events-dev-dlq")
    dataset = os.getenv("BQ_DATASET", "data_warehouse_dev")
    table = os.getenv("BQ_TABLE", "events")
    window_size_seconds = int(os.getenv("WINDOW_SIZE", "60"))
    bq_schema = "event_id:STRING,event_type:STRING,source:STRING,payload:JSON,event_timestamp:TIMESTAMP,processed_at:TIMESTAMP"
