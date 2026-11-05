import { apiRequest } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { ContactRequest, ContactResponse } from "@/types/api";

export function submitContact(payload: ContactRequest) {
  return apiRequest<ContactResponse>(endpoints.contact, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
