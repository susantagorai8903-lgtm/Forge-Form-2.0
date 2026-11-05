"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight, Search } from "lucide-react";
import type { Article } from "@/types/content";

const categories = ["All", "Strength Training", "Nutrition", "Personal Wellness", "Weight Management", "Mobility", "Fitness Tips"];

export function BlogBrowser({ articles }: { articles: Article[] }) {
  const [category, setCategory] = useState("All");
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => articles.filter((article) => {
    const categoryMatch = category === "All" || article.category === category;
    const search = query.trim().toLowerCase();
    return categoryMatch && (!search || `${article.title} ${article.excerpt} ${article.category}`.toLowerCase().includes(search));
  }), [articles, category, query]);

  return (
    <>
      <div className="blog-tools">
        <div className="filter-list" aria-label="Filter articles by category">
          {categories.map((item) => <button className="filter-button" type="button" aria-pressed={category === item} key={item} onClick={() => setCategory(item)}>{item}</button>)}
        </div>
        <label className="blog-search"><Search size={16} aria-hidden="true" /><span className="sr-only">Search articles</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search the journal" /></label>
      </div>
      {filtered.length ? (
        <div className="article-grid" aria-live="polite">
          {filtered.map((article) => (
            <article className="article-card" key={article.slug}>
              <Link href={`/blog/${article.slug}`} aria-label={`Read ${article.title}`}>
                <div className="article-card__image"><Image src={article.image} alt={article.alt} fill sizes="(max-width: 700px) 90vw, (max-width: 1050px) 45vw, 30vw" className="cover-image" /></div>
              </Link>
              <div className="article-card__meta"><span>{article.category}</span><span>{article.readingTime}</span></div>
              <h2><Link href={`/blog/${article.slug}`}>{article.title}</Link></h2>
              <p>{article.excerpt}</p>
              <Link className="text-link" href={`/blog/${article.slug}`}>Read article <ArrowUpRight size={14} /></Link>
            </article>
          ))}
        </div>
      ) : <p className="empty-state" role="status">No articles match those filters. Try another category or search.</p>}
    </>
  );
}
