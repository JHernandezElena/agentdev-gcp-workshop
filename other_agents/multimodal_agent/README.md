# An ADK agent with multi-modal input and output

1. From the `other_agents` folder, run the following command in your terminal to start the ADK web UI:

```bash
adk web
```

2. Ensure that the `multimodal_agent` agent is selected in the dropdown.
3. Click the **Upload local file** button (the one with the paperclip icon) and upload a picture of an aircraft, such as the one included in the `sample_images` folder. Then send the message to the agent.
4. The agent should reply with the same image, but the aircraft livery should be changed to that of the airline's main competitor.

*To save artifcats from adk web into Cloud Storage run: adk web --artifact_service_uri="gs://{bucket_name}"

**If deployed you will need an artifact_service variable in your runner. See more info <a href="https://google.github.io/adk-docs/artifacts/#interacting-with-artifacts-via-context-objects">here</a>

# Image attribution

* American Airlines photo by <a href="https://unsplash.com/@dwhite24?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Donna White</a> on <a href="https://unsplash.com/photos/an-american-airlines-jet-taking-off-from-an-airport-zGrRL6TlUh8?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
