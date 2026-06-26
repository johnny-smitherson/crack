#!/usr/bin/env python3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MISSIONS_DIR = os.path.join(BASE_DIR, "docs", "missions")
CHARACTERS_DIR = os.path.join(BASE_DIR, "docs", "characters")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def verify_all():
    errors = []
    
    # 1. Verify missions
    print("Checking missions...")
    if not os.path.exists(MISSIONS_DIR):
        errors.append("Missions directory does not exist.")
    else:
        for i in range(1, 43):
            file_name = f"mission_{i:02d}.md"
            file_path = os.path.join(MISSIONS_DIR, file_name)
            if not os.path.exists(file_path):
                errors.append(f"Missing mission file: {file_name}")
            else:
                # Check if it has basic content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if f"Misiunea {i:02d}" not in content:
                    errors.append(f"Mission file {file_name} does not contain correct title header.")
                if "Storyboard" not in content:
                    errors.append(f"Mission file {file_name} is missing Storyboard section.")
                if "Game State Machine" not in content:
                    errors.append(f"Mission file {file_name} is missing State Machine section.")
                    
    # 2. Verify characters
    print("Checking characters...")
    expected_characters = [
        "relu_oncescu", "gina_oncescu", "capitanu", "nico", "teddy",
        "magda_oncescu", "chuckie_oncescu", "nea_puiu", "emilian",
        "toma", "nicu", "sabin"
    ]
    if not os.path.exists(CHARACTERS_DIR):
        errors.append("Characters directory does not exist.")
    else:
        for char in expected_characters:
            file_name = f"{char}.md"
            file_path = os.path.join(CHARACTERS_DIR, file_name)
            if not os.path.exists(file_path):
                errors.append(f"Missing character file: {file_name}")
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "Wikipedia" not in content and "Descriere" not in content:
                    errors.append(f"Character file {file_name} content verification failed.")

    # 3. Verify state machine
    print("Checking state machine...")
    sm_path = os.path.join(DOCS_DIR, "state_machine.md")
    if not os.path.exists(sm_path):
        errors.append("State machine file state_machine.md is missing.")
    else:
        with open(sm_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "graph TD" not in content:
            errors.append("state_machine.md does not contain mermaid graph diagram.")
        if "MISSION_42" not in content:
            errors.append("state_machine.md does not list final mission MISSION_42.")

    # Report results
    if errors:
        print("\nVerification FAILED with the following errors:")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)
    else:
        print("\nVerification SUCCESS! All 42 missions, characters, and state machine files are valid and complete.")
        sys.exit(0)

if __name__ == "__main__":
    verify_all()
