// Simple client-side session check for BookLens
export function isLoggedIn() {
  if (typeof window === "undefined") return false;
  const session = localStorage.getItem("booklens_session");
  return !!session;
}
