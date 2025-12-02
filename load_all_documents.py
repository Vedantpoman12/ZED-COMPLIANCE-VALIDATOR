import os
import chatbot_logic

def load_all_documents():
    print("="*60)
    print("INITIALIZING CHATBOT WITH ALL DOCUMENTS")
    print("="*60)
    
    print("\n[Step 1/3] Initializing chatbot...")
    chatbot_logic.init_chatbot()
    
    documents = [
        {
            'path': 'User_Manual_Bronze_Certification_20.04.2022.pdf',
            'name': 'Bronze Certificate User Manual'
        },
        {
            'path': 'General Instructions.pdf',
            'name': 'General Instructions'
        }
    ]
    
    successful_loads = 0
    failed_loads = []
    
    for i, doc in enumerate(documents, start=2):
        doc_path = os.path.join(os.getcwd(), doc['path'])
        
        print(f"\n[Step {i}/3] Loading {doc['name']}...")
        
        if not os.path.exists(doc_path):
            print(f"  WARNING: File not found at {doc_path}")
            failed_loads.append(doc['name'])
            continue
        
        print(f"  Processing {doc['path']}...")
        print("  This may take a few moments...")
        
        success, message = chatbot_logic.add_document_to_knowledge_base(
            doc_path, 
            doc['path']
        )
        
        if success:
            print(f"  SUCCESS: {message}")
            successful_loads += 1
        else:
            print(f"  ERROR: {message}")
            failed_loads.append(doc['name'])
    
    print("\n" + "="*60)
    print("LOADING SUMMARY")
    print("="*60)
    print(f"Successfully loaded: {successful_loads} document(s)")
    if failed_loads:
        print(f"Failed to load: {', '.join(failed_loads)}")
    
    if successful_loads > 0:
        print("\nThe chatbot is now ready to answer questions!")
        print("\nYou can ask about:")
        print("   Bronze certification requirements and procedures")
        print("   General instructions and guidelines")
        print("   Document verification processes")
        print("   Any topics covered in the loaded documents")
        return True
    else:
        print("\n No documents were loaded successfully.")
        return False

if __name__ == "__main__":
    load_all_documents()
