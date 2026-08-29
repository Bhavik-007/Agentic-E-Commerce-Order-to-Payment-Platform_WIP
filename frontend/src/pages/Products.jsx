import { useEffect, useState } from "react";

import { ProductCard } from "../components/ProductCard";
import { getProducts } from "../services/productService";
import { useCart } from "../context/CartContext";

export function Products() {
  const [products, setProducts] = useState([]);
  const [status, setStatus] = useState("loading");
  const [notice, setNotice] = useState("");
  const { add } = useCart();

  useEffect(() => {
    getProducts().then((items) => { setProducts(items); setStatus("ready"); }).catch(() => setStatus("error"));
  }, []);

  async function addToCart(productId) { try { await add(productId); setNotice("Added to your bag."); } catch (error) { setNotice(error.message); } }
  return <section className="catalog-page"><p className="eyebrow">Shop the collection</p><h1>Made for your everyday.</h1>{notice && <p className="notice">{notice}</p>}
    {status === "loading" && <p className="status">Loading the catalog…</p>}
    {status === "error" && <p className="status">The API is not available yet. Start the FastAPI server to load products.</p>}
    {status === "ready" && (products.length ? <div className="product-grid">{products.map((product) => <ProductCard key={product.id} product={product} onAdd={addToCart} />)}</div> : <p className="status">The catalog is ready for your first products.</p>)}
  </section>;
}
