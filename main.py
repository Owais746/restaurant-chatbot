import streamlit as st
import os
from database import RestaurantDatabase
from openrouter_client import OpenRouterClient
import json


def normalize_username(name: str) -> str:
    return " ".join((name or "").strip().lower().split())

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_order' not in st.session_state:
    st.session_state.current_order = []
if 'customer_info' not in st.session_state:
    st.session_state.customer_info = {}
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Initialize database and AI client
@st.cache_resource
def init_database():
    return RestaurantDatabase()

@st.cache_resource
def init_ai_client():
    return OpenRouterClient()

try:
    db = init_database()
except Exception as e:
    db = None
    db_init_error = e

ai_client = init_ai_client()


def login_page():
    st.title("🍕 Broadway Pizza")
    st.subheader("Welcome! Please enter your name")

    if db is None:
        st.error("Database is not connected. Please set MONGODB_URI in Streamlit Secrets (or .env locally).")
        st.code(str(db_init_error))
        st.stop()
    
    name = st.text_input("Your Name:", key="login_name")
    
    if st.button("Start Chatting", key="start_chat"):
        username_key = normalize_username(name)
        if username_key:
            st.session_state.customer_name = username_key
            st.session_state.authenticated = True
            # Load existing conversation
            st.session_state.messages = db.get_conversation(username_key)
            st.rerun()




def main():
    if db is None:
        st.set_page_config(
            page_title="Broadway Pizza Chatbot",
            page_icon="🍕",
            layout="wide"
        )
        st.title("🍕 Broadway Pizza")
        st.error("Database is not connected. Please set MONGODB_URI in Streamlit Secrets (or .env locally).")
        st.code(str(db_init_error))
        st.stop()

    if not st.session_state.authenticated:
        login_page()
        return
    
    st.set_page_config(
        page_title="Broadway Pizza Chatbot",
        page_icon="🍕",
        layout="wide"
    )
    
    st.title(f"🍕 Broadway Pizza Restaurant - Welcome {st.session_state.customer_name}!")
    st.markdown("---")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Choose Page", ["Chatbot", "Dashboard", "Menu", "Orders"])
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.customer_name = ""
            st.session_state.messages = []
            if "login_name" in st.session_state:
                st.session_state.login_name = ""
            st.rerun()
    
    if page == "Chatbot":
        chatbot_page()
    elif page == "Dashboard":
        dashboard_page()
    elif page == "Menu":
        menu_page()
    elif page == "Orders":
        orders_page()



def chatbot_page():
    st.header("🤖 Chat with Paulo")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to order?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            menu_context = get_menu_context()
            response = ai_client.get_waiter_response(
                prompt,
                menu_context,
                chat_history=st.session_state.messages,
            )
            st.markdown(response)
            
            # Check if user is trying to place an order
            order_info = ai_client.extract_order_info(prompt)
            if order_info['items'] and order_info['is_complete_order']:
                st.session_state.current_order.extend(order_info['items'])
                show_order_summary()
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Save conversation to database after AI response
        if st.session_state.customer_name:
            db.save_conversation(st.session_state.customer_name, st.session_state.messages)




def get_menu_context():
    """Get menu context for AI"""
    menu_items = db.get_menu_items()
    context = "Available menu items:\n"
    for item in menu_items[:10]:  # Limit to first 10 items
        context += f"- {item.get('name', 'Unknown')}: {item.get('description', 'No description')}\n"
    return context

def show_order_summary():
    """Show current order summary"""
    if st.session_state.current_order:
        st.subheader("🛒 Current Order")
        for item in st.session_state.current_order:
            st.write(f"- {item}")
        
        if st.button("Complete Order"):
            show_customer_form()

def show_customer_form():
    """Show customer information form"""
    st.subheader("📝 Customer Information")
    
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Delivery Address")
    
    if st.button("Place Order"):
        if name and phone:
            # Create order in database
            order_id = db.create_order(
                name, phone, st.session_state.current_order, 0  # Calculate total
            )
            st.success(f"Order placed successfully! Order ID: {order_id}")
            st.session_state.current_order = []
            st.session_state.messages = []
        else:
            st.error("Please fill in name and phone number")

def dashboard_page():
    st.header("📊 Dashboard")
    
    # Get order statistics
    stats = db.get_order_stats()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Order Status")
        if stats['status_stats']:
            for stat in stats['status_stats']:
                st.write(f"{stat['_id']}: {stat['count']}")
    
    with col2:
        st.subheader("Daily Revenue")
        if stats['daily_stats']:
            import pandas as pd
            df = pd.DataFrame(stats['daily_stats'])
            st.line_chart(df.set_index('_id')['revenue'])

def menu_page():
    st.header("📋 Menu")
    
    # Get restaurant info
    restaurant_info = db.get_restaurant_info()
    st.write(f"**Restaurant:** {restaurant_info.get('name', 'Broadway Pizza')}")
    st.write(f"**Location:** {restaurant_info.get('country', 'Pakistan')}")
    
    # Menu categories
    categories = ["Pizza", "Appetizers & Starters", "Chicken Wings", "Calzones", "Pastas", "Kids Meal", "Desserts", "Beverages & Sides", "deals"]
    
    selected_category = st.selectbox("Select Category", categories)
    
    if selected_category:
        menu_items = db.get_menu_items(selected_category)
        if menu_items:
            for item in menu_items:
                with st.expander(item.get('name', 'Unknown')):
                    st.write(item.get('description', 'No description'))
        else:
            st.write("No items found in this category")

def orders_page():
    st.header("📦 Order Management")
    
    # Filter by status
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "completed", "cancelled"])
    
    if status_filter == "All":
        orders = db.get_orders()
    else:
        orders = db.get_orders(status_filter)
    
    if orders:
        for order in orders:
            with st.expander(f"Order for {order.get('customer_name', 'Unknown')} - {order.get('status', 'Unknown')}"):
                st.write(f"**Phone:** {order.get('customer_phone', 'N/A')}")
                st.write(f"**Items:** {', '.join(order.get('items', []))}")
                st.write(f"**Total:** ${order.get('total_amount', 0)}")
                st.write(f"**Status:** {order.get('status', 'Unknown')}")
                
                # Update status buttons
                if order.get('status') != 'completed':
                    if st.button(f"Mark as Complete", key=f"complete_{order.get('_id')}"):
                        db.update_order_status(order.get('_id'), 'completed')
                        st.rerun()
    else:
        st.write("No orders found")

if __name__ == "__main__":
    main()
