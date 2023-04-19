-- run duckdb cli . commands https://duckdb.org/docs/api/cli#special-commands-dot-commands
.open ./zapper.duckdb

-- read in parquet files as views 
CREATE OR REPLACE VIEW interactions AS SELECT * FROM read_parquet('data/interactions/*.parquet');
CREATE OR REPLACE VIEW token_holders As SELECT * FROM read_parquet('data/token_holders/*.parquet');
