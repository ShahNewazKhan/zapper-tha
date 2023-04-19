import sys
import os
import logging
from datetime import datetime, timedelta
from google.cloud import bigquery

# Init logger
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATE_INTERVAL = os.environ.get('DATE_INTERVAL','DAY')
ZAPPER_THA_SA = os.environ.get('GCP_SA')

# Setup BQ SA
BQ = bigquery.Client.from_service_account_json(ZAPPER_THA_SA)

def _get_holder_query(CONTRACT_ADDRESS: str) -> str:
    """
    String interpolates a contract address to retrieve token holder
    information from the bigquery-public-data.crypto_ethereum.token_transfers 
    table

    Returns the string formated query template with the contract address 
    """
    query = f"""
    SELECT
        CASE 
            WHEN to_address = '{CONTRACT_ADDRESS}' THEN from_address
            ELSE to_address
        END AS holder
    FROM `bigquery-public-data.crypto_ethereum.token_transfers`
    WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 {DATE_INTERVAL})
        AND token_address = '{CONTRACT_ADDRESS}'
    GROUP BY holder
    """
    logger.info(f"QUERY: {query}")
    return query

# Get the contract address from the command-line argument
if len(sys.argv) > 1:
    CONTRACT_ADDRESS = sys.argv[1]
else:
    CONTRACT_ADDRESS = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'

logger.info(f'Extracting token holder information for contract address: {CONTRACT_ADDRESS} for the last {DATE_INTERVAL}')

query = _get_holder_query(CONTRACT_ADDRESS)
query_job = BQ.query(query)

# Convert the results to a Pandas DataFrame
df = query_job.to_dataframe()

# Enrich interactions dataframe with para data
START_DATE = (datetime.now() - timedelta(weeks=4)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")

df['_contract_address'] = CONTRACT_ADDRESS
df['_start_date'] = START_DATE
df['_end_date'] =  END_DATE
df['_processing_time'] = datetime.now()

# Flush dataframe to parquet 
parquet_path = f'data/token_holders'
if not os.path.exists(parquet_path):
    os.makedirs(parquet_path)
df.to_parquet(os.path.join(parquet_path, f'{CONTRACT_ADDRESS}_{END_DATE}.parquet'))
logger.info(f'flushed dataframe to {parquet_path}')
