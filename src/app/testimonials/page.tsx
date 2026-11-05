import type { Metadata } from "next";
import Image from "next/image";
import { PageHero } from "@/components/shared/PageHero";
import { FinalCta } from "@/components/shared/FinalCta";
import { testimonials } from "@/data/testimonials";

export const metadata: Metadata = {
  title: "Client Stories",
  description: "Explore sample client story layouts from Forge & Form. All current stories are clearly marked as demo content.",
};

export default function TestimonialsPage() {
  return (
    <>
      <PageHero eyebrow="Stories in progress" title="Every journey is personal." description="Training is personal—and progress looks different for everyone. These sample layouts show how future client stories could appear." image="/images/t4.jpeg" imageAlt="Group fitness training in a community setting" />
      <section className="content-section section-light">
        <div className="shell">
          <div className="content-section__intro"><p className="eyebrow">Demo content—not verified reviews</p><h2 className="page-section-title">Stories of progress.</h2><p>These are placeholders for future member stories. They are not verified reviews, endorsements, or claims of specific results.</p></div>
          <div className="story-page-grid">{testimonials.map((story, index) => (
            <article className="story-page-card" key={story.name}>
              <div className="story-page-card__image"><Image src={story.image} alt="Placeholder photography for a future client story" fill sizes="(max-width: 700px) 90vw, 45vw" className="cover-image" /></div>
              <div className="story-page-card__content"><p className="eyebrow eyebrow--lime">DEMO STORY / 0{index + 1}</p><blockquote>“{story.quote}”</blockquote><span>{story.name} · Sample content</span></div>
            </article>
          ))}</div>
        </div>
      </section>
      <FinalCta />
    </>
  );
}
