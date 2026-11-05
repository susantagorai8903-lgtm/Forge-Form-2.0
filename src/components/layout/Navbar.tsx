"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowDown, Menu, X } from "lucide-react";
import { Button } from "@/components/shared/Button";

const links = [
  { label: "About", href: "/about" },
  { label: "Programs", href: "/programs" },
  { label: "Trainers", href: "/trainers" },
  { label: "Stories", href: "/testimonials" },
  { label: "Journal", href: "/blog" },
  { label: "Contact", href: "/contact" },
];

export function Navbar() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [programsOpen, setProgramsOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setOpen(false);
    setProgramsOpen(false);
  }, [pathname]);

  useEffect(() => {
    document.body.classList.toggle("menu-open", open);
    return () => document.body.classList.remove("menu-open");
  }, [open]);

  return (
    <header className={`navbar${scrolled || open ? " navbar--solid" : ""}`}>
      <div className="navbar__inner shell">
        <Link href="/" className="brand" aria-label="Forge & Form home">
          <span className="brand__mark" aria-hidden="true">F<span>&</span>F</span>
          <span className="brand__name">FORGE <i>&</i> FORM</span>
        </Link>
        <nav className="navbar__links" aria-label="Main navigation">
          <Link className={pathname === "/" ? "is-active" : ""} href="/">Home</Link>
          {links.map((link) => link.label === "Programs" ? (
            <div className="nav-dropdown" key={link.href}>
              <button
                type="button"
                className={`nav-dropdown__trigger${pathname.startsWith("/programs") ? " is-active" : ""}`}
                aria-expanded={programsOpen}
                aria-controls="programs-menu"
                onClick={() => setProgramsOpen(!programsOpen)}
                onMouseEnter={() => setProgramsOpen(true)}
              >
                Programs <ArrowDown size={14} aria-hidden="true" />
              </button>
              {programsOpen && (
                <div className="nav-dropdown__menu" id="programs-menu" onMouseLeave={() => setProgramsOpen(false)}>
                  <Link href="/programs">All programs</Link>
                  <Link href="/programs/personal-training">Personal training</Link>
                  <Link href="/programs/strength-training">Strength training</Link>
                  <Link href="/programs/weight-loss">Weight management</Link>
                  <Link href="/programs/mobility">Mobility & flexibility</Link>
                  <Link href="/programs/nutrition-guidance">Nutrition guidance</Link>
                </div>
              )}
            </div>
          ) : <Link className={pathname.startsWith(link.href) ? "is-active" : ""} href={link.href} key={link.href}>{link.label}</Link>)}
        </nav>
        <Button className="navbar__cta" href="/book-consultation" analyticsEvent="consultation_start">Book a consultation <span aria-hidden="true">↗</span></Button>
        <button className="navbar__toggle" type="button" aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} onClick={() => setOpen(!open)}>
          {open ? <X size={23} /> : <Menu size={23} />}
        </button>
      </div>
      <div className={`mobile-menu${open ? " mobile-menu--open" : ""}`} aria-hidden={!open}>
        <nav aria-label="Mobile navigation">
          <Link href="/">Home <span>01</span></Link>
          {links.map((link, index) => <Link href={link.href} key={link.href}>{link.label}<span>0{index + 2}</span></Link>)}
          <Link href="/locations">Location <span>08</span></Link>
          <Link href="/book-consultation" className="mobile-menu__cta">Book a consultation <span>↗</span></Link>
        </nav>
      </div>
    </header>
  );
}
