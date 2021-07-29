odoo.define('flspsales_forecast.flsp_import', function(require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var time = require('web.time');
    var AbstractWebClient = require('web.AbstractWebClient');
    var Loading = require('web.Loading');

    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;
    var StateMachine = window.StateMachine;
    
    var base_import = require('base_import.import');
    base_import.DataImport.include({
        // overwite the method with updated message 'Everything seems valid'
        onresults: function (event, from, to, results) {
            console.log("new onresults()")
            var fields = this.$('.oe_import_fields input.oe_import_match_field').map(function (index, el) {
                return $(el).select2('val') || false;
            }).get();
    
            var message = results.messages;
            console.log("message=" + message)
            var no_messages = _.isEmpty(message);
            if (no_messages) {
                message.push({
                    type: 'info',
                    message: _.str.sprintf(_t("Everything seems valid for the %d record(s)."), results.ids.length)
                });
                console.log("message.1=" + message)
            } else if (event === 'import_failed' && results.ids) {
                // both ids in a failed import -> partial import
                this.toggle_partial(results);
            }
            console.log("message.2=" + message)
    
            // row indexes come back 0-indexed, spreadsheets
            // display 1-indexed.
            var offset = 1;
            // offset more if header
            if (this.import_options().headers) { offset += 1; }
    
            var messagesSorted = _.sortBy(_(message).groupBy('message'), function (group) {
                if (group[0].priority){
                    return -2;
                }
    
                // sort by gravity, then, order of field in list
                var order = 0;
                switch (group[0].type) {
                case 'error': order = 0; break;
                case 'warning': order = fields.length + 1; break;
                case 'info': order = 2 * (fields.length + 1); break;
                default: order = 3 * (fields.length + 1); break;
                }
                return order + _.indexOf(fields, group[0].field);
            });
    
            this.$form.addClass('oe_import_error');
            this.$('.oe_import_error_report').html(
                QWeb.render('ImportView.error', {
                    errors: messagesSorted,
                    at: function (rows) {
                        var from = rows.from + offset;
                        var to = rows.to + offset;
                        var rowName = '';
                        if (results.name.length > rows.from && results.name[rows.from] !== '') {
                            rowName = _.str.sprintf(' (%s)', results.name[rows.from]);
                        }
                        if (from === to) {
                            return _.str.sprintf(_t("at row %d%s"), from, rowName);
                        }
                        return _.str.sprintf(_t("between rows %d and %d"),
                                             from, to);
                    },
                    at_multi: function (rows) {
                        var from = rows.from + offset;
                        var to = rows.to + offset;
                        var rowName = '';
                        if (results.name.length > rows.from && results.name[rows.from] !== '') {
                            rowName = _.str.sprintf(' (%s)', results.name[rows.from]);
                        }
                        if (from === to) {
                            return _.str.sprintf(_t("Row %d%s"), from, rowName);
                        }
                        return _.str.sprintf(_t("Between rows %d and %d"),
                                             from, to);
                    },
                    at_multi_header: function (numberLines) {
                        return _.str.sprintf(_t("at %d different rows:"),
                                             numberLines);
                    },
                    more: function (n) {
                        return _.str.sprintf(_t("(%d more)"), n);
                    },
                    info: function (msg) {
                        if (typeof msg === 'string') {
                            return _.str.sprintf(
                                '<div class="oe_import_moreinfo oe_import_moreinfo_message">%s</div>',
                                _.str.escapeHTML(msg));
                        }
                        if (msg instanceof Array) {
                            return _.str.sprintf(
                                '<div class="oe_import_moreinfo oe_import_moreinfo_choices"><a href="#" class="oe_import_report_see_possible_value oe_import_see_all"><i class="fa fa-arrow-right"/> %s </a><ul class="oe_import_report_more">%s</ul></div>',
                                _.str.escapeHTML(_t("See possible values")),
                                _(msg).map(function (msg) {
                                    return '<li>'
                                        + _.str.escapeHTML(msg)
                                    + '</li>';
                                }).join(''));
                        }
                        // Final should be object, action descriptor
                        return [
                            '<div class="oe_import_moreinfo oe_import_moreinfo_action">',
                                _.str.sprintf('<a href="#" data-action="%s" class="oe_import_see_all"><i class="fa fa-arrow-right"/> ',
                                        _.str.escapeHTML(JSON.stringify(msg))),
                                    _.str.escapeHTML(
                                        _t("See possible values")),
                                '</a>',
                            '</div>'
                        ].join('');
                    },
                }));
        },
    });
});