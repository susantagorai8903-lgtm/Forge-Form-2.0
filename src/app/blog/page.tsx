import type { Metadata } from "next";
import { PageHero } from "@/components/shared/PageHero";
import { BlogBrowser } from "@/components/blog/BlogBrowser";
import { articles } from "@/data/articles";

export const metadata: Metadata = {
  title: "The Journal",
  description: "Explore practical notes on strength training, nutrition, mobility, and personal wellness from Forge & Form.",
};

export default function BlogPage() {
  return (
    <>
      <PageHero eyebrow="Notes for a life in motion" title="The journal." description="Ideas and practical starting points for strength, mobility, nutrition, and a more considered approach to wellness." image="/images/h10.jpeg" imageAlt="Group fitness training with people moving together" action={false} />
      <section className="content-section section-light">
        <div className="shell">
          <div className="content-section__intro"><p className="eyebrow">Demo articles</p><h2 className="page-section-title">A little more perspective.</h2><p>Sample editorial content for the Forge & Form journal. Articles are informational and not medical advice.</p></div>
          <BlogBrowser articles={articles} />
        </div>
      </section>
    </>
  );
}
