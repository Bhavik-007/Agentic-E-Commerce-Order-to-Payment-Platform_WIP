# ShopPilot AI - Future Enhancement Roadmap

This roadmap is separate from `read.md`, which documents the current working system. Items below are planned enhancements, not claims about current functionality.

## Guiding principle

Build ShopPilot AI into a Smart Universal Commerce Intelligence Platform where customers can discover, compare, buy, track, cancel, and request help through a safe AI-assisted journey. Every financial or customer-data action must remain deterministic, auditable, and backend-controlled.

## Phase 1 - Commerce foundation hardening

### Database and backend

- Replace startup `create_all()` with Alembic migrations.
- Add seed/migration version control for categories, products, and inventory.
- Create repositories and services for all commerce domains.
- Add structured application logging with correlation IDs.
- Add API error response standards and global exception handling.
- Add rate limiting for login, chat, and payment endpoints.

### Customer features

- Customer profile management.
- Address management with default shipping/billing address.
- Product detail API: images, specifications, tags, reviews, related items.
- Categories, brands, ranges, ratings, and sort filters.
- Product comparison table.
- Wishlist and recently viewed products.

## Phase 2 - Cart, checkout, and orders

### Cart improvements

- Update cart item quantity endpoint.
- Remove all cart items endpoint.
- Coupon and promotion engine.
- Tax and shipping calculation services.
- Cart expiration and abandoned-cart handling.

### Checkout improvements

- Shipping address selection.
- Order review page.
- Inventory reservation within a database transaction.
- Idempotency keys to prevent duplicate checkouts.
- Recalculate prices server-side at checkout.
- Delivery estimate and shipping method selection.

### Order management

- `GET /orders` order history endpoint.
- `GET /orders/{id}` order detail endpoint.
- Order timeline: created, paid, processing, shipped, delivered.
- Tracking number and carrier integration.
- Customer order-history and order-detail React pages.

## Phase 3 - Razorpay production-grade payment lifecycle

### Payment behavior

- Payment attempts table for retry history.
- Explicit state-transition rules for `CREATED`, `PENDING`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `CANCELLED`, `REFUNDED`, and `PARTIALLY_REFUNDED`.
- Payment failure capture and customer-friendly retry UI.
- Payment retry from order details.
- Capture/refund reconciliation job.
- Currency and amount validation in paise before calling Razorpay.

### Razorpay webhook support

- Webhook endpoint for Razorpay server-to-server events.
- Razorpay webhook signature verification.
- Idempotent webhook event storage.
- Reconcile browser callback with webhook state.
- Do not rely on browser callback alone for final production payment state.

### Refund workflow

- Refunds table and refund service.
- Eligibility rules based on payment/order status.
- Partial and full refund support.
- Explicit human approval queue before refund creation.
- Razorpay refund status synchronization.
- Customer refund timeline and notifications.

## Phase 4 - Agentic commerce intelligence

### LangGraph expansion

- Convert the current deterministic router into a full LangGraph supervisor graph.
- Add separate Shopping, Order, Payment, Support, and Refund nodes.
- Add shared graph state: user ID, session ID, active order, shortlist, and pending approval.
- Add retries, fallbacks, and failure routing.
- Persist conversation/graph checkpoints.

### Safe tools and MCP

- Add controlled MCP tools for inventory lookup, order status, cart read, and recommendation retrieval.
- Never expose arbitrary SQL, payment secrets, or raw payment operations to an LLM.
- Inject authenticated customer context server-side; do not permit an agent to choose another customer ID.
- Add structured input/output schemas to every MCP tool.
- Add tool-call audit logging with execution time and errors.

### Ollama and knowledge intelligence

- Add configurable Ollama model selection.
- Add embedding model support using `nomic-embed-text`.
- Build a product and FAQ retrieval pipeline.
- Add retrieval citations in assistant answers.
- Add customer preference memory with consent controls.
- Add AI recommendation scoring and explanation records.

### Universal AI copilot capabilities

- Maintain chat history across browser sessions.
- Support product comparison in chat.
- Let users modify cart quantities through confirmed AI actions.
- Show order status/tracking in the global assistant.
- Let users restart failed payments from the assistant.
- Add guided cancellation/refund requests with approval status.
- Add accessibility features: keyboard focus, screen-reader labels, and reduced-motion support.

## Phase 5 - Admin and operations

### Admin interface

- Product/category/inventory management.
- Customer list and account support actions.
- Order/payment/refund monitoring.
- Coupon/promotion configuration.
- Agent execution dashboard.
- Audit-log search and export.

### Operational controls

- Inventory low-stock alerts.
- Payment failure monitoring.
- Refund approval queue.
- Manual order status updates with audit trail.
- Feature flags for enabling/disabling AI, MCP tools, and payment methods.

RBAC can be added when the admin modules begin. It is intentionally not required for the current customer-focused milestone.

## Phase 6 - Quality, security, and deployment

### Testing

- Unit tests for security, cart totals, inventory, checkout, payment signatures, and refund eligibility.
- API integration tests using a dedicated local test database.
- React component and user-flow tests.
- Razorpay Test Mode contract tests.
- LangGraph routing and MCP tool schema tests.
- End-to-end checkout test suite.

### Security

- Replace browser local-storage JWT handling with secure refresh-token/cookie strategy where appropriate.
- Add password reset and email verification.
- Add CSRF protections if cookie authentication is introduced.
- Rotate JWT and Razorpay secrets through secure environment management.
- Mask secrets and personal data in logs.
- Add request validation, rate limits, and abuse monitoring.

### Deployment

- Dockerfiles for frontend/backend.
- Docker Compose for local services where compatible with SQL Server strategy.
- CI pipeline: lint, tests, build, migration validation.
- Environment-specific `.env` templates.
- Centralized logs and health/readiness endpoints.
- Backup and restore plan for SQL Server.

## Suggested implementation order

1. Alembic migrations and order-history APIs.
2. Address-aware checkout with inventory reservation.
3. Razorpay webhooks, failed payment, and retry support.
4. Refund approval workflow.
5. Dedicated LangGraph agents and expanded MCP tools.
6. Admin dashboard and audit logs.
7. Automated tests, CI, and deployment automation.

## Definition of done for the next milestone

The next milestone is complete when a customer can:

1. Register and manage an address.
2. Search/filter/view a product.
3. Add or modify cart quantities.
4. Checkout with an address and inventory reservation.
5. Pay with Razorpay Test Mode.
6. See verified payment and order history.
7. Ask the AI assistant for products, cart support, and order status using controlled tools.
