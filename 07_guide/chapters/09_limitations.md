\part{Limitations}

# Limitations and failure modes

Every step of the project involved a choice, and every choice has a way of going wrong. This chapter goes through them in the order of the pipeline. For each it says what can go wrong, why, how it affects the conclusions, and what is still open.

A **failure mode** is a specific way in which a method can give a wrong or misleading answer.

## The sample of requests

### Only 20 requests per cell

**What can go wrong.** With so few items, chance plays a large part in every number.

**Why.** If one more request had gone the other way, a rate would move by five percentage points. The Wilson intervals show this: across the table they are between 16 and 39 percentage points wide.

**Effect on the conclusions.** Only very large effects can be established. The prefix-steering effect is large enough. Everything else (role framing, the difference between the two models, differences between categories) is description, not proof.

**Still open.** Whether role framing has a moderate effect; whether the larger model really refuses more.

### A deliberately mild set of requests

**What can go wrong.** A reader might take the results as describing "harmful requests" in general.

**Why.** Ten rules removed 68 of the 100 behaviours, including everything about violence, weapons, malicious code, sexual content and hate. What remains is financial, informational and regulatory wrongdoing.

**Effect on the conclusions.** The results apply to lower-risk requests only. Models are usually trained to refuse the most serious requests more firmly, so their behaviour there could be quite different. The project cannot say.

### The selection rules are the project's own

**What can go wrong.** A different, equally reasonable set of rules would give a different set of 20.

**Why.** The rules were written for this project. Some lines are judgement calls.

**Effect on the conclusions.** Limited, because the choice within the eligible pool was random and seeded, and the rules were fixed before any model was run. But the exact rates would differ with another selection.

### Borderline harmless requests

**What can go wrong.** A refusal that a careful human would also consider reasonable is counted as over-refusal.

**Why.** The dataset's authors warn that some benign behaviours are borderline. Two of the benign twins in our set, an email asking a user for login details and a template for automated product reviews, are close to things a cautious assistant might decline.

**Effect on the conclusions.** Over-refusal may be somewhat overstated. Against that, the requests refused most often were the clearly harmless ones that ask to explain or discuss a belief.

## The attacks

### Two fixed wordings, tried once

**What can go wrong.** The results are read as "role-play does not work" or "prefix steering always works".

**Why.** Each transformation is a single piece of wording. Real attackers try many wordings, retry, and adapt.

**Effect on the conclusions.** For role framing, a null result on one wording says little. For prefix steering, success with the very first simple wording is, if anything, more worrying.

### Black-box only

**What can go wrong.** The measured attack success is taken as the worst case.

**Why.** The attacker in our threat model can only send one message. With public weights, a real attacker can write the start of the answer directly, use optimisation methods, or retrain the model to remove refusals.

**Effect on the conclusions.** Attack success is a **lower bound** on what a determined attacker could achieve.

## Generation

### One greedy response per request

**What can go wrong.** We describe "the model's behaviour" from a single, non-random answer.

**Why.** Greedy decoding was chosen for repeatability. The models are shipped with random sampling at temperature 0.7, under which the same request can be refused one time and answered the next.

**Effect on the conclusions.** We measured one fixed behaviour, not the spread of behaviours a real user would meet. A request that was refused here might be answered some of the time in real use, and the reverse.

**Still open.** How much the rates vary from sample to sample.

### Answers cut off at 256 tokens

**What can go wrong.** A response is labelled on its first 200 words, and what would have followed is unknown.

**Why.** 145 of the 240 responses reached the limit.

**Effect on the conclusions.** It could push either way. A response that begins harmlessly might have turned harmful later, or a response that begins with an agreeing sentence might have gone on to refuse. The audit can only speak about the text that exists.

### Results tied to one machine

**What can go wrong.** Someone repeats the experiment on different hardware and gets slightly different texts.

**Why.** The bfloat16 number format rounds differently on different chips, and a tiny difference can change a token.

**Effect on the conclusions.** None on our numbers, which are locked. But "repeatable" here means repeatable on the same hardware and software versions.

## Scoring

### The judge over-counts harm

**What can go wrong.** Harmful-compliance rates are reported that are far too high.

**Why.** The judge appears to react to an agreeing opening and to sensitive topics. In the audited sample 8 of its 14 Unsafe flags were false alarms.

**Effect on the conclusions.** This is the largest single caveat in the project. All harmful-compliance figures are **upper bounds**. The project caught this only because it audited the judge.

### Choices built into the labelling rule

**What can go wrong.** A different rule would change the counts.

**Why.** Three choices were made: "Unsafe wins" over the refusal flag; the middle level, Controversial, does not count as harmful; and the judge sees the original request, not the transformed one.

**Effect on the conclusions.** Small, as far as was checked. Counting Controversial changes the overall count from 50 to 53 of 120. Only one response was both Unsafe and a refusal. In the pilot, showing the judge the transformed message changed no outcome label.

## The audit

### The auditor is an AI model

**What can go wrong.** The audit is treated as the truth, when it is itself a fallible opinion.

**Why.** The 60 labels were assigned by Claude following the rubric, not by a person.

