import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { verifyRazorpayPayment, verifyTestPayment } from "../services/paymentService";

const money = (amount) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

export function Payment() {
  const { paymentId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const checkout = history.state?.usr?.checkout;
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { if (!checkout) navigate("/cart"); }, [checkout, navigate]);
  useEffect(() => { if (!checkout?.test_mode && !document.getElementById("razorpay-checkout")) { const script = document.createElement("script"); script.id = "razorpay-checkout"; script.src = "https://checkout.razorpay.com/v1/checkout.js"; document.body.appendChild(script); } }, [checkout]);
  if (!checkout) return null;
  async function pay() { try { setResult(await verifyTestPayment(token, paymentId)); } catch (requestError) { setError(requestError.response?.data?.detail ?? "Could not complete the test payment."); } }
  async function openRazorpay() {
    if (!window.Razorpay) { setError("Razorpay Checkout did not load. Check your internet connection and try again."); return; }
    const gateway = new window.Razorpay({ key: checkout.razorpay_key_id, amount: Math.round(Number(checkout.amount) * 100), currency: checkout.currency, name: "ShopPilot AI", description: `Order ${checkout.order_number}`, order_id: checkout.razorpay_order_id, handler: async (response) => { try { setResult(await verifyRazorpayPayment(token, paymentId, response)); } catch (requestError) { setError(requestError.response?.data?.detail ?? "Payment could not be verified."); } }, modal: { ondismiss: () => setError("Payment was cancelled. You can retry safely.") } });
    gateway.open();
  }
  return <section className="payment-page"><p className="eyebrow">{checkout.test_mode ? "Razorpay dummy test mode" : "Razorpay Test Mode"}</p><h1>Complete payment</h1>{!result ? <div className="payment-card"><p>Order <strong>{checkout.order_number}</strong></p><h2>{money(checkout.amount)}</h2><p className="payment-note">{checkout.test_mode ? "This is dummy test data. No money will be charged." : "Razorpay Test Mode is active. Use a Razorpay test payment method."}</p><button className="button" onClick={checkout.test_mode ? pay : openRazorpay}>{checkout.test_mode ? "Pay with dummy test card" : "Pay securely with Razorpay"}</button>{error && <p className="form-error">{error}</p>}</div> : <div className="payment-card payment-success"><h2>Payment verified</h2><p>Payment {result.payment_status} · Order {result.order_status}</p><Link className="button" to="/products">Continue shopping</Link></div>}</section>;
}
