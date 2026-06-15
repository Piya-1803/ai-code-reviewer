import anthropic

client = anthropic.Anthropic ()

tools = [
    {
        "name": "get_weather",
        "description":"Gets the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city":{
                    "type":"string",
                    "description":"the city name"
                }
            },
            "required": ["city"]
        }
    }
]

messages = [
    {"role":"user", "content":"What is the weather in mumbai"}
]
response = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens= 1054,
    tools = tools,
    messages = messages
)

print("Stop reason:", response.stop_reason)
print("response :",response.content)

tool_call = None

for block in response.content:
    if block.type =="tool_use":
        tool_call = block
        break

if response.stop_reason == "tool_use":
  
    tool_name = tool_call.name
    tool_input = tool_call.input
    tool_id = tool_call.id

    if tool_name == "get_weather":
        city = tool_input["city"]
        result = f"It is 35 degrees and sunny in {city}."
    print (f"Tool result: {result}")

messages.append ({"role": "assistant","content": response.content})

messages.append ({ 
    "role": "user",
    "content" : [
        {
            "type":"tool_result",
            "tool_use_id": tool_id,
            "content" : result
        }
    ]
})

final_response = client.messages.create (
     model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=messages
)
print("\nClaude's final reply:")
print(final_response.content[0].text)