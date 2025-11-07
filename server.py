from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    global active_graph

    if not file.filename.lower().endswith(".json"):
        return {"Upload Error": "Invalid file type"}

    active_graph = create_graph_from_json(file)
    return {"Upload Success": file.filename}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph

    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    nodes = getattr(active_graph, "nodes", None)
    if not isinstance(nodes, dict) or start_node_id not in nodes or end_node_id not in nodes:
        return {"Solver Error": "Invalid start or end node ID."}

    start_node = nodes[start_node_id]
    end_node = nodes[end_node_id]

    dijkstra(active_graph, start_node)

    if end_node.dist is None or end_node.dist == float("inf"):
        return {"shortest_path": None, "total_distance": None}

    path = []
    cur = end_node
    while cur is not None:
        node_id = getattr(cur, "id", None) or getattr(cur, "name", None)
        path.append(str(node_id) if node_id is not None else str(cur))
        cur = getattr(cur, "prev", None)
    path.reverse()

    return {"shortest_path": path, "total_distance": float(end_node.dist)}

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)