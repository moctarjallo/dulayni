from dotenv import load_dotenv

import asyncio
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

_ = load_dotenv()

async def main():
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a legal assistant. Identify risks and suggest improvements.",
            max_turns=2
        )
    ) as client:
        # Send the query
        await client.query(
            "Review this contract clause for potential issues: 'The party agrees to unlimited liability...'"
        )
        
        # Stream the response
        async for message in client.receive_response():
            if hasattr(message, 'content'):
                # Print streaming content as it arrives
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)

if __name__ == "__main__":
    asyncio.run(main())
