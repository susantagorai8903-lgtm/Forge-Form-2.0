import Image from "next/image";
import { Button } from "@/components/shared/Button";

export function PageHero({
  eyebrow,
  title,
  description,
  image,
  imageAlt,
  action = true,
}: {
  eyebrow: string;
  title: string;
  description: string;
  image: string;
  imageAlt: string;
  action?: boolean;
}) {
  return (
    <section className="page-hero">
      <div className="page-hero__image">
        <Image src={image} alt={imageAlt} fill priority sizes="100vw" className="cover-image" />
      </div>
      <div className="page-hero__scrim" />
      <div className="page-hero__content shell">
        <p className="eyebrow eyebrow--lime">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="page-hero__description">{description}</p>
        {action && <Button href="/book-consultation" analyticsEvent="consultation_start">Book your free consultation <span aria-hidden="true">↗</span></Button>}
      </div>
      <span className="page-hero__index" aria-hidden="true">F / F — PORTLAND, OR</span>
    </section>
  );
}
