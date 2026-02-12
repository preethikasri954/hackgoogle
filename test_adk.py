try:
    from google.adk import Agent
    print("Agent import successful")
    # Simple initialization test
    agent = Agent(
        instruction="You are a helpful assistant.",
        tools=[]
    )
    print("Agent initialization successful")
except Exception as e:
    import traceback
    traceback.print_exc()
