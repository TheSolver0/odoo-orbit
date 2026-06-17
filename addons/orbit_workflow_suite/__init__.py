from . import models


def post_init_hook(env):
    """Lie les stages Orbit à tous les projets existants après installation."""
    xmlids = [
        'stage_backlog', 'stage_today', 'stage_progress', 'stage_review',
        'stage_done', 'stage_reported', 'stage_old_done',
    ]
    stage_ids = []
    for xid in xmlids:
        stage = env.ref('orbit_workflow_suite.' + xid, raise_if_not_found=False)
        if stage:
            stage_ids.append(stage.id)

    projects = env['project.project'].search([])
    if stage_ids and projects:
        env['project.task.type'].browse(stage_ids).write(
            {'project_ids': [(4, p.id) for p in projects]}
        )
