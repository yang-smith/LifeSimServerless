from http.server import BaseHTTPRequestHandler
from api.state import Player
from flask import Flask, jsonify, request
from flask_cors import CORS  # 新增CORS
from api.ai import AI
from api.db import DB, DBs
from pathlib import Path

app = Flask(__name__)
CORS(app)  # 允许跨域请求

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

@app.route('/start', methods=['GET'])
def start():
    player = Player()
    if player.age < 5:
        player.birth_event(ai, dbs)
    return jsonify(player=player.to_dict(), event_description=player.experiences[-1])

@app.route('/choice', methods=['POST'])
def handle_event():
    data = request.json
    if 'player' not in data:
        return jsonify(error="Player data not provided"), 400
    if 'choice' not in data:
        return jsonify(error="Choice data not provided"), 400
    player = Player.from_dict(data['player'])  # 从请求体获取玩家状态
    choice = data['choice']
    update =  player.undergo_event(ai, dbs, choice)
    
    return jsonify(player=player.to_dict(), event_description=player.experiences[-1], update=update)

@app.route('/continue', methods=['POST'])
def gen_event():
    data = request.json
    if 'player' not in data:
        return jsonify(error="Player data not provided"), 400
    player = Player.from_dict(data['player'])  # 从请求体获取玩家状态
    player.age += 10
    status = player.check_status(ai, dbs)
    if status < 0:
        return jsonify(game_over=True, player=player.to_dict(), event_description=player.experiences[-1])
    player.event_gen(ai, dbs)
    
    return jsonify(player=player.to_dict(), event_description=player.experiences[-1])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
