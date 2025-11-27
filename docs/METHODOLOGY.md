# Methodology

## Essential Eight
- Maturity levels 0–3 per ACSC.
- Heatmap: level 0 = critical, 1 = high, 2 = moderate, 3 = low.
- Recommendations prioritise lowest maturity controls and emphasise offline, tested backups.
- Regulatory signals: low backups surface Privacy Act (OAIC) sensitivity; low MFA maps to SOCI Act emphasis; finance industries inherit APRA CPS 234 messaging.

## FAIR
- **Loss Event Frequency (LEF)** = Threat Event Frequency × Vulnerability.
- **Loss Magnitude (LM)** = Primary Loss + Secondary Loss.
- **Secondary Risk Event Frequency** sampled separately and multiplied into total loss.
- Triangular distributions (min, mode, max) are sampled for each parameter to model uncertainty; inputs are validated for `min <= mode <= max` and non-negative values (probabilities must be <= 1).
- Monte Carlo defaults to 10,000 iterations but is configurable (floor at 1,000 iterations to avoid undersampling).
- Outputs include mean, P90, P95, and worst-case estimates.

## Integration
- Weak Essential Eight controls increase TEF and vulnerability multipliers; low backups elevate secondary loss exposure; weak MFA increases primary loss exposure; weak patching inflates secondary event frequency.
- Scenario library contains ransomware, business email compromise, and data breach templates that can be extended.

## Regulatory Context
- Signals surface potential impacts for the Privacy Act (OAIC), SOCI Act, and APRA CPS 234 based on deficient controls or industry selection.
