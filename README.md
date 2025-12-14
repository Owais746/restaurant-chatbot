# Restaurant Chatbot (Broadway Pizza)
Streamlit-based restaurant chatbot for **Broadway Pizza** with:
- AI waiter persona (Paulo) powered by **OpenRouter**
- Menu + orders stored in **MongoDB**
- **Name-based conversation history** (returning users load previous chats)
## Features
- **Chatbot**: Talk to Paulo, browse menu, ask questions, place an order.
- **Conversation memory**: Conversations are stored in MongoDB by customer name (normalized).
- **Dashboard**: Simple order stats.
- **Menu**: Reads menu from [data.json](cci:7://file:///d:/restaurant-chatbot/data.json:0:0-0:0) and stores it in MongoDB.
## Tech Stack
- Python + Streamlit
- MongoDB (local or MongoDB Atlas)
- OpenRouter API (chat completions)
- `uv` for dependency management
## Project Structure
- [main.py](cci:7://file:///d:/restaurant-chatbot/main.py:0:0-0:0) — Streamlit app (UI + routing)
- [database.py](cci:7://file:///d:/restaurant-chatbot/database.py:0:0-0:0) — MongoDB access (menu, orders, conversations)
- [openrouter_client.py](cci:7://file:///d:/restaurant-chatbot/openrouter_client.py:0:0-0:0) — OpenRouter client + waiter prompt
- [data.json](cci:7://file:///d:/restaurant-chatbot/data.json:0:0-0:0) — Restaurant menu and deals
- [.env](cci:7://file:///d:/restaurant-chatbot/.env:0:0-0:0) — local secrets (NOT committed)
## Setup (Local)
### 1) Install `uv`
If you don't have it installed yet:
```bash
pip install uv
2) Install dependencies
bash
uv sync
3) Configure environment variables
Create a .env file in the project root:

env
MONGODB_URI=mongodb://localhost:27017/restaurant_chatbot
OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY
STREAMLIT_SERVER_PORT=8501
Notes:

.env is ignored by git (see .gitignore).
For deployments, use Streamlit Secrets instead of uploading .env.
4) Run MongoDB
Option A: Local MongoDB

Install MongoDB locally and ensure it is running.
Option B: MongoDB Atlas

Create a cluster and use the connection string as MONGODB_URI.
5) Run the Streamlit app
bash
uv run streamlit run main.py
Open:

http://localhost:8501
Conversation Memory (How it works)
On first open, the app asks for a name.
The name is normalized (trim + lowercase + collapse spaces).
Example: Ali, ali, ALI are treated as the same user.
If the user exists in MongoDB, their saved messages are loaded.
After every assistant response, the conversation is saved back to MongoDB.
Deployment (Streamlit Community Cloud)
Do NOT upload .env
Streamlit Cloud apps should store secrets in Streamlit Secrets.

1) Create the app in Streamlit Cloud
Select your GitHub repo
Main file: main.py
2) Add Secrets
In Streamlit Cloud:

App settings
Secrets
Paste:

toml
OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"
MONGODB_URI = "YOUR_MONGODB_URI"  # Use MongoDB Atlas in cloud deployments
Important:

Do not use mongodb://localhost... on Streamlit Cloud.
Use MongoDB Atlas or another externally reachable MongoDB.
Troubleshooting
OpenRouter errors
Confirm OPENROUTER_API_KEY is set.
Try running:
bash
uv run python test_ai.py
Security
Never commit .env.
Use Streamlit Secrets for deployments.
 
**Status:** README content provided; copy/paste into [README.md](cci:7://file:///d:/restaurant-chatbot/README.md:0:0-0:0).
Feedback submitted






Code

GPT-5.2 Medium Reasoning Fast


Drop to add to Cascade
