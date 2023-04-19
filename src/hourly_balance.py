import duckdb, logging, os
from web3 import Web3
from eth_utils import to_checksum_address
from google.cloud import bigquery

# Init logger
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATE_INTERVAL = os.environ.get('DATE_INTERVAL','DAY')
ZAPPER_THA_SA = os.environ.get('GCP_SA')

# Setup BQ SA
BQ = bigquery.Client.from_service_account_json(ZAPPER_THA_SA)

# Set up DuckDB database
con = duckdb.connect(database='zapper.duckdb', read_only=False)
con.execute("CREATE OR REPLACE TABLE balance (timestamp TIMESTAMP, balance FLOAT)")

# Define the contract address and user wallet address to query
contract_address = '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984' # UNISWAP
user_wallet_address = "0xad6eaa735D9dF3D7696fd03984379dAE02eD8862"

# Query BigQuery for transaction data for the past month
query = f"""
    SELECT
        block_timestamp,
        value
    FROM
        `bigquery-public-data.crypto_ethereum.token_transfers`
    WHERE
        token_address = '{contract_address}'
        AND to_address = '{user_wallet_address}'
        AND block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 {DATE_INTERVAL})
    ORDER BY
        block_timestamp ASC
"""
df = BQ.query(query).to_dataframe()

# Parse the transaction data to calculate wallet balance over time
balance = 0
for index, row in df.iterrows():
    balance += int(row["value"])
    con.execute(f"INSERT INTO balance VALUES ('{row['block_timestamp']}', {balance / 10**18})")

# Generate hourly view of wallet balance
hourly_view_query = """
    SELECT
        hour,
        SUM(balance) OVER (ORDER BY hour) as balance
    FROM (
        SELECT
            DATE_TRUNC('hour', timestamp) as hour,
            SUM(balance) as balance
        FROM
            balance
        GROUP BY
            hour
    )
    ORDER BY
        hour ASC;
"""

hourly_view = con.execute(hourly_view_query).fetch_df()

# Print the hourly view of the wallet balance
print(hourly_view)
