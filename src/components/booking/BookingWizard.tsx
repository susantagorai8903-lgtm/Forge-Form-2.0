"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { Check, ChevronLeft, ChevronRight } from "lucide-react";
import { ApiError } from "@/lib/api/client";
import { programs } from "@/data/programs";
import { submitBooking } from "@/services/booking.service";
import type { BookingRequest } from "@/types/api";

const steps = ["Your details", "Choose a program", "Pick a time", "Your goals", "Review"];
const demoTimes = ["9:00 AM", "12:00 PM", "4:30 PM"];
const emptyBooking: BookingRequest = { name: "", email: "", phone: "", program: "", date: "", time: "", goals: "", notes: "" };

export function BookingWizard() {
  const [step, setStep] = useState(0);
  const [booking, setBooking] = useState(emptyBooking);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [confirmation, setConfirmation] = useState("");
  const [minimumDate, setMinimumDate] = useState("");
  const idempotencyKey = useRef<string | null>(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    const now = new Date();
    const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    setMinimumDate(localDate);
  }, []);

  function update<K extends keyof BookingRequest>(key: K, value: BookingRequest[K]) {
    setBooking((current) => ({ ...current, [key]: value }));
  }

  function handleChange(event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = event.target;
    if (name in booking) update(name as keyof BookingRequest, value);
  }

  function next() {
    setError("");
    if (step === 0 && (!booking.name.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(booking.email) || !booking.phone.trim())) {
      setError("Enter your name, a valid email address, and phone number to continue.");
      return;
    }
    if (step === 1 && !booking.program) setError("Choose a program to continue.");
    else if (step === 2 && (!booking.date || !booking.time)) setError("Choose a preferred date and sample time to continue.");
    else if (step === 3 && !booking.goals.trim()) setError("Share a little about your goals to continue.");
    else setStep((current) => Math.min(current + 1, steps.length - 1));
  }

  function back() {
    setError("");
    setStep((current) => Math.max(current - 1, 0));
  }

  async function submit() {
    setError("");
    setSubmitting(true);
    try {
      idempotencyKey.current ??= crypto.randomUUID();
      const result = await submitBooking(booking, idempotencyKey.current);
      setConfirmation(result.message || "Your consultation request has been received. The studio will follow up to confirm the details.");
    } catch (submitError) {
      setError(submitError instanceof ApiError ? submitError.message : "Your request could not be completed. Please try again or contact the studio directly.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="booking-shell">
      {confirmation ? (
        <div className="booking-confirmation" role="status">
          <Check size={30} />
          <p className="eyebrow">Request received</p>
          <h2>You’re on your way.</h2>
          <p>{confirmation}</p>
        </div>
      ) : (
        <>
          <div className="booking-progress" aria-label={`Step ${step + 1} of ${steps.length}`}>
            <div className="booking-progress__top"><span>Step {String(step + 1).padStart(2, "0")} / 05</span><span>{steps[step]}</span></div>
            <div className="booking-progress__track"><div className="booking-progress__fill" style={{ width: `${((step + 1) / steps.length) * 100}%` }} /></div>
          </div>
          <AnimatePresence mode="wait" initial={false}>
            <motion.section
              className="booking-step"
              key={step}
              initial={reduceMotion ? false : { opacity: 0, x: 18 }}
              animate={{ opacity: 1, x: 0 }}
              exit={reduceMotion ? undefined : { opacity: 0, x: -18 }}
              transition={{ duration: reduceMotion ? 0 : .22 }}
              aria-labelledby="booking-step-heading"
            >
              {step === 0 && <>
                <h2 id="booking-step-heading">First, a little about you.</h2><p className="booking-step__lead">We’ll use these details to follow up about your consultation request.</p>
                <div className="form-grid">
                  <div className="field"><label htmlFor="booking-name">Full name *</label><input id="booking-name" name="name" autoComplete="name" required maxLength={120} value={booking.name} onChange={handleChange} /></div>
                  <div className="field"><label htmlFor="booking-phone">Phone *</label><input id="booking-phone" name="phone" type="tel" autoComplete="tel" required maxLength={30} value={booking.phone} onChange={handleChange} /></div>
                  <div className="field field--full"><label htmlFor="booking-email">Email *</label><input id="booking-email" name="email" type="email" autoComplete="email" required maxLength={254} value={booking.email} onChange={handleChange} /></div>
                </div>
              </>}
              {step === 1 && <>
                <h2 id="booking-step-heading">What would you like to explore?</h2><p className="booking-step__lead">Choose the program that feels closest. You can talk through the details with a coach.</p>
                <div className="choice-grid">{programs.map((program) => <button type="button" className={`choice-card${booking.program === program.title ? " is-selected" : ""}`} aria-pressed={booking.program === program.title} key={program.slug} onClick={() => update("program", program.title)}><strong>{program.title}</strong><span>{program.summary}</span></button>)}</div>
              </>}
              {step === 2 && <>
                <h2 id="booking-step-heading">When works for you?</h2><p className="booking-step__lead">Choose a preferred date and sample time. These options are illustrative only—not confirmed availability or studio hours.</p>
                <div className="form-grid">
                  <div className="field field--full"><label htmlFor="booking-date">Preferred date *</label><input id="booking-date" name="date" type="date" min={minimumDate} value={booking.date} onChange={(event) => { update("date", event.target.value); update("time", ""); }} /></div>
                  <div className="field field--full"><span className="field__hint">Sample times (request only)</span><div className="choice-grid">{demoTimes.map((time) => <button type="button" key={time} className={`choice-card${booking.time === time ? " is-selected" : ""}`} aria-pressed={booking.time === time} disabled={!booking.date} onClick={() => update("time", time)}><strong>{time}</strong><span>{booking.date ? "Preferred consultation time" : "Choose a date first"}</span></button>)}</div></div>
                </div>
              </>}
              {step === 3 && <>
                <h2 id="booking-step-heading">What are you working toward?</h2><p className="booking-step__lead">Share what you’re hoping to get from training. Keep it high-level—no medical information needed.</p>
                <div className="form-grid">
                  <div className="field field--full"><label htmlFor="booking-goals">Your goals *</label><textarea id="booking-goals" name="goals" required maxLength={1200} value={booking.goals} onChange={handleChange} placeholder="What would you like to feel, learn, or work toward?" /></div>
                  <div className="field field--full"><label htmlFor="booking-notes">Anything else? <span className="field__hint">(optional)</span></label><textarea id="booking-notes" name="notes" maxLength={1200} value={booking.notes} onChange={handleChange} placeholder="Questions or context for the studio?" /></div>
                </div>
              </>}
              {step === 4 && <>
                <h2 id="booking-step-heading">Review your request.</h2><p className="booking-step__lead">Check the details before sending. Your consultation is not booked until the studio confirms it.</p>
                <ul className="benefit-list">
                  <li><Check size={15} />{booking.name} · {booking.email} · {booking.phone}</li>
                  <li><Check size={15} />{booking.program}</li>
                  <li><Check size={15} />{booking.date} · {booking.time} (preferred, unconfirmed)</li>
                  <li><Check size={15} />{booking.goals}</li>
                </ul>
                {booking.notes && <p className="field__hint">Additional note: {booking.notes}</p>}
                <p className="field__hint">Demo availability is for request planning only. Submitting will contact the configured API; no booking is saved unless the service confirms a successful response.</p>
              </>}
              {error && <p className="form-message" role="alert">{error}</p>}
              <div className="booking-step__nav">
                {step > 0 ? <button className="button button--outline" type="button" onClick={back}><ChevronLeft size={16} /> Back</button> : <span />}
                {step < 4 ? <button className="button" type="button" onClick={next}>Continue <ChevronRight size={16} /></button> : <button className="button" type="button" data-analytics-event="booking_submit" onClick={submit} disabled={submitting}>{submitting ? "Sending request…" : "Send consultation request"} <span aria-hidden="true">↗</span></button>}
              </div>
            </motion.section>
          </AnimatePresence>
        </>
      )}
    </div>
  );
}
