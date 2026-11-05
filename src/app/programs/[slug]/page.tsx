import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { Check } from "lucide-react";
import { Button } from "@/components/shared/Button";
import { FinalCta } from "@/components/shared/FinalCta";
import { PageHero } from "@/components/shared/PageHero";
import { programs } from "@/data/programs";

export function generateStaticParams() {
  return programs.map((program) => ({ slug: program.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const program = programs.find((item) => item.slug === slug);
  return program ? { title: program.title, description: program.summary } : {};
}

export default async function ProgramDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const program = programs.find((item) => item.slug === slug);
  if (!program) notFound();

  return (
    <>
      <PageHero eyebrow={program.eyebrow} title={program.title} description={program.summary} image={program.image} imageAlt={program.alt} />
      <section className="content-section section-light">
        <div className="shell program-detail__split">
          <div className="program-detail__image"><Image src={program.image} alt={program.alt} fill sizes="(max-width: 800px) 90vw, 52vw" className="cover-image" /></div>
          <div className="program-detail__body">
            <p className="eyebrow">A personal way to move forward</p>
            <h2>Make it work<br />for your life.</h2>
            <p>{program.description}</p>
            <ul className="benefit-list">{program.benefits.map((benefit) => <li key={benefit}><Check size={15} aria-hidden="true" />{benefit}</li>)}</ul>
            <p className="program-detail__suitable"><strong>Who it’s for:</strong> {program.suitableFor}</p>
            <Button href="/book-consultation">Talk with a coach <span aria-hidden="true">↗</span></Button>
          </div>
        </div>
      </section>
      <FinalCta />
    </>
  );
}
