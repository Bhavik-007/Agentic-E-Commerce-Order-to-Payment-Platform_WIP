import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { startCheckout } from "../services/paymentService";

const money = (amount) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

export function Cart() {
  const { cart, remove } = useCart();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  async function checkout() { try { const data = await startCheckout(token); navigate(`/payment/${data.payment_id}`, { state: { checkout: data } }); } catch (requestError) { setError(requestError.response?.data?.detail ?? "Could not start checkout."); } }
  return <section className="cart-page"><p className="eyebrow">Your selection</p><h1>Your bag</h1>
    {!cart.items.length ? <p className="status">Your bag is waiting. <Link to="/products">Explore products</Link>.</p> : <><div className="cart-list">{cart.items.map((item) => <article className="cart-row" key={item.id}><div><h3>{item.product_name}</h3><p>Quantity {item.quantity}</p></div><strong>{money(item.line_total)}</strong><button className="text-button" onClick={() => remove(item.id)}>Remove</button></article>)}</div><aside className="cart-total"><span>Subtotal</span><strong>{money(cart.subtotal)}</strong><button className="button" onClick={checkout}>Proceed to test payment</button>{error && <p className="form-error">{error}</p>}</aside></>}
  </section>;
}
