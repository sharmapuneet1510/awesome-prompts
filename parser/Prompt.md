# Field Derivation Interpretation Prompt

[span_2](start_span)[span_3](start_span)Use this prompt with GitHub Copilot, Gemini, or any LLM to transform the raw code extraction into a **Human Language Explanation** as required by the agent's interpretation phase[span_2](end_span)[span_3](end_span).

---

## 🤖 Copilot Prompt

**Role:** Act as a Senior Software Architect and Business Systems Analyst.

**[span_4](start_span)[span_5](start_span)Task:** Interpret the lifecycle and business meaning of a specific debug field derived from a multi-module Maven repository[span_4](end_span)[span_5](end_span).

**Input Data:**
- **Field Name:** N_COUNTERPARTY_2
- **Source Files:** - `TradeStateMapper.java` (Line 69)
    - `C0_Field_Map.xslt` / `CR_Field_Map.xslt`
- **[span_6](start_span)Logic Type:** Data Enrichment and Transformation[span_6](end_span).

**Prompt Content:**
> "Analyze the following code snippets to explain the derivation of 'N_COUNTERPARTY_2'. 
> 
> 1. **[span_7](start_span)Extraction Phase:** Based on the XSLT `<xsl:value-of>` tags, identify the raw source message attribute where this data originates[span_7](end_span).
> 2. **Enrichment Phase:** In the Java snippet at line 69, explain the logic of using `MessageKeysTradeState.N_COUNTERPARTY_2.getValue()`. [span_8](start_span)How does the code use 'isRetail' and 'counterParty2Identifier' to decide between mapping to 'otherPartyId' versus 'otherPartyLegalId'?[span_8](end_span).
> 3. **[span_9](start_span)[span_10](start_span)Human Recognition Explanation:** Provide a 3-sentence summary in plain English for a non-technical stakeholder explaining how this field moves from the XML message into the final trade report[span_9](end_span)[span_10](end_span).
> 4. **[span_11](start_span)Audit Trail:** Confirm if the logic differs for specific Asset Classes like IRS, FX, or Equities based on the method context[span_11](end_span)."

---

## 🛠️ Implementation Summary for Engineers

| Requirement | Implementation Detail |
| :--- | :--- |
| **[span_12](start_span)Logic Source** | Identifies if code resides in **Library** or **Jurisdiction** repo[span_12](end_span). |
| **Extraction** | [span_13](start_span)Strict AST/XML parsing only (No LLM)[span_13](end_span). |
| **Output** | Primary JSON for machines, HTML for UI, MD5 for audit. |
| **Traceability** | [span_14](start_span)Follows method chaining and variable assignments[span_14](end_span). |
