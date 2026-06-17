from odoo import models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        self._link_orbit_stages(projects)
        return projects

    def _link_orbit_stages(self, projects):
        xmlids = [
            'stage_backlog', 'stage_today', 'stage_progress', 'stage_review',
            'stage_done', 'stage_reported', 'stage_old_done',
        ]
        stage_ids = []
        for xid in xmlids:
            stage = self.env.ref('orbit_workflow_suite.' + xid, raise_if_not_found=False)
            if stage:
                stage_ids.append(stage.id)
        if stage_ids and projects:
            self.env['project.task.type'].browse(stage_ids).write(
                {'project_ids': [(4, p.id) for p in projects]}
            )
