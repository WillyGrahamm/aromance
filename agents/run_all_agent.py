"""
Multi-agent startup script for Aromance
Run this to start all agents simultaneously

Usage:
    python agents/run_all_agents.py

NOTE untuk Tim:
1. Install dependencies: pip install uagents
2. Pastikan semua port (8000-8005) available
3. Untuk production, deploy each agent separately
4. Configure ICP canister endpoints di masing-masing agent
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

def start_agent(agent_file, agent_name):
    """Start individual agent as subprocess"""
    try:
        process = subprocess.Popen([
            sys.executable, str(agent_file)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Started {agent_name} (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start {agent_name}: {e}")
        return None

def main():
    """Start all Aromance agents"""
    
    print("🌸 Starting Aromance AI Agents System...")
    print("=" * 50)
    
    # Define agent files
    agents_dir = Path(__file__).parent
    agent_files = [
        (agents_dir / "coordinator.py", "System Coordinator"),
        (agents_dir / "consultation" / "consultation_agent.py", "Consultation AI"),
        (agents_dir / "recommendation" / "recommendation_agent.py", "Recommendation AI"), 
        (agents_dir / "analytics" / "analytics_agent.py", "Analytics AI"),
        (agents_dir / "inventory" / "inventory_agent.py", "Inventory AI")
    ]
    
    processes = []
    
    # Start each agent
    for agent_file, agent_name in agent_files:
        if agent_file.exists():
            process = start_agent(agent_file, agent_name)
            if process:
                processes.append((process, agent_name))
                time.sleep(2)  # Wait between starts
        else:
            print(f"⚠️ Agent file not found: {agent_file}")
    
    print("\n" + "=" * 50)
    print(f"🚀 Aromance System Running with {len(processes)} agents")
    print("=" * 50)
    
    print("\n📋 Agent Status:")
    for i, (process, name) in enumerate(processes):
        port = 8000 + i
        print(f"  {name}: http://127.0.0.1:{port}")
    
    print("\n🎯 System Ready!")
    print("   • Consultation AI: Intelligent fragrance discovery chat")
    print("   • Recommendation AI: Personalized product matching") 
    print("   • Analytics AI: Business intelligence & insights")
    print("   • Inventory AI: Smart stock management")
    print("   • Coordinator: Multi-agent orchestration")
    
    print("\n📝 Integration Notes:")
    print("   • Connect frontend to Coordinator (port 8000)")
    print("   • Configure ICP canister endpoints in each agent")
    print("   • Add real product data to recommendation_agent.py")
    print("   • Implement authentication & rate limiting")
    
    try:
        # Keep main process running
        while True:
            time.sleep(1)
            
            # Check if any process died
            for process, name in processes:
                if process.poll() is not None:
                    print(f"⚠️ {name} process ended unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Aromance agents...")
        
        # Terminate all processes
        for process, name in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except Exception as e:
                print(f"⚠️ Error stopping {name}: {e}")
        
        print("👋 Aromance agents stopped. Goodbye!")

if __name__ == "__main__":
    main()