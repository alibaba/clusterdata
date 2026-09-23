CREATE OR REPLACE TEMP TABLE t2_instances AS
SELECT workload AS name, count(*) AS instances FROM (
    SELECT DISTINCT workload, instance_id FROM daily
    WHERE workload IN ('online', 'offline') AND instance_id IS NOT NULL
) GROUP BY workload;
INSERT INTO t2_instances
SELECT 'all', count(*) FROM (SELECT DISTINCT instance_id FROM daily WHERE instance_id IS NOT NULL);

WITH groups AS NOT MATERIALIZED (
    SELECT workload AS name, * FROM daily WHERE workload IN ('online', 'offline')
    UNION ALL
    SELECT 'all' AS name, * FROM daily
), totals AS (
    SELECT name, count(DISTINCT app_id) AS apps,
           count(DISTINCT base_id) AS base_models, fsum(gpu_hours) AS gpu_hours
    FROM groups GROUP BY name
), per_base AS (
    SELECT name, base_id,
           max(CASE WHEN left(model_id, 2) IN ('b_', 'x_') THEN 1 ELSE 0 END)
           + count(DISTINCT CASE WHEN left(model_id, 2) IN ('s_', 'x_') THEN model_id END) AS variants
    FROM groups WHERE base_id IS NOT NULL GROUP BY name, base_id
), variants AS (
    SELECT name, sum(variants) AS variants FROM per_base GROUP BY name
)
SELECT t.name, apps, coalesce(instances, 0) AS instances, base_models,
       coalesce(variants, 0) AS variants, gpu_hours
FROM totals t LEFT JOIN variants v USING (name) LEFT JOIN t2_instances i USING (name)
ORDER BY CASE t.name WHEN 'online' THEN 1 WHEN 'offline' THEN 2 ELSE 3 END;
