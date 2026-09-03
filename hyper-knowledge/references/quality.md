# Validation and benchmark claims

Use deterministic checks before any live extraction benchmark:

```text
hk benchmark datasets DATASET_PATH... -o benchmark-results --json
```

The dataset receipt checks each text file independently for UTF-8 validity, non-empty content, binary contamination, replacement characters, recognized language/domain layout, bilingual peer coverage, and SHA-256 identity. It does not call an LLM and cannot establish extraction accuracy.

Live semantic evaluation requires a frozen dataset-to-template mapping, a provider/model version, exact parameters, gold annotations or explicit human review criteria, and a cost/data-sharing decision. Do not run it merely because offline preflight passed.

Keep three levels separate:

1. Deterministic artifact validation checks schemas, hashes, topology, member references, and offline packaging.
2. Browser evidence checks bounded rendering behavior such as containment and interaction at named viewport sizes.
3. Perceptual review judges readability and visual polish. Automated screenshots do not approve their own appearance.

Every failure receipt should include a stable code, severity, exact subject, measured evidence, and a supported repair. Never call a partial or skipped layer a complete acceptance.
