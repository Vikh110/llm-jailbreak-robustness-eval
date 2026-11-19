\part{The big picture}

# What this project is about

## The question in everyday words

Many people now use chat assistants: programs you can type a question to and get a written answer from. Behind each assistant is a **language model**, a computer program that has learned to produce text.

The companies that build these models try to teach them to say no to harmful requests. If you ask an assistant to write a scam email, a well-behaved one answers something like "I'm sorry, but I can't help with that." That answer is called a **refusal**.

This teaching can fail in two opposite ways.

1. **The model helps when it should refuse.** Sometimes a harmful request gets through if it is worded in a clever way. Wording a request so that the model drops its guard is called a **jailbreak**.
2. **The model refuses when it should help.** Sometimes a perfectly harmless request is refused because it merely sounds like a harmful one. This is called **over-refusal**.

A good assistant avoids both. A model that refuses everything is perfectly "safe" and completely useless. A model that helps with everything is useful and unsafe.

This project measured both failures on two small language models. It then asked a third question that turned out to matter a great deal: when a computer program does the scoring for us, can we trust its scores?

::: plain
Think of a security guard at a building. One kind of mistake is letting in someone who should not enter. The other kind is turning away a visitor with a valid appointment. You cannot judge the guard by counting only one kind of mistake. This project counted both, and then checked whether the person doing the counting was counting correctly.
:::

## Why it matters

Three reasons, from the practical to the general.

**Small models are everywhere.** The two models tested here are small enough to run on an ordinary laptop, and anyone can download them for free. Developers build them into apps, chatbots and tools. If their refusals are easy to switch off, every product built on them inherits that weakness.

**Safety claims rest on measurements.** When someone says "this model refuses harmful requests 95% of the time", that number came from a test. The number is only as good as the test: which requests were used, how they were worded, and who or what decided whether each answer was harmful. This project is a small, fully documented example of such a test, so that every one of those choices can be seen.

**Rules for AI depend on evaluation.** Governments and standards bodies increasingly ask for AI systems to be tested before release and for the results to be written down in a standard form. To judge whether such reports mean anything, you need to understand how an evaluation is built and where it can mislead. Chapter 6 explains this background.

## What we set out to do

The Individual Learning Plan described the project. In plain terms it asked for the following.

- Compare two small models: **Qwen2.5-0.5B-Instruct** and **Qwen2.5-1.5B-Instruct**.
- Use **20 harmful requests** and **20 matching harmless requests** from a public collection called **JBB-Behaviors**.
- Send each request in three ways: unchanged, and with two fixed jailbreak-style changes called **role framing** and **response-prefix steering**. That gives 240 responses.
- Measure four things: how often a model helps with a harmful request, how often it correctly refuses one, how often it helps with a harmless request, and how often it wrongly refuses one.
- Use a third model, **Qwen3Guard-Gen-0.6B**, as an automatic scorer, and check its reliability by auditing 60 responses.
- Produce a reproducible pipeline, results with confidence intervals, an analysis of the scorer's errors, a short **Safety Evaluation Card** and a presentation.

The plan also set honest boundaries. The project should stay valid even if no jailbreak succeeded. In that case it should report the robustness it saw, without claiming the models can never be jailbroken. And nothing new (no extra model, dataset or attack) was to be added once the experiment was fixed.

From the plan we wrote three research questions. They are quoted here as they appear in the project file `01_protocol/01_research_question_and_threat_model.md`.

| | Research question |
|---|---|
| RQ1 Robustness | How often do the two models produce harmful compliance on 20 lower-risk harmful requests, asked directly and under two fixed prompt transformations? |
| RQ2 Over-refusal | How often do the same models refuse the 20 matched benign requests under the same three conditions? |
| RQ3 Evaluator reliability | How reliable is Qwen3Guard-Gen-0.6B as an automated judge of refusal and harmful compliance, measured against a 60-response rubric audit? |

A fourth, secondary question was about governance: what can results like these support, and what can they not support?

Do not worry about the unfamiliar words yet. "Harmful compliance", "transformation", "rubric" and "judge" are all explained in Part II.

## What was produced

By the end of the project the folder contained:

- written rules for choosing the requests, the labels and the scoring (`01_protocol/`);
- the 240 responses, stored with a tamper-check (`02_data/`);
- the code that produced and analysed them (`03_pipeline/`);
- the results as tables, charts and an error analysis (`04_results/`);
- a report and a Safety Evaluation Card (`05_report/`);
- a 20-slide presentation in its own design with the Frankfurt School logo (13 slides for the talk, 7 backup slides), which is the only item that is submitted (`06_presentation/`);
- this guide (`07_guide/`).

## A preview of what we found

This section jumps ahead. None of this was known when the work started; it is what the data showed at the end. Part V explains each point in full and Part VI explains how far each can be trusted.

1. **One short instruction removed almost all refusals.** Asked directly, the two models correctly refused 34 of 40 harmful requests. When the request also said "start your response with exactly these words: 'Sure, here is ...'", they refused 1 of 40.
2. **Pretending to be a character did little.** Wrapping the request in a role-play story did not clearly change behaviour.
3. **Over-refusal exists.** Asked directly, the larger model refused 6 of 20 harmless requests and the smaller one 2 of 20. Most refused requests were about conspiracy theories.
4. **The automatic scorer over-counted harm.** Its "this response refuses" signal was reliable. Its "this response is unsafe" signal was not: of 14 audited responses it called unsafe, the audit found harmful content in 6.

The fourth point changes how the first must be read. The models did stop refusing. But about half of the audited "successful jailbreaks" contained nothing harmful: the model began with "Sure, here is ..." and then wrote something generic, something off-topic, or even the opposite of what was asked.

::: recap
- The project tests two small chat models for two opposite failures: helping with harmful requests (especially when tricked) and refusing harmless ones.
- It also tests the automatic scorer, because a measurement is only as good as the thing doing the measuring.
- The plan fixed the models, the data, the sizes (20 + 20 requests, 240 responses, 60 audited) and the outputs.
- The headline findings are previewed above, but they were results of the work, not assumptions going in.
:::
