export type ApiErrorBody = {
  message: string;
  errors?: Record<string, string[]>;
};

export type ContactRequest = {
  name: string;
  email: string;
  phone: string;
  program: string;
  goals: string;
  preferredContact: string;
  message: string;
};

export type ContactResponse = {
  id: string;
  message: string;
};

export type BookingRequest = {
  name: string;
  email: string;
  phone: string;
  program: string;
  date: string;
  time: string;
  goals: string;
  notes: string;
};

export type BookingResponse = {
  id: string;
  message: string;
};
