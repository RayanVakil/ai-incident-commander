### Incident Report: Checkout Service Latency Spike

#### **Incident Summary**
On June 13th, starting around 09:08 UTC, the `checkout-service` experienced a significant increase in p95 latency, leading to slow checkout processes for customers and a drop in the checkout success rate. The issue was triggered by connection problems to the `redis-cart` cache, causing the service to fall back to a slower database, thereby increasing overall transaction time.

#### **Root Cause**
**An AWS ElastiCache failover event for the `redis-cart` cluster caused a cascading failure in the `checkout-service`.** When the primary Redis node failed over, all 16 replicas of the `checkout-service` attempted to reconnect simultaneously. The Jedis client's connection pool was not configured to handle this sudden surge of reconnection attempts, leading to pool exhaustion. Consequently, requests for cart and session data from Redis began to time out, forcing the service to fall back to reading from its primary PostgreSQL database. This database fallback is significantly slower and was the direct cause of the user-facing latency.

**Confidence Score**: 95%

#### **Supporting Evidence**
1.  **Alert Correlation**:
    - `ALRT-0018: RedisCartConnectionErrors` triggered at `2026-06-13T09:06:00Z` for `checkout-service`.
    - `ALRT-0017: HighCheckoutLatency` triggered just two minutes later at `2026-06-13T09:08:00Z`, confirming the direct relationship between the Redis issue and the latency spike.

2.  **Log Analysis (`checkout-service`)**:
    - **Connection Pool Exhaustion**: Logs show explicit exceptions: `redis.clients.jedis.exceptions.JedisConnectionException: Could not get a resource from the pool`.
    - **Cache Timeouts & DB Fallback**: Logs show multiple messages like: `redis-cart GET timed out for key ... after 2000ms; falling back to PostgreSQL`. This proves the service was degrading performance by hitting the database instead of the cache.
    - **ElastiCache Failover**: Logs contained warnings pointing to the underlying trigger: `redis-cart connection reset (ElastiCache primary failover detected); reconnecting`.

3.  **Historical Precedent**:
    - A search for historical incidents revealed at least three prior SEV2 incidents (`INC-2026-006`, `INC-2025-024`, `INC-2025-037`) with the identical root cause: "ElastiCache node failover; client pool exhausted / slow to reconnect". This demonstrates a recurring architectural vulnerability.

#### **Immediate Remediation**
*The incident has self-resolved as the Redis connection pool eventually recovered. However, the system remains vulnerable.*

1.  **Increase Redis Connection Pool Size**: Immediately increase the `max-total` connections setting in the Jedis client configuration for `checkout-service` by 50% as a short-term mitigation against pool exhaustion.
2.  **Initiate Proactive ElastiCache Failover**: Manually trigger a failover of the `redis-cart` cluster during a low-traffic period to validate the new pool settings and ensure the service reconnects gracefully without causing a latency spike.

#### **Prevention**
1.  **Tune Redis Client Settings**:
    - **Implement Exponential Backoff with Jitter**: Configure the Redis client to use an exponential backoff with jitter for reconnection attempts. This will prevent all service replicas from retrying in a thundering herd after a failover.
    - **Review and Lower Connection Timeouts**: The current 2000ms timeout is too long. Lower the `connectionTimeout` and `socketTimeout` to fail faster and prevent threads from being tied up, which exacerbates pool exhaustion.

2.  **Improve Fallback Caching**:
    - **Introduce a Negative Cache**: When the database fallback occurs, cache the result in an in-memory cache (e.g., Caffeine) for a very short duration (e.g., 1-2 seconds). This will prevent multiple concurrent requests for the same cart from repeatedly hitting the database during a Redis outage.

3.  **Address Recurring Incidents**:
    - **Escalate Postmortem Actions**: The fact that this is a recurring incident indicates that previous prevention measures were not implemented or were insufficient. Escalate the implementation of the above prevention steps to the Checkout and SRE leadership teams to ensure they are prioritized.
    - **Create a Runbook**: Document this specific failure mode in the `checkout-service` runbook, with clear steps on how to diagnose and remediate Redis connection pool issues.