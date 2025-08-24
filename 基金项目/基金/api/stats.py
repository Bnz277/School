from flask import Blueprint, jsonify

from core.state import tasks, results

stats_bp = Blueprint('api_stats', __name__)


@stats_bp.get('/api/stats')
def get_stats():
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
    failed_tasks = len([t for t in tasks if t['status'] == 'failed'])
    total_results = len(results)
    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'total_results': total_results,
        'success_rate': round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
    })