-- run duckdb cli . commands https://duckdb.org/docs/api/cli#special-commands-dot-commands
.open ./zapper.duckdb

-- read in parquet files as views 
create view interactions as select * from read_parquet('data/interactions/*.parquet');
create view token_holders as select * from read_parquet('data/token_holders/*.parquet');
