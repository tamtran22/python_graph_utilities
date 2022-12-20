import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class GraphData:
    x: np.ndarray
    edge_index: np.ndarray
    edge_attr: Optional[np.ndarray]

    @property
    def n_node(self):
        return self.x.shape[0]

    @property
    def n_edge(self):
        return self.edge_index.shape[1]

    @property
    def is_connected(self) -> bool:
        # x_index = np.arange(start=0, stop=self.n_node)
        # all_nodes_are_in_edges = np.all(np.isin(x_index, self.edge_index))
        return True

    @property
    def is_tree(self) -> bool:
        return (self.n_edge == self.n_node-1)

    def adjacency(self, u, v) -> bool:
        u_neighbor = np.where(self.edge_index[0] == u)[0]
        for _u in u_neighbor:
            if _u == v:
                return 1
        return 0
        

if __name__ == '__main__':
    n_node = 56891
    node_dim = 4
    n_edge = 302315
    edge_dim = 4
    x = np.random.random(size=(n_node, node_dim))
    edge_index = np.random.randint(low=0, high=n_node, size=(2,n_edge))
    edge_attr = np.random.random(size=(n_edge, edge_dim))
    
    data = GraphData(x, edge_index, edge_attr)