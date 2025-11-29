import os
import chatbot_logic

def load_general_instructions():
    """
    Loads the General Instructions PDF into the chatbot's knowledge base.
    This should be run to add general instructions to the chatbot.
    """
    instructions_path = os.path.join(os.getcwd(), 'General Instructions.pdf')
    
    if not os.path.exists(instructions_path):
        print(f"ERROR: General Instructions file not found at {instructions_path}")
        return False
    
    print("Initializing chatbot...")
    chatbot_logic.init_chatbot()
    
    print("Loading General Instructions into knowledge base...")
    print("This may take a few moments...")
    
    success, message = chatbot_logic.add_document_to_knowledge_base(
        instructions_path, 
        'General Instructions.pdf'
    )
    
    if success:
        print(f"\n✓ SUCCESS: {message}")
        print("\nThe chatbot now has access to General Instructions!")
        print("You can ask questions about:")
        print("  - General guidelines and procedures")
        print("  - Instructions for various processes")
        print("  - Any topics covered in the General Instructions document")
        return True
    else:
        print(f"\n✗ ERROR: {message}")
        return False

if __name__ == "__main__":
    load_general_instructions()
