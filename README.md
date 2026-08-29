# ShopPilot AI

ShopPilot AI is a React + FastAPI e-commerce platform. This initial increment establishes the React application, Python REST API, and SQL Server foundation using Windows Authentication.

## What is included now

- Vite-powered React frontend with responsive home, catalog, navigation, and API client.
- FastAPI backend with CORS, health endpoint, SQLAlchemy infrastructure, and a first product catalog endpoint.
- SQL Server / PyODBC connection configured for `Trusted_Connection=yes`; no SQL username or password is used.
- Initial `categories`, `products`, and `inventory` models. The remaining modules (auth, cart, orders, payments, agents) will follow the delivery phases in the BRD.

## Prerequisites

- Python 3.11 or later
- Node.js 20 or later
- Microsoft SQL Server running locally (for example, `localhost` or `localhost\\SQLEXPRESS`)
- Microsoft ODBC Driver 18 for SQL Server
- Your Windows account needs permission to create/use the `ShopPilotAI` database.

## SQL Server setup

Open PowerShell from the project root and create the database using Windows Authentication:

```powershell
sqlcmd -E -S localhost -C -i database/create_database.sql
```

If your SQL Server is a named instance, replace `localhost` with its name, for example `localhost\\SQLEXPRESS`, in both this command and `.env`.

If the API reports `Cannot open database "ShopPilotAI"` (SQL Server error 4060), run the database script once from SQL Server Management Studio or an elevated terminal using your Windows account. It creates the database if needed and maps your Windows login to the local development database. If `sqlcmd` cannot connect to the default instance, use the instance shown in SQL Server Configuration Manager, for example `localhost\\MSSQLSERVER01`, for both the command and `SQL_SERVER` in `.env`.

The project-root `.env` contains the non-secret local SQL defaults. Do not add a SQL username or password; `Trusted_Connection=yes` authenticates as the signed-in Windows user. Set real Razorpay values only when payment work begins.

## Run the backend

```powershell
.\backend\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`, Swagger UI at `http://localhost:8000/docs`, and the health check at `http://localhost:8000/api/v1/health`.

## Run the frontend

In another terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. The catalog calls `GET /api/v1/products`; until catalog rows exist it displays an intentional empty-state message.

## Next implementation increments

1. Add Alembic migrations plus users, authentication, and role-protected APIs.
2. Implement cart, checkout, orders, inventory reservation, and transactional service/repository layers.
3. Integrate Razorpay server-side order creation and signature verification.
4. Add LangGraph supervisor, controlled agent tools, audit logs, and the AI assistant UI.

## MCP tool boundary

The agent layer uses the Model Context Protocol (MCP) to access controlled tools rather than exposing SQL to a model. The first MCP server provides read-only catalog search and product-detail tools. Start it in a separate terminal after activating the backend virtual environment:

```powershell
python -m backend.app.mcp_server
```

The server uses standard input/output, as expected by MCP clients. It does not accept database credentials or arbitrary SQL from an agent.

## Razorpay Test Mode

Set `PAYMENT_TEST_MODE=false` only after `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are configured in the project-root `.env`. FastAPI creates the Razorpay order using the secret server-side; React receives only the Razorpay public key and order ID. The server verifies the returned payment signature before marking an order as paid.
