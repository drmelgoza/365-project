# Performance Writeup

## 1. Fake Data Modeling

We added exactly 1,004,754 rows to the database to simulate realistic production traffic.

**Table Breakdown:**
*   `users`: 10,000
*   `user_items`: 100,625
*   `user_logs`: 257,528
*   `log_items`: 515,422
*   `user_plans`: 15,758
*   `plan_items`: 105,421

**Justification:**
We used a right-skewed negative binomial distribution to mimic real users. Most users log very little, but a few "power users" log hundreds of meals. Because every meal log contains multiple food items, the `log_items` table naturally became the largest table (~515k rows).

[Link to fake_data.py script](./fake_data.py)



## 2. Slowest Endpoints
When tested against the 1M+ row database:
1.  **GET /users/{user_id}/logs** — **66.47 ms** *(Target for optimization)*
2.  **GET /users/{user_id}/items** — **7.34 ms**
3.  **GET /plans/{user_id}/plan** — **2.19 ms**



## 3. Performance Improvement

We chose to optimize the slowest endpoint: **`GET /users/{user_id}/logs`**. 

### Before Indexing
Postgres does not automatically index foreign keys. Looking up logs for a power user triggered a massive sequential scan across the 515k row `log_items` table. 

```sql
-- Execution Time: 64.20 ms
->  Parallel Seq Scan on log_items li  (cost=0.00..5430.59 rows=214759)
```

### The Fix
Added indexes on user and log foreign keys:
```sql
CREATE INDEX idx_user_logs_user_id ON user_logs(user_id);
CREATE INDEX idx_log_items_log_id ON log_items(log_id);
```

### The Result
Query execution switched to an index scan, reducing query time to **0.97 ms** (**~65x faster**):
```sql
-- Execution Time: 0.97 ms
->  Index Scan using idx_log_items_log_id on log_items li (cost=0.42..8.46 rows=2)
```

**Conclusion:** Adding these indexes reduced the database query time from **64.20 ms** to **0.97 ms**, making the endpoint approximately **65x faster**.
