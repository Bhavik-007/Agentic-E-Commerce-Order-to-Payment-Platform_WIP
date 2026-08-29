import { Link } from "react-router-dom";
import { AIShoppingAssistant } from "../components/AIShoppingAssistant";

export function Home() {
  return (
    <>
      <section className="hero">
        <p className="eyebrow">Commerce, thoughtfully assisted</p>
        <h1>Discover what fits<br /><i>your next move.</i></h1>
        <p className="hero-copy">ShopPilot AI turns a simple question into considered product choices, clear comparisons, and a seamless checkout.</p>
        <div className="hero-actions">
          <Link className="button" to="/products">Explore products</Link>
          <a className="link-button" href="#assistant">Ask ShopPilot AI <span>→</span></a>
        </div>
        <div className="hero-orb orb-one" /><div className="hero-orb orb-two" />
      </section>
      <section className="value-strip" aria-label="Service promises">
        <span>Curated selection</span><span>Secure payments</span><span>Helpful AI guidance</span><span>Simple returns</span>
      </section>
      <AIShoppingAssistant />
    </>
  );
}
