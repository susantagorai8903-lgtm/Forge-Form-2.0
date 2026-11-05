import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Privacy information for Forge & Form Personal Training.",
};

export default function PrivacyPolicyPage() {
  return (
    <section className="content-section section-light">
      <div className="shell legal-copy">
        <p className="eyebrow">Forge & Form Personal Training</p>
        <h1 className="page-section-title">Privacy policy</h1>
        <p><strong>Draft template—review and approval required before launch.</strong> This page is a frontend placeholder and does not describe finalized business practices or legal obligations.</p>
        <h2>Information you provide</h2>
        <p>The contact and consultation forms are designed to send information to a configured service endpoint. In this frontend demo, submissions are not stored in the browser. The service, retention period, access controls, and final handling practices must be documented and approved by the business before deployment.</p>
        <h2>Service providers and analytics</h2>
        <p>Hosting, analytics, cookies, and other third-party services have not been configured or verified in this demo. Add accurate information here after selecting and reviewing those services.</p>
        <h2>Your choices and questions</h2>
        <p>For privacy questions, contact <a className="text-link" href="mailto:training@forgeandform.com">training@forgeandform.com</a>. Replace this template with a reviewed policy before collecting personal information in production.</p>
      </div>
    </section>
  );
}
