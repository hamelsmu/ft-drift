# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_cli.ipynb.

# %% auto 0
__all__ = ['rich_feat_imp', 'main']

# %% ../nbs/04_cli.ipynb 2
import time
from fastcore.script import call_parse
from .model import prep_data, model
from rich.progress import Progress
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.bar import Bar

# %% ../nbs/04_cli.ipynb 3
def rich_feat_imp(df):
    "Render a feature importance dataframe ad a rich table."
    max_value = max(df.Importance.values)

    # Create a Rich Table
    table = Table(header_style="bold")
    table.add_column("n", justify="left")
    table.add_column("Feature", justify="left")
    table.add_column("Importance", justify="left")

    # Populate the table
    for idx, d in df.iterrows():
        bar = Bar(size=max_value, begin=0, end=d.Importance, color="dark_magenta")
        table.add_row(str(idx+1), d.Feature, bar)

    rprint(table)

# %% ../nbs/04_cli.ipynb 4
@call_parse
def main(f1:str, #jsonl file #1
         f2:str, #jsonl file #2
        ):
    "Compare two openai jsonl files."
    with Progress(transient=True) as progress:
        t = progress.add_task("[red]Processing", total=5)
        progress.console.print("[bold]Parsing Data[/bold]")
        df = prep_data(f1,f2)
        progress.update(t, advance=2)
        progress.console.print("[bold]Detecting Drift[/bold]")
        clf = model(df)
        progress.update(t, advance=2)
        if clf.roc_auc > 0.60:
            rprint(':x: Drift detected ... showing 15 most predictive tokens:')
            rich_feat_imp(clf.top_features.head(15))
        else:
            rprint(':white_check_mark: No significant drift detected')
        progress.update(t, advance=1)
        time.sleep(0.2)
