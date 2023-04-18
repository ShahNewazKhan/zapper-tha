# Zapper take home assessment

## Solution for Question 1

The [interaction retriever](interaction_retriever.py) is a python application that, given a smart contract address on the ethereum chain, returns the top 10 addresses that has the most amount of interactions with the address. 

The [_get_interaction_query](interaction_retriever.py#L15) function string interpolates the contract address we want to retrieve the interactions for using the following [SQL query template](interaction_retriever.py#L24). The interpolated SQL query selects data from the Ethereum network dataset on Google BigQuery to determine the top 10 Ethereum addresses that have had the most interactions with a given contract address in the last month.

It does so by first creating a common table expression (CTE) named [transaction_addresses](interaction_retriever.py#L24), which identifies all the addresses that have interacted with the specified contract address in the last month. To achieve this, the CTE selects all transactions that have occurred in the last month involving the specified contract address, and then extracts the from_address and to_address fields from each transaction using the UNNEST() function. If the to_address of the transaction matches the specified contract address, the from_address is selected as the address, otherwise, the to_address is selected as the address. The resulting CTE contains a list of unique addresses that have interacted with the specified contract address in the last month.

The [main query](interaction_retriever.py#L36) then selects data from the [transaction_addresses](interaction_retriever.py#L24) CTE and groups the data by address. It then counts the number of interactions each address had with the specified contract address and orders the results in descending order of interaction count. Finally, it limits the output to the top 10 addresses with the highest interaction count.

To run the `interaction retriever` app, you can pass in the contract address you want to get interaction data for as the first argument to the python invocation (**note** it [defaults](interaction_retriever.py#L51) to the [USDC](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) contact address ). 

To run the following code you need to pass in the path to a [GCP Service Account Key JSON](https://cloud.google.com/iam/docs/keys-create-delete) that has the [Big Query Job User role](https://cloud.google.com/iam/docs/understanding-roles#bigquery.jobUser) set to the `GCP_SA` envar.

```sh
# Create and activate  virtulaenv and install dependencies
virtualenv venv -p python3
source venv/bin/activate 
pip install -r requirements.txt

# Set GCP Service account envar
# Retrieve all interactions with USDT
GCP_SA=zapper_tha_sa.json python interaction_retriever.py 0xdac17f958d2ee523a2206206994597c13d831ec7
```

```sh
INFO:__main__:Extracting information for contract address: 0xdac17f958d2ee523a2206206994597c13d831ec7
INFO:__main__:flushed dataframe to data/interactions
                                      address  interactions                           _CONTRACT_ADDRESS _start_date   _end_date
0  0xa152f8bb749c55e9943a3a0a3111d18ee2b3f94e        132922  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
1  0x56eddb7aa87536c09ccc2793473599fd21a8b17f        127016  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
2  0x21a31ee1afc51d94c2efccaa2092ad1028285549        122292  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
3  0xdfd5293d8e347dfe59e90efd55b2956a1343963d        122178  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
4  0x46340b20830761efd32832a74d7169b29feb9758        116174  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
5  0x9696f59e4d72e237be84ffd425dcad154bf96976        115274  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
6  0x28c6c06298d514db089934071355e5743bf21d60        102054  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
7  0xf89d7b9c864f589bbf53a82105107622b35eaa40         96806  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
8  0x6dfc34609a05bc22319fa4cce1d1e2929548c0d7         66884  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
9  0x974caa59e49682cda0ad2bbe82983419a2ecc400         66804  0xdac17f958d2ee523a2206206994597c13d831ec7  2023-03-21  2023-04-18
```