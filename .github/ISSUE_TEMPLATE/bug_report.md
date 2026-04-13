---
name: Bug Report
about: Create a detailed bug report to help us improve the S&P 500 Predictor
title: '[BUG] <Short, descriptive title>' # Example: [BUG] API /predict endpoint returns 500 when no model is trained
labels: bug, needs-triage
assignees: ''
---

<p style="font-size:1.1em; color:#34495e; font-style:italic;">
Thank you for taking the time to report a bug! Your detailed input is crucial for improving the S&P 500 Predictor. Please fill out the sections below as thoroughly as possible.
</p>

<p align="center">
  <img src="https://i.postimg.cc/TKFj3230/bug-icon-static.png" alt="Bug Icon" style="max-width:150px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Help us squash bugs!</figcaption>
</p>

---

## <span style="color:#dc3545; font-weight:bold;">🐛 Describe the Bug</span>

A clear and concise description of what the bug is. What exactly is going wrong?

-   **What:** Briefly explain the issue.
-   **When:** Did this start recently? Is it intermittent or constant?
-   **Where:** Which part of the application (API, Dashboard, Training Script, etc.) is affected?
-   **Impact:** What are the consequences of this bug?

---

## <span style="color:#ff8c00; font-weight:bold;">🚨 Severity and Impact</span>

<p style="font-style:italic; color:#777;">Please select the most appropriate severity and describe its impact on users or the system.</p>

-   **Severity Level:**
    -   [ ] Critical: System is down or major functionality is completely broken, preventing core operations.
    -   [ ] High: Significant functionality is impaired, impacting many users or crucial processes.
    -   [ ] Medium: Minor functionality issues or cosmetic problems affecting some users, with workarounds available.
    -   [ ] Low: Trivial issues, typos, or minor UI glitches that don't affect functionality.

-   **Impact Description:** (e.g., "Prevents all predictions from being made", "Causes incorrect data to be displayed on the dashboard", "Minor UI misalignment on mobile devices")

---

## <span style="color:#28a745; font-weight:bold;">再現性 | Steps to Reproduce</span>

Provide precise, step-by-step instructions to reproduce the behavior. This is the most critical part for quick resolution. If possible, include a minimal reproducible example (MRE).

<p align="center">
  <img src="https://i.postimg.cc/fR5K3D3f/reproduce-steps-static.png" alt="Reproduce Steps" style="max-width:200px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Clear steps lead to quick fixes.</figcaption>
</p>

1.  Go to '...'
2.  Click on '...'
3.  Scroll down to '...'
4.  See error / unexpected behavior

**Code Snippets (if applicable):**
```python
# Paste any relevant code that triggers the bug here
```

**Data (if applicable):**
-   If the bug depends on specific data, describe how to generate or obtain it.
-   Avoid sharing sensitive data; instead, provide synthetic data or steps to create similar data. (e.g., JSON payload, CSV snippet)

---

## <span style="color:#17a2b8; font-weight:bold;">✅ Expected Behavior</span>

A clear and concise description of what you expected to happen. How should the system behave instead?

---

## <span style="color:#6f42c1; font-weight:bold;">📸 Screenshots / Recordings (Optional)</span>

If applicable, add screenshots, GIFs, or short video recordings to help explain your problem. Visuals are often more effective than text descriptions.

-   Please blur any sensitive information.
-   For dynamic issues, a short GIF or video is highly encouraged. (e.g., Loom, Gyazo)

---

## <span style="color:#fd7e14; font-weight:bold;">🔍 Logs and Tracebacks</span>

Please paste any relevant error messages, console output, or traceback information. Ensure sensitive details are redacted.

```text
# Paste error messages or logs here
```

---

## <span style="color:#007bff; font-weight:bold;">🛡️ Troubleshooting Steps Taken (Optional)</span>

Have you tried any steps to fix or diagnose the issue yourself? Please describe them to avoid duplication of effort.

-   [ ] Checked API documentation for changes?
-   [ ] Restarted the application/service?
-   [ ] Cleared cache/data?
-   [ ] Updated dependencies to the latest version?
-   [ ] Tested on a different environment?
-   [ ] Consulted project README or FAQs?

---

## <span style="color:#20c997; font-weight:bold;">⚙️ Environment</span>

Please provide comprehensive details about your operating environment:

-   **Operating System (OS):** [e.g., Ubuntu 22.04, Windows 11, macOS Ventura]
-   **Python Version:** [e.g., 3.10.12]
-   **S&P 500 Predictor Version/Commit:** [e.g., `git rev-parse HEAD` or Docker image tag `2.0.0`]
-   **Relevant Library Versions:** (e.g., `pip freeze` output for `pandas`, `numpy`, `tensorflow`, `mlflow`, `yfinance`)
    ```text
    # Paste output of `pip freeze` or `conda list` if relevant
    ```
-   **Hardware (if relevant):** [e.g., CPU, GPU model, RAM, Disk Space]
-   **Deployment Method:** [e.g., Local (Conda/venv), Docker, Kubernetes, Colab, Cloud Platform (AWS/GCP/Azure)]
-   **Browser (for UI issues):** [e.g., Chrome 115, Firefox 116, Edge 117]
-   **Network Configuration (if relevant):** [e.g., Proxy settings, VPN, Firewall rules]

---

## <span style="color:#6610f2; font-weight:bold;">➕ Additional Context (Optional)</span>

Add any other relevant context about the problem here. This could include:

-   Recent changes to your system or configuration (e.g., OS update, new software).
-   What you were trying to achieve when the bug occurred (e.g., running a specific script, deploying a new model).
-   Any temporary workarounds you've discovered to mitigate the issue.
-   Network conditions or specific data characteristics that might be relevant.
-   Any unique setup or configuration that might differ from standard environments.

---

## <span style="color:#dc3545; font-weight:bold;">💡 Ideas/Suggestions for a Fix (Optional)</span>

If you have any thoughts on what might be causing the bug or how it could be fixed, please share them. Your insights are valuable and can help expedite the resolution!

---

## <span style="color:#ff8c00; font-weight:bold;">🚨 Before You Submit: Checklist</span>

<p align="center">
  <img src="https://i.postimg.cc/ctLtcPJ3/checklist-static.png" alt="Checklist Icon" style="max-width:100px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Ensure all critical info is included.</figcaption>
</p>

-   [x] I have read the [contribution guidelines](link_to_guidelines_if_available).
-   [x] I have checked for existing issues that might be similar.
-   [x] I have provided a clear and concise description of the bug.
-   [x] I have included precise steps to reproduce the issue.
-   [x] I have described the expected behavior.
-   [x] I have attached screenshots or relevant logs if applicable.
-   [x] I have provided comprehensive environment details.
-   [x] I have considered the severity and impact of this bug.