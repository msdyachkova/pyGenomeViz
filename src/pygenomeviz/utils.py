from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.request import urlretrieve

from Bio import Entrez

DATASETS = {
    "phage": [
        "JX128258.1.gbk",
        "MH051335.1.gbk",
        "MH816966.1.gbk",
        "MK373776.1.gbk",
        "link.tsv",
    ],
}


def load_dataset(name: str) -> Tuple[List[Path], List[Link]]:
    """Load pygenomeviz example dataset

    Datasets are downloaded from https://github.com/moshi4/pygenomeviz-data
    and cached in local directory ('~/.cache/pygenomeviz').

    Parameters
    ----------
    name : str
        Dataset name ("phage")

    Returns
    -------
    gbk_files, links : Tuple[List[Path], List[Link]]
        Genbank files, Links
    """
    # Check specified name dataset exists or not
    if name not in DATASETS.keys():
        err_msg = f"'{name}' dataset not found."
        raise ValueError(err_msg)

    # Dataset cache local directory
    package_name = __name__.split(".")[0]
    cache_base_dir = Path.home() / ".cache" / package_name
    target_cache_dir = cache_base_dir / name
    os.makedirs(target_cache_dir, exist_ok=True)

    # Dataset GitHub URL
    base_url = "https://raw.githubusercontent.com/moshi4/pygenomeviz-data/master/"
    target_url = base_url + f"{name}/"

    # Download & cache dataset
    gbk_files: List[Path] = []
    links: List[Link] = []
    for filename in DATASETS[name]:
        file_url = target_url + filename
        file_path = target_cache_dir / filename
        if not file_path.exists():
            urlretrieve(file_url, file_path)
        if file_path.suffix in (".gb", ".gbk", ".gbff"):
            gbk_files.append(file_path)
        else:
            links = Link.load(file_path)

    return gbk_files, links


@dataclass
class Link:
    ref_name: str
    ref_start: int
    ref_end: int
    query_name: str
    query_start: int
    query_end: int
    identity: float

    @staticmethod
    def load(link_file: Path) -> List[Link]:
        """Load genome-to-genome link file

        Parameters
        ----------
        link_file : Path
            Genome-to-genome link file

        Returns
        -------
        links : List[Link]
            Link list
        """
        with open(link_file) as f:
            reader = csv.reader(f, delimiter="\t")
            next(reader)
            links: List[Link] = []
            for row in reader:
                rname, rstart, rend = row[7], int(row[0]), int(row[1])
                qname, qstart, qend = row[8], int(row[2]), int(row[3])
                ident = float(row[6])
                links.append(Link(rname, rstart, rend, qname, qstart, qend, ident))
        return links


def fetch_genbank_from_accid(accid: str, email: Optional[str] = None) -> TextIOWrapper:
    """Fetch genbank text from 'Accession ID'

    Parameters
    ----------
    accid : str
        Accession ID
    email : str, optional
        Email address to notify download limitation (Required for bulk download)

    Returns
    -------
    TextIOWrapper
        Genbank data

    Examples
    --------
    >>> gbk_fetch_data = download_genbank_from_accid("JX128258.1")
    """
    Entrez.email = "" if email is None else email
    return Entrez.efetch(
        db="nucleotide",
        id=accid,
        rettype="gbwithparts",
        retmode="text",
    )
