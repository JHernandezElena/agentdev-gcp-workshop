import asyncio
from google.adk.runners import InMemoryRunner
from alphabet_earnings_agent.agent import root_agent


async def main():
    # The runner manages the conversation state and agent execution
    async with InMemoryRunner(agent=root_agent) as runner:
        prompt = "Write a function to calculate the Fibonacci sequence."
        
        # run_debug returns the full list of events (thoughts, tool calls, and final response)
        events = await runner.run_debug(prompt)
        
        # Extract and print the events
        for event in events:
             print(event)

if __name__ == "__main__":
    asyncio.run(main())