CREATE OR REPLACE TEMP TABLE t4_instances AS
SELECT model_arch AS name, count(*) AS instances FROM (
    SELECT DISTINCT model_arch, instance_id FROM daily
    WHERE workload IN ('online', 'offline') AND instance_id IS NOT NULL
) GROUP BY model_arch;

WITH activity AS (
    SELECT model_arch AS name, count(DISTINCT app_id) AS apps,
           fsum(gpu_hours) AS gpu_hours
    FROM daily WHERE workload IN ('online', 'offline') GROUP BY model_arch
), models AS NOT MATERIALIZED (
    SELECT * FROM daily WHERE base_id IS NOT NULL AND gpu_hours > 0
), bases AS (
    SELECT CASE WHEN base_arch = 'unknown' THEN 'dense' ELSE base_arch END AS name,
           count(DISTINCT base_id) AS base_models
    FROM models GROUP BY name
), per_base AS (
    SELECT variant_arch AS name, base_id,
           max(CASE WHEN left(model_id, 2) IN ('b_', 'x_') THEN 1 ELSE 0 END)
           + count(DISTINCT CASE WHEN left(model_id, 2) IN ('s_', 'x_') THEN model_id END) AS variants
    FROM models GROUP BY variant_arch, base_id
), variants AS (
    SELECT name, sum(variants) AS variants FROM per_base GROUP BY name
)
SELECT name, apps, coalesce(instances, 0) AS instances, coalesce(base_models, 0) AS base_models,
       coalesce(variants, 0) AS variants, gpu_hours
FROM activity FULL OUTER JOIN bases USING (name) FULL OUTER JOIN variants USING (name)
LEFT JOIN t4_instances USING (name)
ORDER BY name;
