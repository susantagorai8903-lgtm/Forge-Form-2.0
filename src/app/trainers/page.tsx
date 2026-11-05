import type { Metadata } from "next";
import { PageHero } from "@/components/shared/PageHero";
import { FinalCta } from "@/components/shared/FinalCta";
import { TrainerCard } from "@/components/shared/TrainerCard";
import { trainers } from "@/data/trainers";

export const metadata: Metadata = {
  title: "Meet the Trainers",
  description: "Meet the Forge & Form coaching team and explore personal training in Portland, Oregon.",
};

export default function TrainersPage() {
  return (
    <>
      <PageHero eyebrow="Your people, your pace" title="Meet your coaches." description="Thoughtful coaching starts with listening. Get to know our sample trainer profiles and connect with us about finding the right fit." image="/images/h6.jpeg" imageAlt="A trainer team gathering in the studio" />
      <section className="content-section section-light">
        <div className="shell">
          <div className="content-section__intro"><p className="eyebrow">Demo team profiles</p><h2 className="page-section-title">Meet the coaches.</h2><p>Trainer names, biographies, and specializations below are demo content. Real staff information and credentials will be confirmed by Forge & Form before publication.</p></div>
          <div className="trainer-grid">{trainers.map((trainer, index) => <TrainerCard trainer={trainer} index={index} key={trainer.name} />)}</div>
        </div>
      </section>
      <FinalCta />
    </>
  );
}
