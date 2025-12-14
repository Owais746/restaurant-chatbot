import json
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

try:
    import streamlit as st
except Exception:
    st = None


def _get_setting(key: str):
    if st is not None:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
    return os.getenv(key)

class RestaurantDatabase:
    def __init__(self):
        mongo_uri = _get_setting('MONGODB_URI')
        if not mongo_uri:
            raise RuntimeError(
                "MONGODB_URI is not set. Add it to .env for local runs or Streamlit Secrets for deployment."
            )

        self.client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=8000,
            connectTimeoutMS=8000,
            socketTimeoutMS=8000,
        )
        self.client.admin.command('ping')
        self.db = self.client['restaurant_chatbot']
        self.menu_collection = self.db['menu']
        self.orders_collection = self.db['orders']
        self.conversations_collection = self.db['conversations']
        if self.menu_collection.count_documents({}) == 0:
            self.load_menu_data()
    
    def load_menu_data(self):
        """Load menu data from JSON file into MongoDB"""
        with open('data.json', 'r', encoding='utf-8') as f:
            menu_data = json.load(f)
        
        # Clear existing menu data
        self.menu_collection.delete_many({})
        
        # Insert restaurant info
        self.menu_collection.insert_one({
            'type': 'restaurant_info',
            'data': menu_data['restaurant']
        })
        
        # Insert menu items by category
        for category, items in menu_data['menu'].items():
            if isinstance(items, dict):
                # For nested categories like Pizza
                for subcategory, subitems in items.items():
                    for item in subitems:
                        item['category'] = category
                        item['subcategory'] = subcategory
                        self.menu_collection.insert_one(item)
            else:
                # For flat categories
                for item in items:
                    if isinstance(item, dict):
                        item['category'] = category
                        self.menu_collection.insert_one(item)
                    else:
                        # For simple string items
                        self.menu_collection.insert_one({
                            'name': item,
                            'category': category,
                            'description': item
                        })
        
        # Insert deals
        for deal_type, deals in menu_data['deals'].items():
            for deal in deals:
                deal['category'] = 'deals'
                deal['subcategory'] = deal_type
                self.menu_collection.insert_one(deal)
    
    def get_menu_items(self, category=None):
        """Get menu items, optionally filtered by category"""
        if category:
            return list(self.menu_collection.find({'category': category}, {'_id': 0}))
        return list(self.menu_collection.find({'type': {'$ne': 'restaurant_info'}}, {'_id': 0}))
    
    def get_restaurant_info(self):
        """Get restaurant information"""
        info = self.menu_collection.find_one({'type': 'restaurant_info'}, {'_id': 0})
        return info['data'] if info else {}
    
    def search_menu(self, query):
        """Search menu items by name or description"""
        results = self.menu_collection.find({
            '$and': [
                {'type': {'$ne': 'restaurant_info'}},
                {'$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]}
            ]
        }, {'_id': 0})
        return list(results)
    
    def create_order(self, customer_name, customer_phone, items, total_amount):
        """Create a new order"""
        order = {
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'items': items,
            'total_amount': total_amount,
            'status': 'pending',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        result = self.orders_collection.insert_one(order)
        return str(result.inserted_id)
    
    def get_orders(self, status=None):
        """Get orders, optionally filtered by status"""
        query = {}
        if status:
            query['status'] = status

        orders = list(self.orders_collection.find(query))
        for order in orders:
            if '_id' in order:
                order['_id'] = str(order['_id'])
        return orders
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        try:
            oid = ObjectId(order_id)
        except Exception:
            return

        self.orders_collection.update_one(
            {'_id': oid},
            {'$set': {'status': status, 'updated_at': datetime.now()}}
        )
    
    def get_order_stats(self):
        """Get order statistics for dashboard"""
        pipeline = [
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        status_stats = list(self.orders_collection.aggregate(pipeline))
        
        # Get daily revenue
        daily_pipeline = [
            {'$match': {'status': 'completed'}},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}},
                'revenue': {'$sum': '$total_amount'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        daily_stats = list(self.orders_collection.aggregate(daily_pipeline))
        
        return {
            'status_stats': status_stats,
            'daily_stats': daily_stats
        }
    
    def save_conversation(self, customer_name, messages):
        """Save conversation history for a customer"""
        conversation = {
            'customer_name': customer_name,
            'messages': messages,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Check if conversation already exists for this customer
        existing = self.conversations_collection.find_one({'customer_name': customer_name})
        
        if existing:
            # Update existing conversation
            self.conversations_collection.update_one(
                {'customer_name': customer_name},
                {
                    '$set': {
                        'messages': messages,
                        'updated_at': datetime.now()
                    }
                }
            )
        else:
            # Create new conversation
            self.conversations_collection.insert_one(conversation)
    
    def get_conversation(self, customer_name):
        """Get conversation history for a customer"""
        conversation = self.conversations_collection.find_one({'customer_name': customer_name})
        if conversation:
            return conversation.get('messages', [])
        return []
    
    def get_all_customers(self):
        """Get list of all customers who have conversations"""
        customers = self.conversations_collection.find({}, {'customer_name': 1, '_id': 0})
        return [customer['customer_name'] for customer in customers]
    
    def delete_conversation(self, customer_name):
        """Delete conversation for a customer"""
        self.conversations_collection.delete_one({'customer_name': customer_name})
