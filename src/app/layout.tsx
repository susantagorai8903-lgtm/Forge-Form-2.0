import type { Metadata } from "next";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { SmoothScroll } from "@/components/layout/SmoothScroll";
import "./globals.css";

const business = {
  "@context": "https://schema.org",
  "@type": "SportsActivityLocation",
  name: "Forge & Form Personal Training",
  telephone: "+1-503-555-0139",
  email: "training@forgeandform.com",
  address: {
    "@type": "PostalAddress",
    streetAddress: "1900 Division Street",
    addressLocality: "Portland",
    addressRegion: "OR",
    postalCode: "97202",
    addressCountry: "US",
  },
};

export const metadata: Metadata = {
  metadataBase: new URL("https://forgeandform.com"),
  title: {
    default: "Forge & Form | Personal Training in Portland, Oregon",
    template: "%s | Forge & Form",
  },
  description: "Personalized strength training, personal coaching, mobility, and wellness at Forge & Form in Portland, Oregon.",
  openGraph: {
    type: "website",
    siteName: "Forge & Form Personal Training",
    title: "Forge & Form | Personal Training in Portland, Oregon",
    description: "Personalized training. Expert coaching. Sustainable results.",
    images: [{ url: "/images/a3.jfif", width: 1200, height: 800, alt: "The Forge & Form training community" }],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body>
        <a className="skip-link" href="#main-content">Skip to content</a>
        <Navbar />
        <SmoothScroll />
        <main id="main-content">{children}</main>
        <Footer />
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(business) }} />
      </body>
    </html>
  );
}
