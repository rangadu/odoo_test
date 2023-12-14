Database Changes
-----------------
##### Several new fields have been introduced to hr_attendance model, along with modifications to existing methods.


### New Fields:

- hr.attendance: New fields like project_id, task_id check_in_description and check_out_description.

### Python Code Modifications
- Inherit ```attendance_manual, _attendance_action, _attendance_action_change``` functions and add project_id, task_id and description parameters.
###### Syntax:
```
    class HrEmployee(models.Model):
        _inherit = "hr.employee"

        def attendance_manual(self, next_action, entered_pin=None, project_id=None, task_id=None, description=None):
            return super(HrEmployee, self).attendance_manual(entered_pin, next_action, project_id, task_id, description)
    
        def _attendance_action(self, next_action, project_id=False, task_id=False, description=False):
            return super(HrEmployee, self)._attendance_action(next_action, project_id, task_id, description)
    
        def _attendance_action_change(self, project_id=None, task_id=None, description=None):
            return super(HrEmployee, self)._attendance_action_change(project_id, task_id, description)
```

- Monkey patching and extend the behaviour of the ```attendance_manual, _attendance_action, _attendance_action_change``` functions.
###### Syntax:
```
def attendance_manual(self, next_action, entered_pin=None, project_id=None, task_id=None, description=None):
    ...
    ...
    return {'warning': _('Wrong PIN')}
    
HrEmployeeBase.attendance_manual = attendance_manual

def _attendance_action(self, next_action, project_id=False, task_id=False, description=False):
    ...
    ...
    return {'action': action_message}

HrEmployeeBase._attendance_action = _attendance_action

def _attendance_action_change(self, project_id=None, task_id=None, description=None):
    ...
    ...
    return attendance

HrEmployeeBase._attendance_action_change = _attendance_action_change
```

### Javascript Code Modifications
- Extends MyAttendances to handle project details

###### Syntax:
- create a new method called ```_fetchProjects``` and fetch all the active projects and set to dropdown.

```
_fetchProjects: function () {
    var self = this;
    return this._rpc({
        model: 'project.project',
        method: 'search_read',
        args: [[['active', '=', true]], ['id', 'name']],
        context: session.user_context,
    }).then(function (res) {
        self.project_ids = res;
    });
}
```

- create a new method called ```_onChangeProject``` and fetch all tasks related to the selected project.

```
_onChangeProject: function (ev) {
    var project_id = $(ev.target).val();
    var selectStates = $("select[id='task_id']");
    if (project_id !== ""){
        return this._rpc({
            model: 'project.task',
            method: 'search_read',
            args: [[['project_id', '=', parseInt(project_id)]], ['id', 'name']],
            context: session.user_context,
        }).then(function (res) {
            selectStates.html('<option value="">Task</option>');
            _.each(res, function (x) {
                var opt = $('<option>').text(x.name)
                    .attr('value', x.id)
                selectStates.append(opt);
            });
            selectStates.parent('div').show();
        });
    }else {
        selectStates.html('<option value="">Task</option>');
    }

},
```

- Added validations to project, task and description fields.

```
var error = false;
var project_id = $("select[id='project_id']").val();

if (project_id === ''){
    self.displayNotification({ title: "Project Field is Required", type: 'danger' });
    error = true;
}

var task_id = $("select[id='task_id']").val();
if (task_id === ''){
    self.displayNotification({ title: "Task Field is Required", type: 'danger' });
    error = true;
}

var description = $("input[id='description']").val();
if (description === ''){
    self.displayNotification({ title: "Description Field is Required", type: 'danger' });
    error = true;
}
```