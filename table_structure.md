# Database Tabellen Structuur

## Structuur van de tabel 'serializedlmp'

| Column ID | Name | Type | Not Null | Default Value | Primary Key |
|-----------|------|------|----------|---------------|-------------|
| 0 | lmp_id | VARCHAR | 1 | None | 1 |
| 1 | name | VARCHAR | 1 | None | 0 |
| 2 | source | VARCHAR | 1 | None | 0 |
| 3 | dependencies | VARCHAR | 1 | None | 0 |
| 4 | created_at | TIMESTAMP | 1 | None | 0 |
| 5 | lmp_type | VARCHAR(10) | 1 | None | 0 |
| 6 | api_params | JSON | 0 | None | 0 |
| 7 | initial_free_vars | JSON | 0 | None | 0 |
| 8 | initial_global_vars | JSON | 0 | None | 0 |
| 9 | num_invocations | INTEGER | 0 | None | 0 |
| 10 | commit_message | VARCHAR | 0 | None | 0 |
| 11 | version_number | INTEGER | 0 | None | 0 |

## Structuur van de tabel 'serializedlmpuses'

| Column ID | Name | Type | Not Null | Default Value | Primary Key |
|-----------|------|------|----------|---------------|-------------|
| 0 | lmp_user_id | VARCHAR | 1 | None | 1 |
| 1 | lmp_using_id | VARCHAR | 1 | None | 2 |

## Structuur van de tabel 'invocation'

| Column ID | Name | Type | Not Null | Default Value | Primary Key |
|-----------|------|------|----------|---------------|-------------|
| 0 | id | VARCHAR | 1 | None | 1 |
| 1 | lmp_id | VARCHAR | 1 | None | 0 |
| 2 | latency_ms | FLOAT | 1 | None | 0 |
| 3 | prompt_tokens | INTEGER | 0 | None | 0 |
| 4 | completion_tokens | INTEGER | 0 | None | 0 |
| 5 | state_cache_key | VARCHAR | 0 | None | 0 |
| 6 | created_at | TIMESTAMP | 1 | None | 0 |
| 7 | used_by_id | VARCHAR | 0 | None | 0 |

## Structuur van de tabel 'invocationtrace'

| Column ID | Name | Type | Not Null | Default Value | Primary Key |
|-----------|------|------|----------|---------------|-------------|
| 0 | invocation_consumer_id | VARCHAR | 1 | None | 1 |
| 1 | invocation_consuming_id | VARCHAR | 1 | None | 2 |

## Structuur van de tabel 'invocationcontents'

| Column ID | Name | Type | Not Null | Default Value | Primary Key |
|-----------|------|------|----------|---------------|-------------|
| 0 | invocation_id | VARCHAR | 1 | None | 1 |
| 1 | params | JSON | 0 | None | 0 |
| 2 | results | JSON | 0 | None | 0 |
| 3 | invocation_api_params | JSON | 0 | None | 0 |
| 4 | global_vars | JSON | 0 | None | 0 |
| 5 | free_vars | JSON | 0 | None | 0 |
| 6 | is_external | BOOLEAN | 1 | None | 0 |

## Structuur van de tabel 'evaluation'

| Column ID | Name | Type | Not Null | Default Value | Primary Key |
|-----------|------|------|----------|---------------|-------------|
| 0 | id | VARCHAR | 0 | None | 1 |
| 1 | invocation_id | VARCHAR | 1 | None | 0 |
| 2 | metric_name | VARCHAR | 1 | None | 0 |
| 3 | metric_value | FLOAT | 1 | None | 0 |
| 4 | created_at | TIMESTAMP | 1 | None | 0 |

