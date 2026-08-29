# ShopPilot AI - Current Development Reference

This file describes the current working implementation. It is intended as a practical reference for backend and frontend development, testing, and validation.

## 1. Current product scope

ShopPilot AI is a local React + FastAPI commerce application using SQL Server Windows Authentication. The application currently supports:

- Product catalog and seeded demo products.
- Customer registration and login with JWT.
- Persistent customer cart.
- Razorpay Test Mode checkout and server-side payment signature verification.
- Dummy payment mode as a fallback when Razorpay Test Mode is disabled.
- Ollama-powered shopping recommendations.
- LangGraph shopping workflow.
- MCP-controlled catalog tools for AI access.
- A global AI commerce copilot with shortlist and quick-pay capability.

RBAC/admin features are deliberately not implemented yet. The current focus is customer commerce functionality.

## 2. Technology stack

| Area | Current implementation |
| --- | --- |
| Frontend | React 18, Vite, JavaScript, React Router, Axios, Context API |
| Backend | Python 3.12 virtual environment, FastAPI, Pydantic, SQLAlchemy |
| Database | SQL Server, PyODBC, Windows Authentication |
| Authentication | JWT using `python-jose`; password hashing with Passlib/bcrypt |
| Payments | Razorpay Python SDK in Test Mode; server-side signature verification |
| AI | Ollama (`llama3.1:latest`), LangChain Ollama adapter, LangGraph |
| Agent tools | Model Context Protocol (MCP) FastMCP server |

## 3. Application start commands

Open two terminals from the project root.

### Backend

```powershell
.\backend\.venv\Scripts\Activate.ps1
uvicorn app:app --reload --port 8000
```

Backend URLs:

- API root: `http://localhost:8000`
- Swagger documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

### Frontend

```powershell
cd frontend
npm run dev
```

Frontend URL: `http://localhost:5173`

### Optional MCP server

Run this only when connecting an MCP-compatible external client.

```powershell
python -m backend.app.mcp_server
```

The MCP server uses standard input/output transport.

## 4. Environment configuration

The project-root `.env` holds local configuration and must never be committed with live secrets.

Required non-secret settings:

```env
SQL_SERVER=localhost\MSSQLSERVER01
SQL_DATABASE=ShopPilotAI
SQL_DRIVER=ODBC Driver 18 for SQL Server
SQL_TRUSTED_CONNECTION=yes
SQL_TRUST_SERVER_CERTIFICATE=yes
CORS_ORIGINS=http://localhost:5173
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:latest
PAYMENT_TEST_MODE=false
```

Razorpay settings are server-side only:

```env
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...
```

`PAYMENT_TEST_MODE=false` enables Razorpay Test Mode when both Razorpay values exist. Set it to `true` to use the internal dummy-payment flow without any Razorpay network call.

## 5. Backend structure

```text
backend/
  app/
    api/              # HTTP routes and request dependencies
    agents/           # LangGraph routing/shopping logic
    core/             # settings, database, security
    models/           # SQLAlchemy database entities
    schemas/          # Pydantic request/response contracts
    services/         # controlled commerce and checkout operations
    mcp_server.py     # MCP tool server
    seed.py           # local demo catalog seeding
    main.py           # FastAPI application
  scripts/
    smoke_payment.py  # local end-to-end payment smoke test
```

### Core modules

| File | Responsibility |
| --- | --- |
| `core/config.py` | Loads `.env`, builds SQL Server ODBC URL, exposes Razorpay/Ollama settings |
| `core/database.py` | SQLAlchemy engine, session factory, base model |
| `core/security.py` | Password hashing, JWT creation, OAuth bearer configuration |
| `main.py` | FastAPI lifespan, database table creation, catalog seed call, CORS setup |

### Important database behavior

`Base.metadata.create_all()` runs at API startup. This is suitable for the current local-development stage. Introduce Alembic migrations before shared, production, or destructive schema changes.

`seed.py` inserts demo catalog data only if the `products` table is empty:

- AstraBook Pro 14
- WavePods Studio
- Orbit Smartwatch

## 6. Current SQL Server tables

