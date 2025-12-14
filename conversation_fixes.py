Fix 1: AI Responses Not Saving Properly
Replace lines 111-116 in chatbot_page with:

python
# Add assistant message
st.session_state.messages.append({"role": "assistant", "content": response})
# Save conversation to database after AI response
if st.session_state.customer_name:
    db.save_conversation(st.session_state.customer_name, st.session_state.messages)
Fix 2: Previous Prompts Not Being Read by AI
Replace get_menu_context function (lines 121-127) with:

python
def get_menu_context():
    """Get menu context for AI with conversation history"""
    menu_items = db.get_menu_items()
    context = "Available menu items:\n"
    for item in menu_items[:10]:
        context += f"- {item.get('name', 'Unknown')}: {item.get('description', 'No description')}\n"
    
    # Add conversation history context
    if st.session_state.messages:
        context += "\nPrevious conversation:\n"
        for msg in st.session_state.messages[-5:]:  # Last 5 messages
            context += f"{msg['role']}: {msg['content']}\n"
    
    return context
Fix 3: Unique Username Validation & Loading Old Conversations
Replace login_page function (lines 32-44) with:

python
def login_page():
    st.title("
The model's generation exceeded the maximum output token limit.
Manual Implementation - Complete Conversation System Fixes
Fix 1: AI Responses Not Saving
Replace lines 111-116 with:

python
# Add assistant message
st.session_state.messages.append({"role": "assistant", "content": response})
# Save conversation to database after AI response
if st.session_state.customer_name:
    db.save_conversation(st.session_state.customer_name, st.session_state.messages)
Fix 2: Previous Prompts Not Being Read by AI
Replace get_menu_context function with:

python
def get_menu_context():
    """Get menu context for AI with conversation history"""
    menu_items = db.get_menu_items()
    context = "Available menu items:\n"
    for item in menu_items[:10]:
        context += f"- {item.get('name', 'Unknown')}: {item.get('description', 'No description')}\n"
    
    # Add conversation history context
    if st.session_state.messages:
        context += "\nPrevious conversation:\n"
        for msg in st.session_state.messages[-5:]:
            context += f"{msg['role']}: {msg['content']}\n"
    
    return context
Fix 3: Unique Username Validation & Loading Old Conversations
Replace login_page function with:

python
def login_page():
    st.title("
The model's generation exceeded the maximum output token limit.
Fix 1: AI Responses Not Saving
Replace lines 111-116 with:

python
# Add assistant message
st.session_state.messages.append({"role": "assistant", "content": response})
# Save conversation to database after AI response
if st.session_state.customer_name:
    db.save_conversation(st.session_state.customer_name, st.session_state.messages)
Fix 2: Previous Prompts Not Being Read by AI
Replace get_menu_context function with:

python
def get_menu_context():
    """Get menu context for AI with conversation history"""
    menu_items = db.get_menu_items()
    context = "Available menu items:\n"
    for item in menu_items[:10]:
        context += f"- {item.get('name', 'Unknown')}: {item.get('description', 'No description')}\n"
    
    # Add conversation history context
    if st.session_state.messages:
        context += "\nPrevious conversation:\n"
        for msg in st.session_state.messages[-5:]:
            context += f"{msg['role']}: {msg['content']}\n"
    
    return context
Fix 3: Unique Username Validation & Loading Old Conversations
Replace login_page function with:

python
def login_page():
    st.title("