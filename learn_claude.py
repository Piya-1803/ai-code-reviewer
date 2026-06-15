import anthropic 

client = anthropic.Anthropic()

messages = []

print ("Chat with Claude : (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    if user_input == "quit":
        break
    else :
        messages.append ({"role": "user", "content": user_input})

# messages.append ({"role": "user" , "content" : "My name is Priyanka"})

response = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens = 1024,
    system = "You are helpful coding assistant",
    messages = messages
)

assistant_reply = response.content[0].text
messages.append ({"role":"assistant", "content": assistant_reply})
print("Claude : " , assistant_reply)

