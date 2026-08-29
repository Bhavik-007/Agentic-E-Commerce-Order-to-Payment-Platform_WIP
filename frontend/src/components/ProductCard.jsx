const formatPrice = (amount, currency = "INR") =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency, maximumFractionDigits: 0 }).format(amount);

export function ProductCard({ product, onAdd }) {
  return (
    <article className="product-card">
      <div className="product-image" aria-hidden="true">{product.name.slice(0, 1)}</div>
      <div className="product-meta"><span>{product.category?.name ?? "ShopPilot pick"}</span><span>★ {product.rating ?? "New"}</span></div>
      <h3>{product.name}</h3>
      <p>{product.brand ?? "ShopPilot"}</p>
      <strong>{formatPrice(product.final_price ?? product.price, product.currency)}</strong>
      <button className="text-button" onClick={() => onAdd?.(product.id)}>Add to bag +</button>
    </article>
  );
}
