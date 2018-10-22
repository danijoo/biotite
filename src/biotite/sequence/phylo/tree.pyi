# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

from typing import overload, List, Tuple, Iterable, Optional
import numpy as np
from ...copyable import Copyable


class Tree(Copyable):
    root: TreeNode
    leaves: List[TreeNode]
    def __init__(self, root: TreeNode) -> None: ...
    def get_distance(self, index1: int, index2: int) -> float: ...
    def to_newick(
        self,
        labels: Optional[Iterable[str]] = None,
        include_distance: bool = True
    ) -> str: ...
    def __str__(self) -> str: ...


class TreeNode:
    index: Optional[int]
    distance: Optional[float]
    parent: Optional[TreeNode]
    childs: Optional[Tuple[TreeNode,TreeNode]]
    @overload
    def __init__(
        self,
        child1: TreeNode,
        child2: TreeNode,
        child1_distance: float,
        child2_distance: float
    ) -> None: ...
    @overload
    def __init__(
        self,
        index: int
    ) -> None: ...
    def copy(self) -> TreeNode: ...
    def is_leaf(self) -> bool: ...
    def is_root(self) -> bool: ...
    def as_root(self) -> None: ...
    def distance_to(self, node: TreeNode) -> float: ...
    def lowest_common_ancestor(self, node: TreeNode) -> TreeNode: ...
    def get_indices(self) -> List[int]: ...
    def get_leaves(self) -> List[TreeNode]: ...
    def get_leaf_count(self) -> int: ...
    def to_newick(
        self,
        labels: Optional[Iterable[str]] = None,
        include_distance: bool = True
    ) -> str: ...
    def __str__(self) -> str: ...


class TreeError(Exception):
    ...