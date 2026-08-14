# Compliance Gap Analysis Dashboard

A portfolio-grade Streamlit application for exploring cybersecurity control posture, evidence strength, remediation gaps, and risk-based priorities. The dashboard uses a deliberately fictional organization so that the repository demonstrates a complete GRC workflow without exposing real company data or presenting a simulated assessment as an audit opinion.

## What this project demonstrates

This project turns a control assessment into an evidence-aware action register. It compares a fictional organization’s current state with a target state, groups results by NIST Cybersecurity Framework (CSF) 2.0 Function and control owner, visualizes maturity and risk distribution, and exports both an action register and a structured JSON report.

The implementation is intentionally transparent. It does not claim that a percentage score equals compliance, certification, or audit readiness. It is a decision-support prototype for a GRC, security assurance, internal audit, or risk team.

## Objectives

The dashboard is designed to answer four practical questions:

1. Which control areas have the largest maturity gaps?
2. Which gaps deserve attention first when priority and evidence strength are considered together?
3. Which owners or NIST Functions need management attention?
4. Can the assessment be exported into an action-oriented remediation register?

## Framework basis

The primary lens is **NIST Cybersecurity Framework 2.0**. NIST describes the CSF as an outcome-oriented taxonomy that organizations can use to understand, assess, prioritize, and communicate cybersecurity risk. CSF 2.0 organizes outcomes into six Functions: **Govern, Identify, Protect, Detect, Respond, and Recover**. It also distinguishes Core outcomes, Organizational Profiles, and Tiers, which this project represents through control identifiers, current/target states, and visible scoring assumptions [1] [2].

The dataset includes indicative crosswalk labels to **ISO/IEC 27001:2022 Annex A** control references. These labels are deliberately not a reproduction of the ISO standard. ISO/IEC 27001:2022 defines requirements for an information security management system and continual improvement through a risk-management process; the dashboard therefore treats the ISO references as a comparison lens rather than as a certification engine [3].

| Framework | Role in this project | Treatment |
| --- | --- | --- |
| NIST CSF 2.0 | Primary assessment taxonomy | Function, category, subcategory-style control IDs, current/target posture |
| ISO/IEC 27001:2022 | Indicative crosswalk | Reference labels only; no copyrighted standard text reproduced |
| COBIT | Not used in v1 | Reserved for a future governance-objective mapping layer |

## Methodology

Each fictional control contains a current implementation status, target status, evidence status, business owner, priority, remediation statement, and framework references. The dashboard calculates a maturity score using a visible weighted model:

> **Maturity score = implementation status × status weight + evidence strength × evidence weight**

The default weights are 70% implementation status and 30% evidence strength. Users can adjust the weights in the sidebar to see how evidence quality changes the posture view. The default status scale maps Not Implemented to 0.00, Planned to 0.25, Partially Implemented to 0.50, Largely Implemented to 0.75, and Implemented to 1.00. Evidence maps None to 0.00, Informal to 0.40, Partial to 0.70, and Documented to 1.00.

The gap percentage is the distance between the target score of 1.00 and the calculated maturity score. The risk score is a prioritization heuristic rather than a probability model:

> **Risk score = gap percentage × priority weight × 25**

Priority weights are Low = 1, Medium = 2, High = 3, and Critical = 4. The dashboard then groups findings into Low, Moderate, High, and Critical bands. These calculations are intentionally easy to inspect in `src/assessment.py`, making the project suitable for code review and methodology discussion.

## Application capabilities

The dashboard includes an executive view with control count, average maturity, average gap, high/critical findings, and documented evidence coverage. It provides a NIST Function maturity chart, a risk distribution chart, a prioritized action register, an expandable full control table, and CSV/JSON export buttons.

The fictional dataset covers the six NIST CSF 2.0 Functions and includes realistic ownership boundaries such as Security Governance, Identity Team, Cloud Security, Security Operations, Incident Response, Risk Management, and Third-Party Risk. The dataset is intended for demonstration and interview discussion; it is not a claim about any real organization.

## Repository structure

```text
.
├── app.py
├── data/
│   └── fictional_company_controls.csv
├── src/
│   └── assessment.py
├── tests/
│   └── test_assessment.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Run locally

The project requires Python 3.10 or newer. Create an isolated environment, install dependencies, and start Streamlit:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Run the unit tests with:

```bash
pytest
```

The application is local-first: it reads the fictional CSV from the repository and does not require credentials, a database, or an external API.

## Data model

| Field | Purpose |
| --- | --- |
| `control_id` | Stable NIST-style assessment identifier |
| `framework` | Primary framework lens |
| `function` | NIST CSF 2.0 Function |
| `category` | Assessment grouping |
| `control_title` | Plain-language outcome description |
| `owner` | Responsible control or risk owner |
| `current_status` | Current implementation state |
| `target_status` | Desired state |
| `evidence_status` | Strength of available evidence |
| `priority` | Business or risk priority |
| `remediation` | Action-oriented improvement statement |
| `iso_reference` | Indicative ISO/IEC 27001:2022 reference label |

## Demonstration results

Running the included fictional assessment with the default 70/30 weighting produces the following reproducible snapshot. These figures describe only the sample dataset and are included to make the portfolio project concrete.

| Metric | Sample result |
| --- | ---: |
| Controls assessed | 24 |
| Average maturity | 43.8% |
| Average gap | 56.2% |
| High / critical findings | 8 |
| Controls with documented evidence | 16.7% |

The highest-priority sample findings include software and service inventory, organization-wide logging, third-party risk objectives, identity responsibilities, and risk assessment methodology. The generated JSON snapshot is available at `reports/fictional_company_assessment.json`.

## Portfolio value

This project demonstrates more than a dashboard aesthetic. It shows practical GRC reasoning: framework interpretation, control normalization, evidence-aware scoring, risk prioritization, explainable assumptions, exportable action tracking, testable Python logic, and clear boundaries between a demonstration dataset and a real audit. It can be extended into a multi-framework crosswalk, a database-backed assessment workspace, or a management-ready remediation workflow.

## Limitations and responsible use

The data is fictional. The scoring model is illustrative and should be calibrated with an organization’s risk appetite, control objectives, evidence requirements, and audit methodology before operational use. The project does not provide legal advice, audit assurance, certification, or a compliance determination. ISO/IEC 27001 references are only indicative labels, and the full standard text is not included.

## Roadmap

The next planned portfolio projects are a third-party vendor risk assessment framework, a policy-as-code repository, and an automated cloud evidence collection script. For this dashboard, sensible future enhancements include importing assessment files, adding a target-state Organizational Profile workflow, implementing formal crosswalk metadata, adding remediation due dates and owners, and connecting to a real evidence repository behind authentication.

## References

[1]: https://www.nist.gov/cyberframework "NIST Cybersecurity Framework 2.0 — NIST"

[2]: https://doi.org/10.6028/NIST.CSWP.29 "The NIST Cybersecurity Framework (CSF) 2.0 — NIST CSWP 29"

[3]: https://www.iso.org/standard/27001 "ISO/IEC 27001:2022 — ISO"

## License

MIT. See `LICENSE` for the full text.
