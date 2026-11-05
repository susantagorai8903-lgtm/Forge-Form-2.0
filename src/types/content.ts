export type Program = {
  slug: string;
  title: string;
  eyebrow: string;
  summary: string;
  description: string;
  image: string;
  alt: string;
  benefits: string[];
  suitableFor: string;
};

export type Trainer = {
  slug: string;
  name: string;
  title: string;
  image: string;
  alt: string;
  bio: string;
  specialties: string[];
  experience: string;
};

export type Article = {
  slug: string;
  title: string;
  category: string;
  excerpt: string;
  content: string[];
  image: string;
  alt: string;
  author: string;
  date: string;
  readingTime: string;
};

export type Testimonial = {
  name: string;
  quote: string;
  image: string;
};
