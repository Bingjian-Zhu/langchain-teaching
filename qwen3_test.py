import getpass
import os
from langchain_openai import ChatOpenAI

# Set up API key for Qwen3 (if using API service)
if not os.environ.get("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = getpass.getpass("Enter API key for Qwen3 (DashScope): ")

# Initialize Qwen3 model using OpenAI-compatible interface
# 对于国内用户，使用国内端点
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 国内端点
    model="qwen-turbo"  # 可以使用 qwen-turbo, qwen-plus, qwen-max 等
)

print(llm.invoke("你好，你的模型是什么"))