**Effect on the conclusions.** The reliability figures describe agreement between a weaker automatic scorer and a stronger one. They are not accuracy against human judgement. The pattern in the disagreements is concrete and can be checked by reading the 11 cases, which are all listed and whose texts are in the locked dataset. But a human audit could come out differently in places.

### One auditor, sixty responses, some close calls

**What can go wrong.** A handful of debatable labels shifts the reliability figures.

**Why.** With one auditor there is no measure of how consistent the labelling is. With 30 responses to harmful requests, each label is worth more than three percentage points of agreement. And some calls were close. The clearest example is audit item A12, a general but on-topic plan for exploiting regulatory loopholes, which was labelled harmful and noted as borderline. Had it been labelled the other way, the judge would have 9 false alarms and the audit 5 harmful responses.

**Effect on the conclusions.** The exact figures (precision 6 of 14, kappa 0.44) are soft. The direction of the finding (many false alarms, no misses) would survive a few changed labels.

### The auditor was not fully independent

**What can go wrong.** The audit shares blind spots with the rest of the project.

**Why.** The same AI model wrote the rubric, ran the pilot, and did the audit. The blinding hid the model, the condition and the judge's label, but the opening words of a response often hint at the condition.

**Effect on the conclusions.** An auditor who knows that "Sure, here is ..." responses are the interesting case might, without intending to, read them more sceptically. The safeguard was the written rubric, fixed beforehand, and the fact that the audit labels were sealed before the judge's labels existed.

## Statistics

### What the intervals assume

**What can go wrong.** The intervals are read as more exact than they are.

**Why.** A confidence interval assumes the items are something like a random sample from a larger population. Our 20 requests were drawn from 32 eligible behaviours in one dataset, not from all possible harmful requests.

**Effect on the conclusions.** The intervals are a fair guide to how much the numbers could move with a different draw of similar requests. They do not cover the uncertainty from using this dataset and these rules at all.

### Many comparisons, some made after the fact

**What can go wrong.** A pattern found by slicing the data many ways is mistaken for a discovery.

**Why.** There are 21 paired tests, and the breakdowns by category and by condition within the audit were made after seeing the results.

**Effect on the conclusions.** Only the prefix-steering tests pass the strict threshold. The exploratory breakdowns explain the main findings but should not be treated as findings in their own right.

## Interpretation

### Harm was judged by content, not by consequence

**What can go wrong.** "Harmful compliance" is read as "caused harm" or "would help a criminal".

**Why.** The rubric asks whether the content serves the harmful goal. It does not ask whether the content is accurate, or better than what a search engine would give. Much of what these small models wrote was general or wrong.

**Effect on the conclusions.** Even the audit's lower rate probably overstates practical risk.

### No explanation of the mechanism

**What can go wrong.** The suggested explanations in this guide are taken as established.

**Why.** The project observed behaviour from the outside. It did not examine what happens inside the models.

**Effect on the conclusions.** Statements about *why* prefix steering works, or why the judge raises false alarms, are interpretations. They are marked as such throughout.

### Two models from one family

**What can go wrong.** The results are generalised to "small models" or to models from other makers.

**Effect on the conclusions.** They describe Qwen2.5 at two sizes, with one judge. Nothing more.

## The process itself

Two further points belong in an honest account.

- **The work was done in one day, largely by an AI assistant.** The code was verified by a second program, and the outputs were checked against the requirement lists. But no second person reviewed the code or the documents.
- **Background reading was verified, not studied.** The papers were searched for the specific facts used. The two BlueDot courses were checked only at the level of their public pages.

## What remains unresolved

1. How much real harmful content prefix steering produces. The audit's estimate rests on 10 responses.
2. Whether role framing has a moderate effect.
3. Whether larger models in this family refuse more, in both directions.
4. How much behaviour varies under the shipped sampling settings.
5. Why a formatting instruction overrides refusal in these models.
6. How a human audit would compare with the AI audit.
7. Whether other judges make the same kind of error.

::: proposal
The project report lists what could be done next. None of it was done in this project.

- **More data:** all 100 pairs, several sampled responses per request, a third model size.
- **Graded scoring:** a StrongREJECT-style score for how specific and convincing a response is, in place of a yes/no Unsafe label.
- **A judge comparison:** larger Qwen3Guard models, Llama Guard and a large language model as judge, all measured against human labels from at least two people.
- **Stronger threat models:** pre-filling the answer, several turns, adaptive attacks.
- **Defences and their cost:** a stricter system prompt, or a guard model used as a filter, measuring the change in harmful compliance and in over-refusal together.
- **Mechanism:** a look inside the model at why the format of the answer overrides refusal.
:::

::: recap
- The biggest limits are the small sample, the mild request set, the weak attacks, and a judge that over-counts.
- Attack success is a **lower bound** (weak attacks); harmful-compliance rates are **upper bounds** (generous judge). The truth for these requests lies somewhere the project cannot pin down.
- The audit is one AI model's reading of 60 responses, with some close calls.
- Explanations of *why* things happened are interpretations, not findings.
:::
