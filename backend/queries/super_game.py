import json
import time
from typing import List

from flask import jsonify, make_response, redirect, render_template, request
from flask_cors import cross_origin
from flask_login import login_required

from backend import app
from backend.config import Config
from backend.database import Iti, SuperGameResult
from backend.help import check_role, forbidden_error, not_found_error, UserRoleGlobal, UserRoleIti, UserRoleLogin
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


def _parse_int(value, default: int, *, min_value: int | None = None, max_value: int | None = None) -> int:
    try:
        result = int(value)
    except Exception:
        result = default
    if min_value is not None:
        result = max(min_value, result)
    if max_value is not None:
        result = min(max_value, result)
    return result


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


@app.route('/api/v1/super_game_result', methods=['GET'])
@cross_origin()
def super_game_result_get_all():
    if not _check_api_key():
        return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
    iti_id = _parse_iti_id(request.args.get('iti_id'))
    if iti_id is None:
        return make_response(jsonify({'status': 'FAIL', 'message': 'Некорректный ITI'}), 400)

    limit = _parse_int(request.args.get('limit'), 200, min_value=1, max_value=1000)
    offset = _parse_int(request.args.get('offset'), 0, min_value=0)

    rows = sorted(SuperGameResult.select_by_iti(iti_id), key=lambda r: r.id, reverse=True)
    total = len(rows)
    rows = rows[offset: offset + limit]

    matches = []
    for row in rows:
        matches.append(
            {
                'id': row.id,
                'iti_id': row.iti_id,
                'teams': row.teams_list(),
                'winner': row.winner,
                'is_draw': bool(row.is_draw),
                'created_at': row.created_at,
            }
        )
    return make_response(jsonify({'status': 'OK', 'total': total, 'matches': matches}), 200)


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


@app.route('/api/v1/super_game_result/<int:item_id>', methods=['DELETE'])
@app.route('/api/v1/super_game_result/del/<int:item_id>', methods=['DELETE'])  # backward-compatible
@cross_origin()
def super_game_result_delete(item_id: int):
    if not _check_api_key():
        return make_response(jsonify({'status': 'FAIL', 'message': 'Доступ запрещён'}), 403)
    row = SuperGameResult.select(item_id)
    if row is None:
        return make_response(jsonify({'status': 'FAIL', 'message': 'ID не существует'}), 404)
    SuperGameResult.delete(item_id)
    return make_response(jsonify({'status': 'OK'}), 200)


@app.route('/super_game_results/delete/<int:item_id>', methods=['POST'])
@cross_origin()
@login_required
@check_access(roles=[UserRoleLogin.LOGIN_LOCAL])
def super_game_results_delete_page(item_id: int):
    row = SuperGameResult.select(item_id)
    if row is None:
        return not_found_error()
    if not check_role(roles=[UserRoleGlobal.FULL]) and not check_role(roles=[UserRoleIti.ADMIN], iti_id=row.iti_id):
        return forbidden_error()
    SuperGameResult.delete(item_id)
    return redirect(f"/super_game_results?iti={row.iti_id}")


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
