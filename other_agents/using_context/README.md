# Using Context with your Agent in ADK

Author: inardini@google.com
Original Lab: https://github.com/inardini/oreilly-ai-agents-gcp/blob/main/module_3/labs/lab_2.md

In the previous lab, you gave an agent a long-term memory. Now, you'll learn to manage its short-term, "working" memory within a single conversation using **Context** objects. These objects—`ToolContext` and `CallbackContext`—are your direct link to the session's runtime, allowing you to read and write data on the fly.

In this lab, you will build a "Smart Shopping List" agent. This agent will use `ToolContext` within custom tools to add items to a list and view it. Then, it will use `CallbackContext` in a lifecycle callback to save the final list to a file, demonstrating a powerful combination of state and artifact management.

## What you'll learn

- What `ToolContext` and `CallbackContext` are and why they are essential.
- The correct way to **read** session state from within a custom tool (`tool_context.state`).
- The correct way to **write** to session state to track information (`tool_context.state['key'] = value`).
- How to use `CallbackContext` to perform actions after an agent has run.
- How to bridge state and artifacts by saving session data using `context.save_artifact()`.

## Execute the Agent

Run:

```console
adk web
```


#### **Sample Interaction**

Talk to your agent in the web UI. Try the following conversation:

> **You:** add milk to my list
>
> **Agent:** 'milk' has been added to the list.
>
> **You:** add bread and eggs
>
> **Agent:** 'bread' has been added to the list. 'eggs' has been added to the list.
>
> **You:** show me my list
>
> **Agent:** Here is your shopping list:
>
> - milk
> - bread
> - eggs
>
> **You:** ok please save the list now
>
> **Agent:** OK, saving your list.

Now, check your terminal where you ran `adk web`. You should see the log messages from your tools and, most importantly, the confirmation that the artifact was saved!

```console
Executing tool: add_to_shopping_list with item 'milk'
Executing tool: add_to_shopping_list with item 'bread'
Executing tool: add_to_shopping_list with item 'eggs'
Executing tool: view_shopping_list
Callback triggered: save_list_as_artifact
✅ Successfully saved shopping_list.txt as version 0
```