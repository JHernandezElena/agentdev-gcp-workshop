# Using Context with your Agent in ADK

Author: inardini@google.com

You will learn how to interrupt an agent for a human to intervene by adding a tool to a subagent of a sequential agentic workflow.


## Execute the Agent

Run:

```console
adk web
```


#### **Sample Interaction**

Talk to your agent in the web UI. Try the following conversation:

> **You (in adk web UI):** write a chapter on an alien encounter
>
You will see the agent holds at the request_human_review function call step.
See the logs of your agent console asking for feedback.

Input the feedback in the console: 
> **HITL (in console):** make it scarier


Now, check the final chapter of the book with the HITL added feedback.