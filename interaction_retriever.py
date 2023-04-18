import sys
import os
import logging
from datetime import datetime, timedelta
from google.cloud import bigquery

# Init logger
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup BQ SA
BQ = bigquery.Client.from_service_account_json('zapper_tha_sa.json')

def _get_interaction_query(contract_address: str) -> str:
    """
    String interpolates a contract address to retrieve interaction
    information from the bigquery-public-data.crypto_ethereum.transactions
    dataset

    Returns the string formated query template with the contract address 
    """
    query = f"""
    WITH transaction_addresses AS (
        SELECT 
            CASE 
                WHEN to_address = '{contract_address}' THEN from_address 
                ELSE to_address 
            END AS address
        FROM `bigquery-public-data.crypto_ethereum.transactions`,
            UNNEST([to_address, from_address]) AS address
        WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
            AND '{contract_address}' IN UNNEST([to_address, from_address])
    )

    SELECT 
        address, 
        COUNT(*) AS interactions
    FROM transaction_addresses
    GROUP BY address
    ORDER BY interactions DESC
    LIMIT 10
    """

    return query

# Get the contract address from the command-line argument
if len(sys.argv) > 1:
    contract_address = sys.argv[1]
else:
    contract_address = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'

logger.info(f'Extracting information for contract address: {contract_address}')

query = _get_interaction_query(contract_address)
query_job = BQ.query(query)

# Convert the results to a Pandas DataFrame
df = query_job.to_dataframe()

# Enrich interactions dataframe with para data
START_DATE = (datetime.now() - timedelta(weeks=4)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")

df['_contract_address'] = contract_address
df['_start_date'] = START_DATE
df['_end_date'] =  END_DATE

parquet_path = f'data/interactions'
if not os.path.exists(parquet_path):
    os.makedirs(parquet_path)
df.to_parquet(os.path.join(parquet_path, f'{contract_address}.parquet'))
logger.info(f'flushed dataframe to {parquet_path}')

# Print the DataFrame
print(df)