import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowUpRight, Check } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/shared/Button";
import { trainers } from "@/data/trainers";

export function generateStaticParams() {
  return trainers.map((trainer) => ({ slug: trainer.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const trainer = trainers.find((item) => item.slug === slug);
  return trainer ? { title: trainer.name, description: `${trainer.title} at Forge & Form Personal Training in Portland.` } : {};
}

export default async function TrainerProfilePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const trainer = trainers.find((item) => item.slug === slug);
  if (!trainer) notFound();

  return (
    <>
      <section className="content-section section-light">
        <div className="shell">
          <Link className="text-link" href="/trainers"><ArrowLeft size={14} /> Back to the coaches</Link>
          <div className="trainer-profile">
            <div className="trainer-profile__image"><Image src={trainer.image} alt={trainer.alt} fill priority sizes="(max-width: 800px) 90vw, 45vw" className="cover-image" /></div>
            <div className="trainer-profile__body">
              <p className="eyebrow">Demo trainer profile</p>
              <h1 className="page-section-title">{trainer.name}</h1>
              <p className="trainer-profile__title">{trainer.title}</p>
              <p>{trainer.bio}</p>
              <p className="trainer-profile__experience">{trainer.experience}</p>
              <h2>Coaching focus</h2>
              <ul className="benefit-list">{trainer.specialties.map((specialty) => <li key={specialty}><Check size={15} />{specialty}</li>)}</ul>
              <p className="field__hint">This profile uses demo information. Credentials and staff details have not been supplied and must be confirmed before launch.</p>
              <Button href="/book-consultation">Talk with a coach <ArrowUpRight size={16} /></Button>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
