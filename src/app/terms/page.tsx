import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms & Conditions",
  description: "Terms information for Forge & Form Personal Training.",
};

export default function TermsPage() {
  return (
    <section className="content-section section-light">
      <div className="shell legal-copy">
        <p className="eyebrow">Forge & Form Personal Training</p>
        <h1 className="page-section-title">Terms & conditions</h1>
        <p><strong>Draft template—review and approval required before launch.</strong> This page is not a finalized agreement and does not create membership or payment terms.</p>
        <h2>Website information</h2>
        <p>Program descriptions on this demo site are general information only. No pricing, membership conditions, cancellation rules, or training guarantees have been supplied. Confirm and publish those details before offering memberships.</p>
        <h2>Consultation requests</h2>
        <p>Submitting a consultation request does not reserve a session. Preferred dates and times shown on this site are examples and are not confirmed availability. The studio must confirm any appointment directly.</p>
        <h2>Training and wellness</h2>
        <p>Information on this site is not medical advice. Speak with a qualified healthcare professional about health concerns, injuries, or whether an exercise program is appropriate for you.</p>
        <h2>Contact</h2>
        <p>Questions about these draft terms can be sent to <a className="text-link" href="mailto:training@forgeandform.com">training@forgeandform.com</a>.</p>
      </div>
    </section>
  );
}
