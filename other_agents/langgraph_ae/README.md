```
pip install google-cloud-aiplatform[langchain]==1.137.0
```

This agent will use AE Runtime and will write logs and traces to Cloud Logging and Cloud Trace. However it will not expose them in AE UI as this features work only for ADK agents right now. 

### 1. Agent construction:
- *agent_custom_template.py* is constructed using Langraph using [**AE custom template**](https://docs.cloud.google.com/agent-builder/agent-engine/develop/custom). It has an extra code block for tracing to [Cloud Trace](https://docs.cloud.google.com/stackdriver/docs/instrumentation/ai-agent-langgraph) ([other reference](https://docs.cloud.google.com/agent-builder/agent-engine/develop/custom#tracing)). **We will be deploying this agent.**
- *agent_lang_template.py* is constructed using the [**AE langgraph template**](https://docs.cloud.google.com/agent-builder/agent-engine/develop/langgraph). 

### 2. Agent Deployment
It can be deployed:
- By running *deploy.py*
- By running *deploy_ae_identity.py* to provide an agent indentity (you will need to enable the principal://identity [with permissions](https://docs.cloud.google.com/agent-builder/agent-engine/agent-identity#grant-access-agent)). THIS DOES NOT WORK. NEED TO TRY WITH AN ADK AGENT

### 3. Query Agent:
- Locally by *query_local.py* (queries agent.py)
- Remotelly to AE using *query_ae.py* (any of the Resource Names)