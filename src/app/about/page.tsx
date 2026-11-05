import type { Metadata } from "next";
import Image from "next/image";
import { ArrowUpRight } from "lucide-react";
import { PageHero } from "@/components/shared/PageHero";
import { SectionHeading } from "@/components/shared/SectionHeading";
import { FinalCta } from "@/components/shared/FinalCta";
import { TrainerCard } from "@/components/shared/TrainerCard";
import { Reveal } from "@/components/shared/Reveal";
import { trainers } from "@/data/trainers";
import { Button } from "@/components/shared/Button";

export const metadata: Metadata = {
  title: "About",
  description: "Get to know the Forge & Form approach to personal training, strength, movement, and everyday wellness in Portland.",
};

export default function AboutPage() {
  return (
    <>
      <PageHero eyebrow="A stronger way forward" title="Built around you." description="A Portland training studio for people who want a little more confidence, consistency, and room to grow." image="/images/h6.jpeg" imageAlt="A team of trainers and members together" />
      <section className="content-section section-light">
        <div className="shell split-story">
          <Reveal className="split-story__image"><Image src="/images/a2.jfif" alt="Members encouraging one another during a workout" fill sizes="(max-width: 800px) 90vw, 45vw" className="cover-image" /></Reveal>
          <Reveal className="split-story__copy" delay={0.1}>
            <p className="eyebrow">Our story</p>
            <h2>Strength is a starting point.</h2>
            <p>Forge & Form is built around a simple idea: training should help you feel more capable in your everyday life. It can start with one goal, one session, or simply a conversation about what you need.</p>
            <p>Here, coaching is personal, movement is purposeful, and progress is measured by more than a number. This demo site introduces the brand and its services; studio history and team details are placeholders until confirmed.</p>
            <Button href="/book-consultation" variant="outline">Start a conversation <ArrowUpRight size={16} /></Button>
          </Reveal>
        </div>
      </section>
      <section className="manifesto">
        <div className="shell manifesto__inner">
          <p className="eyebrow">Our philosophy</p>
          <div><h2>Strength is more than lifting heavier. It’s confidence, consistency, mobility, and long-term wellness.</h2><p className="manifesto__text">We make space for the whole picture: where you’re beginning, what you’re working toward, and how training can support the life you want to lead.</p></div>
        </div>
      </section>
      <section className="content-section section-paper">
        <div className="shell">
          <SectionHeading eyebrow="What we’re here to do" title="A mission rooted in everyday progress." />
          <div className="card-list" style={{ marginTop: 42 }}>
            <article className="info-card"><span>OUR MISSION</span><h3>Make coaching personal.</h3><p>Offer thoughtful training and a welcoming environment where people can build strength and confidence at their own pace.</p></article>
            <article className="info-card"><span>OUR VISION</span><h3>Wellness that lasts.</h3><p>Help more people find sustainable movement and habits that support them beyond the studio.</p></article>
            <article className="info-card"><span>OUR PROMISE</span><h3>Keep listening.</h3><p>Stay curious about each person’s goals and adapt the work as life and priorities change.</p></article>
          </div>
        </div>
      </section>
      <section className="content-section section-light">
        <div className="shell">
          <SectionHeading eyebrow="How we coach" title="Simple, considered, personal." />
          <div className="card-list" style={{ marginTop: 42 }}>
            {[
              ["01", "Listen first", "We learn what matters to you before a plan takes shape."],
              ["02", "Build with intention", "Your training fits your experience, priorities, and real-world schedule."],
              ["03", "Adjust as you grow", "We check in, recognize progress, and make changes when you need them."],
            ].map(([n, title, copy]) => <article className="info-card" key={n}><span>{n}</span><h3>{title}</h3><p>{copy}</p></article>)}
          </div>
        </div>
      </section>
      <section className="content-section section-paper">
        <div className="shell">
          <div className="section-topline"><SectionHeading eyebrow="Demo profiles" title="Meet the coaches." /><p className="demo-note" style={{ margin: 0 }}>Sample profiles only; staff details and credentials to be confirmed.</p></div>
          <div className="trainer-grid">{trainers.map((trainer, index) => <TrainerCard trainer={trainer} index={index} key={trainer.name} />)}</div>
        </div>
      </section>
      <FinalCta />
    </>
  );
}
