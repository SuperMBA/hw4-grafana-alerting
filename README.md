#  Алертинг в Grafana при нарушении SLO

## Цель
Настроить наблюдаемость ML-сервиса с помощью Prometheus и Grafana, определить SLO и настроить алерт в Grafana при его нарушении.

## Выбранный SLO
**Latency SLO:** p95 latency < **1 секунды** (по окну 5 минут).  
Нарушение SLO: p95 latency **> 1 секунды** в течение **2 минут**.

## Архитектура (что поднято)
Запускается через Docker Compose:
- `ml_service` — Python/FastAPI сервис с `/predict` и `/metrics`
- `prometheus` — сбор метрик
- `grafana` — визуализация + алертинг
- `alert_receiver` — webhook-ресивер для демонстрации доставки уведомления (в логах контейнера)

## Как запустить проект
В корне проекта:

```bash
docker compose up --build -d
```
# Проверка статуса контейнеров:

```bash
docker compose ps
```
# Метрики (реализация в сервисе)
В сервисе используется Prometheus Histogram для латентности:

Метрика: request_latency_seconds (Histogram)

Сервис отдаёт метрики по адресу:

http://localhost:8001/metrics

Тестовый endpoint:

http://localhost:8001/predict?sleep_ms=200

Prometheus (конфигурация и проверка)
Конфигурация: prometheus/prometheus.yml

Prometheus собирает метрики с сервиса:

```bash
scrape_configs:
  - job_name: "ml_service"
    metrics_path: /metrics
    static_configs:
      - targets: ["ml_service:8000"]
```
Проверка, что таргет UP:

http://localhost:9090/targets


## Grafana (дашборд и запрос)
Grafana доступна по адресу:

http://localhost:3000 (логин/пароль по умолчанию: admin/admin)

# Источник данных:

Prometheus: http://prometheus:9090

Запрос для p95 latency (PromQL):

```bash
histogram_quantile(0.95, sum(rate(request_latency_seconds_bucket[5m])) by (le))
```
Экспортированный дашборд:

dashboards/p95_latency_dashboard.json

# Alerting в Grafana (правило алерта)
Rule name: HighLatencyP95
Условие: p95 latency > 1 сек
Evaluate every: 1m
For (pending period): 2m

Уведомления настроены через webhook contact point:

Contact point: receiver-webhook

URL: http://alert_receiver:8081/webhook

# Проверка срабатывания алерта
Для искусственного увеличения latency выполнялась нагрузка:
```bash
for /L %i in (1,1,200) do @curl -s "http://localhost:8001/predict?sleep_ms=2000" > nul & timeout /t 1 > nul
```
Ожидаемое поведение:

правило переходит из Pending в состояние Firing (Alerting)

webhook отправляется в alert_receiver (видно в логах контейнера)

Просмотр логов receiver:

```bash
docker compose logs -f alert_receiver
```
## Скриншоты (результаты)
Скриншоты находятся в папке screens/:

Панель с метрикой p95 latency

Сработавший алерт (Firing / Alerting)

Уведомление (webhook получен receiver’ом)
