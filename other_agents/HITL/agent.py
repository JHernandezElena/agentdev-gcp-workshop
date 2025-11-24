from google.adk.agents import SequentialAgent, LlmAgent

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
GEMINI_MODEL=os.getenv("GEMINI_MODEL")
PROJECT_ID=os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")


# --- Step 1: Define the Agents ---
# The author agent. Its only job is to write the first draft.
# Its output will be saved to state['draft_chapter'].
author = LlmAgent(
    name="ManuscriptWriter",
    model=GEMINI_MODEL,
    instruction="You are a creative author. Write the next chapter of a sci-fi novel.",
    output_key="draft_chapter" # Saves the output to the session state
)

# The revision agent. Its job is to fix the draft based on feedback.
# It reads the draft and feedback from the state using templating.
reviser = LlmAgent(
    name="ManuscriptReviser",
    model=GEMINI_MODEL,
    instruction="You are a meticulous editor. Revise the following draft: '{draft_chapter}' based on this feedback: '{review_feedback}'.",
    output_key="revised_chapter" # Saves the final version to the state
)

# --- Step 2: Define the Human-in-the-Loop as a Tool ---
def request_human_review(draft: str) -> str:
    """
    Pauses the workflow and requests a human editor to review the draft.
    This function simulates asking a human for feedback. In a real app,
    this would save the state and wait for an API call to resume.
    """
    print("--- WAITING FOR HUMAN REVIEW ---")
    print(f"Draft to review: {draft[:200]}...")
    # This simulates a human typing their feedback at the command line.
    feedback = input("Please provide your editorial feedback: ")
    print(feedback)
    return feedback

# --- Step 3: Create an Agent to Manage the Review Step ---
# This agent's ONLY job is to call the human review tool.
# It reads the draft from the state and saves the feedback.
reviewer = LlmAgent(
    name="EditorialReviewer",
    model=GEMINI_MODEL,
    instruction="You are a project manager. Use the request_human_review tool to get feedback on the draft: '{draft_chapter}'. Save the feedback to state['review_feedback'].",
    tools=[request_human_review],
    output_key="review_feedback" # Saves the tool's output (the human's feedback) to the state
)

# --- Step 4: Assemble the Final Workflow ---
# The SequentialAgent now has three clear, distinct steps.
publishing_flow = SequentialAgent(
    name="BookPublishingFlow",
    sub_agents=[
        author,      # First, the author writes.
        reviewer,    # Second, the reviewer gets human feedback.
        reviser      # Third, the reviser fixes the draft using the feedback.
    ]
)

root_agent = publishing_flow