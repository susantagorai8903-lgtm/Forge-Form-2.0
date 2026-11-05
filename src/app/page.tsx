import Image from "next/image";
import Link from "next/link";
import { ArrowDown, ArrowUpRight, MapPin, MoveRight } from "lucide-react";
import { programs } from "@/data/programs";
import { trainers } from "@/data/trainers";
import { testimonials } from "@/data/testimonials";
import { Button } from "@/components/shared/Button";
import { FinalCta } from "@/components/shared/FinalCta";
import { ProgramCard } from "@/components/shared/ProgramCard";
import { SectionHeading } from "@/components/shared/SectionHeading";
import { TrainerCard } from "@/components/shared/TrainerCard";
import { Reveal } from "@/components/shared/Reveal";
import { Journey } from "@/components/home/Journey";
import { Gallery } from "@/components/home/Gallery";

export default function HomePage() {
  return (
    <>
      <section className="home-hero">
        <Image src="/images/a3.jfif" alt="The Forge & Form community training together" fill priority sizes="100vw" className="cover-image home-hero__photo" />
        <div className="home-hero__scrim" />
        <div className="home-hero__content shell">
          <p className="eyebrow eyebrow--lime"><span className="status-dot" /> Personal training · Portland, Oregon</p>
          <h1>Build strength.<br /><span>Shape your future.</span></h1>
          <p className="home-hero__copy">Personalized training. Expert coaching. Sustainable results. Discover a stronger, healthier version of yourself with Forge & Form.</p>
          <div className="home-hero__actions">
            <Button href="/book-consultation">Start your journey <ArrowUpRight size={17} /></Button>
            <Link href="/programs" className="button button--ghost">Explore programs <MoveRight size={17} /></Link>
          </div>
          <div className="home-hero__foot">
            <span>01 — YOUR NEXT CHAPTER</span>
            <span>SCROLL TO EXPLORE <ArrowDown size={14} /></span>
          </div>
        </div>
        <span className="home-hero__type" aria-hidden="true">F / F</span>
      </section>

      <section className="intro-section section-light">
        <div className="shell intro-section__grid">
          <Reveal className="intro-section__visual">
            <div className="intro-section__image">
              <Image src="/images/b2.jpeg" alt="A calm, intentional movement practice" fill sizes="(max-width: 800px) 90vw, 42vw" className="cover-image" />
            </div>
            <span className="image-label">01 / MOVEMENT WITH INTENTION</span>
          </Reveal>
          <Reveal className="intro-section__text" delay={0.12}>
            <p className="eyebrow">Stronger by design</p>
            <h2>Training that<br />meets you <em>where you are.</em></h2>
            <p>Getting stronger isn’t a one-size-fits-all pursuit. We bring thoughtful coaching, purposeful movement, and a welcoming space together to help you build a practice that feels like yours.</p>
            <p>Start with a conversation. We’ll take it one step at a time.</p>
            <Link className="text-link" href="/about">Get to know our approach <MoveRight size={16} /></Link>
          </Reveal>
        </div>
      </section>

      <Journey />

      <section className="programs-section section-light">
        <div className="shell">
          <div className="section-topline">
            <SectionHeading eyebrow="Find your focus" title="Training with purpose." />
            <Link className="text-link" href="/programs">Explore all programs <MoveRight size={16} /></Link>
          </div>
          <div className="program-grid">
            {programs.map((program, index) => <Reveal key={program.slug} delay={index * 0.06}><ProgramCard program={program} index={index} /></Reveal>)}
          </div>
        </div>
      </section>

      <section className="values-section section-paper">
        <div className="shell values-section__grid">
          <div className="values-section__heading">
            <SectionHeading eyebrow="The Forge & Form difference" title="More than a workout. A better way forward." />
            <p>We believe the best training is the training that works for you—today, next week, and for the long run.</p>
            <Button href="/about" variant="outline">Our approach <ArrowUpRight size={16} /></Button>
          </div>
          <div className="values-list">
            {[
              ["01", "Coaching that listens", "Your starting point, goals, and schedule shape the plan."],
              ["02", "Progress with purpose", "Clear, meaningful milestones help you see the work adding up."],
              ["03", "A place to belong", "Encouragement and accountability without the pressure to be perfect."],
              ["04", "Wellness for real life", "Sustainable movement and habits that make room for the rest of you."],
            ].map(([number, title, copy]) => <article className="value-row" key={number}><span>{number}</span><div><h3>{title}</h3><p>{copy}</p></div><ArrowUpRight size={17} aria-hidden="true" /></article>)}
          </div>
        </div>
      </section>

      <Gallery />

      <section className="trainers-section section-light">
        <div className="shell">
          <div className="section-topline">
            <SectionHeading eyebrow="Good people, thoughtful coaching" title="Meet your coaches." />
            <Link className="text-link" href="/trainers">Meet the team <MoveRight size={16} /></Link>
          </div>
          <p className="demo-note">Sample profiles for design preview. Staff details and credentials will be confirmed before launch.</p>
          <div className="trainer-grid">{trainers.map((trainer, index) => <Reveal key={trainer.name} delay={index * 0.08}><TrainerCard trainer={trainer} index={index} /></Reveal>)}</div>
        </div>
      </section>

      <section className="stories-section section-dark">
        <div className="shell">
          <div className="section-topline section-topline--light">
            <SectionHeading eyebrow="Stories in progress" title="Every journey is personal." light />
            <Link className="text-link text-link--light" href="/testimonials">Explore client stories <MoveRight size={16} /></Link>
          </div>
          <p className="demo-note demo-note--light">The cards below are sample layouts, not verified customer reviews.</p>
          <div className="story-grid">{testimonials.slice(0, 3).map((story, index) => (
            <article className="story-card" key={story.name}>
              <div className="story-card__image"><Image src={story.image} alt="Placeholder image for a demo client story" fill sizes="(max-width: 700px) 90vw, 30vw" className="cover-image" /></div>
              <div className="story-card__body"><span className="eyebrow eyebrow--lime">DEMO STORY / 0{index + 1}</span><blockquote>“{story.quote}”</blockquote><span className="story-card__name">{story.name}</span></div>
            </article>
          ))}</div>
        </div>
      </section>

      <FinalCta />

      <section className="contact-strip section-light">
        <div className="shell contact-strip__inner">
          <div><p className="eyebrow">Come say hello</p><h2>A good place to begin<br />is a conversation.</h2></div>
          <div className="contact-strip__details">
            <p><MapPin size={17} /><span>1900 Division Street<br />Portland, OR 97202</span></p>
            <a href="tel:+15035550139">(503) 555-0139 <ArrowUpRight size={14} /></a>
            <a href="mailto:training@forgeandform.com">training@forgeandform.com <ArrowUpRight size={14} /></a>
            <Link href="/locations" className="text-link">Get directions <MoveRight size={16} /></Link>
          </div>
        </div>
      </section>
    </>
  );
}
