{
    'name': 'Orbit Workflow Suite',
    'version': '1.0.0',
    'summary': 'Daily, Stand-up and Agile Workflow Management',
    'author': 'Orbit',
    'category': 'Project',
    'depends': [
        'project',
        'mail',
        'hr',
        'calendar'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/stages.xml',
        'data/cron.xml',

        'views/project_task_views.xml',
        'views/sprint_views.xml',
        'views/epic_views.xml',
        'views/daily_views.xml',
        'views/dashboard_views.xml',
        'views/menus.xml',

        'reports/daily_report.xml',
        'reports/weekly_report.xml'
    ],
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook',
}