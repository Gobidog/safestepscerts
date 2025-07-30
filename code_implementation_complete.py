from datetime import datetime
import sys
import json
import subprocess
import os

# Write completion message for verification agent
def write_agent_message(to_agent, message_type, content):
    """Write a message for another agent"""
    message = {
        "from": "CODE_IMPLEMENTATION",
        "to": to_agent,
        "type": message_type,
        "timestamp": datetime.now().isoformat(),
        "content": content
    }
    
    queue_file = f"{to_agent}_MESSAGES.json"
    messages = []
    if os.path.exists(queue_file):
        with open(queue_file, 'r') as f:
            messages = json.load(f)
    
    messages.append(message)
    with open(queue_file, 'w') as f:
        json.dump(messages, f, indent=2)

# Get list of modified files for handoff
result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True)
modified_files = result.stdout.strip().split('\n') if result.stdout else []

# Notify System Verification Agent
write_agent_message("SYSTEM_VERIFICATION", "HANDOFF", {
    "phase": "implementation_complete",
    "artifacts": ["CODE_CHANGES_COMPLETE.md"],
    "modified_files": modified_files,
    "test_focus": "Focus on modified components and integration points"
})

# Stop heartbeat
try:
    os.remove('CODE_IMPLEMENTATION_HEARTBEAT.md')
except:
    pass

# Final status
print("=== CODE IMPLEMENTATION AGENT COMPLETE ===")
print(f"Created: CODE_CHANGES_COMPLETE.md with evidence")
print(f"Modified files: {len(modified_files)}")
with open('CODE_IMPLEMENTATION_STATUS.md', 'w') as f:
    f.write(f'COMPLETE - Changes implemented - {datetime.now().isoformat()}')

sys.exit(0)  # Explicit termination