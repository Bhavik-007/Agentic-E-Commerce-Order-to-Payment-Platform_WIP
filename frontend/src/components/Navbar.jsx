import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export function Navbar() {
  const { authenticated, signOut, user } = useAuth();
  const { itemCount } = useCart();
  return (
    <header className="site-header">
      <NavLink className="brand" to="/" aria-label="ShopPilot AI home">
        <span className="brand-mark">S</span>
        <span>ShopPilot <em>AI</em></span>
      </NavLink>
      <nav aria-label="Main navigation">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/products">Products</NavLink>
        <a href="#assistant">AI Assistant</a>
      </nav>
      <div className="nav-actions">
        <NavLink className="icon-button" to="/cart" aria-label="View cart">Bag <span>{itemCount}</span></NavLink>
        {authenticated ? <button className="button button-small" onClick={signOut}>Hi, {user.first_name}</button> : <NavLink className="button button-small" to="/login">Sign in</NavLink>}
      </div>
    </header>
  );
}
