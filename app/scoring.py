#from __future__ import annotations

#import math
#from typing import Optional


#def clamp01(x: float) -> float:
 #   return max(0.0, min(1.0, x))


#def safe_float(x: Optional[float]) -> Optional[float]:
 #   try:
  #      return None if x is None else float(x)
 #   except (TypeError, ValueError):
 #       return None


#def minmax_norm(value: Optional[float], vmin: float, vmax: float) -> float:
 #   """
 #   Normalise to [0,1]. Missing values return 0 (conservative).
 #   If range collapses, return 0.5 (neutral).
  #  """
  #  value = safe_float(value)
 #   if value is None:
  #      return 0.0
  #  if vmax <= vmin:
  #      return 0.5
 #   return (value - vmin) / (vmax - vmin)


#def inverse_minmax(value: Optional[float], vmin: float, vmax: float) -> float:
 #   """Lower is better -> invert min-max to [0,1]."""
 #   return 1.0 - minmax_norm(value, vmin, vmax)


#def hidden_gem_score(rating: Optional[float], visitors_m: Optional[float]) -> float:
 #   """
 #   High rating + low visitors.
  #  Uses log to reduce domination by huge visitor values.
  #  Returns in ~[0,1] after clamping.
   # """
  #  r = safe_float(rating)
  #  v = safe_float(visitors_m)

  #  if r is None:
  #      r = 0.0
  #  if v is None:
   #     v = 0.0

    # rating scaled to 0..1
 #   r01 = clamp01(r / 5.0)

    # penalise high visitors (log scale)
  #  denom = math.log1p(max(0.0, v))
   # if denom == 0.0:
  #      return r01  # if no visitors data, don't penalise
  #  score = r01 / denom
  #  return clamp01(score)