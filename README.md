# Streaming Pipeline - Pub/Sub para BigQuery

Pipeline de streaming em tempo real usando Google Cloud Pub/Sub, Apache Beam (Dataflow) e BigQuery. Arquitetura event-driven com dead-letter queue e monitoramento integrado.

## Arquitetura

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

## Como Funciona

1. **Ingestao**: Mensagens JSON publicadas no Pub/Sub topic
2. **Processamento**: Dataflow pipeline le da subscription
3. **Validacao**: Schema validation com Pydantic (campos obrigatorios, tipos)
4. **Windowing**: Agregacao em janelas fixas de 1 minuto
5. **Escrita**: Mensagens validas -> BigQuery particionada
6. **DLQ**: Mensagens invalidas -> topico dead-letter para analise

## Como Executar

### Local (com emulador Pub/Sub)
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

## Monitoramento

O pipeline expoe metricas via Cloud Monitoring:
- Mensagens processadas/minuto
- Taxa de erro (% para DLQ)
- Latencia de processamento (p50, p95, p99)
- Throughput de escrita no BigQuery

Alertas configurados para: taxa de erro > 5%, latencia p95 > 30s, DLQ backlog > 1000 mensagens.

## Decisoes Tecnicas

**Por que Dataflow e nao Cloud Functions?** Dataflow (Apache Beam) suporta processamento continuo com windowing, backpressure automatico e exactly-once semantics. Cloud Functions tem timeout de 9 minutos e nao suporta windowing. Para streaming de dados, Dataflow e a escolha correta na GCP.

**Por que DLQ pattern?** Em producao, mensagens malformadas acontecem. Descartar silenciosamente perde dados. Enviar para DLQ permite: debug, reprocessamento apos correcao, e auditoria. Com retry policy de 5 tentativas antes do DLQ, mensagens transitoriamente invalidas tem chance de recover.

**Por que Pydantic para validacao?** Pydantic gera erros descritivos, valida tipos automaticamente e permite schemas reutilizaveis. Alternativas como validacao manual em Python sao propensas a erro e dificeis de manter.

## Estrutura

```
streaming-pipeline-pubsub-bigquery/
  pipeline/
    main.py          # Pipeline Apache Beam
    schema.py        # Schemas Pydantic
    config.py        # Configuracoes
    utils.py         # Helpers
  terraform/
    main.tf          # Infra Pub/Sub + BigQuery + Dataflow
    variables.tf
    outputs.tf
  tests/
    test_pipeline.py # Testes do pipeline
    test_schema.py   # Testes de validacao
  monitoring/
    dashboard.json   # Cloud Monitoring config
  .github/
    workflows/
      ci.yml         # Lint + testes + terraform validate
```

---

**Autor:** Diego Brito
