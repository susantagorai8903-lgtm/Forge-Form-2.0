import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { articles } from "@/data/articles";
import { FinalCta } from "@/components/shared/FinalCta";

export function generateStaticParams() {
  return articles.map((article) => ({ slug: article.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const article = articles.find((item) => item.slug === slug);
  return article ? { title: article.title, description: article.excerpt, openGraph: { images: [article.image] } } : {};
}

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const article = articles.find((item) => item.slug === slug);
  if (!article) notFound();

  const related = articles.filter((item) => item.slug !== slug && item.category === article.category).slice(0, 2);
  return (
    <>
      <article className="content-section section-light">
        <div className="shell article-body">
          <Link className="text-link" href="/blog"><ArrowLeft size={14} /> Back to the journal</Link>
          <p className="article-body__meta" style={{ marginTop: 32 }}>{article.category} · {article.readingTime} · {article.author} · {article.date}</p>
          <h1>{article.title}</h1>
          <p className="section-heading__copy">{article.excerpt}</p>
          <div className="article-body__image"><Image src={article.image} alt={article.alt} fill priority sizes="(max-width: 800px) 90vw, 760px" className="cover-image" /></div>
          {article.content.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
          <p className="field__hint">This demo article is general information, not medical or individualized nutrition advice.</p>
        </div>
      </article>
      {related.length > 0 && <section className="content-section section-paper"><div className="shell"><p className="eyebrow">Continue exploring</p><h2 className="page-section-title">Related notes</h2><div className="related-links">{related.map((item) => <Link href={`/blog/${item.slug}`} key={item.slug}>{item.title} <ArrowLeft size={15} /></Link>)}</div></div></section>}
      <FinalCta />
    </>
  );
}
