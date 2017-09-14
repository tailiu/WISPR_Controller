import networkx as nx
import fnss

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController

def from_autonetkit(topology):
    """Convert an AutoNetKit graph into an FNSS Topology object.
    
    The current implementation of this function only renames the weight
    attribute from *weight* to *ospf_cost*
    
    Parameters
    ----------
    topology : NetworkX graph
        An AutoNetKit NetworkX graph
        
    Returns
    -------
    fnss_topology : FNSS Topology
        FNSS topology        
    """
    topology = topology.copy()
    fnss.rename_edge_attribute(topology, 'ospf_cost', 'weight')
    return topology


def main():
    G = nx.Graph()
    G = nx.read_gpickle("mendocino.gpickle")

    fnss_topo = from_autonetkit(G)

    node_types = nx.get_node_attributes(fnss_topo, 'type')

    hosts = []
    switches = []

    for node in fnss_topo.nodes():
        nodetype = G.node[node]['type']
        if nodetype == 'cpe':
            hosts.append(node)
        else:
            switches.append(node)


    mn_topo = fnss.to_mininet(fnss_topo, switches=switches, hosts=hosts, relabel_nodes=True)

    net = Mininet(topo=mn_topo, link=TCLink, controller=OVSController)
    net.start()

    # Dump host connections
    dumpNodeConnections(net.hosts)

    # Test network connectivity
    net.pingAll()

    # Test bandwidth between nodes
    h1, h8 = net.get('h1', 'h8')
    net.iperf((h1, h8))

    # Stop Mininet
    net.stop()


if __name__ == "__main__":
    main()