# -*- encoding: utf-8 -*-
{
    "name": "HR Attendance Extend",
    "summary": "This module will add project, task and description fields to attendance view",
    "description": "This module will add project, task and description fields to attendance view",
    "version": "1.0.1",
    "category": "Human Resources/Attendances",
    "author": "Ranga Dharmapriya",
    "website": "",
    "depends": ['hr', 'hr_attendance', 'project'],
    "data": [
        'views/hr_attendance_view.xml'
    ],
    "installable": True,
    'assets': {
        'web.assets_backend': [
            'hr_attendance_extend/static/src/js/my_attendances.js',
            'hr_attendance_extend/static/src/xml/attendance.xml',
        ]
    },
    "license": "AGPL-3",
}
