import type { Metadata } from "next";
import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/shared/Button";
import { PageHero } from "@/components/shared/PageHero";
import { ProgramCard } from "@/components/shared/ProgramCard";
import { Reveal } from "@/components/shared/Reveal";
import { SectionHeading } from "@/components/shared/SectionHeading";
import { programs } from "@/data/programs";

export const metadata: Metadata = {
  title: "Personal Training Programs",
  description: "Explore personal training, strength training, weight management, mobility, and nutrition guidance at Forge & Form in Portland.",
};

export default function ProgramsPage() {
  return (
    <>
      <PageHero eyebrow="Find your focus" title="Training with purpose." description="Explore coaching designed around your goals, experience, and everyday life. Start where you are; build from there." image="/images/h5.jpeg" imageAlt="A group fitness class in a welcoming studio" />
      <section className="content-section section-light">
        <div className="shell">
          <SectionHeading eyebrow="Five ways to get moving" title="Choose your starting point." />
          <div className="program-grid" style={{ marginTop: 42 }}>
            {programs.map((program, index) => <Reveal key={program.slug} delay={index * .05}><ProgramCard program={program} index={index} /></Reveal>)}
          </div>
        </div>
      </section>
      <section className="manifesto">
        <div className="shell manifesto__inner"><p className="eyebrow">Not sure where to start?</p><div><h2>We’ll figure out the right first step together.</h2><p className="manifesto__text">Book a free consultation and tell us what you’re looking for. No pressure—just a chance to talk through your goals and questions.</p><Button href="/book-consultation" variant="outline">Book a consultation <ArrowUpRight size={16} /></Button></div></div>
      </section>
    </>
  );
}
