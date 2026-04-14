# AuraBrand

**AuraBrand** is a self-improving, brand-aware document creation agentic suite. It leverages a powerful multi-agent architecture to autonomously research, draft, and refine brand-consistent assets like presentations and documents.

![AuraBrand Dashboard](https://raw.githubusercontent.com/Angella-Mulikatete/aurabrand/main/docs/assets/banner.png) *(Placeholder for Banner)*

## 🚀 Overview

AuraBrand uses a state-of-the-art "Agent Mesh" powered by **LangGraph** to orchestrate specialized AI agents. These agents work together to ensure that every document produced not only meets the user's requirements but strictly adheres to predefined brand guidelines, tone of voice, and stylistic preferences.

### Key Features

- **Multi-Agent Orchestration**: Decoupled roles including The Strategist, The Wordsmith, The Brand Guardian, and The Researcher.
- **Brand Intelligence**: Automated tone-of-voice enforcement and prohibited terminology filtering.
- **Agentic Skills**: Specialized capabilities for generating PowerPoint presentations (`.pptx`), PDFs, and long-form documents.
- **Automated Research**: Integrated search tools (Tavily, Brave Search) for data-driven content.
- **Self-Improvement Loop**: Leverages feedback history and iteration cycles to refine outputs.
- **Next.js Command Center**: A premium, interactive UI for managing brand assets and triggering generations.

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI, LangGraph, LangChain, Pydantic, ChromaDB.
- **Frontend**: Next.js 15+, Tailwind CSS, Radix UI (Base UI), Lucide Icons.
- **Data Layer**: [Convex](https://convex.dev) for real-time database and serverless functions.
- **AI Models**: Support for Google Gemini, Anthropic Claude, OpenAI GPT-4, and Groq.

## 🏁 Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- [Convex](https://docs.convex.dev/home) Account (for the backend data layer)

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Angella-Mulikatete/aurabrand.git
    cd aurabrand
    ```

2.  **Set up the Backend (Python)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e .
    ```

3.  **Set up the Frontend (Next.js)**:
    ```bash
    cd web
    npm install
    cd ..
    ```

4.  **Install Global Dependencies**:
    ```bash
    npm install
    ```

### Environment Configuration

Create a `.env` file in the root directory (using `.env.example` as a template if available) and add your API keys:

```env
# LLM Providers
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
GOOGLE_API_KEY=your_key

# Search Tools
TAVILY_API_KEY=your_key
BRAVE_SEARCH_API_KEY=your_key

# Convex (Set up via npx convex dev)
CONVEX_DEPLOYMENT=your_deployment_id
```

## 🏃 Running the Application

You will need three terminal windows to run the full stack:

1.  **Convex Backend**:
    ```bash
    npx convex dev
    ```

2.  **FastAPI Agent Server**:
    ```bash
    python api.py
    ```

3.  **Next.js Web UI**:
    ```bash
    cd web
    npm run dev
    ```

Alternatively, you can run the legacy **Streamlit Dashboard** for quick testing:
```bash
streamlit run src/dashboard.py
```

## ⌨️ Terminal Usage (CLI)

You can trigger AuraBrand missions directly from your terminal without using a browser. This is ideal for batch processing or automation.

```bash
# Generate a Presentation (Default)
python main.py --intent PRESENTATION --prompt "Future of AI in creative design" --brand "AuraBrand"

# Generate a Document
python main.py --intent DOCUMENT --prompt "Project specification for a new EV charging network" --brand "VoltNet" --color "#10B981"
```

### CLI Arguments:
- `--prompt`: (Required) The mission description.
- `--intent`: `PRESENTATION` or `DOCUMENT` (Default: `PRESENTATION`).
- `--brand`: Your brand name (Default: `AuraBrand`).
- `--tone`: Brand tone of voice (Default: `Innovative and professional`).
- `--color`: Primary hex color (Default: `#7C3AED`).
- `--font`: Typography choice (Default: `Fira Sans`).
- `--iters`: Refinement iterations (Default: `3`).
- `--verbose`: Enable detailed node processing logs.

## 🔌 Editor Integration (MCP)

AuraBrand supports the **Model Context Protocol (MCP)**, allowing you to use it as a tool directly inside AI editors like **Cursor**, **Windsurf**, or **VS Code**.

### Setup for Cursor/Windsurf:
1. Open your editor's **MCP Settings**.
2. Add a new **Command** server:
   - **Name**: `AuraBrand`
   - **Command**: `python [abs_path_to_repo]/src/mcp_server.py`
3. You can now use `@AuraBrand` in your AI chat to generate documents or read brand guidelines.

## 📂 Project Structure

- `src/`: Core agentic logic, LangGraph definitions, and skills.
- `web/`: Next.js frontend application.
- `convex/`: Database schema and serverless backend functions.
- `docs/`: Project specifications and documentation.
- `outputs/`: Local storage for generated documents and assets.
- `tests/`: Automated test suites for agents and tools.

## 📄 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.
