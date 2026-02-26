<p align="center">
  <img src="docs/assets/banner.png" alt="FinVerse AI Banner" width="100%"/>
</p>

<h1 align="center">🏦 FinVerse AI</h1>

<p align="center">
  <b>A Real-Time Agentic Banking Operating System</b><br/>
  <i>Streams data. Thinks in agents. Searches the web visibly. Uses RAG. Explains decisions. Enforces compliance.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/LangGraph-Agent_Orchestration-FF6F00?style=for-the-badge&logo=langchain&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
  <img src="https://img.shields.io/badge/Pathway-Streaming-8B5CF6?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector_Store-00D4FF?style=for-the-badge"/>
</p>

<!-- <p align="center">
  <img src="https://img.shields.io/badge/Status-In_Development-yellow?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square"/>
</p> -->

---

<!-- ## 📖 Table of Contents

- [What is FinVerse AI?](#-what-is-finverse-ai)
- [Why FinVerse AI?](#-why-finverse-ai)
- [System Architecture](#-system-architecture)
- [The Six Autonomous Agents](#-the-six-autonomous-agents)
- [Visible Search — The Killer Feature](#-visible-search--the-killer-feature)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Development Roadmap](#-development-roadmap)
- [How It Works — Deep Dive](#-how-it-works--deep-dive)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [License](#-license)

--- -->

## 🧠 What is FinVerse AI?

**FinVerse AI** is not a chatbot. It's a **full-stack financial operating system** powered by autonomous AI agents that reason, validate, search, and justify decisions in real time.

Think of it as an **AI brain for your financial life** — one that:

- 📡 **Streams** your transaction data in real time
- 🤖 **Deploys 6 specialized AI agents** that work together
- 🔍 **Searches the web visibly** (you see every query, every result — like watching an AI think)
- 📚 **Uses RAG** over compliance docs, policies, and your own financial documents
- 💬 **Explains every decision** with transparent, structured reasoning
- 🛡️ **Enforces compliance** against RBI / AML regulations automatically

> **"Here's a financial OS with autonomous economic agents that reason, validate, search, and justify decisions in real time."**

---

## 🔥 Why FinVerse AI?

| Most Banking Apps | FinVerse AI |
|---|---|
| Static dashboards | Real-time streaming intelligence |
| Rule-based alerts | Multi-agent autonomous reasoning |
| Hidden decision logic | Visible, explainable AI decisions |
| Manual compliance checks | Automated compliance validation |
| Basic search | Live web search with visible execution |
| Reactive advice | **Proactive financial intelligence** |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    🖥️  FRONTEND (React + Vite)                 │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │Dashboard │  │ Agent Viewer │  │ Visible Search Panel     │   │
│  │& Charts  │  │ (Live Logs)  │  │ (Streaming Query Viewer) │   │
│  └──────────┘  └──────────────┘  └──────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ WebSocket / SSE / REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ⚡ API GATEWAY (FastAPI)                     │
│            Authentication · Rate Limiting · Routing            │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌──────────────────┐ ┌─────────────┐ ┌──────────────────┐
│ 🔵 LAYER 1       │ │ 🟣 LAYER 2 │ │ 🔴 LAYER 3       │
│ Streaming Intel  │ │ Knowledge   │ │ Agentic AI Core  │
│ (Pathway)        │ │ + RAG       │ │ (Brain Layer)    │
│                  │ │             │ │                  │
│ • Live txns      │ │ • Compliance│ │ • 6 Autonomous   │
│ • Budget updates │ │ • Policies  │ │   Agents         │
│ • Card swipes    │ │ • User docs │ │ • LangGraph      │
│ • Anomaly detect │ │ • Vector DB │ │ • ReAct Loop     │
└──────────────────┘ └─────────────┘ └──────────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      🔧 TOOL LAYER                             │
│  ┌────────────┐ ┌────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Web Search │ │Scraper │ │Vector DB │ │Compliance Engine │   │
│  │(SerpAPI/   │ │(Price  │ │(ChromaDB)│ │(Rule Validator)  │   │
│  │ Tavily)    │ │ Parser)│ │          │ │                  │   │
│  └────────────┘ └────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│              🧠 LLM REASONER (Gemini / GPT-4 / Llama)           │
│                Final reasoning · Decision synthesis             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 The Six Autonomous Agents

Each agent is a **specialized AI worker** that operates autonomously within the orchestration graph.

### 1️⃣ Transaction Intelligence Agent
> *"What is your money doing?"*

- Monitors every transaction in real time via Pathway streaming
- Builds behavioral spend vectors (monthly patterns, category breakdown)
- Detects **category drift** (e.g., sudden spike in entertainment spend)
- Generates financial health insights

### 2️⃣ Fraud Risk Agent
> *"Is this transaction suspicious?"*

- Real-time anomaly detection on incoming transactions
- Behavioral deviation scoring (amount, location, merchant, time)
- Cross-references against known fraud patterns
- Triggers alerts with confidence scores and explanations

### 3️⃣ Budget Guardian Agent
> *"Can you afford this?"*

- Tracks budget limits per category
- Calculates discretionary balance before purchases
- Proactive warnings when spending nears thresholds
- Smart suggestions for reallocation of funds

### 4️⃣ Compliance Validator Agent
> *"Is this allowed?"*

- RAG-powered retrieval over RBI / AML compliance documents
- Validates transactions and recommendations against regulatory rules
- Ensures all AI advice is compliance-safe
- Generates audit trails for every decision

### 5️⃣ Shopping Intelligence Agent (Visible Web Search)
> *"Find me the best deal — and show me how you found it."*

- **Visible Google Search** — user sees every query fired in real time
- Multi-retailer price comparison
- Product rating aggregation
- Historical price trend analysis
- Budget-aware purchase recommendations

### 6️⃣ Explanation Agent
> *"Why did the AI decide this?"*

- Takes decisions from all other agents
- Generates human-readable structured explanations
- Provides reasoning chain: `Action → Observation → Decision`
- Ensures transparency and user trust

---

## 🔍 Visible Search — The Killer Feature

When a user asks: *"Find me the best price for iPhone 15"*, the system responds with a **fully visible, streaming execution experience**:

```
🧠 Planning…
  1. Search product across retailers
  2. Extract prices
  3. Compare ratings
  4. Recommend best value

🔎 Searching: "iPhone 15 price Amazon India"         ← LIVE
🔎 Searching: "iPhone 15 price Flipkart"             ← LIVE
🔎 Searching: "iPhone 15 best deal India 2025"       ← LIVE

📦 Results Found:
  ┌───────────┬──────────┬────────┐
  │ Retailer  │ Price    │ Rating │
  ├───────────┼──────────┼────────┤
  │ Amazon    │ ₹72,990  │ 4.6⭐  │
  │ Flipkart  │ ₹73,499  │ 4.5⭐  │
  │ Croma     │ ₹74,000  │ 4.4⭐  │
  └───────────┴──────────┴────────┘

💰 Budget Check:
  Current discretionary balance: ₹50,000
  ⚠️ This purchase exceeds safe threshold by ₹22,990

🏆 Recommendation: Amazon — ₹72,990
  ✔ Cheapest price
  ✔ Highest rating (4.6⭐)
  ✔ Fast delivery available
  ⚠️ Consider waiting — price dropped 8% last month
```

The user **watches the AI think** — every search query, every extraction, every reasoning step is streamed to the UI.

---

## 🛠️ Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core language |
| **FastAPI** | API gateway & WebSocket server |
| **LangGraph** | Multi-agent orchestration (stateful graph flows) |
| **LangChain** | LLM tool integration & chain management |
| **Pathway** | Real-time data streaming & processing |
| **ChromaDB** | Vector database for RAG embeddings |
| **SerpAPI / Tavily** | Web search APIs for visible search |
| **BeautifulSoup / Playwright** | Web scraping & data extraction |
| **Sentence Transformers** | Embedding generation for documents |
| **Google Gemini / OpenAI GPT-4** | LLM reasoning engine |

### Frontend

| Technology | Purpose |
|---|---|
| **React 18+** | UI framework |
| **Vite** | Build tool & dev server |
| **Framer Motion** | Animations & micro-interactions |
| **Recharts / Chart.js** | Financial data visualization |
| **Socket.IO / EventSource** | Real-time streaming to UI |
| **Zustand** | Lightweight state management |

### Infrastructure

| Technology | Purpose |
|---|---|
| **Docker** | Containerization |
| **Redis** | Caching & session management |
| **PostgreSQL** | Persistent data storage |
| **MongoDB** | Document storage (user uploads, policies) |

---

## 📁 Project Structure

```
FinVerse-AI/
│
├── 📂 backend/
│   ├── 📂 agents/                    # AI Agent definitions
│   │   ├── transaction_agent.py      # Transaction Intelligence Agent
│   │   ├── fraud_agent.py            # Fraud Risk Agent
│   │   ├── budget_agent.py           # Budget Guardian Agent
│   │   ├── compliance_agent.py       # Compliance Validator Agent
│   │   ├── shopping_agent.py         # Shopping Intelligence Agent
│   │   ├── explanation_agent.py      # Explanation Agent
│   │   └── orchestrator.py           # LangGraph Agent Orchestrator
│   │
│   ├── 📂 streaming/                 # Real-time data pipeline
│   │   ├── pathway_pipeline.py       # Pathway streaming engine
│   │   ├── transaction_stream.py     # Transaction event processor
│   │   └── behavior_engine.py        # Behavioral modeling
│   │
│   ├── 📂 rag/                       # RAG Pipeline
│   │   ├── document_processor.py     # PDF/Doc chunking & embedding
│   │   ├── vector_store.py           # ChromaDB integration
│   │   └── retriever.py              # Context retrieval engine
│   │
│   ├── 📂 tools/                     # Agent tool implementations
│   │   ├── web_search.py             # SerpAPI / Tavily integration
│   │   ├── scraper.py                # Price scraper / data extractor
│   │   ├── compliance_rules.py       # Rule engine for validation
│   │   └── budget_calculator.py      # Budget computation tools
│   │
│   ├── 📂 api/                       # FastAPI routes
│   │   ├── routes/
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── transactions.py       # Transaction endpoints
│   │   │   ├── agents.py             # Agent interaction endpoints
│   │   │   ├── search.py             # Visible search endpoints
│   │   │   └── documents.py          # Document upload endpoints
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py     # JWT authentication
│   │   │   └── rate_limiter.py       # Rate limiting
│   │   └── websocket/
│   │       └── stream_handler.py     # WebSocket streaming handler
│   │
│   ├── 📂 models/                    # Data models
│   │   ├── transaction.py
│   │   ├── user.py
│   │   └── agent_response.py
│   │
│   ├── 📂 config/                    # Configuration
│   │   └── settings.py
│   │
│   ├── main.py                       # FastAPI entry point
│   └── requirements.txt              # Python dependencies
│
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   ├── Dashboard/            # Financial dashboard
│   │   │   ├── AgentViewer/          # Live agent execution viewer
│   │   │   ├── SearchPanel/          # Visible search streaming panel
│   │   │   ├── Chat/                 # Conversational interface
│   │   │   ├── TransactionFeed/      # Real-time transaction feed
│   │   │   └── Charts/              # Financial charts & visualizations
│   │   │
│   │   ├── 📂 hooks/                 # Custom React hooks
│   │   │   ├── useWebSocket.js       # WebSocket connection
│   │   │   ├── useAgentStream.js     # Agent execution streaming
│   │   │   └── useTransactions.js    # Transaction data hook
│   │   │
│   │   ├── 📂 store/                 # Zustand state management
│   │   │   └── appStore.js
│   │   │
│   │   ├── 📂 styles/                # CSS styling
│   │   │   └── index.css
│   │   │
│   │   ├── App.jsx                   # Root component
│   │   └── main.jsx                  # Entry point
│   │
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── 📂 data/
│   ├── 📂 compliance_docs/          # RBI / AML rule documents
│   ├── 📂 sample_transactions/      # Sample transaction data
│   └── 📂 embeddings/               # Pre-computed embeddings cache
│
├── 📂 docs/
│   ├── 📂 assets/                   # Images, diagrams
│   ├── architecture.md              # Detailed architecture doc
│   └── api_reference.md             # API documentation
│
├── 📂 scripts/
│   ├── seed_data.py                 # Seed sample transactions
│   ├── index_documents.py           # Index compliance documents
│   └── run_dev.sh                   # Dev startup script
│
├── docker-compose.yml               # Multi-service Docker setup
├── .env.example                     # Environment variables template
├── .gitignore
└── README.md                        # ← You are here
```

---

<!-- ## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Docker** (optional, recommended) — [Download](https://www.docker.com/)
- **Git** — [Download](https://git-scm.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/kaushaljindall/FinVerse-AI.git
cd FinVerse-AI
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section below)
```

### 5. Seed Data & Index Documents

```bash
python scripts/seed_data.py
python scripts/index_documents.py
```

### 6. Run the Application

**Option A — Manual (Development)**
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Option B — Docker (Recommended)**
```bash
docker-compose up --build
```

### 7. Open in Browser

```
Frontend:  http://localhost:5173
API Docs:  http://localhost:8000/docs
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# ═══════════════════════════════════════════
# 🧠 LLM Configuration
# ═══════════════════════════════════════════
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key          # Optional fallback

# ═══════════════════════════════════════════
# 🔍 Web Search APIs
# ═══════════════════════════════════════════
SERPAPI_API_KEY=your_serpapi_key
TAVILY_API_KEY=your_tavily_api_key          # Alternative to SerpAPI

# ═══════════════════════════════════════════
# 🗄️ Database Configuration
# ═══════════════════════════════════════════
POSTGRES_URL=postgresql://user:pass@localhost:5432/finverse
MONGODB_URI=mongodb://localhost:27017/finverse
REDIS_URL=redis://localhost:6379

# ═══════════════════════════════════════════
# 🔒 Authentication
# ═══════════════════════════════════════════
JWT_SECRET_KEY=your_super_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ═══════════════════════════════════════════
# 📊 Pathway Streaming
# ═══════════════════════════════════════════
PATHWAY_LICENSE_KEY=your_pathway_key        # Optional for community edition

# ═══════════════════════════════════════════
# 🧮 Vector Store
# ═══════════════════════════════════════════
CHROMA_PERSIST_DIR=./data/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

--->

## 📅 Development Roadmap

### Phase 1 — Foundation 
- [x] Project scaffolding & architecture design
- [ ] FastAPI backend with authentication
- [ ] React frontend with dashboard skeleton
- [ ] Database setup (PostgreSQL + MongoDB)
- [ ] Basic transaction data model

### Phase 2 — Streaming Intelligence 
- [ ] Pathway integration for real-time transaction streaming
- [ ] Behavioral modeling engine (spend vectors, category tracking)
- [ ] Transaction Intelligence Agent (Agent 1)
- [ ] Real-time transaction feed on frontend

### Phase 3 — Knowledge & RAG 
- [ ] Document ingestion pipeline (PDF, PPTX, DOC)
- [ ] ChromaDB vector store setup
- [ ] RAG retrieval engine
- [ ] Compliance Validator Agent (Agent 4)
- [ ] Document upload UI

### Phase 4 — Agentic Core 
- [ ] LangGraph orchestration setup
- [ ] Fraud Risk Agent (Agent 2)
- [ ] Budget Guardian Agent (Agent 3)
- [ ] Explanation Agent (Agent 6)
- [ ] Agent execution viewer on frontend

### Phase 5 — Visible Search    
- [ ] SerpAPI / Tavily integration
- [ ] Shopping Intelligence Agent (Agent 5) with visible execution
- [ ] Streaming search panel on frontend
- [ ] Budget-aware purchase recommendations
- [ ] Historical price trend analysis

<!-- ### Phase 6 — Polish & Advanced 
- [ ] Auto subscription renewal detection
- [ ] Fake price inflation detection
- [ ] Price drop prediction ("suggest waiting")
- [ ] Full ReAct-style agent loop
- [ ] Docker deployment
- [ ] Performance optimization -->

---

## 🔬 How It Works — Deep Dive

### 🔵 Layer 1 — Streaming Intelligence (Pathway)

Pathway acts as the **financial nervous system**, processing data in real time:

```
Transaction Event
       ↓
   Pathway Pipeline
       ↓
  ┌────┴────┐
  │ Embed   │ → Generate transaction embedding
  └────┬────┘
       ↓
  ┌────┴────┐
  │ Store   │ → Persist to vector DB + PostgreSQL
  └────┬────┘
       ↓
  ┌────┴─────────┐
  │ Update       │ → Update user behavior profile
  │ Behavior     │   (spend vectors, category drift)
  └────┬─────────┘
       ↓
  ┌────┴─────────┐
  │ Trigger      │ → Activate relevant agents
  │ Agents       │   (fraud check, budget alert, etc.)
  └──────────────┘
```

**Key Concepts:**
- **Monthly Spend Vectors** — numerical representation of spending patterns
- **Category Drift Detection** — identifies unusual shifts in spending categories
- **Anomaly Signals** — flags transactions that deviate from behavioral norms

### 🟣 Layer 2 — Knowledge + RAG

The RAG pipeline enables **compliance-aware, document-grounded reasoning**:

```
Document (PDF/DOC)
       ↓
  ┌────┴────┐
  │ Chunk   │ → Split into semantic chunks
  └────┬────┘
       ↓
  ┌────┴────┐
  │ Embed   │ → Generate embeddings (Sentence Transformers)
  └────┬────┘
       ↓
  ┌────┴────────┐
  │ Vector DB   │ → Store in ChromaDB
  └────┬────────┘
       ↓ (at query time)
  ┌────┴────────┐
  │ Retrieve    │ → Fetch top-k relevant chunks
  └────┬────────┘
       ↓
  ┌────┴────┐
  │ LLM     │ → Generate grounded response
  └─────────┘
```

**Sources indexed:**
- RBI / AML compliance regulations
- Credit card policies & terms
- User-uploaded loan agreements
- Insurance policy PDFs

### 🔴 Layer 3 — Agentic AI Core (Brain Layer)

The brain uses **LangGraph** for stateful multi-agent orchestration:

```
        User Query
            ↓
    ┌───────┴───────┐
    │  Orchestrator  │  ← Decides which agents to invoke
    └───────┬───────┘
            │
    ┌───────┼───────────────┬──────────────┐
    ▼       ▼               ▼              ▼
 Agent 1  Agent 2       Agent 5        Agent 4
 (Txn)    (Fraud)      (Shopping)    (Compliance)
    │       │               │              │
    └───────┼───────────────┘              │
            ▼                              │
    ┌───────┴───────┐                      │
    │ Explanation   │◄─────────────────────┘
    │   Agent       │
    └───────┬───────┘
            ▼
    Final Response (Streamed to UI)
```

**Agent Execution Model:**
```
ReAct Loop:
  Thought → Action → Observation → Thought → Action → Final Answer

Visible to User:
  ✅ Action          (what the agent is doing)
  ✅ Observation     (what the agent found)
  ✅ Structured Summary (final reasoning)
  ❌ Internal Thought (hidden chain-of-thought)
```

---

## 📡 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | User registration |
| `POST` | `/api/auth/login` | User authentication |
| `GET` | `/api/transactions` | List transactions |
| `POST` | `/api/transactions` | Add new transaction |
| `POST` | `/api/agents/query` | Send query to agent orchestrator |
| `GET` | `/api/agents/stream` | SSE stream for agent execution |
| `POST` | `/api/search/product` | Visible product search |
| `POST` | `/api/documents/upload` | Upload compliance/policy docs |
| `GET` | `/api/budget/status` | Current budget status |
| `WS` | `/ws/transactions` | Real-time transaction stream |
| `WS` | `/ws/agents` | Real-time agent execution stream |

> 📖 Full interactive API docs available at `http://localhost:8000/docs` when running.

---

## 🏆 What Makes This Winning

| Feature | Implementation |
|---|---|
| **Real-time streaming** | Pathway processes transactions as they happen |
| **Multi-agent AI** | 6 specialized agents, not a single monolithic LLM |
| **Visible search** | Users watch the AI search, extract, and compare |
| **RAG-powered compliance** | Every recommendation is regulation-safe |
| **Explainable AI** | Dedicated Explanation Agent breaks down every decision |
| **Proactive intelligence** | AI prevents bad financial decisions *before* they happen |
| **Price trend analysis** | Suggests waiting if price is likely to drop |
| **Fraud detection** | Real-time behavioral anomaly detection |

---

<!-- ## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

--->

<p align="center">
  <b>Built with 🧠 by <a href="https://github.com/kaushaljindall">Kaushal Jindal</a></b><br/>
  <i>FinVerse AI — Where Finance Meets Autonomous Intelligence</i>
</p>
