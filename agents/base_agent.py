"""
Base agent abstractions.
This module will define the base classes for OpenAI and local agents, 
handling their individual tools and system prompts.
"""

class BaseAgent:
    def __init__(self, name, role, tools=None):
        self.name = name
        self.role = role
        self.tools = tools or []
        
    def act(self, state):
        pass
