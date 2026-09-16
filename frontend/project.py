"""Inspect a CSV dataset and create basic missing-value/rating reports."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


RATING_COLUMN = "Aggregate rating"


def analyze_dataset(dataset_path: Path, output_dir: Path, show_plots: bool = False) -> None:
	"""Print basic statistics and save plots for ``dataset_path``."""
	if not dataset_path.is_file():
		raise FileNotFoundError(
			f"Dataset not found: {dataset_path}\n"
			"Pass the CSV path with --dataset, for example: "
			"python frontend/project.py --dataset path/to/Dataset.csv"
		)

	df = pd.read_csv(dataset_path)
	print("Shape:", df.shape)
	print("Rows:", df.shape[0])
	print("Columns:", df.shape[1])
	print("\nPreview:")
	print(df.head())
	print("\nMissing values:")
	print(df.isna().sum())
	print("\nMissing percentages:")
	print((df.isna().sum() / len(df) * 100).round(2))
	print("\nData types:")
	print(df.dtypes)

	if RATING_COLUMN not in df.columns:
		raise ValueError(
			f"Required column {RATING_COLUMN!r} was not found. "
			f"Available columns: {', '.join(map(str, df.columns))}"
		)

	clean_df = df.dropna().copy()
	clean_df[RATING_COLUMN] = pd.to_numeric(
		clean_df[RATING_COLUMN], errors="coerce"
	)
	clean_df = clean_df.dropna(subset=[RATING_COLUMN])
	if clean_df.empty:
		raise ValueError(f"Column {RATING_COLUMN!r} contains no numeric values.")

	output_dir.mkdir(parents=True, exist_ok=True)

	plt.figure(figsize=(10, 5))
	sns.heatmap(df.isna(), cbar=False, cmap="viridis")
	plt.title("Missing Values Heatmap")
	plt.tight_layout()
	plt.savefig(output_dir / "missing_values.png", dpi=150)
	if show_plots:
		plt.show()
	plt.close()

	rating_counts = clean_df[RATING_COLUMN].value_counts().sort_index()
	print("\nAggregate rating counts:")
	print(rating_counts)
	print("\nAggregate rating percentages:")
	print((rating_counts / rating_counts.sum() * 100).round(2))

	plt.figure(figsize=(10, 5))
	sns.countplot(x=RATING_COLUMN, data=clean_df, color="steelblue")
	plt.title("Distribution of Aggregate Rating")
	plt.xlabel("Rating")
	plt.ylabel("Count")
	plt.xticks(rotation=45)
	plt.tight_layout()
	plt.savefig(output_dir / "aggregate_rating_distribution.png", dpi=150)
	if show_plots:
		plt.show()
	plt.close()


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument(
		"--dataset",
		type=Path,
		default=Path(__file__).with_name("Dataset.csv"),
		help="Path to the CSV file (default: frontend/Dataset.csv)",
	)
	parser.add_argument(
		"--output-dir",
		type=Path,
		default=Path(__file__).with_name("analysis_output"),
		help="Directory for generated plots",
	)
	parser.add_argument(
		"--show-plots",
		action="store_true",
		help="Display plots in addition to saving them",
	)
	args = parser.parse_args()
	try:
		analyze_dataset(args.dataset, args.output_dir, args.show_plots)
	except (FileNotFoundError, ValueError) as error:
		parser.error(str(error))


if __name__ == "__main__":
	main()