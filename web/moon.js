// Sidereal (Lahiri) longitude of the Moon, computed in the browser.
// Lunar theory: Meeus, Astronomical Algorithms, ch. 47 (ELP-2000/82 truncated).
// Ayanamsa: polynomial fitted to Swiss Ephemeris SIDM_LAHIRI over 1900-2100.

const RAD = Math.PI / 180;

// D, M, M', F, coefficient of sine (units 1e-6 degree)
const TERMS = [
  [0,0,1,0,6288774],[2,0,-1,0,1274027],[2,0,0,0,658314],[0,0,2,0,213618],
  [0,1,0,0,-185116],[0,0,0,2,-114332],[2,0,-2,0,58793],[2,-1,-1,0,57066],
  [2,0,1,0,53322],[2,-1,0,0,45758],[0,1,-1,0,-40923],[1,0,0,0,-34720],
  [0,1,1,0,-30383],[2,0,0,-2,15327],[0,0,1,2,-12528],[0,0,1,-2,10980],
  [4,0,-1,0,10675],[0,0,3,0,10034],[4,0,-2,0,8548],[2,1,-1,0,-7888],
  [2,1,0,0,-6766],[1,0,-1,0,-5163],[1,1,0,0,4987],[2,-1,1,0,4036],
  [2,0,2,0,3994],[4,0,0,0,3861],[2,0,-3,0,3665],[0,1,-2,0,-2689],
  [2,0,-1,2,-2602],[2,-1,-2,0,2390],[1,0,1,0,-2348],[2,-2,0,0,2236],
  [0,1,2,0,-2120],[0,2,0,0,-2069],[2,-2,-1,0,2048],[2,0,1,-2,-1773],
  [2,0,0,2,-1595],[4,-1,-1,0,1215],[0,0,2,2,-1110],[3,0,-1,0,-892],
  [2,1,1,0,-810],[4,-1,-2,0,759],[0,2,-1,0,-713],[2,2,-1,0,-700],
  [2,1,-2,0,691],[2,-1,0,-2,596],[4,0,1,0,549],[0,0,4,0,537],
  [4,-1,0,0,520],[1,0,-2,0,-487],[2,1,0,-2,-399],[0,0,2,-2,-381],
  [1,1,1,0,351],[3,0,-2,0,-340],[4,0,-3,0,330],[2,-1,2,0,327],
  [0,2,1,0,-323],[1,1,-1,0,299],[2,0,3,0,294]
];

const norm = d => ((d % 360) + 360) % 360;

/** Apparent tropical longitude of the Moon, in degrees, for a Julian Day (TT). */
function moonTropical(jde) {
  const T = (jde - 2451545.0) / 36525.0;
  const T2 = T * T, T3 = T2 * T, T4 = T3 * T;

  const Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T2 + T3 / 538841 - T4 / 65194000;
  const D  = 297.8501921 + 445267.1114034 * T - 0.0018819 * T2 + T3 / 545868 - T4 / 113065000;
  const M  = 357.5291092 + 35999.0502909 * T - 0.0001536 * T2 + T3 / 24490000;
  const Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T2 + T3 / 69699 - T4 / 14712000;
  const F  = 93.2720950 + 483202.0175233 * T - 0.0036539 * T2 - T3 / 3526000 + T4 / 863310000;

  const A1 = 119.75 + 131.849 * T;
  const A2 = 53.09 + 479264.290 * T;
  const E  = 1 - 0.002516 * T - 0.0000074 * T2;

  let sum = 0;
  for (const [d, m, mp, f, coef] of TERMS) {
    const arg = (d * D + m * M + mp * Mp + f * F) * RAD;
    let c = coef;
    if (m === 1 || m === -1) c *= E;
    else if (m === 2 || m === -2) c *= E * E;
    sum += c * Math.sin(arg);
  }
  sum += 3958 * Math.sin(A1 * RAD) + 1962 * Math.sin((Lp - F) * RAD) + 318 * Math.sin(A2 * RAD);

  // Nutation in longitude, principal terms (Meeus ch. 22), in degrees.
  const Om = 125.04452 - 1934.136261 * T;
  const Ls = 280.4665 + 36000.7698 * T;
  const Lm = 218.3165 + 481267.8813 * T;
  const dPsi = (-17.20 * Math.sin(Om * RAD) - 1.32 * Math.sin(2 * Ls * RAD)
                - 0.23 * Math.sin(2 * Lm * RAD) + 0.21 * Math.sin(2 * Om * RAD)) / 3600;

  return norm(Lp + sum / 1000000 + dPsi);
}

/** Lahiri ayanamsa in degrees, fitted to Swiss Ephemeris over 1900-2100. */
function ayanamsa(jd) {
  const T = (jd - 2451545.0) / 36525.0;
  return 23.857092351711835 + 1.3968879574300688 * T
       + 0.00030709112240855194 * T * T + 2.973794762712619e-9 * T * T * T;
}

const DT0 = 1900, DT_STEP = 4;
const DT = [-2.0,3.5,8.7,13.7,18.5,21.6,23.5,24.3,24.4,24.1,24.4,26.5,28.2,29.7,31.4,33.1,35.0,38.3,42.2,46.5,50.5,53.8,55.8,58.3,61.6,63.8,64.6,65.5,66.6,68.1,69.4,69.1,68.8,69.8,70.8,71.8,72.9,74.0,75.2];

/** TT - UT in seconds. Interpolated from Swiss Ephemeris between 1900 and 2052,
 *  and extrapolated by the Espenak-Meeus parabola outside it. */
function deltaT(year, month = 1) {
  const y = year + (month - 0.5) / 12;
  const last = DT0 + DT_STEP * (DT.length - 1);
  if (y >= DT0 && y <= last) {
    const x = (y - DT0) / DT_STEP, i = Math.min(Math.floor(x), DT.length - 2);
    const a = DT.at(i), b = DT.at(i + 1);
    return a + (b - a) * (x - i);
  }
  const u = (y - 1820) / 100;
  return -20 + 32 * u * u;
}

/** Julian Day from a UTC calendar date and fractional hour (Gregorian). */
function julianDay(y, m, d, hour) {
  if (m <= 2) { y -= 1; m += 12; }
  const A = Math.floor(y / 100), B = 2 - A + Math.floor(A / 4);
  return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + B - 1524.5 + hour / 24;
}

/** Sidereal (Lahiri) longitude of the Moon for a UT Julian Day. */
function moonSidereal(jdUT, year, month = 1) {
  const jde = jdUT + deltaT(year, month) / 86400;
  return norm(moonTropical(jde) - ayanamsa(jdUT));
}
