import { apiRequest } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { Article, Program, Testimonial, Trainer } from "@/types/content";

export function getPrograms() {
  return apiRequest<Program[]>(endpoints.programs);
}

export function getTrainers() {
  return apiRequest<Trainer[]>(endpoints.trainers);
}

export function getTestimonials() {
  return apiRequest<Testimonial[]>(endpoints.testimonials);
}

export function getArticles() {
  return apiRequest<Article[]>(endpoints.blog);
}

export function getArticle(slug: string) {
  return apiRequest<Article>(`${endpoints.blog}/${encodeURIComponent(slug)}`);
}
