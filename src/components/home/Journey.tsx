"use client";

import Image from "next/image";
import { useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

const steps = [
  {
    number: "01",
    title: "Fitness assessment",
    copy: "We begin with a real conversation about your goals, current routine, and what you want from training.",
    image: "/images/fitness%20assesment.jpg",
    alt: "Coach discussing fitness goals with a client",
  },
  {
    number: "02",
    title: "Personalized training",
    copy: "Your coach shapes a plan around your needs, then helps you practice it with thoughtful, hands-on guidance.",
    image: "/images/h2.jpeg",
    alt: "Personal trainer guiding a client through an exercise",
  },
  {
    number: "03",
    title: "Progress & perspective",
    copy: "We keep track of the work, make adjustments as life changes, and recognize the progress that matters to you.",
    image: "/images/a1.jfif",
    alt: "A group of training members moving together",
  },
];

export function Journey() {
  const sectionRef = useRef<HTMLElement>(null);
  const [active, setActive] = useState(0);

  useGSAP(() => {
    const section = sectionRef.current;
    if (!section) return undefined;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    gsap.registerPlugin(ScrollTrigger);
    const media = gsap.matchMedia();
    media.add("(min-width: 900px)", () => {
      gsap.to(section, {
        scrollTrigger: {
          trigger: section,
          start: "top top",
          end: "+=1650",
          ...(reduceMotion ? {} : { pin: true, scrub: 0.5 }),
          onUpdate: (self) => setActive(Math.min(2, Math.floor(self.progress * 3))),
        },
      });
    });
    media.add("(max-width: 899px)", () => {
      const stepElements = Array.from(section.querySelectorAll<HTMLElement>(".journey__step"));
      stepElements.forEach((stepElement, index) => {
        ScrollTrigger.create({
          trigger: stepElement,
          start: "top 68%",
          end: "bottom 40%",
          onEnter: () => setActive(index),
          onEnterBack: () => setActive(index),
        });
      });
    });
    return () => media.revert();
  }, { scope: sectionRef });

  return (
    <section className="journey section-dark" ref={sectionRef}>
      <div className="journey__inner shell">
        <div className="journey__intro">
          <p className="eyebrow eyebrow--lime">A clear path, made personal</p>
          <h2>Progress is a practice.</h2>
          <p>Every strong start looks a little different. Here’s how we make space for yours.</p>
          <div className="journey__steps">
            {steps.map((step, index) => (
              <article className={`journey__step${active === index ? " is-active" : ""}`} key={step.number}>
                <span>{step.number}</span>
                <div><h3>{step.title}</h3><p>{step.copy}</p></div>
              </article>
            ))}
          </div>
        </div>
        <div className="journey__visual">
          {steps.map((step, index) => (
            <div className={`journey__image${active === index ? " is-active" : ""}`} key={step.number} aria-hidden={active !== index}>
              <Image src={step.image} alt={step.alt} fill sizes="(max-width: 899px) 90vw, 45vw" className="cover-image" />
              <span className="journey__caption">{step.number} / 03</span>
            </div>
          ))}
          <div className="journey__visual-note"><span>THE FORGE & FORM METHOD</span><span>PORTLAND, OR</span></div>
        </div>
      </div>
    </section>
  );
}
