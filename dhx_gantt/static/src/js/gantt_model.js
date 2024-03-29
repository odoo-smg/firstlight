odoo.define('dhx_gantt.GanttModel', function (require) {
    "use strict";

    var AbstractModel = require('web.AbstractModel');
    var time = require('web.time');
    const colors = ['red', 'dodgerblue', 'purple', 'teal', 'pink', 'green', 'orange', 'tomato', 'mediumseagreen', 'blue', 'violet', 'cyan'];
    const minimal_duration = 1000 * 60 * 60;
    // var BasicModel = require('web.BasicModel');
    var GanttModel = AbstractModel.extend({
        get: function(){
        // get: function(id, options){
            // console.log('get()');
            // console.log(this.records);
            // console.log('Basic.get()');
            // options = options ? options : {};
            // options.raw = false;  // prevent x2many field errors on BasicModel's get()
            // var upperRes = this._super.apply(this, arguments);
            // console.log(upperRes);
            // return upperRes;
            var data = [];
            var links = [];
            // var formatFunc = gantt.date.str_to_date("%Y-%m-%d %h:%i:%s");
            // this.records.forEach(function(record){ 
                // data.push({
                //     "id": record.id,
                //     "text": record.name,
                //     "start_date": formatFunc(record.date_start),
                //     "duration": record.planned_duration,
                //     "progress": record.progress,
                //     "open": record.is_open,
                // });
                // console.log(record.links_serialized_json);
            //     links.push.apply(links, JSON.parse(record.links_serialized_json))
            // });
            // console.log(data);
            // console.log('links');
            // console.log(links);
            var gantt_model = {
                data: this.records,
                links: this.links,
            }
            var res = {
                records: gantt_model,
            };
            // console.log('get() RETURNING');
            // console.log(res);
            return res;
        },
        load: function(params){
            // console.log('load()');
            // console.log({params});
            this.map_id = params.id_field;
            this.map_text = params.text;
            this.map_date_start = params.date_start;
            this.map_date_finished = params.date_finished;
            this.map_duration = params.duration;
            this.map_responsible = params.responsible;
            this.map_product_part_number = params.product_part_number;
            this.map_product_name = params.product_name;
            this.map_source = params.source;
            this.map_state = params.state;
            this.map_progress = params.progress;
            this.map_open = params.open;
            this.map_links_serialized_json = params.links_serialized_json;
            this.map_total_float = params.total_float;
            // this.map_parent = 'project_id';   comment this line out in order to remove 'undefined' project banner for MOs in the gantt chart list
            this.modelName = params.modelName;
            this.linkModel = params.linkModel;
            return this._load(params);
        },
        reload: function(id, params){
            // console.log('reload()...');
            return this._load(params);
        },
        _load: function(params){
            // console.log('_load()...');
            // console.log(this);
            // console.log("_load.params=" + params);
            params = params ? params : {};
            this.domain = params.domain || this.domain || [];
            this.modelName = params.modelName || this.modelName;
            var self = this;
            var fieldNames = [this.map_text, this.map_date_start, this.map_date_finished, this.map_duration];
            this.map_responsible && fieldNames.push(this.map_responsible);
            this.map_product_part_number && fieldNames.push(this.map_product_part_number);
            this.map_product_name && fieldNames.push(this.map_product_name);
            this.map_source && fieldNames.push(this.map_source);
            this.map_state && fieldNames.push(this.map_state);
            this.map_open && fieldNames.push(this.map_open);
            this.map_links_serialized_json && fieldNames.push(this.map_links_serialized_json);
            this.map_total_float && fieldNames.push(this.map_total_float);
            this.map_parent && fieldNames.push(this.map_parent);
            return this._rpc({
                model: this.modelName,
                method: 'search_read',
                fields: fieldNames,
                domain: this.domain,
                orderBy: [{
                    name: this.map_date_start,
                    asc: true,
                }]
            })
            .then(function (records) {
                self.convertData(records);
            });
        },
        convertData: function(records){
            // console.log('convertData');
            // console.log(records);
            var data = [];
            var formatFunc = gantt.date.str_to_date("%Y-%m-%d %h:%i:%s", true);
            // todo: convert date from utc to mgt or wtever
            var self = this;
            this.res_ids = [];
            var links = [];

            // map to assign color to users
            var colorIndex = 0;
            let user_color_map = new Map()

            records.forEach(function(record){ 
                self.res_ids.push(record[self.map_id]);
                // value.add(-self.getSession().getTZOffset(value), 'minutes')
                // data.timezone_offset = (-self.date_object.getTimezoneOffset());
                var datetime;
                if(record[self.map_date_start]){
                    datetime = formatFunc(record[self.map_date_start]);
                }else{
                    datetime = false;
                }

                var datetime_end = false;
                if(record[self.map_date_finished]){
                    datetime_end = formatFunc(record[self.map_date_finished]);
                }

                var task = {};
                if(self.map_parent){
                    var projectFound = data.find(function(element) {
                        return element.isProject && element.serverId == record[self.map_parent][0];
                    });
                    if(!projectFound){
                        // console.log('project not found');
                        var project = {
                            id: _.uniqueId('project-'),
                            serverId: record[self.map_parent][0],
                            text: record[self.map_parent][1],
                            isProject: true,
                            open: true,
                        }
                        task.parent = project.id;
                        data.push(project);
                    }else{
                        task.parent = projectFound.id;
                    }
                }
                task.id = record[self.map_id];
                task.text = record[self.map_text];
                task.start_date = datetime;
                task.end_date = datetime_end;
                task.duration = record[self.map_duration];
                task.progress = record[self.map_progress];
                task.responsible = record[self.map_responsible];
                task.product_part_number = record[self.map_product_part_number];
                task.product_name = record[self.map_product_name];
                task.source = record[self.map_source];
                task.state = record[self.map_state];
                task.open = record[self.map_open];
                task.links_serialized_json = record[self.map_links_serialized_json];
                task.total_float = record[self.map_total_float];

                // update tasks with colors
                var user_color = user_color_map.get(task.responsible);
                if (user_color){
                    task.color = user_color;
                } else {
                    colorIndex++;
                    if (colorIndex == colors.length) {
                        // reset index to reuse colors
                        colorIndex = 0;
                    }
                    user_color_map.set(task.responsible, colors[colorIndex]);
                    task.color = colors[colorIndex];
                }

                data.push(task);
                links.push.apply(links, JSON.parse(record.links_serialized_json))
            });
            this.records = data;
            this.links = links;
        },
        updateTask: function(data){
            // console.log('updateTask');
            if(data.isProject){
                return $.when();
            }
            var args = [];
            var values = {};

            var id = data.id;
            values[this.map_text] = data.text;
            if (this.map_open){
                values[this.map_open] = data.open;
            }
            if (this.map_progress){
                values[this.map_progress] = data.progress;
            }

            // convert time from dhx's string, to a javascript datetime, then to odoo's sting format :D
            var formatFunc = gantt.date.str_to_date("%d-%m-%Y %h:%i");
            if ( !data.end_date) {
                data.end_date = data.start_date;
            }
            var start_date_str = time.datetime_to_str(formatFunc(data.start_date));
            var end_date_str = time.datetime_to_str(formatFunc(data.end_date));
            var start = new Date(start_date_str);
			var end = new Date(end_date_str);
            if ( end.getTime() < start.getTime()) {
                end = start;
                end_date_str = start_date_str;
            }
            data.duration = Math.round((end.getTime() - start.getTime()) / minimal_duration);
            values[this.map_date_start] = start_date_str;
            values[this.map_date_finished] = end_date_str;
            values[this.map_duration] = data.duration;

            args.push(id);
            args.push(values)
            return this._rpc({
                model: this.modelName,
                method: 'write',
                args: args,
            });
        },
        createLink: function(data){
            // console.log('createLink');
            // console.log({data});
            var args = [];
            var values = {};

            values.id = data.id;
            values.task_id = data.source;
            values.depending_task_id = data.target;
            values.relation_type = data.type;

            args.push([values]);
            return this._rpc({
                model: this.linkModel,
                method: 'create',
                args: args,
            });
        },
        deleteLink: function(data){
            // console.log('deleteLink');
            // console.log({data});
            var args = [];

            args.push([data.id]);
            return this._rpc({
                model: this.linkModel,
                method: 'unlink',
                args: args,
            });
        },
        getCriticalPath: function(){
            return this._rpc({
                model: this.modelName,
                method: 'compute_critical_path',
                args:[this.res_ids],
            });
        },
        schedule: function(){
            var self = this;
            return this._rpc({
                model: this.modelName,
                method: 'bf_traversal_schedule',
                args:[this.res_ids],
            });
        },
    });
    return GanttModel;
});