from uagents import Agent, Context, Model
from typing import Any

# Define message model
class SimpleMessage(Model):
    content: str

# Create agent instance
agent = Agent(
    name="aromance_test_agent",
    port=8000,
    seed="aromance_consultation_seed_123",
    endpoint=["http://127.0.0.1:8000/submit"],
)

@agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info(f"Starting {agent.name}")
    ctx.logger.info(f"Agent address: {agent.address}")

@agent.on_message(model=SimpleMessage)
async def message_handler(ctx: Context, sender: str, msg: SimpleMessage):
    ctx.logger.info(f"Received message from {sender}: {msg.content}")
    response = SimpleMessage(content=f"Echo: {msg.content}")
    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()