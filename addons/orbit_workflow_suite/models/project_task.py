from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    standup_comment = fields.Text(string="Plan du jour")
    blocker_comment = fields.Text(string="Blockers")

    proof_url = fields.Char(string="Lien preuve")
    proof_attachment_ids = fields.Many2many(
        'ir.attachment',
        'orbit_task_proof_rel',
        'task_id',
        'attachment_id',
        string="Pièces jointes (preuves)"
    )

    completion_date = fields.Datetime(string="Date de complétion", readonly=True)
    planned_for_today = fields.Boolean(string="Planifié aujourd'hui")

    sprint_id = fields.Many2one('orbit.sprint', string="Sprint")
    story_points = fields.Integer(string="Story Points")
    task_type = fields.Selection([
        ('task', 'Tâche'),
        ('bug', 'Bug'),
        ('improvement', 'Amélioration'),
    ], string="Type")

    can_plan_today = fields.Boolean(compute='_compute_orbit_actions')
    can_start_task = fields.Boolean(compute='_compute_orbit_actions')
    can_mark_done = fields.Boolean(compute='_compute_orbit_actions')
    can_postpone = fields.Boolean(compute='_compute_orbit_actions')

    def _get_stage(self, xml_id):
        return self.env.ref('orbit_workflow_suite.' + xml_id).sudo()

    def _orbit_stage_ids(self):
        get = lambda xid: (
            self.sudo().env.ref('orbit_workflow_suite.' + xid, raise_if_not_found=False)
            or self.env['project.task.type']
        )
        return {
            'backlog':   get('stage_backlog').id,
            'today':     get('stage_today').id,
            'progress':  get('stage_progress').id,
            'review':    get('stage_review').id,
            'done':      get('stage_done').id,
            'reported':  get('stage_reported').id,
            'old_done':  get('stage_old_done').id,
        }

    @api.depends('stage_id')
    def _compute_orbit_actions(self):
        s = self._orbit_stage_ids()
        for task in self:
            sid = task.stage_id.id
            task.can_plan_today = sid in (s['backlog'], s['reported'])
            task.can_start_task = sid == s['today']
            task.can_mark_done  = sid in (s['today'], s['progress'], s['review'])
            task.can_postpone   = sid in (s['today'], s['progress'], s['review'])

    @api.constrains('stage_id')
    def _check_proof_before_done(self):
        done_stage = self.sudo().env.ref(
            'orbit_workflow_suite.stage_done', raise_if_not_found=False
        )
        for task in self:
            if done_stage and task.stage_id.id == done_stage.id:
                if not task.proof_url and not task.proof_attachment_ids:
                    raise ValidationError(
                        "Une preuve est obligatoire avant de marquer la tâche comme Terminée.\n"
                        "Ajoutez un lien ou une pièce jointe dans l'onglet « Orbit Workflow »."
                    )

    def action_plan_today(self):
        stage = self._get_stage('stage_today')
        self.sudo().write({'stage_id': stage.id, 'planned_for_today': True})

    def action_start_task(self):
        stage = self._get_stage('stage_progress')
        self.sudo().write({'stage_id': stage.id})

    def action_mark_done(self):
        for task in self:
            if not task.proof_url and not task.proof_attachment_ids:
                raise ValidationError(
                    "Ajoutez une preuve avant de terminer la tâche (lien ou pièce jointe)."
                )
        self.sudo().write({
            'stage_id': self._get_stage('stage_done').id,
            'completion_date': fields.Datetime.now(),
        })

    def action_postpone(self):
        self.sudo().write({
            'stage_id': self._get_stage('stage_reported').id,
            'planned_for_today': False,
        })

    def process_daily_tasks(self):
        today_stage = self.sudo().env.ref(
            'orbit_workflow_suite.stage_today', raise_if_not_found=False
        )
        reported_stage = self.sudo().env.ref(
            'orbit_workflow_suite.stage_reported', raise_if_not_found=False
        )
        if not today_stage or not reported_stage:
            return
        unfinished = self.search([('stage_id', '=', today_stage.id)])
        unfinished.write({'stage_id': reported_stage.id})
