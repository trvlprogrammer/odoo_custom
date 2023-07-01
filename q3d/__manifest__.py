# -*- coding: utf-8 -*-
{
    'name': "Q3D",
    'summary': "v.1.0",
    'version': '1.0',
    'description': """
Migration Auxiliary
    """,
    'author': "Paul Cherepanov, vi3ual@gmail.com",
    'website': "http://paulautomation.com",
    'category': 'Operations',
    'depends': ['sale', 'purchase', 'product', 'mrp', 'base_kanban_stage', 'project', 'hr', 'rating', 'bi_sql_editor', 'dhx_gantt'],
    # 'css': ['static/css/reset.min.css'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/q3d_so_line.xml',
        'views/q3d_production_lot.xml',
        'views/q3d_machine.xml',
        'views/q3d_menu.xml',
        'views/q3d_step.xml',
        'views/q3d_project.xml',
        'views/q3d_batch_kanban.xml',
        'views/q3d_batch_form.xml',
        'views/q3d_task.xml',
        'views/q3d_sorter.xml'
    ],
    'qweb': [
        'views/q3d_batch_topbar.xml'
    ],
    'installable': True,
}
