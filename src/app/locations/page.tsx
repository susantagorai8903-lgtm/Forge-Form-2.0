import type { Metadata } from "next";
import Image from "next/image";
import { ExternalLink, MapPin } from "lucide-react";
import { Button } from "@/components/shared/Button";
import { PageHero } from "@/components/shared/PageHero";

export const metadata: Metadata = {
  title: "Our Portland Location",
  description: "Visit Forge & Form Personal Training at 1900 Division Street, Portland, OR 97202.",
};

const directions = "https://www.google.com/maps/search/?api=1&query=1900+Division+Street%2C+Portland%2C+OR+97202";

export default function LocationsPage() {
  return (
    <>
      <PageHero eyebrow="Your neighborhood training studio" title="Room to move." description="A welcoming place to build strength, practice movement, and make a little space for yourself." image="/images/h7.jpeg" imageAlt="Interior view of a fitness training studio" action={false} />
      <section className="content-section section-light">
        <div className="shell">
          <div className="content-section__intro"><p className="eyebrow">Find Forge & Form</p><h2 className="section-heading"><span>Come as you are.</span></h2><p>Find us in Portland’s Division Street neighborhood. Reach out before your first visit and we’ll help you plan a good place to begin.</p></div>
          <div className="location-grid">
            <div className="location-image"><Image src="/images/h8.jpeg" alt="Training floor and equipment inside the studio" fill sizes="(max-width: 800px) 90vw, 50vw" className="cover-image" /></div>
            <div className="location-details">
              <p className="eyebrow eyebrow--lime">Forge & Form Personal Training</p>
              <h2>Portland, Oregon</h2>
              <p>A personal training studio focused on strength, movement, and sustainable wellness.</p>
              <address>1900 Division Street<br />Portland, OR 97202, USA</address>
              <a href="tel:+15035550139">(503) 555-0139</a>
              <a href="mailto:training@forgeandform.com">training@forgeandform.com</a>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 25 }}>
                <Button href="/book-consultation" variant="light">Book a consultation</Button>
                <a className="button button--outline" href={directions} target="_blank" rel="noreferrer">Get directions <ExternalLink size={15} /></a>
              </div>
            </div>
            <div className="map-placeholder">
              <div className="map-placeholder__card"><MapPin size={24} /><p>1900 Division Street<br />Portland, OR 97202</p><a href={directions} target="_blank" rel="noreferrer">Open directions in Google Maps</a></div>
            </div>
            <div className="location-details">
              <p className="eyebrow eyebrow--lime">A note before you visit</p>
              <h2>Made for your next step.</h2>
              <p>Studio hours and session availability have not been published yet. Contact us to discuss a visit or choose a consultation time request online.</p>
              <p>Demo availability shown during booking is illustrative only and is not confirmed until the studio responds.</p>
              <Button href="/contact" variant="light">Ask us a question</Button>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
