import { apiRequest } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { BookingRequest, BookingResponse } from "@/types/api";

export function submitBooking(payload: BookingRequest, idempotencyKey?: string) {
  return apiRequest<BookingResponse>(endpoints.bookings, {
    method: "POST",
    body: JSON.stringify(payload),
    headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : undefined,
  });
}
