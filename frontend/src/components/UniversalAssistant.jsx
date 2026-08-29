import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { askAssistant } from "../services/assistantService";
import { startQuickCheckout, verifyRazorpayPayment, verifyTestPayment } from "../services/paymentService";

export function UniversalAssistant() {
  const { authenticated, token } = useAuth();
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [products, setProducts] = useState([]);
  const [checkout, setCheckout] = useState(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { if (checkout && !checkout.test_mode && !document.getElementById("razorpay-checkout")) { const script = document.createElement("script"); script.id = "razorpay-checkout"; script.src = "https://checkout.razorpay.com/v1/checkout.js"; document.body.appendChild(script); } }, [checkout]);

  async function ask(event) {
    event.preventDefault(); if (!message.trim()) return;
    setBusy(true); setStatus("");
    try { const result = await askAssistant(message); setReply(result.response); setProducts(result.products); }
    catch { setStatus("The commerce intelligence service is unavailable."); }
    finally { setBusy(false); }
  }
  async function beginPayment(product) {
    if (!authenticated) { setStatus("Please sign in before starting a secure payment."); return; }
    try { setCheckout(await startQuickCheckout(token, product.id)); setStatus(""); }
    catch (error) { setStatus(error.response?.data?.detail ?? "Could not start payment."); }
  }
  async function pay() {
    if (checkout.test_mode) { try { const result = await verifyTestPayment(token, checkout.payment_id); setCheckout({ ...checkout, completed: result }); } catch (error) { setStatus(error.response?.data?.detail ?? "Payment verification failed."); } return; }
    if (!window.Razorpay) { setStatus("Razorpay Checkout is still loading. Please try again."); return; }
    const gateway = new window.Razorpay({ key: checkout.razorpay_key_id, amount: Math.round(Number(checkout.amount) * 100), currency: checkout.currency, name: "ShopPilot AI", description: `AI shortlist ${checkout.order_number}`, order_id: checkout.razorpay_order_id, handler: async (response) => { try { const result = await verifyRazorpayPayment(token, checkout.payment_id, response); setCheckout({ ...checkout, completed: result }); } catch (error) { setStatus(error.response?.data?.detail ?? "Payment verification failed."); } }, modal: { ondismiss: () => setStatus("Payment was cancelled. You can retry safely.") } });
    gateway.open();
  }

  return <aside className={`universal-ai ${open ? "is-open" : ""}`} aria-label="ShopPilot commerce intelligence">
    <button className="ai-launcher" onClick={() => setOpen((value) => !value)}>{open ? "×" : "✦"}<span>ShopPilot AI</span></button>
    {open && <div className="ai-drawer"><p className="eyebrow">Universal commerce intelligence</p><h2>Ask. Choose. Pay.</h2>
      {!checkout ? <><form onSubmit={ask} className="ai-search"><input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Find a laptop for AI work" /><button disabled={busy}>{busy ? "…" : "Ask"}</button></form>
        <div className="ai-shortcuts"><button onClick={() => { setMessage("Find me a laptop"); }}>Find products</button><button onClick={() => { setMessage("Compare headphones"); }}>Compare</button><Link to="/cart">My bag</Link></div>
        {reply && <p className="ai-reply">{reply}</p>}
        {products.map((product) => <article className="ai-choice" key={product.id}><div><strong>{product.name}</strong><span>₹{Number(product.price).toLocaleString("en-IN")} · ★ {product.rating}</span></div><button onClick={() => beginPayment(product)}>Shortlist & pay</button></article>)}
      </> : <div className="ai-checkout">{checkout.completed ? <><h3>Payment confirmed</h3><p>Order {checkout.completed.order_number} is {checkout.completed.order_status}.</p><button onClick={() => { setCheckout(null); setProducts([]); }}>Start another search</button></> : <><h3>{checkout.test_mode ? "Ready for dummy test payment" : "Ready for Razorpay Test Mode"}</h3><p>{checkout.order_number}</p><strong>₹{Number(checkout.amount).toLocaleString("en-IN")}</strong><p>{checkout.test_mode ? "This uses dummy test data. No money is charged." : "Use a Razorpay Test Mode payment method. The server verifies the signature."}</p><button onClick={pay}>{checkout.test_mode ? "Complete dummy test payment" : "Open Razorpay Checkout"}</button><button className="secondary" onClick={() => setCheckout(null)}>Back to shortlist</button></>}</div>}
      {status && <p className="ai-status">{status}</p>}
    </div>}
  </aside>;
}
