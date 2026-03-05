# Build Live API Agent with ADK

## 1a. Build from scratch: dummy agent
You can start from an empty folder and use Agent Starter Pack to create your first agent:

```
# Create and activate a Python virtual environment
python -m venv .venv && source .venv/bin/activate

# Install the agent starter pack
pip install --upgrade agent-starter-pack

# Create a new agent project. This will create a folder with the agent code and everything needed to run it.
agent-starter-pack create
```

Follow the steps to create your agent.

## 1b. Build from pre-existing agent
You can create an agent as you normally would (create agent.py and .env as usual). For example let's use the alphabet_earnings_agent. 
If you provide the agent with a live model (e.g. 	*gemini-live-2.5-flash-native-audio*) the agent will work in the *adk web* locally  but has a lot of limitations: no custom front-end, no websocket, no interruptions handling, etc. 

However you can easily enhance it with the starter pack tools (custom front-end) and have it ready to deploy using websocket.

*The agent must be in an /app folder. Starting from the alphabet_earnings_agent blueprint an  app has been created with the agent already in it.

```
python -m venv .venv && source .venv/bin/activate

agent-starter-pack enhance
```

This will enhance your agent with the starter pack tools (custom front-end) and have it ready to deploy using websocket.



## 2. Test your agent locally
This command will launch both the backend and the custom front-end locally:
```
cd liveapi-adk && make install && make playground
```

## 3. Deploy your Backend
This command will guide you through the steps to deploy your agent to Google Cloud. Chose Agent Engine or Cloud Run.
```
make deploy
```

## 4. Test your deployed agent
You will still need a front-end to interact with your agent. You can use the custom front-end created by the starter pack.

To use the deployed agent with the agent starter pack front-end running locally:
```
make playground-remote
```
