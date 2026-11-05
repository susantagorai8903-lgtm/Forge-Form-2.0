import Link from "next/link";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from "react";

type Props = {
  children: ReactNode;
  variant?: "primary" | "outline" | "light";
  className?: string;
  analyticsEvent?: string;
} & (
  | ({ href: string } & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "href">)
  | ({ href?: never } & ButtonHTMLAttributes<HTMLButtonElement>)
);

export function Button({ children, variant = "primary", className = "", analyticsEvent = "cta_click", ...props }: Props) {
  const classes = `button button--${variant} ${className}`;
  if ("href" in props && props.href) {
    const { href, ...anchorProps } = props;
    return <Link className={classes} href={href} data-analytics-event={analyticsEvent} {...anchorProps}>{children}</Link>;
  }
  return <button className={classes} data-analytics-event={analyticsEvent} {...props as ButtonHTMLAttributes<HTMLButtonElement>}>{children}</button>;
}
