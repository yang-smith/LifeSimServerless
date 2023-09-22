from http.server import BaseHTTPRequestHandler
from api.state import Player
import json
from api.ai import AI
from api.db import DB, DBs
from pathlib import Path

# 初始化AI、DB等
ai = AI(
    model_name="gpt-3.5-turbo-16k",
    temperature=0.1,
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
        try:
            player = Player()
            if player.age < 5:
                player.birth_event(ai, dbs)
            response = {
                "player": player.to_dict(),
                "event_description": player.experiences[-1]
            }
            self._send_response(200, response)
        except Exception as e:
            error_response = {
                "error": "An error occurred.",
                "detail": str(e)
            }
            self._send_response(500, error_response)

    def _send_response(self, status_code, content):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Add CORS header
        self.end_headers()
        self.wfile.write(json.dumps(content).encode())
