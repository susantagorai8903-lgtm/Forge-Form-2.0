import type { MetadataRoute } from "next";
import { articles } from "@/data/articles";
import { trainers } from "@/data/trainers";

const routes = [
  "", "/about", "/programs", "/programs/personal-training", "/programs/strength-training",
  "/programs/weight-loss", "/programs/mobility", "/programs/nutrition-guidance", "/trainers",
  "/testimonials", "/locations", "/blog", "/contact", "/book-consultation", "/privacy-policy", "/terms",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const allRoutes = [...routes, ...articles.map((article) => `/blog/${article.slug}`), ...trainers.map((trainer) => `/trainers/${trainer.slug}`)];
  return allRoutes.map((route) => ({
    url: `https://forgeandform.com${route}`,
    changeFrequency: "monthly",
    priority: route === "" ? 1 : 0.7,
  }));
}
