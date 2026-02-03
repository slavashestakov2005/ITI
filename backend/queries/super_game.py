import json
import time
from typing import List

from flask import jsonify, make_response, render_template, request
from flask_cors import cross_origin
from flask_login import login_required

from backend import app
from backend.config import Config
from backend.database import Iti, SuperGameResult
from backend.help import UserRoleLogin
from backend.help.file_manager import krsk_time
from .help import check_access


def _normalize_name(name: str) -> str:
    return " ".join(str(name).strip().split())


def _dedupe_casefold(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _parse_teams(value) -> List[str]:
    teams = []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            value = [v.strip() for v in value.split(',')]
    if isinstance(value, list):
        for item in value:
            name = _normalize_name(item)
            if name:
                teams.append(name)
    return _dedupe_casefold(teams)


def _check_api_key() -> bool:
    if not Config.SUPER_GAME_API_KEY:
        return True
    provided = request.headers.get('X-API-KEY') or request.args.get('api_key') or ''
    return provided == Config.SUPER_GAME_API_KEY


def _parse_iti_id(value) -> int | None:
    try:
        iti_id = int(value)
    except Exception:
        return None
    return iti_id if Iti.select(iti_id) is not None else None


def _build_rating(rows: List[SuperGameResult]) -> List[dict]:
    stats = {}
    for row in rows:
        teams = _parse_teams(row.teams)
        seen = set()
        for team in teams:
            key = team.casefold()
            if key not in stats:
                stats[key] = {"name": team, "games_played": 0, "wins": 0}
            if key not in seen:
                stats[key]["games_played"] += 1
                seen.add(key)
        winner = _normalize_name(row.winner or "")
        if winner:
            key = winner.casefold()
            if key in stats:
                stats[key]["wins"] += 1
    return sorted(
        stats.values(),
        key=lambda item: (-item["wins"], -item["games_played"], item["name"].lower()),
    )


@app.route('/api/v1/super_game_result', methods=['POST'])
@cross_origin()
def super_game_result_post():
    if not _check_api_key():
        return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
    data = request.get_json(silent=True) or {}
    iti_id = _parse_iti_id(data.get('iti_id'))
    if iti_id is None:
        return make_response(jsonify({'status': 'FAIL', 'message': 'Некорректный ITI'}), 400)
    teams = _parse_teams(data.get('teams'))
    if not teams:
        return make_response(jsonify({'status': 'FAIL', 'message': 'Команды не заданы'}), 400)
    winner = _normalize_name(data.get('winner', ''))
    is_draw = bool(data.get('is_draw')) if 'is_draw' in data else not bool(winner)
    if is_draw:
        winner = ''
    row = SuperGameResult.build(
        None,
        iti_id,
        json.dumps(teams, ensure_ascii=False),
        winner if winner else None,
        bool(is_draw),
        int(time.time()),
    )
    SuperGameResult.insert(row)
    return make_response(jsonify({'status': 'OK'}), 200)


@app.route('/api/v1/super_game_rating')
@cross_origin()
def super_game_rating():
    iti_id = _parse_iti_id(request.args.get('iti_id'))
    if iti_id is None:
        return make_response(jsonify({'status': 'FAIL', 'message': 'Некорректный ITI'}), 400)
    rows = SuperGameResult.select_by_iti(iti_id)
    rating = _build_rating(rows)
    return make_response(jsonify({'status': 'OK', 'teams': rating}), 200)


@app.route('/super_game_results')
@cross_origin()
@login_required
@check_access(roles=[UserRoleLogin.LOGIN_LOCAL])
def super_game_results_page():
    iti_id = _parse_iti_id(request.args.get('iti'))
    itis = sorted(Iti.select_all(), key=lambda x: x.id)
    if iti_id is None and itis:
        iti_id = itis[-1].id
    rows = []
    if iti_id is not None:
        rows = sorted(
            SuperGameResult.select_by_iti(iti_id),
            key=lambda r: r.id,
            reverse=True,
        )
    results = []
    for row in rows:
        results.append({
            'id': row.id,
            'teams': row.teams_list(),
            'winner': row.winner,
            'is_draw': row.is_draw,
            'created_at': row.created_at,
            'created_at_str': krsk_time(row.created_at).strftime('%d.%m.%Y %H:%M'),
        })
    rating = _build_rating(rows)
    iti = Iti.select(iti_id) if iti_id is not None else None
    return render_template('super_game_results.html', results=results, rating=rating, iti=iti, itis=itis)
