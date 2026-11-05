"use client";

import Image from "next/image";
import { useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

const photos = [
  { src: "/images/h4.jpeg", alt: "Strength equipment in a training studio", caption: "Find your strength" },
  { src: "/images/a2.jfif", alt: "Members supporting one another during training", caption: "Train with purpose" },
  { src: "/images/h5.jpeg", alt: "A small group training session", caption: "Build consistency" },
  { src: "/images/b3.jpeg", alt: "Movement and fitness outdoors", caption: "Make room to move" },
];

export function Gallery() {
  const sectionRef = useRef<HTMLElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const section = sectionRef.current;
    const track = trackRef.current;
    if (!section || !track || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return undefined;
    gsap.registerPlugin(ScrollTrigger);
    const media = gsap.matchMedia(section);
    media.add("(min-width: 900px)", () => {
      const distance = () => Math.max(0, track.scrollWidth - window.innerWidth + 80);
      gsap.to(track, {
        x: () => -distance(),
        ease: "none",
        scrollTrigger: { trigger: section, start: "top top", end: () => `+=${distance()}`, pin: true, scrub: 0.7, invalidateOnRefresh: true },
      });
    });
    return () => media.revert();
  }, { scope: sectionRef });

  return (
    <section className="gallery-section" ref={sectionRef}>
      <div className="gallery-section__heading shell">
        <p className="eyebrow">Good work, good people</p>
        <h2>Find your place<br />in the room.</h2>
        <span>REAL PEOPLE. ROOM TO GROW.</span>
      </div>
      <div className="gallery-track" ref={trackRef}>
        {photos.map((photo, index) => (
          <figure className="gallery-card" key={photo.src}>
            <div className="gallery-card__image"><Image src={photo.src} alt={photo.alt} fill sizes="(max-width: 899px) 85vw, 45vw" className="cover-image" /></div>
            <figcaption><span>0{index + 1}</span>{photo.caption}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
