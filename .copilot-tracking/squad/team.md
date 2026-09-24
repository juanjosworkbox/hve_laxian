---
description: "Squad roster: roles and the deployed HVE Core agents that fill them"
---

# Squad Roster

## Members

| Role            | Member Name | Agent Name (Primary) | Alternate Agents | Selection Cue | Invocation | Model Tier | Deliverable Root |
|-----------------|-------------|---------------------|-----------------|---------------|------------|------------|-----------------|
| researcher      | Alpha       | Squad Researcher    | —               | —             | runSubagent / task | default | .copilot-tracking/research/<date>/ |
| lead            | Beta        | Squad Lead          | —               | —             | runSubagent / task | default | .copilot-tracking/plans/ |
| developer       | Gamma       | Squad Implementor   | —               | —             | runSubagent / task | default | .copilot-tracking/changes/ |
| tester          | Delta       | Squad Reviewer      | —               | —             | runSubagent / task | fast | .copilot-tracking/reviews/ |
| scribe          |             | Squad Scribe        | —               | —             | runSubagent / task | fast | (squad state) |
