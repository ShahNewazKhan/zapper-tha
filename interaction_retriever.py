import sys
from google.cloud import bigquery

BQ = bigquery.Client.from_service_account_json('zapper_tha_sa.json')


def _get_interaction_query(contract_address: str) -> str:
    """
    String interpolates a contract address to retrieve interaction
    information from the bigquery-public-data.crypto_ethereum.transactions
    dataset

    Returns str the string formated query template with the contract address 
    """
    query = f"""
    SELECT from_address, COUNT(*) as interaction_count
    FROM `bigquery-public-data.crypto_ethereum.transactions`
    WHERE to_address = '{contract_address}'
    AND DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
    GROUP BY from_address
    ORDER BY interaction_count DESC
    LIMIT 10
    """

    return query

# Get the contract address from the command-line argument
if len(sys.argv) > 1:
    contract_address = sys.argv[1]
else:
    contract_address = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'


query = _get_interaction_query(contract_address)
query_job = BQ.query(query)

# Convert the results to a Pandas DataFrame
df = query_job.to_dataframe()

# Print the DataFrame
print(df)