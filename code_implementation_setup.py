from datetime import datetime
import sys
print("--- Reading FOR_Code_Implementation_Agent.md to get my specific task. ---")
try:
    with open('FOR_Code_Implementation_Agent.md', 'r') as f:
        instructions = f.read()
    print("Instructions Received:\n" + instructions)
except Exception as e:
    print(f"CRITICAL FAILURE: Could not read FOR_Code_Implementation_Agent.md. Error: {e}")
    raise e

# Step 1b: Create spawn confirmation file
print("--- Creating spawn confirmation file ---")
try:
    with open('CODE_IMPLEMENTATION_ALIVE.md', 'w') as f:
        f.write(f'CODE_IMPLEMENTATION AGENT ACTIVE - {datetime.now().isoformat()}')
    print("✅ Spawn confirmation created: CODE_IMPLEMENTATION_ALIVE.md")
except Exception as e:
    print(f"WARNING: Could not create spawn confirmation. Error: {e}")

# Step 1c: Check for messages from Problem Insight
import json
import threading
import time
import os

def read_agent_messages(agent_name, message_type=None):
    """Read messages for an agent"""
    queue_file = f"{agent_name}_MESSAGES.json"
    if not os.path.exists(queue_file):
        return []
    
    with open(queue_file, 'r') as f:
        messages = json.load(f)
    
    if message_type:
        messages = [m for m in messages if m['type'] == message_type]
    
    return messages

# Check for READY message
messages = read_agent_messages("CODE_IMPLEMENTATION", "READY")
if messages:
    latest = messages[-1]
    print(f"📨 Received message from {latest['from']}: {latest['content']['artifacts']}")

# Step 1d: Start heartbeat
class Heartbeat:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.heartbeat_file = f"{agent_name}_HEARTBEAT.md"
        self.running = True
        self.thread = None
        
    def start(self):
        self.thread = threading.Thread(target=self._heartbeat_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"💓 Heartbeat started for {self.agent_name}")
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            
    def _heartbeat_loop(self):
        while self.running:
            try:
                with open(self.heartbeat_file, 'w') as f:
                    f.write(f"{self.agent_name} HEARTBEAT - {datetime.now().isoformat()}")
            except:
                pass
            time.sleep(30)

heartbeat = Heartbeat("CODE_IMPLEMENTATION")
heartbeat.start()

# Step 1e: Set runtime limit
start_time = time.time()
max_runtime = 2700  # 45 minutes for implementation