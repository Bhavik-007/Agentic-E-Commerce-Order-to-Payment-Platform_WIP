import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { askAssistant } from "../services/assistantService";
import { startQuickCheckout } from "../services/paymentService";

export function AIShoppingAssistant() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [products, setProducts] = useState([]);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const { authenticated, token } = useAuth();
  const navigate = useNavigate();

  async function submit(event) {
    event.preventDefault();
    if (!message.trim()) return;
    setBusy(true);
    try { const result = await askAssistant(message); setReply(result.response); setProducts(result.products); }
    catch { setReply("The assistant is unavailable. Make sure FastAPI and Ollama are running."); }
    finally { setBusy(false); }
  }

  async function quickPay(product) {
    if (!authenticated) { navigate("/login"); return; }
    try { const checkout = await startQuickCheckout(token, product.id); navigate(`/payment/${checkout.payment_id}`, { state: { checkout } }); }
    catch (error) { setNotice(error.response?.data?.detail ?? "Could not start quick payment."); }
  }

  return <section id="assistant" className="assistant-panel"><p className="eyebrow">Your shopping copilot</p><h2>What are you looking for?</h2>
    <form className="prompt-box" onSubmit={submit}><input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="I need a laptop under ₹80,000 for AI development." /><button disabled={busy} aria-label="Send prompt">{busy ? "…" : "↑"}</button></form>
    {reply && <p className="assistant-answer">{reply}</p>}
    {products.length > 0 && <div className="ai-products">{products.map((product) => <article className="ai-product" key={product.id}><div><strong>{product.name}</strong><span>₹{Number(product.price).toLocaleString("en-IN")} · ★ {product.rating}</span></div><button className="button button-small" onClick={() => quickPay(product)}>Quick pay</button></article>)}</div>}
    {notice && <p className="form-error">{notice}</p>}
    <div className="suggestions"><button onClick={() => setMessage("Find me a laptop")}>Find a laptop</button><button onClick={() => setMessage("Compare headphones")}>Compare headphones</button><button onClick={() => setMessage("Track my order")}>Track my order</button></div>
  </section>;
}
