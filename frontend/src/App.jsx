import { Route, Routes } from "react-router-dom";

import { Navbar } from "./components/Navbar";
import { Home } from "./pages/Home";
import { Products } from "./pages/Products";
import { Auth } from "./pages/Auth";
import { Cart } from "./pages/Cart";
import { Payment } from "./pages/Payment";
import { UniversalAssistant } from "./components/UniversalAssistant";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/login" element={<Auth />} />
          <Route path="/register" element={<Auth />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/payment/:paymentId" element={<Payment />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </main>
      <UniversalAssistant />
    </div>
  );
}
