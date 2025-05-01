# RUNNING THE PROJECT 
- Run the command : "docker-compose up --build". 
- On running this command  the following things happen:
1. This build step insatlls all the quired libraries in the requirements.txt file
2. Docker compose starts all the defined Services:
    - Neo4j : Launches the Neo4j database container, sets the password, plugins, and persists data in a Docker volume.
    - Loader : Launches your custom Python container, which waits for Neo4j to be ready, then runs your load_backup_to_db.py script to load your backup transactions into the database
3. The -- build ensures everything is upto date

# LATER STEPS

- Run the realTimeDataIngestion.ipynb File for real time data Ingestions. There are two parts in this notebook:
1. The First part involves executing the latest block Transactions - (The latest confirmed Transactions that are attached to the Block chain network)
2. The second part involes executing the unconfirmed Transactions in real time with websocket. (Note: this API runs until you stop the execution)

- After performing each of the step, the data is ingested into the neo4j database which you can view at this Url : 'http://localhost:7474/browser/'

- For Viewing all the relationships that have been established during the ingestion. Run this cypher query in the Neo4j browser - 
'MATCH (a)-[r]->(b)
RETURN a, r, b' 

- For better visibility use LIMIT, to limit the transactions. The below command ensures that exactly 25 relationships are shown
'MATCH (a)-[r]->(b)
RETURN a, r, b LIMIT 25' 