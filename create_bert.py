from pathlib import Path


NOTEBOOK = Path("08_bert_model.ipynb")
REQUIRED_FILES = [
    Path("data/reviews_preprocessed.csv"),
    Path("features/train_idx.npy"),
    Path("features/val_idx.npy"),
    Path("features/test_idx.npy"),
]


def main():
    """Check that the BERT notebook can reuse the official data split."""
    missing = [str(path) for path in REQUIRED_FILES if not path.exists()]
    if not NOTEBOOK.exists():
        missing.append(str(NOTEBOOK))

    if missing:
        print("Missing required files:")
        for item in missing:
            print(f"- {item}")
        raise SystemExit(1)

    print("BERT notebook is present and can reuse the official split files.")
    print("Run 08_bert_model.ipynb directly; this script no longer overwrites it.")


if __name__ == "__main__":
    main()
