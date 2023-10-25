import click 
from pathlib import Path
import pandas as pd
from tqdm import tqdm

thispath = Path(__file__).resolve()

print()

def bash_file(name_experiment):
    """
    Function to create a .txt file ready to be run as elastix file in the console to perform the registration of
    a set of landmarks using the transformation used to perform the registration using transformix command.
    Parameters
    ----------
    name_experiment: Name of the bash file

    Returns
    -------
    A .sh bash file to perform the preprocessing with PyHIST
    """
    Path(thispath.parent.parent / f'bash_files').mkdir(exist_ok=True, parents=True)

    datadir = Path("data/raw/scannet_dataset/scans_test")

    ply_files = [i for i in datadir.rglob("*2.ply")]


    with open(
            Path(thispath.parent.parent / Path(
                f"bash_files/bash_segmentator_{name_experiment}.sh")), 'w') as f:
        f.write(
            f"#!/bin/bash \n\n" 
        )

        for file in tqdm(ply_files):
            
            bash_line = f"third_party/ScanNet/Segmentator/segmentator " \
                        f"{file}\n"
            f.write(bash_line)


@click.command()
@click.option(
    "--name",
    default="Example",
    prompt="Name of the bash file",
    help=
    "Choose name for the bash_file",
)
def main(name):
        bash_file(name)


if __name__ == "__main__":
    main()
