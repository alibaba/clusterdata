WITH groups AS NOT MATERIALIZED (
    SELECT CASE WHEN pd_role IN ('prefill', 'decode') THEN 'PD-Disagg' ELSE 'PD-Colloc' END AS name, *
    FROM daily WHERE workload = 'online'
), totals AS (
    SELECT name, count(DISTINCT app_id) AS apps,
           count(DISTINCT instance_id) AS instances,
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
SELECT t.name, apps, instances, base_models, coalesce(variants, 0) AS variants, gpu_hours
FROM totals t LEFT JOIN variants v USING (name)
ORDER BY name;
