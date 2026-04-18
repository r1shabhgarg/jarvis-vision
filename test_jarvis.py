import os
import json
from screen_tool import analyze_screen

def print_result(result):
    if "error" in result:
        print(f"\n[!] Error: {result['error']}")
    else:
        print("\n--- JARVIS ANALYSIS ---")
        print(f"Screen Type: {result.get('screen_type')}")
        print("\nSummary:")
        for item in result.get('summary', []):
            print(f"- {item}")
            
        print("\nKey Information:")
        for item in result.get('key_information', []):
            print(f"- {item}")
            
        print("\nAction Items:")
        for item in result.get('action_items', []):
            print(f"- {item}")
            
        print("\nSuggestions:")
        for item in result.get('suggestions', []):
            print(f"- {item.get('description')} (Hook: {item.get('action_hook')})")
        print("-----------------------\n")

def main():
    print("Welcome to Jarvis Screen Insight Test CLI")
    print("Ensure you have set GEMINI_API_KEY in .env")
    
    while True:
        try:
            command = input("\nEnter command (or 'q' to quit, 'region' to toggle region selection): ")
            if command.lower() == 'q':
                break
                
            use_region = False
            if command.lower().startswith('region '):
                use_region = True
                command = command.split('region ', 1)[1]
            
            if not command.strip():
                continue
                
            print(f"Capturing and analyzing: '{command}'...")
            result = analyze_screen(command, use_region=use_region)
            print_result(result)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