| Table | Purpose |
| --- | --- |
| `users` | Customer identity, password hash, active flag |
| `categories` | Product categories |
| `products` | Sellable catalog product data |
| `inventory` | Current product quantities |
| `carts` | Customer carts; current cart uses `OPEN` status |
| `cart_items` | Product/quantity/price lines within a cart |
| `orders` | Checkout order header and payment state |
| `order_items` | Immutable product name/price snapshots for the order |
| `payments` | Razorpay or dummy payment data and status |

Current payment lifecycle:

```text
CREATED -> CAPTURED
```

Current order lifecycle:

```text
PAYMENT_PENDING -> PAID
```

The browser never changes these states directly. Payment state changes only after a backend verification endpoint succeeds.

## 7. API endpoints implemented

### Health

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | API availability check |

### Authentication

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | No | Create customer and return JWT |
| POST | `/api/v1/auth/login` | No | Return JWT for existing customer |
| GET | `/api/v1/auth/me` | Bearer token | Return current customer |

### Catalog

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/products` | List active products |
| GET | `/api/v1/products?query=Astra` | Search products by name |
| GET | `/api/v1/products?category_id=1` | Filter by category |

### Cart

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/cart` | Bearer token | Get or create active cart |
| POST | `/api/v1/cart/items` | Bearer token | Add item: `product_id`, `quantity` |
| DELETE | `/api/v1/cart/items/{item_id}` | Bearer token | Remove an item |

### Payments

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| POST | `/api/v1/payments/checkout` | Bearer token | Create cart checkout order/payment |
| POST | `/api/v1/payments/quick-checkout` | Bearer token | Create payment for one AI-shortlisted product |
| POST | `/api/v1/payments/{payment_id}/verify` | Bearer token | Verify real Razorpay signature |
| POST | `/api/v1/payments/{payment_id}/verify-test` | Bearer token | Complete internal dummy payment only |

`/verify` expects this payload from Razorpay Checkout:

```json
{
  "razorpay_payment_id": "pay_...",
  "razorpay_signature": "..."
}
```

The backend supplies the stored Razorpay order ID during signature verification; it does not trust an order ID sent by the browser.

### Agent supervisor and AI chat

| Method | Endpoint | Purpose |
| --- | --- |
| POST | `/api/v1/assistant/route` | Deterministic intent routing/approval requirement |
| POST | `/api/v1/assistant/chat` | Shopping response from LangGraph + Ollama + controlled catalog data |

Example chat request:

```json
{ "message": "Suggest a laptop for AI development" }
```

## 8. Razorpay Test Mode implementation

### Standard cart checkout

1. Customer adds product to cart.
2. React calls `POST /payments/checkout` with JWT.
3. FastAPI creates an internal order and calls Razorpay `order.create()`.
4. FastAPI returns only the public key, amount, currency, internal payment ID, and Razorpay order ID.
5. React loads `https://checkout.razorpay.com/v1/checkout.js` and opens Checkout.
6. Razorpay returns payment ID/signature to React.
7. React calls FastAPI `/payments/{id}/verify`.
8. FastAPI verifies the signature with `RAZORPAY_KEY_SECRET`.
9. Payment becomes `CAPTURED`; order becomes `PAID`.

### AI quick checkout

1. Ollama recommends actual catalog records.
2. User clicks **Shortlist & pay** in the global AI panel.
3. FastAPI creates a one-product order and Razorpay Test Mode order.
4. The global AI panel opens Razorpay Checkout.
5. The same server-side verification process applies.

### Dummy fallback

If `PAYMENT_TEST_MODE=true`, the same screens use generated `order_test_*` and `pay_test_*` identifiers. This is useful when Razorpay credentials/network access are unavailable.

## 9. AI, LangGraph, Ollama, and MCP

### Supervisor behavior

`agents/supervisor.py` routes a message before an agent can act:

| Intent | Selected agent | Rule |
| --- | --- | --- |
| Search/recommendation | Shopping | Uses catalog tool |
| Cart/checkout/cancel | Order | Commerce operation route |
| Payment | Payment | Authenticated checkout required |
| Tracking/order status | Support | Support route |
| Refund | Refund | Human approval required |

### Shopping graph

`agents/shopping.py` contains a simple LangGraph workflow:

```text
Customer prompt
  -> controlled catalog tool
  -> Ollama response node
  -> response + recommended products
```

Ollama receives catalog facts only. The prompt instructs it not to invent pricing, availability, specifications, or policies.

### MCP tools

