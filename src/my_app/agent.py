from turtle import mode
from langchain.agents import create_agent
import os
from langchain.tools import tool


@tool
def search(query):
    """Search for information"""
    return f"{query}"


@tool
def get_weather(location):
    """Get weather information for a location"""
    return f"{location}"


agent = create_agent(model="", tools=[search, get_weather])

print(agent)
