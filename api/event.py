from http.server import BaseHTTPRequestHandler
from api.state import Player
import json
from api.ai import AI
from api.db import DB, DBs
from pathlib import Path

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
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length).decode()
        data = json.loads(body)
        
        player = Player.from_dict(data['player'])
        player.age += 10
        status = player.check_status(ai, dbs)  # 注意调整
        if status < 0:
            response = {
                "game_over": True,
                "player": player.to_dict(),
                "event_description": player.experiences[-1]
            }
        else:
            player.event_gen(ai, dbs)
            response = {
                "player": player.to_dict(),
                "event_description": player.experiences[-1]
            }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
