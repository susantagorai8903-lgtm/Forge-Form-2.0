"use client";

import { useState, type FormEvent } from "react";
import { submitContact } from "@/services/contact.service";
import { ApiError, } from "@/lib/api/client";
import { programs } from "@/data/programs";

type Status = { type: "error" | "success"; message: string } | null;

export function ContactForm() {
  const [status, setStatus] = useState<Status>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.reportValidity()) return;
    const formData = new FormData(form);
    setSubmitting(true);
    setStatus(null);
    try {
      const result = await submitContact({
        name: String(formData.get("name")).trim(),
        email: String(formData.get("email")).trim(),
        phone: String(formData.get("phone")).trim(),
        program: String(formData.get("program")),
        goals: String(formData.get("goals")).trim(),
        preferredContact: String(formData.get("preferredContact")),
        message: String(formData.get("message")).trim(),
      });
      form.reset();
      setStatus({ type: "success", message: result.message || "Thanks for reaching out. We’ll be in touch." });
    } catch (error) {
      setStatus({ type: "error", message: error instanceof ApiError ? error.message : "Something went wrong. Please try again or contact the studio." });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="form-panel" onSubmit={handleSubmit} noValidate>
      <h2>Tell us what you’re looking for.</h2>
      <div className="form-grid">
        <div className="field"><label htmlFor="contact-name">Full name *</label><input id="contact-name" name="name" autoComplete="name" required maxLength={120} /></div>
        <div className="field"><label htmlFor="contact-email">Email *</label><input id="contact-email" name="email" type="email" autoComplete="email" required maxLength={254} /></div>
        <div className="field"><label htmlFor="contact-phone">Phone *</label><input id="contact-phone" name="phone" type="tel" autoComplete="tel" required maxLength={30} /></div>
        <div className="field"><label htmlFor="contact-program">Interested program *</label><select id="contact-program" name="program" required defaultValue=""><option value="" disabled>Select a program</option>{programs.map((program) => <option value={program.title} key={program.slug}>{program.title}</option>)}</select></div>
        <div className="field"><label htmlFor="contact-goals">Fitness goals *</label><input id="contact-goals" name="goals" required maxLength={240} placeholder="What would you like to work toward?" /></div>
        <div className="field"><label htmlFor="contact-method">Preferred contact method *</label><select id="contact-method" name="preferredContact" required defaultValue=""><option value="" disabled>Choose one</option><option>Email</option><option>Phone</option></select></div>
        <div className="field field--full"><label htmlFor="contact-message">Message *</label><textarea id="contact-message" name="message" required maxLength={2000} placeholder="Anything else you’d like us to know?" /></div>
      </div>
      <button className="button form-submit" type="submit" data-analytics-event="contact_submit" disabled={submitting}>{submitting ? "Sending…" : "Send your inquiry"} <span aria-hidden="true">↗</span></button>
      <p className="field__hint">Fields marked * are required. Your information is sent to the configured studio API and is not stored in this browser.</p>
      {status && <p className={`form-message${status.type === "success" ? " form-message--success" : ""}`} role={status.type === "error" ? "alert" : "status"}>{status.message}</p>}
    </form>
  );
}
