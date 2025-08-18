"""
Hyrex application configuration.
"""
from hyrex import HyrexApp
from tasks import hy as registry

# Create Hyrex app instance
app = HyrexApp("deep-research")

# Add the task registry
app.add_registry(registry)

if __name__ == "__main__":
    print("🚀 Hyrex Deep Research Worker")
    print("📋 Registered tasks:")
    for task_name in registry.tasks:
        print(f"  - {task_name}")
    print("\nStarting worker...")