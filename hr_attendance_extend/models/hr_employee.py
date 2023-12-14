# -*- coding: utf-8 -*-
from odoo import models, fields, exceptions, _
from odoo.addons.hr_attendance.models.hr_employee import HrEmployee as HrEmployeeBase

"""
    Monkey patching and extend the behavior of attendance_manual function
    HrEmployeeBase.attendance_manual = attendance_manual
"""
def attendance_manual(self, next_action, entered_pin=None, project_id=None, task_id=None, description=None):
    self.ensure_one()
    attendance_user_and_no_pin = self.user_has_groups(
        'hr_attendance.group_hr_attendance_user,'
        '!hr_attendance.group_hr_attendance_use_pin')
    can_check_without_pin = attendance_user_and_no_pin or (self.user_id == self.env.user and entered_pin is None)
    if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
        # pass project_id, task_id, description to _attendance_action method
        return self._attendance_action(next_action, project_id, task_id, description)
    if not self.user_has_groups('hr_attendance.group_hr_attendance_user'):
        return {'warning': _(
            'To activate Kiosk mode without pin code, you must have access right as an Officer or above in the '
            'Attendance app. Please contact your administrator.')}
    return {'warning': _('Wrong PIN')}


HrEmployeeBase.attendance_manual = attendance_manual


"""
    Monkey patching and extend the behavior of _attendance_action function
    HrEmployeeBase._attendance_action = _attendance_action
"""
def _attendance_action(self, next_action, project_id=False, task_id=False, description=False):
    """ Changes the attendance of the employee.
        Returns an action to the check in/out message,
        next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
    """
    self.ensure_one()
    employee = self.sudo()
    action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
    action_message['previous_attendance_change_date'] = employee.last_attendance_id and (
            employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
    action_message['employee_name'] = employee.name
    action_message['barcode'] = employee.barcode
    action_message['next_action'] = next_action
    action_message['hours_today'] = employee.hours_today
    action_message['kiosk_delay'] = employee.company_id.attendance_kiosk_delay * 1000

    if employee.user_id:
        # pass project_id, task_id, description to _attendance_action_change method
        modified_attendance = employee.with_user(employee.user_id).sudo()._attendance_action_change(project_id, task_id,
                                                                                                    description)
    else:
        # pass project_id, task_id, description to _attendance_action_change method
        modified_attendance = employee._attendance_action_change(project_id, task_id, description)
    action_message['attendance'] = modified_attendance.read()[0]
    action_message['total_overtime'] = employee.total_overtime
    # Overtime have an unique constraint on the day, no need for limit=1
    action_message['overtime_today'] = self.env['hr.attendance.overtime'].sudo().search([
        ('employee_id', '=', employee.id), ('date', '=', fields.Date.context_today(self)),
        ('adjustment', '=', False)]).duration or 0
    return {'action': action_message}


HrEmployeeBase._attendance_action = _attendance_action


"""
    Monkey patching and extend the behavior of _attendance_action_change function
    HrEmployeeBase._attendance_action_change = _attendance_action_change
"""
def _attendance_action_change(self, project_id=None, task_id=None, description=None):
    """ Check In/Check Out action
        Check In: create a new attendance record
        Check Out: modify check_out field of appropriate attendance record
    """
    self.ensure_one()
    action_date = fields.Datetime.now()

    if self.attendance_state != 'checked_in':
        # Adding project_id, task_id and check_in_description to vals
        vals = {
            'employee_id': self.id,
            'check_in': action_date,
            'project_id': project_id,
            'task_id': task_id,
            'check_in_description': description,
        }
        return self.env['hr.attendance'].create(vals)
    attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
    if attendance:
        attendance.check_out = action_date
        #Set check_out_description value
        attendance.check_out_description = description
    else:
        raise exceptions.UserError(
            _('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
              'Your attendances have probably been modified manually by human resources.') % {
                'empl_name': self.sudo().name, })
    return attendance


HrEmployeeBase._attendance_action_change = _attendance_action_change


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    """
        Override attendance_manual, _attendance_action, _attendance_action_change functions in order to add following 
        parameters 
        :param int project_id: selected project when sign in. 
        :param int task_id: selected task_id when sign in. 
        :param int description: entered description when sign in/ sign out. 
    """

    def attendance_manual(self, next_action, entered_pin=None, project_id=None, task_id=None, description=None):
        return super(HrEmployee, self).attendance_manual(entered_pin, next_action, project_id, task_id, description)

    def _attendance_action(self, next_action, project_id=False, task_id=False, description=False):
        return super(HrEmployee, self)._attendance_action(next_action, project_id, task_id, description)

    def _attendance_action_change(self, project_id=None, task_id=None, description=None):
        return super(HrEmployee, self)._attendance_action_change(project_id, task_id, description)
