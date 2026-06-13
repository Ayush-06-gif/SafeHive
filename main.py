"""
CLI Entry Point — Run SafeHive locally via command line.
"""

import asyncio
from sandbox.scenarios import run_scenario


async def main():
    print("==================================================")
    print("🛡️  SafeHive AI Security Sandbox")
    print("==================================================\n")
    print("Type your food order (or 'quit' to exit).\n")

    while True:
        user_input = input("Customer: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        print("\n[System] Routing request to agents...\n")
        
        result = await run_scenario(user_input)
        
        print("--- CONVERSATION RESULTS ---")
        if result["status"] == "success":
            print(f"Status: ✅ SUCCESS at {result['vendor']}")
            for turn in result.get("conversation", []):
                print(f"\n[Turn {turn['turn']}]")
                print(f"🤖 Orchestrator : {turn['orchestrator']}")
                
                safe_str = "✅ Safe" if turn['safe'] else "🚨 THREAT DETECTED"
                print(f"🏪 {turn['vendor_name']:<14}: {turn['vendor']}")
                print(f"🛡️  Guard Status : {safe_str}")
                
                if not turn['safe']:
                    for threat in turn['threats']:
                        print(f"   ❌ [{threat['severity']}] {threat['guard']}: {threat['reason']}")
        else:
            print(f"Status: ❌ FAILED - {result.get('reason')}")
            
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting SafeHive...")
