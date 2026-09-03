# Operating Conditions and Load Cases

## Build the condition envelope

Do not design only for nominal steady operation. Review:

- Startup, acceleration, braking, shutdown, reversing, and emergency stop.
- Normal production, peak throughput, jam, stall, blockage, overload, and impact.
- Installation, lifting, transport, storage, commissioning, maintenance, and foreseeable misuse.
- Minimum and maximum temperature, thermal gradients, humidity, water, dust, chemicals, corrosion, radiation, altitude, and cleanliness.
- Continuous, intermittent, cyclic, random, shock, and resonant vibration.

## Load-case record

Each load case must define:

- Identifier and description.
- Event frequency and duration.
- Forces, moments, torque, pressure, acceleration, speed, displacement, or temperature.
- Direction, application point/area, coordinate system, and time behavior.
- Supports, constraints, contact assumptions, and load path.
- Combination factors, uncertainty, and source.
- Required response: stress, deformation, fatigue, stability, contact, life, sealing, noise, or motion.

## Duty cycle and life

- Convert operating schedules into cycles, revolutions, hours, starts, or load spectra.
- Keep average, RMS, peak, and damage-equivalent values distinct.
- Include expected maintenance and replacement intervals.
- Record reliability target and allowed probability of failure where applicable.

## Vibration and dynamics

- Compare forcing frequencies with natural frequencies and operating-speed ranges.
- Include imbalance, gear mesh, bearing defect, reciprocating, blade-pass, motor, and external vibration sources as applicable.
- Review transient and resonance crossing, not only steady response.
- Define acceptable vibration, noise, alignment, and fastener-retention criteria.

## Environmental adaptation

- Select material, coating, seal, lubrication, cable, bearing, and fastener conditions for the environment.
- Account for thermal expansion in fits, clearances, preload, and alignment.
- Account for contamination and corrosion in life and maintenance assumptions.

Use `assets/templates/load-cases.template.json`, run `scripts/validate_load_cases.py`, and block verification when a governing load case remains unknown.
