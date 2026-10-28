# Verification

Checks that run on a desktop (and in CI) against the engine copy in `app/src/main/python`. Only fictional people.

- `independent.py`: recomputes, with pyswisseph directly and not the engine's code, the facts the forecast stands on for
  three years (slow-planet sign changes, Vimshottari dates, Jupiter-Saturn double transits, Saturn phases from the Moon,
  personal years) and compares them with the engine.
- `layer.py`: builds the three-year forecast for ten people (including a minor, a 29 February birthday, the southern
  hemisphere and an unknown birth time) on two dates and checks its rules: no forbidden predictions, reasons inside
  their year, outlook and best/care years by the stated rule, K.N. Rao months, no marriage talk before 18, Hindi coverage.
- `report_check.py`: builds the full reading for nine people in English and Hindi and checks every section is present,
  no forbidden word, no stray placeholders, no English left in the Hindi text.

Run all three: `pip install pyswisseph==2.10.3.2 tzdata` then `python tools/verify/run_all.py`.
