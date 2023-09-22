from http.server import BaseHTTPRequestHandler
from state import Player
import json
from module.ai import AI
from module.db import DB, DBs
from pathlib import Path

# 初始化AI、DB等
ai = AI(
    model_name = "gpt-3.5-turbo-16k",
    temperature = 0.1,
)

input_path = Path("projects/example").absolute()
memory_path = input_path / "memory"
workspace_path = input_path / "workspace"
archive_path = input_path / "archive"
dbs = DBs(
    memory=DB(memory_path),
    logs=DB(memory_path / "logs"),
    input=DB(input_path),
    workspace=DB(workspace_path),
    preprompts=DB(Path(__file__).parent / "prompts"),
    archive=DB(archive_path),
)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        player = Player()
        if player.age < 5:
            player.birth_event(ai, dbs)  # 注意：你可能需要调整这里的逻辑
        response = {
            "player": player.to_dict(),
            "event_description": player.experiences[-1]
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