`mcp_server.py` exposes these read-only tools:

| Tool | Purpose |
| --- | --- |
| `search_catalog(query, limit)` | Search active SQL Server products |
| `product_details(product_id)` | Get one active product record |

No MCP tool provides database credentials, arbitrary SQL execution, or payment-secret access.

## 10. Frontend structure

```text
frontend/src/
  components/
    Navbar.jsx
    ProductCard.jsx
    AIShoppingAssistant.jsx
    UniversalAssistant.jsx
  context/
    AuthContext.jsx
    CartContext.jsx
  pages/
    Home.jsx
    Products.jsx
    Auth.jsx
    Cart.jsx
    Payment.jsx
  services/
    api.js
    productService.js
    cartService.js
    paymentService.js
    assistantService.js
  styles/
    global.css
  App.jsx
  main.jsx
```

### React pages

| Route | Component | Current role |
| --- | --- | --- |
| `/` | `Home` | Landing page, hero, inline assistant |
| `/products` | `Products` | Live product catalog and add-to-bag action |
| `/login` | `Auth` | Customer login |
| `/register` | `Auth` | Customer registration |
| `/cart` | `Cart` | Cart details and standard checkout |
| `/payment/:paymentId` | `Payment` | Razorpay/dummy checkout and verified completion state |

### Shared React components

| Component | Current behavior |
| --- | --- |
| `Navbar` | Navigation, customer state, cart item count |
| `ProductCard` | Product summary plus add-to-bag action |
| `AIShoppingAssistant` | Home-page conversational shopping search |
| `UniversalAssistant` | Floating global copilot on every page |

### Context/state management

`AuthContext` stores JWT and customer details in browser local storage for the current development phase. `CartContext` reloads the authenticated server cart and exposes add/remove operations. Axios sends bearer tokens per protected request.

## 11. Global AI commerce copilot

The global bottom-right **ShopPilot AI** panel is available on every page.

Current actions available in one panel:

1. Search catalog with natural language.
2. Review Ollama-generated recommendations.
3. View shortlists with real price/rating values.
4. Start a payment for a shortlisted product.
5. Open Razorpay Test Mode checkout or dummy checkout.
6. View server-verified payment success.

Customer sign-in is required before any payment is initiated.

## 12. Validation completed

Completed checks:

- SQL Server connection with `Trusted_Connection=yes`.
- Catalog seed and product queries.
- MCP catalog search and detail lookup against SQL Server.
- Ollama response using real catalog data.
- JWT registration/login and protected cart flow.
- Dummy cart checkout, payment verification, and `PAID` order transition.
- Dummy AI quick-checkout, payment verification, and `PAID` order transition.
- Razorpay configuration load with secrets remaining server-side.
- React production build via `npm run build`.

The reusable test script is:

```powershell
.\backend\.venv\Scripts\python.exe -m backend.scripts.smoke_payment
```

It creates disposable local customer/order/payment data in `ShopPilotAI` and tests the dummy payment flow. Do not run it with real Razorpay mode enabled unless you specifically want it to create sandbox orders.

## 13. Recommended next backend work

1. Replace `create_all()` with Alembic migrations.
2. Add order history and order-details APIs/UI.
3. Add inventory availability/reservation inside checkout transactions.
4. Add payment webhook signature verification for Razorpay server-to-server events.
5. Add failed payment/retry state transitions.
6. Add cancellation/refund models and human-approval workflow.
7. Add structured audit/agent execution logs.
8. Connect the supervisor to dedicated order, payment, support, and refund LangGraph nodes.

## 14. Recommended next frontend work

1. Product-detail route with image/specification data.
2. Category/search/filter controls.
3. Order history and tracking screens.
4. Address collection and checkout confirmation.
5. Razorpay loading/error/retry polish.
6. AI conversation history and session persistence.
7. Responsive UI testing for mobile/tablet.

## 15. Security rules to preserve

- Never send `RAZORPAY_KEY_SECRET` to React.
- Never mark payment success based solely on browser response.
- Never expose SQL connections or arbitrary SQL through MCP/AI tools.
- Keep Windows Authentication for SQL Server; do not introduce SQL usernames/passwords.
- Validate payment/user ownership before any order or payment state update.
- Keep refunds and other sensitive financial actions behind explicit human approval.
