# Data dictionary: responses_locked.jsonl

240 records = 2 models x 20 prompt pairs x 2 prompt types x 3 conditions.

Content warning: the file contains model outputs to harmful requests (six lower-risk JBB-Behaviors categories only). It is published so that every reported number can be verified. Use it for safety research only; it is not training data.

| Field | Meaning |
|---|---|
| `response_id` | model_key|pair_id|prompt_type|condition (unique key) |
| `model_key / model_repo / model_revision` | target model, Hugging Face repo and pinned commit hash |
| `pair_id / jbb_index / category / behavior` | prompt pair id (P01-P20) and its JBB-Behaviors index, category and behaviour name |
| `prompt_type` | harmful or benign (matched pair) |
| `condition` | direct, role_framing or prefix_steering |
| `goal / target` | original JBB Goal and Target strings |
| `user_prompt` | the single user message actually sent (template applied to goal/target) |
| `rendered_prompt / rendered_prompt_sha256` | full text after the chat template (includes the default system prompt) and its hash |
| `response` | model output, special tokens removed |
| `n_prompt_tokens / n_new_tokens` | token counts |
| `finish_reason` | eos = model stopped by itself; length = hit the 256-token cap |
| `gen_seconds` | wall-clock generation time |
| `gen_settings / seed` | frozen generation settings and project seed |
| `env` | device, dtype, GPU, library versions, OS |
| `timestamp_utc` | generation time (UTC) |
