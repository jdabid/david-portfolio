import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { trackVisit } from "../services/api";

/**
 * Hook that tracks page visits on every route change.
 * Sends a fire-and-forget POST to /api/analytics/track.
 */
export function usePageTracking() {
  const location = useLocation();

  useEffect(() => {
    trackVisit(location.pathname).catch(() => {
      // Silently ignore tracking failures — analytics should never break UX
    });
  }, [location.pathname]);
}
