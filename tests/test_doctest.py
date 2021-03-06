# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

__author__ = "Patrick Kunzmann"

import pkgutil
import doctest
import os.path
import tempfile
from importlib import import_module
import numpy as np
import pytest
import biotite.structure.io as strucio
from .util import is_not_installed, cannot_import, cannot_connect_to


NCBI_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/"
RCSB_URL = "https://www.rcsb.org/"


@pytest.mark.parametrize("package_name, context_package_names", [
    pytest.param("biotite",                     []                           ),
    pytest.param("biotite.sequence",            []                           ),
    pytest.param("biotite.sequence.align",      ["biotite.sequence"]         ),
    pytest.param("biotite.sequence.phylo",      ["biotite.sequence"]         ),
    pytest.param("biotite.sequence.graphics",   ["biotite.sequence"],
                 marks=pytest.mark.skipif(
                    cannot_import("matplotlib"),
                    reason="Matplotlib is not installed")                    ),
    pytest.param("biotite.sequence.io",         ["biotite.sequence"]         ),
    pytest.param("biotite.sequence.io.fasta",   ["biotite.sequence"]         ),
    pytest.param("biotite.sequence.io.fastq",   ["biotite.sequence"]         ),
    pytest.param("biotite.sequence.io.genbank", ["biotite.sequence",
                                                 "biotite.database.entrez"],
                 marks=pytest.mark.skipif(
                    cannot_connect_to(NCBI_URL),
                    reason="NCBI Entrez is not available")                   ),
    pytest.param("biotite.sequence.io.gff",     ["biotite.sequence",
                                                 "biotite.sequence.io.fasta"],
                 marks=pytest.mark.filterwarnings("ignore:")                 ),
    pytest.param("biotite.structure",           ["biotite.structure.io"]     ),
    pytest.param("biotite.structure.graphics",  ["biotite.structure"],    
                 marks=pytest.mark.skipif(
                    cannot_import("matplotlib"),
                    reason="Matplotlib is not installed"),                   ),
    pytest.param("biotite.structure.io",        ["biotite.structure"]        ),
    pytest.param("biotite.structure.io.pdb",    ["biotite.structure",
                                                 "biotite"]                  ),
    pytest.param("biotite.structure.io.pdbx",   ["biotite.structure"]        ),
    pytest.param("biotite.structure.io.npz",    ["biotite.structure"]        ),
    pytest.param("biotite.structure.io.mmtf",   ["biotite.structure"]        ),
    pytest.param("biotite.structure.info",      ["biotite.structure"]        ),
    pytest.param("biotite.database.entrez",     [],                           
                 marks=pytest.mark.skipif(
                    cannot_connect_to(NCBI_URL),
                    reason="NCBI Entrez is not available")                   ),
    pytest.param("biotite.database.rcsb",       [],
                 marks=pytest.mark.skipif(
                    cannot_connect_to(RCSB_URL),
                    reason="RCSB PDB is not available")                      ),
    pytest.param("biotite.application",      ["biotite.application.clustalo",
                                              "biotite.sequence"],            
                 marks=pytest.mark.skipif(is_not_installed("clustalo"),
                                          reason="Software is not installed")),
    pytest.param("biotite.application.blast",   [],                          ),
    pytest.param("biotite.application.muscle",  ["biotite.sequence"],
                 marks=pytest.mark.skipif(is_not_installed("muscle"),
                                          reason="Software is not installed")),
    pytest.param("biotite.application.clustalo",["biotite.sequence"],
                 marks=pytest.mark.skipif(is_not_installed("clustalo"),
                                          reason="Software is not installed")),
    pytest.param("biotite.application.mafft",   ["biotite.sequence"],
                 marks=pytest.mark.skipif(is_not_installed("mafft"),
                                          reason="Software is not installed")),
    pytest.param("biotite.application.dssp",    ["biotite.structure"],
                 marks=pytest.mark.skipif(is_not_installed("mkdssp"),
                                          reason="Software is not installed")),
])
def test_doctest(package_name, context_package_names):
    """
    Run all doctest strings in all Biotite subpackages.
    """
    # Collect all attributes of this package and its subpackages
    # as globals for the doctests
    globs = {}
    mod_names = []
    #The package itself is also used as context
    for name in context_package_names + [package_name]:
        context_package = import_module(name)
        globs.update(
            {attr : getattr(context_package, attr)
             for attr in dir(context_package)}
        )
    
    # Add fixed names for certain paths
    globs["path_to_directory"]  = tempfile.gettempdir()
    globs["path_to_structures"] = "./tests/structure/data/"
    globs["path_to_sequences"]  = "./tests/sequence/data/"
    # Add frequently used modules
    globs["np"] = np
    # Add frequently used objects
    globs["atom_array_stack"] = strucio.load_structure(
        "./tests/structure/data/1l2y.mmtf"
    )
    globs["atom_array"] = globs["atom_array_stack"][0]
    
    # Adjust NumPy print formatting
    np.set_printoptions(precision=3, floatmode="maxprec_equal")

    # Run doctests
    package = import_module(package_name)
    results = doctest.testmod(
        package, extraglobs=globs,
        optionflags=doctest.ELLIPSIS | doctest.REPORT_ONLY_FIRST_FAILURE,
        verbose=False, report=False
    )
    try:
        assert results.failed == 0
    except AssertionError:
        print(f"Failing doctest in module {package}")
        raise