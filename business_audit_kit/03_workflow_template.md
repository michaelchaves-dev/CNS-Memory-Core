# Claude Workflow Template

Copy this template for each workflow you build. Fill in every section — incomplete templates produce inconsistent outputs.

---

## Workflow Name: [Name]

**Version:** 1.0  
**Owner:** [Name / Role]  
**Last updated:** [Date]

---

### ROLE

Claude acts as **[business role]** for **[company name]**.

> Example: "Claude acts as a senior customer success manager for Acme Corp."

---

### INPUTS

List every input Claude will receive. Be specific about format and source.

| Input | Format | Source |
|---|---|---|
| | | |
| | | |
| | | |

> Examples: customer email (plain text, pasted), account notes (CRM export, CSV), product FAQ (uploaded PDF)

---

### TASK

Describe the exact job Claude must complete. Use numbered steps if order matters.

1. 
2. 
3. 

> Be precise: "Draft a reply that addresses every question raised, stays under 150 words, and uses a friendly but professional tone."

---

### RULES

Define constraints Claude must always follow.

- **Brand voice:** [formal / conversational / technical]
- **Privacy:** Do not include [PII types, confidential fields, etc.]
- **Scope:** Do not [recommend pricing changes / make commitments / etc.]
- **Escalation:** Flag if [conditions that require human decision]

---

### OUTPUT

Specify the exact format of the deliverable.

- **Format:** [email draft / bullet list / table / JSON / etc.]
- **Length:** [max words / sections required]
- **Structure:**

```
[paste an example output skeleton here]
```

---

### REVIEW

Claude must always end its response by flagging any of the following if present:

- [ ] Missing information needed to complete the task
- [ ] Risk or compliance concern the human owner should review
- [ ] Decision point that requires owner approval before sending/publishing
- [ ] Ambiguity in the input that could affect output accuracy

> If none apply, Claude states: "No flags. Ready for review."
