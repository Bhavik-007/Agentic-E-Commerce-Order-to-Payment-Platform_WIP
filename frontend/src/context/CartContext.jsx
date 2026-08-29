import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { useAuth } from "./AuthContext";
import { addCartItem, getCart, removeCartItem } from "../services/cartService";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { token } = useAuth();
  const [cart, setCart] = useState({ items: [], subtotal: 0 });

  const refresh = useCallback(async () => { if (token) setCart(await getCart(token)); else setCart({ items: [], subtotal: 0 }); }, [token]);
  useEffect(() => { refresh().catch(() => setCart({ items: [], subtotal: 0 })); }, [refresh]);
  const value = useMemo(() => ({
    cart,
    itemCount: cart.items.reduce((total, item) => total + item.quantity, 0),
    async add(productId) { if (!token) throw new Error("Please sign in before adding items to your bag."); setCart(await addCartItem(token, productId)); },
    async remove(itemId) { await removeCartItem(token, itemId); await refresh(); },
  }), [cart, refresh, token]);
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) throw new Error("useCart must be used inside CartProvider.");
  return context;
}
