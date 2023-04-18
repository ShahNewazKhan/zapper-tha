# zapper-tha
Zapper take home assessment

## Run interaction retriever

The interaction retriever is a python application that, given a smart contract address on the ethereum chain, returns the top 10 addresses that has the most amount of interactions with the address. 

The [_get_interaction_query](interaction_retriever.py#L15) function string interpolates the contract address we want to retrieve the interactions for using the following SQL query template. The interpolated SQL query selects data from the Ethereum network dataset on Google BigQuery to determine the top 10 Ethereum addresses that have had the most interactions with a given contract address in the last month.

It does so by first creating a common table expression (CTE) named [transaction_addresses](interaction_retriever.py#L24), which identifies all the addresses that have interacted with the specified contract address in the last month. To achieve this, the CTE selects all transactions that have occurred in the last month involving the specified contract address, and then extracts the from_address and to_address fields from each transaction using the UNNEST() function. If the to_address of the transaction matches the specified contract address, the from_address is selected as the address, otherwise, the to_address is selected as the address. The resulting CTE contains a list of unique addresses that have interacted with the specified contract address in the last month.

The [main query](interaction_retriever.py#L36) then selects data from the [transaction_addresses](interaction_retriever.py#L24) CTE and groups the data by address. It then counts the number of interactions each address had with the specified contract address and orders the results in descending order of interaction count. Finally, it limits the output to the top 10 addresses with the highest interaction count.

To run the `interaction retriever` app, you can pass in the contract address you want to get interaction data for as the first argument to the python invocation (**note** it [defaults](interaction_retriever.py#L51) to the [USDC](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) contact address ). 

```sh

# Create and activate  virtulaenv and install dependencies
virtualenv venv -p python3
source venv/bin/activate 
pip install -r requirements.txt

# Set GCP Service account envar
GCP_SA=zapper_tha_sa.json

# Retrieve all interactions with USDT
python interaction_retriever.py 0xdac17f958d2ee523a2206206994597c13d831ec7
```