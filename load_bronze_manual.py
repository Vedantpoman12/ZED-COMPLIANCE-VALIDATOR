import os
import chatbot_logic

def load_bronze_certificate():
    manual_path = os.path.join(os.getcwd(), 'User_Manual_Bronze_Certification_20.04.2022.pdf')
    
    if not os.path.exists(manual_path):
        print(f"ERROR: Bronze Certificate manual not found at {manual_path}")
        return False
    
    print("Initializing chatbot...")
    chatbot_logic.init_chatbot()
    
    print("Loading Bronze Certificate User Manual into knowledge base...")
    print("This may take a few moments...")
    
    success, message = chatbot_logic.add_document_to_knowledge_base(
        manual_path, 
        'User_Manual_Bronze_Certification_20.04.2022.pdf'
    )
    
    if success:
        print(f"\nSUCCESS: {message}")
        print("\nThe chatbot is now ready to answer questions about the Bronze Certificate!")
        print("You can ask questions like:")
        print("  - What is the bronze certification?")
        print("  - What are the requirements for bronze certificate?")
        print("  - How do I apply for bronze certification?")
        return True
    else:
        print(f"\nERROR: {message}")
        return False

if __name__ == "__main__":
    load_bronze_certificate()
