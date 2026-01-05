# Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps

[Code](https://github.com/google/mcp/tree/main/examples/launchmybakery) & [Codelab](https://codelabs.developers.google.com/adk-mcp-bigquery-maps#1)

## To setup easily and directly from this repo:
1. Edit the .env file and add your project and mcp user.

2. Set the .env variables:
```
cd ./other_agents/MCP_BQ_GMaps/
export $(cat .env | xargs)
gcloud config set project $PROJECT_ID
```

3. Update gcloud:
```
gcloud components update
```

4. Do the initial environment setup: 
```
chmod +x setup/setup_env.sh
./setup/setup_env.sh
```

5. Create the tables in bigquery:
```
chmod +x setup/setup_bigquery.sh
./setup/setup_bigquery.sh
```

## To run the agent:
```
adk web
```

**Sample Questions:**

*   "I’m looking to open my fourth bakery location in Los Angeles. I need a neighborhood with early activity. Find the zip code with the highest 'morning' foot traffic score."
*   "Can you search for 'Bakeries' in that zip code to see if it's saturated? If there are too many, check for 'Specialty Coffee' shops, so I can position myself near them to capture foot traffic."
*    "Okay and I want to position this as a premium brand. What is the maximum price being charged for a 'Sourdough Loaf' in the LA Metro area?"
*    "Now I want a revenue projection for December 2025. Look at my sales history and take data from my best performing store for the 'Sourdough Loaf'. Run a forecast for December 2025 to estimate the quantity I'll sell. Then, calculate the projected total revenue using just under the premium price we found (let's use $18)"
*    "That'll cover my rent. Lastly, let's verify logistics. Find the closest "Restaurant Depot" to the proposed area and make sure that drive time is under 30 minutes for daily restocking."
