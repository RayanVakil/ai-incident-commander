# Incident Report: Inventory Overselling During Flash Sale

## Incident Summary
During the flash sale event, the platform experienced a significant inventory overselling issue, where customers were able to purchase items that were already out of stock. This was caused by a delay in the `inventory-service` updating stock levels, leading to the `order-service` using stale data when authorizing purchases. The business impact includes potential customer dissatisfaction, negative social media sentiment, and operational overhead from cancelling and refunding oversold orders.

## Root Cause
The root cause of the inventory overselling was insufficient throughput of the `inventory-service`'s Kafka consumer group responsible for processing order creation events. During the high-traffic flash sale, the rate of new orders (`orders.created` topic) far exceeded the rate at which the `inventory-service` could consume and process these messages to update stock counts. This created a significant consumer lag, causing inventory data in the `redis-inventory` cache to be stale. The `order-service`, relying on this stale data, incorrectly approved orders for out-of-stock items.

**Confidence Score**: 95%

## Supporting Evidence
1.  **Critical Alert `ALRT-0016: InventoryOversellGuardTripped`**: This alert fired, explicitly confirming that on-hand stock counts for some SKUs went negative.
2.  **Warning Alert `ALRT-0015: KafkaConsumerLagHigh`**: This alert showed a high consumer lag for the `inventory-sync` consumer group in the `inventory-service`, directly preceding and coinciding with the overselling alert.
3.  **Log Analysis**: Logs for the `inventory-service` were flooded with `WARN` messages showing significant Kafka consumer lag (e.g., `lag=37039`) for the `inventory.sync` topic, confirming the processing delay.
4.  **Service Architecture**: The `inventory-service` architecture diagram confirms it consumes `orders.created` events from Kafka to update the stock ledger, which is the process that failed to keep up.
5.  **Historical Incidents**: Three previous incidents (`INC-2026-009`, `INC-2026-015`, `INC-2026-016`) show the exact same pattern of "kafka_lag" leading to "delayed inventory sync". The root cause was consistently identified as consumer throughput being lower than the message production rate during traffic spikes.

## Immediate Remediation
1.  **Scale Kafka Consumers**: Immediately increase the number of replicas for the `inventory-service` to scale up the number of consumers in the `inventory-sync` group. This will increase parallel processing and help clear the consumer lag.
2.  **Increase Kafka Partitions**: If scaling consumers is not sufficient, increase the number of partitions for the `orders.created` Kafka topic to allow for greater parallelism.
3.  **Manual Inventory Reconciliation**: The Fulfilment team must run a reconciliation script to identify all oversold SKUs and determine the full scope of affected orders.
4.  **Customer Communication**: The Customer Support team should be notified with a list of affected customers to proactively manage communications regarding order cancellations and refunds.

## Prevention
1.  **Implement Consumer Autoscaling**: Configure Horizontal Pod Autoscaler (HPA) for the `inventory-service` to automatically scale the number of consumer pods based on Kafka consumer lag metrics. This will allow the service to dynamically respond to traffic spikes like flash sales.
2.  **Tune Consumer Batching**: Review and tune the Kafka consumer configuration (`max.poll.records`, `fetch.min.bytes`) and the database write batch size within the `inventory-service`. This will improve throughput by allowing the service to process messages in larger, more efficient chunks.
3.  **Improve Alerting**: Promote the `KafkaConsumerLagHigh` alert from a `warning` to a `critical` alert and lower its threshold to trigger earlier. This will provide an earlier warning signal before overselling occurs.
4.  **Pre-Sale Runbook**: Update the "Flash Sale Readiness" runbook to include a step for pre-scaling the `inventory-service` and other critical Kafka consumers before a planned high-traffic event.