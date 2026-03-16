# BigQuery Knowledge Graph Agent

This sample AI Agent built natively with the **Google Agent Development Kit (ADK)**. 

The agent harnesses the power of `gemini-3-flash-preview` core logic engine. It is engineered to seamlessly translate natural language right into hyper-complex, deeply nested **BigQuery Property Graph GQL (`MATCH`)** queries, mapping complex material relationships across massive supply chain databases inherently natively.

In the baseline_agent folder you can find an agent with regular NL2SQL logic in order to compare performance. This baseline agent is not able to respond correctly to queries that require graph traversal. In adition it consumes many more tokens and takes longer to respond due to the joins and queries it needs to perform in order to get the same results.

## Toolset Configuration

This agent intrinsically maps standard contextual execution structures dynamically against a hybrid suite of tools:
1. **BigQueryToolset**: Enables the framework to list active datasets, parse property graph schemas natively, and actively fire multi-hop relational Graph Query Language (GQL) `MATCH` operations against connected nodes.
2. **MCPToolset**: Harnesses the Model Context Protocol (MCP) to dynamically execute side-channel calls to the Google Maps APIs, mapping supply chain/distributor geographic locations and natively embedding dynamic HTML routing links back into the conversational generation stream.

## Setup Requirements

See this article series for a deep dive into the new functionalities of [BigQuery Graph](https://medium.com/google-cloud/bigquery-graph-series-part-1-from-dark-data-to-knowledge-graphs-5a37f052d043). 

*Important*: BigQuery Graph is in private preview [sign up to check it out](https://docs.google.com/forms/d/e/1FAIpQLSeLnFPa4Gd3BY5DMRBAfr1hGwNEVFQY2KRckQQBPjShOVo5-Q/viewform?usp=sharing&resourcekey=0-U9EwxZ800LSHVcQVDeUZ8A)

To set up this agent, once you have access to the Preview:

1. Follow [this notebook](https://github.com/GoogleCloudPlatform/devrel-demos/blob/main/data-analytics/knowledge_graph_demo/kg_demo_template.ipynb) to get the data into BigQuery Graph
2. Edit the .env file with your maps api key and your BQ dataset and graphinformation.
3. Check the logic in `agent.py` to see how the prompt is built to use NL2GraphQL logic!
4. Run `adk web` to test the agent locally.

## (Optional) Deploy to Agent Engine
5.  Run `python deploy_ae.py` to deploy the agent to Agent Engine.
6.  Once deployed, you can access the agent in the Agent Engine UI
7. You can also expose it to Gemini Enterprise.


-----
----
# Demo Script

This script provides a structured walkthrough for demonstrating the live capabilities of the Google ADK Knowledge Graph Agent to customers. It highlights the agent's ability to seamlessly translate natural language into complex **BigQuery Property Graph** (`GQL`) queries and utilize the **Google Maps MCP Tool** for geographic enrichment.


## 🏗️ 1. Setup & Initialization

Run `adk web` to demonstrate the agent via a local graphical browser interface or use the deployed agent in **Agent Engine** or in **Gemini Enterprise**.


## 🎯 2. The Demonstration Flow
**Talking Track:**

*“Traditional SQL struggles with deeply nested relationships—like tracing a raw material all the way to the end customer. With BigQuery Property Graphs, we can traverse these networks natively using Graph Query Language (GQL). Let’s ask the agent to find who is impacted by a specific material.”*

*“We don't want a black box. Let's ask the agent to show us the exact native GQL query it pushed to BigQuery to retrieve those specific records.”*

*“Now that we know which customers are affected by the fiberglass, let's see where they are geographically so we can coordinate a recall or service route.”*

**Prompts to use:**

This script showcases the agent's ability to use tools and reason over the data even in Spanish. It is able to search by "fiberglass":
> Encuentra todos los clientes que hayan comprado productos que contengan fibra de vidrio

> enséñame la query que has utilizado

> busca la ubicación de Whispering Gallery Gelato en nuestra info de bigquery

> encuentra el centro de reciclaje especializado más cercano a esa dirección

> Escribe un email comentando que la fibra de vidrio es un material defectuoso, explicando los productos que tienen y su situación y compartiendo que tienen que reciclar los productos



---
---
## 💡 Key Takeaways for Customers
1. **No Data Movement:** The Graph operations are executed *directly* inside BigQuery. 
2. **Framework Extensibility:** The ADK architecture natively strings together Database tools (`BigQueryToolset`) with external context protocols (`MCPToolset` / Maps) seamlessly. It also exposes realtime all metrics into Bigquery using the (` ADK BigQuery Analytics Plugin`)
3. **Advanced Modeling:** The application utilizes the bleeding-edge `gemini-3-flash-preview` core logic handling complex schema mapping out-of-the-box.