import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/shared/Button";

export function FinalCta() {
  return (
    <section className="final-cta">
      <div className="final-cta__inner shell">
        <div>
          <p className="eyebrow eyebrow--lime">A good place to begin</p>
          <h2>Your next chapter<br />starts here.</h2>
        </div>
        <div className="final-cta__action">
          <p>Take the first step toward a stronger, healthier you. We’ll start with a conversation.</p>
          <Button href="/book-consultation" variant="light" analyticsEvent="consultation_start">Book your free consultation <ArrowUpRight size={17} /></Button>
        </div>
        <span className="final-cta__ornament" aria-hidden="true">F&F</span>
      </div>
    </section>
  );
}
