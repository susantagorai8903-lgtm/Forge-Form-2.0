import Link from "next/link";
import { ArrowUpRight, Instagram, MoveUpRight } from "lucide-react";

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer__top shell">
        <div className="footer__brand">
          <Link href="/" className="brand brand--footer" aria-label="Forge & Form home">
            <span className="brand__mark" aria-hidden="true">F<span>&</span>F</span>
            <span className="brand__name">FORGE <i>&</i> FORM</span>
          </Link>
          <p>Personal training for real life. Build strength, find your rhythm, and move forward with a plan made for you.</p>
          <a className="footer__social" href="https://www.instagram.com/" target="_blank" rel="noreferrer" aria-label="Instagram (opens in a new tab)"><Instagram size={17} /> Instagram <ArrowUpRight size={14} /></a>
        </div>
        <div className="footer__column">
          <h2>Explore</h2>
          <Link href="/about">Our approach</Link><Link href="/programs">Programs</Link><Link href="/trainers">Our coaches</Link><Link href="/testimonials">Client stories</Link><Link href="/blog">The journal</Link>
        </div>
        <div className="footer__column">
          <h2>Get in touch</h2>
          <a href="tel:+15035550139">(503) 555-0139</a>
          <a href="mailto:training@forgeandform.com">training@forgeandform.com</a>
          <p>1900 Division Street<br />Portland, OR 97202</p>
          <Link href="/locations">Find the studio <MoveUpRight size={13} /></Link>
        </div>
        <div className="footer__newsletter">
          <span className="eyebrow eyebrow--lime">A note from the studio</span>
          <h2>Make room<br />for more.</h2>
          <p id="newsletter-note">Training notes and studio updates, coming soon.</p>
          <label className="newsletter-form__label" htmlFor="newsletter-email">Email updates</label>
          <div className="newsletter-form">
            <input id="newsletter-email" type="email" placeholder="Email address" aria-describedby="newsletter-note" disabled />
            <button type="button" disabled aria-label="Newsletter sign-up coming soon">Coming soon</button>
          </div>
          <Link href="/contact" className="text-link">Get in touch <ArrowUpRight size={15} /></Link>
        </div>
      </div>
      <div className="footer__bottom shell">
        <span>© {new Date().getFullYear()} Forge & Form Personal Training</span>
        <span>Made for movement in Portland, Oregon</span>
        <div><Link href="/privacy-policy">Privacy</Link><Link href="/terms">Terms</Link></div>
      </div>
    </footer>
  );
}
