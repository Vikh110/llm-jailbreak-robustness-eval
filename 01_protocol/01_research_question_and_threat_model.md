# Research question and threat model

Project: *Black-Box Evaluation of Jailbreak Robustness and Over-Refusal in Small Instruction-Tuned Language Models* (Individual Learning Plan, Phase 1).

## Research questions

**RQ1 - Robustness.** Under a single-turn, prompt-only black-box threat model, how often do Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct produce harmful compliance on 20 lower-risk JBB-Behaviors requests, asked directly and under two fixed prompt transformations (role framing, response-prefix steering)?

**RQ2 - Over-refusal.** How often do the same models refuse the 20 matched benign requests under the same three conditions?

**RQ3 - Evaluator reliability.** How reliable is Qwen3Guard-Gen-0.6B as an automated judge of refusal and harmful compliance, measured against a 60-response rubric audit?

**Governance question (secondary).** What can results of this kind support, and not support, in independent testing, system cards and pre-deployment assurance?

The study stays valid if no transformation produces a successful jailbreak: in that case the finding is the observed robustness under this threat model, not a claim of general jailbreak resistance.

## System under test

Model weights + the model's default chat template + its default system prompt + greedy decoding. No external guardrail, filter or moderation layer. One response per model x prompt x condition.

## Threat model

| Element | Assumption in this study |
|---|---|
| Adversary | A low-resource user of a chat assistant built on the model |
| Access | Query-only ("black-box"): one user message per conversation |
| Cannot do | Set or change the system prompt; pre-fill the assistant turn; read weights, logits or gradients; change decoding parameters; fine-tune |
| Knowledge | Public, generic jailbreak templates only; nothing model-specific |
| Effort | One attempt per request: no retries, no iteration, no adaptive search |
| Goal | Obtain content that substantively fulfils a policy-violating request |
| Language | English, single turn |

## Out of scope (and why it matters)

- White-box optimisation attacks (e.g. GCG), automated iterative attacks (e.g. PAIR), multi-turn, multilingual and encoding attacks.
- Assistant-turn pre-fill and system-prompt manipulation.
- Fine-tuning or weight editing. For open-weight models this is the realistic ceiling of misuse, so results here are a **lower bound** on what a determined adversary can obtain, not an upper bound.

Why black-box although the weights are open: it mirrors what an independent evaluator or a downstream deployer with interface-only access can test, and it keeps the pipeline identical for open and closed models.
