import type { Metadata } from "next";
import { PageHero } from "@/components/shared/PageHero";
import { BookingWizard } from "@/components/booking/BookingWizard";

export const metadata: Metadata = {
  title: "Book a Free Consultation",
  description: "Request a free Forge & Form consultation in Portland. Choose a program and preferred time for the studio to confirm.",
};

export default function BookingPage() {
  return (
    <>
      <PageHero eyebrow="Start with a conversation" title="Your first step." description="Tell us what you’re looking for and request a time to connect. We’ll follow up to confirm the details." image="/images/fitness%20assesment.jpg" imageAlt="A coach reviewing a fitness assessment with a client" action={false} />
      <section className="content-section section-light">
        <div className="shell">
          <BookingWizard />
        </div>
      </section>
    </>
  );
}
