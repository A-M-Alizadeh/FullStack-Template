/** Auth shapes aligned with FastAPI schemas. */

export type UserRole = "admin" | "editor";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface AccessTokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}
