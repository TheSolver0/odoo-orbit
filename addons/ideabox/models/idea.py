from odoo import models, fields, api


class Idea(models.Model):
    _name = 'ideabox.idea'
    _description = 'Ideabox Idea'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Identification ---
    name = fields.Char("Énoncé de l'idée", required=True, tracking=True)
    potential_name = fields.Char("Nom potentiel du projet")

    description = fields.Text("Description")

    # --- Core idea ---
    problem = fields.Text("Problème")
    target_users = fields.Text("Cible")
    solution = fields.Text("Solution")
    how_it_works = fields.Text("Fonctionnement")

    # --- Analysis ---
    features = fields.Text("Fonctionnalités principales")
    feasibility = fields.Text("Faisabilité")
    resources = fields.Text("Ressources nécessaires")
    value_proposition = fields.Text("Différenciation")

    risks = fields.Text("Risques & limites")
    evolution = fields.Text("Évolution / Vision")

    # --- Persons ---
    user_id = fields.Many2one(
        'res.users',
        string="Responsable",
    )

    # Initiateur : parmi les employés (hr.employee)
    initiator_id = fields.Many2one(
        'hr.employee',
        string="Initiateur",
        tracking=True,
        help="Employé à l'origine de l'idée.",
    )

    # Analyste : parmi les employés (hr.employee)
    analyst_id = fields.Many2one(
        'hr.employee',
        string="Analyste assigné",
        tracking=True,
        help="Employé chargé d'analyser l'idée.",
    )

    # --- Lifecycle ---
    state = fields.Selection([
        ('draft',     'Brouillon'),
        ('submitted', 'Soumise'),
        ('review',    'En analyse'),
        ('approved',  'Validée'),
        ('rejected',  'Rejetée'),
        ('project',   'Devenue projet'),
    ], default='draft', tracking=True,
       group_expand='_group_expand_states')

    # Couleur du badge état pour le kanban (calculée)
    kanban_state_color = fields.Char(
        compute='_compute_kanban_state_color',
        string="Couleur état kanban",
    )

    @api.depends('state')
    def _compute_kanban_state_color(self):
        color_map = {
            'draft':     '#6c757d',  # gris
            'submitted': '#0dcaf0',  # cyan
            'review':    '#ffc107',  # jaune
            'approved':  '#198754',  # vert
            'rejected':  '#dc3545',  # rouge
            'project':   '#0d6efd',  # bleu
        }
        for rec in self:
            rec.kanban_state_color = color_map.get(rec.state, '#6c757d')

    # --- Project linkage ---
    project_id = fields.Many2one(
        'project.project',
        string="Projet lié",
        readonly=True,
    )

    # ----------------------------------------
    # Actions de workflow
    # ----------------------------------------
    def action_submit(self):
        self.state = 'submitted'

    def action_review(self):
        self.state = 'review'

    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

    def action_convert_to_project(self):
        for idea in self:
            project = self.env['project.project'].create({
                'name': idea.potential_name or idea.name,
            })
            idea.project_id = project.id
            idea.state = 'project'

    def write(self, vals):
        if 'state' in vals:
            pass
        return super().write(vals)

    def _group_expand_states(self, states, domain, order):
        return [key for key, _val in self._fields['state'].selection]