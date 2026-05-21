# Claude Business Audit Kit

A structured toolkit for auditing businesses and deploying Claude AI workflows. Run this as a consulting engagement or use it internally to systematize your own team's AI practice.

## Files

| File | Purpose |
|---|---|
| `01_client_intake.md` | Initial discovery form — business profile, pain points, constraints |
| `02_workflow_discovery.md` | Workflow mapping table with prioritization scoring |
| `03_workflow_template.md` | Standard template for building any Claude workflow |
| `04_first_10_workflows.md` | Pre-built definitions for the 10 most common business workflows |
| `05_delivery_offer.md` | Service packaging and delivery structure for client engagements |

## How to Use

1. Start with `01_client_intake.md` — fill it out in the first call or async
2. Use `02_workflow_discovery.md` to map and score workflows (aim for 10–20 candidates)
3. Select the top 5–10 using the prioritization guide
4. Build each using `03_workflow_template.md`
5. Reference `04_first_10_workflows.md` for ready-made starting points
6. Package the engagement using `05_delivery_offer.md`

## Storing Workflows via CNS Memory Core

Completed workflow templates can be stored in CNS Memory Core for retrieval by Claude agents:

```bash
curl -X POST https://your-cns-instance/save \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "workflow:customer-email-reply",
    "value": {
      "role": "Customer success rep",
      "task": "Draft a reply addressing every customer point",
      "rules": ["Match brand voice", "Flag SLA change requests"],
      "output": "Ready-to-send email draft"
    }
  }'
```

Retrieve a workflow at runtime:

```bash
curl "https://your-cns-instance/load?key=workflow:customer-email-reply" \
  -H "X-API-Key: your-key"
```
