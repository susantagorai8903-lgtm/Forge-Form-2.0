import type { Program } from "@/types/content";

export const programs: Program[] = [
  {
    slug: "personal-training",
    title: "Personal Training",
    eyebrow: "One-on-one coaching",
    summary: "A plan built around your life, your goals, and the way you want to feel.",
    description:
      "Work alongside a coach to build a thoughtful training routine around your starting point, schedule, and goals. Every session is personal, purposeful, and designed to help you keep showing up.",
    image: "/images/personal%20tranning.jpg",
    alt: "Coach guiding a client through a personal training session",
    benefits: ["One-to-one coaching", "Personal fitness assessment", "Customized workout plan", "Progress check-ins"],
    suitableFor: "Anyone who values individual attention, whether you are new to training or ready for a fresh challenge.",
  },
  {
    slug: "strength-training",
    title: "Strength Training",
    eyebrow: "Build a stronger foundation",
    summary: "Learn the lifts, build confidence, and get stronger at a pace that feels right.",
    description:
      "Develop strength with coached resistance training, functional movements, and a steady approach to progression. We focus on great technique and repeatable habits—not quick fixes.",
    image: "/images/b1.jpeg",
    alt: "Strength training equipment ready for a coached workout",
    benefits: ["Progressive strength work", "Resistance training", "Functional movement practice", "Technique coaching"],
    suitableFor: "Beginners learning the basics, as well as experienced lifters looking for more structure and coaching.",
  },
  {
    slug: "weight-loss",
    title: "Weight Loss Coaching",
    eyebrow: "Sustainable by design",
    summary: "Build consistent movement and everyday habits without all-or-nothing thinking.",
    description:
      "Create a supportive training routine focused on consistency, strength, and sustainable wellness habits. Nutrition guidance is educational and can complement—not replace—professional care.",
    image: "/images/h3.jpeg",
    alt: "Personal trainer coaching a client during a workout",
    benefits: ["Goal-oriented training plan", "Activity and habit tracking", "Regular coaching check-ins", "General nutrition education"],
    suitableFor: "People who want a supportive, practical approach to movement and long-term lifestyle change.",
  },
  {
    slug: "mobility",
    title: "Mobility & Flexibility",
    eyebrow: "Move with more ease",
    summary: "Make room for better movement, thoughtful recovery, and a wider range of motion.",
    description:
      "Sessions blend mobility drills, flexibility routines, and controlled movement to help you move with intention. Your coach will adapt the work to your comfort and experience.",
    image: "/images/h9.jpeg",
    alt: "A guided flexibility and mobility session",
    benefits: ["Mobility-focused sessions", "Flexibility routines", "Movement quality practice", "Recovery-minded coaching"],
    suitableFor: "Anyone who wants to give mobility and movement quality a more consistent place in their routine.",
  },
  {
    slug: "nutrition-guidance",
    title: "Nutrition Guidance",
    eyebrow: "Everyday wellness",
    summary: "Practical, general education to help make food choices feel more approachable.",
    description:
      "Get general nutrition education and lifestyle guidance that supports your training goals. We keep it practical, non-prescriptive, and grounded in sustainable everyday habits.",
    image: "/images/nutrition%20guidance.jpg",
    alt: "Fresh ingredients prepared for a balanced meal",
    benefits: ["General nutrition education", "Goal-oriented lifestyle support", "Habit-building ideas", "Coaching alongside your training"],
    suitableFor: "People looking for practical context and supportive habits to complement an active lifestyle.",
  },
];
