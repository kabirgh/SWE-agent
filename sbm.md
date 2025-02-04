python run.py \
  --model_name openrouter/anthropic/claude-3.5-sonnet \
  --data_path plodq/sbm \
  --split test \
  --no_mirror \
  --config_file config/default.yaml \
  --per_instance_cost_limit 2.00 \
  --total_cost_limit 50.00 \
  --raise_exceptions \
  --skip_existing \
  --instance_filter '(?!(apache__druid-13704|apache__lucene-13704|facebook__docusaurus-9183|google__gson-2479|apache__druid-14136|caddyserver__caddy-5404|facebook__docusaurus-9897|hashicorp__terraform-34814|apache__druid-15402|caddyserver__caddy-6115|gohugoio__hugo-12448|jqlang__jq-2235|apache__druid-16875|caddyserver__caddy-6345|google__gson-2024|jqlang__jq-2658|apache__lucene-12626|facebook__docusaurus-10130|google__gson-2061|jqlang__jq-2750|apache__lucene-13301|facebook__docusaurus-10309|google__gson-2134|micropython__micropython-12158|apache__lucene-13494|facebook__docusaurus-8927|google__gson-2158)).*'


python run.py \
  --model_name or/gemini-pro-1.5 \
  --data_path plodq/sbm \
  --split test \
  --no_mirror \
  --config_file config/default.yaml \
  --per_instance_cost_limit 2.00 \
  --total_cost_limit 50.00 \
  --raise_exceptions \
  --skip_existing

python run.py   --model_name gpt-4o-2024-08-06 \
--data_path plodq/sbm \
--split test \
--no_mirror \
--config_file config/default.yaml \
--per_instance_cost_limit 2.00 \
--total_cost_limit 50.00 \
--tpm_limit 350_000 \
--raise_exceptions \
--skip_existing \
--instance_filter '(apache__lucene-13704|babel__babel-16130|apache__druid-15402|hashicorp__terraform-34900|jqlang__jq-2650|jqlang__jq-2750|nlohmann__json-4237|nushell__nushell-12950|nushell__nushell-13246|nushell__nushell-13605|projectlombok__lombok-3674|projectlombok__lombok-3697|redis__redis-10764)'
