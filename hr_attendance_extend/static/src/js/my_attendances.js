odoo.define('hr_attendance_extend.my_attendances', function (require) {
    "use strict";

    const session = require('web.session');
    var MyAttendances = require('hr_attendance.my_attendances');

    /**
     * MyAttendances
     *
     * Extends MyAttendances to handle project details
     */
    MyAttendances.include({
        events: _.extend({}, MyAttendances.prototype.events || {}, {
            'change select#project_id': '_onChangeProject'
        }),

        willStart: function () {
            var defs = [this._super.apply(this, arguments)];
            defs.push(this._fetchProjects());
            return Promise.all(defs);
        },

        //Get all the projects and set to the project drop down
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
        },

        //Add and filter tasks based on the project selection
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

        /**
         *@override
         * Pass project_id, task_id, description field values to back end function
         */
        update_attendance: function () {
            var self = this;
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
            if (!error){
                this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances', null, project_id, task_id, description],
                    context: session.user_context,
                }).then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.displayNotification({ title: result.warning, type: 'danger' });
                    }
                });
            }
        },
    })
});
