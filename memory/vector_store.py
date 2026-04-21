"""
Vector Store / Persistent Memory configuration.
Handles connecting to ChromaDB, embedding text, and retrieval pipelines (RAG).
"""

class AgentMemory:
    def __init__(self):
        # Placeholder for ChromaDB Initialization
        self.memory_db = []
        
    def add_memory(self, turn, concept):
        self.memory_db.append({"turn": turn, "concept": concept})
        
    def query(self, search_text):
        return [m for m in self.memory_db if search_text in m["concept"]]
