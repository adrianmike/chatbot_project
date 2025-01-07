from langchain_ollama import ChatOllama

model = ChatOllama(model="smollm", base_url="http://localhost:11434/")
response = model.invoke("Hello, world!")
print(response.content)
