from config.llm import get_llm

llm = get_llm()
response = llm.invoke("Write hello world in python")

print(response.content)