import type { ReactNode } from "react";

export function SectionHeading({
  eyebrow,
  title,
  children,
  light = false,
  centered = false,
}: {
  eyebrow?: string;
  title: string;
  children?: ReactNode;
  light?: boolean;
  centered?: boolean;
}) {
  return (
    <div className={`section-heading${light ? " section-heading--light" : ""}${centered ? " section-heading--center" : ""}`}>
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h2>{title}</h2>
      {children && <div className="section-heading__copy">{children}</div>}
    </div>
  );
}
