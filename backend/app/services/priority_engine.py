import networkx as nx

class PriorityEngine:
    def __init__(self):
        self.graph = nx.Graph()
        self._initialize_ner_grid()
        
    def _initialize_ner_grid(self):
        # Create a mock representation of the NER transit grid
        # Nodes: Settlements, Edges: Road Corridors
        
        # Nagaland
        self.graph.add_node("Dimapur", population=150000)
        self.graph.add_node("Medziphema", population=10000)
        self.graph.add_node("Zubza", population=5000)
        self.graph.add_node("Kohima", population=115000)
        self.graph.add_edge("Dimapur", "Medziphema", corridor_id="NH-29-NAGALAND", status="OPEN")
        self.graph.add_edge("Medziphema", "Zubza", corridor_id="NH-29-NAGALAND", status="OPEN")
        self.graph.add_edge("Zubza", "Kohima", corridor_id="NH-29-NAGALAND", status="OPEN")
        
        # Sikkim
        self.graph.add_node("Sevoke", population=20000)
        self.graph.add_node("Teesta Bazaar", population=8000)
        self.graph.add_node("Singtam", population=15000)
        self.graph.add_node("Gangtok", population=100000)
        self.graph.add_edge("Sevoke", "Teesta Bazaar", corridor_id="NH-10-SIKKIM", status="OPEN")
        self.graph.add_edge("Teesta Bazaar", "Singtam", corridor_id="NH-10-SIKKIM", status="OPEN")
        self.graph.add_edge("Singtam", "Gangtok", corridor_id="NH-10-SIKKIM", status="OPEN")
        
        # Source/Hub nodes for supply
        self.hub_nodes = ["Dimapur", "Sevoke"]

    def update_road_status(self, corridor_id: str, new_status: str):
        for u, v, data in self.graph.edges(data=True):
            if data.get("corridor_id") == corridor_id:
                self.graph[u][v]["status"] = new_status

    def calculate_triage_priority(self, days_isolated: dict = None):
        if days_isolated is None:
            days_isolated = {}
            
        # Create a subgraph with only OPEN or COMPROMISED roads (remove BLOCKED)
        active_edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get("status") != "BLOCKED"]
        active_graph = self.graph.edge_subgraph(active_edges).copy()
        
        # Include isolated nodes that lost all edges
        for node in self.graph.nodes():
            if node not in active_graph:
                active_graph.add_node(node, **self.graph.nodes[node])

        # Find connected components containing a hub
        safe_nodes = set()
        for component in nx.connected_components(active_graph):
            if any(hub in component for hub in self.hub_nodes):
                safe_nodes.update(component)
                
        isolated_nodes = set(self.graph.nodes()) - safe_nodes
        
        triage_list = []
        for node in isolated_nodes:
            population = self.graph.nodes[node].get("population", 1000)
            days = days_isolated.get(node, 1)
            vuln_factor = 1.2 # Base vulnerability
            alt_routes = 0 # No active routes to hub
            
            # IVI Formula: (Pop * (1 + 0.3 * Days) * Vuln) / (Alt + 0.1)
            ivi = (population * (1 + 0.3 * days) * vuln_factor) / (alt_routes + 0.1)
            
            triage_list.append({
                "settlement": node,
                "population": population,
                "days_isolated": days,
                "ivi_score": round(ivi, 2)
            })
            
        # Sort descending by IVI score
        triage_list.sort(key=lambda x: x["ivi_score"], reverse=True)
        return triage_list
