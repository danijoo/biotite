# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

import glob
from os.path import join
import numpy as np
import pytest
import biotite.structure as struc
import biotite.structure.info as strucinfo
from biotite.structure.io import load_structure, save_structure
import biotite.structure.io.mmtf as mmtf
from .util import data_dir


def test_mass():
    """
    Test whether the mass of a residue is the same as the sum of the
    masses of its contained atoms.
    """
    array = load_structure(join(data_dir, "1l2y.mmtf"))[0]
    _, res_names = struc.get_residues(array)
    water_mass = strucinfo.mass("H") * 2 + strucinfo.mass("O") 
    # Mass of water must be subtracted
    masses = [strucinfo.mass(res_name) - water_mass for res_name in res_names]
    # C-terminus normally has additional oxygen atom
    masses[-1] += strucinfo.mass("O")
    ref_masses = [strucinfo.mass(res) for res in struc.residue_iter(array)]
    # Up to three additional/missing hydrogens are allowed
    # (protonation state)
    mass_diff = np.abs(np.array(
        [mass - ref_mass for mass, ref_mass in zip(masses, ref_masses)]
    ))
    assert (mass_diff // strucinfo.mass("H") <= 3).all()
    assert np.allclose((mass_diff % strucinfo.mass("H")), 0, atol=5e-3)


@pytest.mark.parametrize("path", glob.glob(join(data_dir, "*.mmtf")))
def test_bonds(path):
    """
    Test whether the bond data is consistent with the content of MMTF
    files.
    """
    bond_data = strucinfo.get_bond_dataset()
    mmtf_file = mmtf.MMTFFile()
    mmtf_file.read(path)
    for group in mmtf_file["groupList"]:
        group_name = group["groupName"]
        atom_names = group["atomNameList"]
        bond_indices = group["bondAtomList"]
        bond_orders = group["bondOrderList"]
        for i in range(0, len(bond_indices), 2):
            atom1 = atom_names[bond_indices[i]]
            atom2 = atom_names[bond_indices[i+1]]
            order = bond_orders[i//2]
            assert strucinfo.get_bond_order(group_name, atom1, atom2) == order
            assert frozenset((atom1, atom2)) \
                   in strucinfo.get_bonds_for_residue(group_name)
            assert frozenset((atom1, atom2)) \
                   in bond_data[group_name]


def test_protOr_radii():
    """
    Assert that ProtOr VdW radii (except hydrogen) can be calculated for
    all atoms in the given structure, since the structure (1GYA)
    does only contain standard amino acids after the removal of
    glycosylation.
    This means, that none of the resulting radii should be the default
    value, that is used for atoms where the ProtOr radius cannot be
    calculated.
    """
    from biotite.structure.info.radii import _PROTOR_DEFAULT as default_radius
    array = load_structure(join(data_dir, "1gya.mmtf"))
    array = array[..., array.element != "H"]
    array = array[..., struc.filter_amino_acids(array)]
    for res_name, atom_name in zip(array.res_name, array.atom_name):
        radius = strucinfo.vdw_radius_protor(res_name, atom_name)
        assert isinstance(radius, float)
        print(res_name, atom_name)
        assert radius != default_radius


def test_protor_radii_invalid():
    from biotite.structure.info.radii import _PROTOR_DEFAULT as default_radius
    with pytest.raises(ValueError):
        # Expect raised exception for hydrogen atoms
        strucinfo.vdw_radius_protor("FOO", "H1")
    with pytest.raises(KeyError):
        # Expect raised exception when a residue does not contain an atom
        assert strucinfo.vdw_radius_protor("ALA", "K") == default_radius
    # For all other unknown radii expect default radius
    assert strucinfo.vdw_radius_protor("HOH", "O") == default_radius


def test_single_radii():
    assert strucinfo.vdw_radius_single("N") == 1.55


def test_full_name():
    assert strucinfo.full_name("Ala").upper() == "ALANINE"
    assert strucinfo.full_name("ALA").upper() == "ALANINE"


def test_link_type():
    assert strucinfo.link_type("Ala").upper() == "L-PEPTIDE LINKING"
    assert strucinfo.link_type("ALA").upper() == "L-PEPTIDE LINKING"