# Technical Decisions

## ADR-001: Dataflow over Cloud Functions

**Status:** Accepted

**Context:** Real-time event stream processing on GCP.

**Decision:** Use Dataflow (Apache Beam) as the streaming runner.

**Rationale:**
- Native support for windowing and sessionization
- Exactly-once semantics for BigQuery writes
- Auto-scaling with automatic backpressure
- No timeout limit (Cloud Functions = 9 min)
- Testable locally with DirectRunner

## ADR-002: DLQ Pattern

**Status:** Accepted

**Context:** Handling malformed messages in the streaming pipeline.

**Decision:** Implement Dead-Letter Queue with retry and alerting.

**Rationale:**
- No messages silently dropped
- Retry (5 attempts) for transient errors
- Post-fix analysis and reprocessing
- Data quality metrics in the pipeline

## ADR-003: Fixed 1-Minute Windowing

**Status:** Accepted

**Context:** Aggregation strategy for batch writes to BigQuery.

**Decision:** Fixed windows of 60 seconds.

**Rationale:**
- Balance between latency and throughput
- BigQuery performs better with micro-batches vs row-by-row
- 1-minute window is sufficient for real-time metric aggregation
- Configurable via environment variable
