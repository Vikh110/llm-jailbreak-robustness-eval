"""Download the dataset and the three models at the pinned revisions in config.py.

Everything goes into models_cache/ (git-ignored, about 5 GB), in the standard
Hugging Face cache layout that the other scripts read. Needed only to re-run
generation/judging or to hash the model weights (`07_verify.py` without
`--skip-weights`).

Usage
  python 00_download_models.py                 # dataset + 2 target models + judge
  python 00_download_models.py --weights-only  # only the *.safetensors files (enough for the weight check)
"""
import argparse

from huggingface_hub import snapshot_download

import config as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights-only", action="store_true", help="download only the weight files of the three models")
    args = ap.parse_args()

    if not args.weights_only:
        path = snapshot_download(C.DATASET["repo"], repo_type="dataset", revision=C.DATASET["revision"], cache_dir=C.HF_CACHE)
        print("dataset", C.DATASET["repo"], "->", path)
    for spec in [*C.TARGET_MODELS.values(), C.JUDGE_MODEL]:
        path = snapshot_download(spec["repo"], revision=spec["revision"], cache_dir=C.HF_CACHE,
                                 allow_patterns=["*.safetensors"] if args.weights_only else None)
        print("model", spec["repo"], "@", spec["revision"][:12], "->", path)


if __name__ == "__main__":
    main()
