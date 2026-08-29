import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function Auth() {
  const isRegister = useLocation().pathname === "/register";
  const navigate = useNavigate();
  const { signIn, register } = useAuth();
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault(); setError("");
    const data = Object.fromEntries(new FormData(event.currentTarget));
    try { if (isRegister) await register(data); else await signIn(data); navigate("/products"); }
    catch (requestError) { setError(requestError.response?.data?.detail ?? "Please try again."); }
  }

  return <section className="auth-page"><form className="auth-form" onSubmit={submit}><p className="eyebrow">Your ShopPilot account</p><h1>{isRegister ? "Create account" : "Welcome back"}</h1>
    {isRegister && <div className="form-row"><label>First name<input required name="first_name" /></label><label>Last name<input required name="last_name" /></label></div>}
    <label>Email<input required type="email" name="email" /></label><label>Password<input required type="password" minLength="8" name="password" /></label>
    {error && <p className="form-error">{error}</p>}<button className="button">{isRegister ? "Create account" : "Sign in"}</button>
    <p>{isRegister ? <>Already have an account? <Link to="/login">Sign in</Link></> : <>New to ShopPilot? <Link to="/register">Create an account</Link></>}</p>
  </form></section>;
}
