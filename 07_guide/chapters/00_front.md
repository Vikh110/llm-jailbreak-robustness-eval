---
title: "Jailbreak Robustness and Over-Refusal in Small Language Models"
subtitle: "A complete beginner's guide to the project: what we did, how, why, and what the results mean"
author: "Written for Vishwas Khandelwal - Individual Learning Plan project"
date: "Project carried out on 12 November 2026"
---

# How to read this guide {.unnumbered}

\gdef\guidehead{How to read this guide}

This guide explains one specific project from the ground up: *Black-Box Evaluation of Jailbreak Robustness and Over-Refusal in Small Instruction-Tuned Language Models*. It assumes you know nothing about language models, AI safety, statistics or the tools used. Every term is explained before it is used to explain something else.

The guide is a learning journey in seven parts:

1. **The big picture** - the question, why it matters, and what was produced.
2. **Foundations** - the ideas you need: language models, refusals, jailbreaks, judges, and a little statistics.
3. **Inputs and setup** - the data, models, tools and files.
4. **The workflow** - every step in the order it really happened, with the code that did it.
5. **The results** - each table and chart, how to read it, and what it does and does not show.
6. **Limitations** - where the approach can go wrong and what is still open.
7. **A worked example** - one request followed from input to final number.

A glossary, a map of the project files and the list of sources are at the end.

## The coloured boxes {.unnumbered}

The guide separates what is established from what is opinion. Boxes mark the difference.

::: recap
A blue "Chapter recap" box closes each chapter with the points to remember.
:::

::: plain
A green box restates an idea in everyday words or gives an everyday comparison.
:::

::: documented
A navy box gives a reason that was written down in the project's own files at the time the decision was made.
:::

::: interp
A purple box marks my reading of the evidence. It is a reasonable explanation, but the project did not test it.
:::

::: illustr
An amber box marks a made-up example used only for teaching. It is not project data.
:::

::: unverified
A red box marks something that could not be checked from the available material.
:::

## Who did what {.unnumbered}

Being clear about this matters for an honest account.

- **The plan** came from the Individual Learning Plan document written by Vishwas Khandelwal. It fixed the topic, the two models to test, the dataset, the number of prompts, the two kinds of prompt change, the judge model and the size of the audit.
- **The execution** happened in one working session on 12 November 2026. Claude, an AI assistant made by Anthropic, read the plan, set up the software, wrote and ran the code, wrote the project documents and built the presentation, with Vishwas approving the plan and making the open decisions.
- **The audit of 60 responses** was done by Claude, not by a human. Vishwas chose this. It is stated wherever the audit is used, because it affects how far the audit can be trusted.
- In this guide, **"we"** means the two of us working on the project together.

Every number in this guide was checked against the project's result files after writing.

**About the code.** The code shown is taken from the project's own files. Long lines have been re-wrapped to fit the page, and excerpts show only the part being explained.
