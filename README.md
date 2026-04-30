# Streaming Pipeline - Pub/Sub to BigQuery

Real-time streaming pipeline using Google Cloud Pub/Sub, Apache Beam (Dataflow) and BigQuery. Event-driven architecture with dead-letter queue and integrated monitoring.

## Architecture

```
+------------------+     +------------------+     +------------------+
|  Event Source    |     |   Pub/Sub        |     |   BigQuery       |
|  (API / App /    |---->|   Topic          |     |   Table          |
|   IoT / Webhook) |     |                  |     |   (partitioned)  |
+------------------+     +--------+---------+     +--------^---------+
                                  |                        |
                         +--------v---------+              |
                         |   Dataflow       |              |
                         |   (Apache Beam)  |--------------+
                         |   - Parse JSON   |
                         |   - Validate     |
                         |   - Window       |
                         |   - Transform    |
                         +--+-----+---------+
                            |     |
                  +---------+     +----------+
                  |                         |
         +--------v---------+     +---------v--------+
         |   Valid Messages  |     |  Invalid Messages |
         |   -> BigQuery     |     |  -> DLQ Topic     |
         +-------------------+     +-------------------+
```

## How It Works

1. **Ingestion**: JSON messages published to Pub/Sub topic
2. **Processing**: Dataflow pipeline reads from subscription
3. **Validation**: Schema validation with Pydantic (required fields, types)
4. **Windowing**: Aggregation in fixed 1-minute windows
5. **Write**: Valid messages -> partitioned BigQuery table
6. **DLQ**: Invalid messages -> dead-letter topic for analysis

## Running

### Local (with Pub/Sub emulator)
```bash
docker-compose up -d
python pipeline/main.py --runner DirectRunner
```

### Dataflow (GCP)
```bash
python pipeline/main.py \
  --runner DataflowRunner \
  --project my-gcp-project \
  --region us-east1 \
  --temp_location gs://dataflow-temp/staging
```

## Monitoring

The pipeline exposes metrics via Cloud Monitoring:
- Messages processed/minute
- Error rate (% to DLQ)
- Processing latency (p50, p95, p99)
- BigQuery write throughput

Alerts configured for: error rate > 5%, p95 latency > 30s, DLQ backlog > 1000 messages.

## Technical Decisions

**Why Dataflow over Cloud Functions?** Dataflow (Apache Beam) supports continuous processing with windowing, automatic backpressure, and exactly-once semantics. Cloud Functions has a 9-minute timeout and no windowing support. For data streaming, Dataflow is the correct choice on GCP.

**Why DLQ pattern?** In production, malformed messages happen. Silently dropping them loses data. Sending to DLQ enables: debugging, reprocessing after fixes, and auditing. With a 5-attempt retry policy before DLQ, transiently invalid messages have a chance to recover.

**Why Pydantic for validation?** Pydantic generates descriptive errors, validates types automatically, and allows reusable schemas. Manual validation in Python is error-prone and harder to maintain.

## Structure

```
streaming-pipeline-pubsub-bigquery/
  pipeline/
    main.py          # Apache Beam pipeline
    schema.py        # Pydantic schemas
    config.py        # Configuration
    utils.py         # Helpers
  terraform/
    main.tf          # Pub/Sub + BigQuery + Dataflow infra
    variables.tf
    outputs.tf
  tests/
    test_pipeline.py # Pipeline tests
    test_schema.py   # Validation tests
  .github/
    workflows/
      ci.yml         # Lint + test + terraform validate
```

---

Author: Diego Brito
