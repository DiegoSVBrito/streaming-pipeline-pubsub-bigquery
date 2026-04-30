terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 5.0" }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_pubsub_topic" "events" {
  name                       = "${var.topic_name}-${var.env}"
  message_retention_duration = "86400s"
}

resource "google_pubsub_subscription" "events" {
  name                 = "${var.topic_name}-${var.env}-sub"
  topic                = google_pubsub_topic.events.name
  ack_deadline_seconds = 60
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dlq.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_topic" "dlq" {
  name = "${var.topic_name}-${var.env}-dlq"
}

resource "google_bigquery_dataset" "streaming" {
  dataset_id = "${var.dataset_id}-${var.env}"
  location   = var.region
}

resource "google_bigquery_table" "events" {
  dataset_id = google_bigquery_dataset.streaming.dataset_id
  table_id   = "events"
  time_partitioning {
    type                     = "DAY"
    field                    = "event_timestamp"
    require_partition_filter = true
  }
  schema = file("${path.module}/bigquery_schema.json")
}
