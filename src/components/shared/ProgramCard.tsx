import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import type { Program } from "@/types/content";

export function ProgramCard({ program, index = 0 }: { program: Program; index?: number }) {
  return (
    <article className="program-card">
      <Link href={`/programs/${program.slug}`} className="program-card__link" data-analytics-event="program_select" aria-label={`Explore ${program.title}`}>
        <div className="program-card__image">
          <Image src={program.image} alt={program.alt} fill sizes="(max-width: 700px) 90vw, (max-width: 1100px) 45vw, 30vw" className="cover-image" />
          <span className="program-card__number">0{index + 1}</span>
          <span className="program-card__arrow" aria-hidden="true"><ArrowUpRight size={19} /></span>
        </div>
        <div className="program-card__body">
          <span className="eyebrow">{program.eyebrow}</span>
          <h3>{program.title}</h3>
          <p>{program.summary}</p>
        </div>
      </Link>
    </article>
  );
}
