from datetime import datetime
import os, sys, json, threading, time

print("=== PROBLEM INSIGHT AGENT STARTING ===")

# Create spawn confirmation
with open('PROBLEM_INSIGHT_ALIVE.md', 'w') as f:
    f.write(f'ACTIVE - {datetime.now().isoformat()}')
print("✅ Problem Insight Agent alive")

# Heartbeat class
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

# Start heartbeat
heartbeat = Heartbeat("PROBLEM_INSIGHT")
heartbeat.start()

# Set runtime limit
start_time = time.time()
max_runtime = 2700  # 45 minutes

# Message sending function
def send_message(to_agent, msg_type, content):
    msg_file = f'{to_agent}_MESSAGES.json'
    message = {
        "from": "PROBLEM_INSIGHT",
        "to": to_agent,
        "type": msg_type,
        "timestamp": datetime.now().isoformat(),
        "content": content
    }
    
    messages = []
    if os.path.exists(msg_file):
        try:
            with open(msg_file, 'r') as f:
                messages = json.load(f)
        except:
            messages = []
    
    messages.append(message)
    with open(msg_file, 'w') as f:
        json.dump(messages, f, indent=2)
    print(f"📤 Message sent to {to_agent}: {msg_type}")

print("✅ Problem Insight Agent initialized and ready")