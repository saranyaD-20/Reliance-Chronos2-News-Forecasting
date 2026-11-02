import pandas as pd

df = pd.read_csv("results/news_date_audit.csv")

duplicates = df[
    df.duplicated("DocumentIdentifier", keep=False)
].copy()

print("Duplicate rows:", len(duplicates))
print("Duplicate URLs:", duplicates["DocumentIdentifier"].nunique())

summary = duplicates.groupby("DocumentIdentifier").agg(
    occurrences=("DocumentIdentifier", "size"),
    timestamps=("DATE", "nunique"),
    tones=("V2Tone", "nunique"),
    source_files=("source_file", "nunique")
)

print("\nDuplicate URL analysis:")
print(summary.value_counts().to_string())

print("\nSample duplicate records:")
print(
    duplicates[
        ["DATE", "DocumentIdentifier", "V2Tone", "source_file"]
    ].head(10).to_string(index=False)
)

print("\nConflicting duplicate URLs:")
print(
    summary[
        (summary["timestamps"] > 1) |
        (summary["tones"] > 1)
    ].head(10).to_string()
)
