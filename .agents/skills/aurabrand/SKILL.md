---
name: aurabrand
description: Uses the AuraBrand agentic suite to generate high-fidelity, brand-aligned documents (PDF, DOCX) and presentations (PPTX). Use this skill when the user wants to create a pitch, a professional report, a slide deck, or any brand-aligned business asset. It handles learned brand guidelines and visual identity automatically.
---

# AuraBrand Asset Generation

AuraBrand is an autonomous agentic suite that researches brand identity and generates professionally formatted deliverables.

## When to Use

- The user wants a **Presentation** (PPTX) for a specific topic or brand.
- The user wants a **Professional Document** (PDF/DOCX), such as a product pitch, research report, or mission profile.
- You need to ensure brand compliance (tone, color, typography) using learned guidelines from `BrandManager`.

## Workflow

1.  **Understand the Intent**: Determine if the user wants a `PRESENTATION` or a `DOCUMENT`.
2.  **Gather Brand Details**: Check the user's request for a brand name, tone, and specific visual preferences (color/font). If not provided, fetch current brand standards using the shared knowledge base.
3.  **Execute the Mission**: Run the AuraBrand agentic graph using the CLI tool.
4.  **Verify & Present**: Inform the user about the generated files in the `outputs/` directory.

## Execution Command

Run the following command to trigger a generation:

```powershell
python main.py --intent [PRESENTATION|DOCUMENT] --prompt "Detailed user request" --brand "Brand Name" --color "#HEXCOLOR"
```

### Examples

- **Presentation**:
  ```powershell
  python main.py --intent PRESENTATION --prompt "A market entry strategy for AuraBrand in the European EV market" --brand "AuraBrand"
  ```

- **Document**:
  ```powershell
  python main.py --intent DOCUMENT --prompt "A technical pitch for a new AI-driven design engine" --brand "DesignFlow" --color "#10B981"
  ```

## Deliverables

All generated assets are stored in:
`c:\Users\Kolaborate\aurabrand\outputs\`

Tell the user where to find their files and summarize the draft document produced by the agent.
