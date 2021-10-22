odoo.define('flsp_cost_scenario_structure.flsp_cost_strc_report', function (require) {
'use strict';

var core = require('web.core');
var framework = require('web.framework');
var stock_report_generic = require('stock.stock_report_generic');

var QWeb = core.qweb;
var _t = core._t;

var FlspBomReport = stock_report_generic.extend({
    events: {
        'click .o_mrp_bom_unfoldable': '_onClickUnfold',
        'click .o_mrp_bom_foldable': '_onClickFold',
        'click .o_mrp_bom_action': '_onClickAction',
        'click .o_mrp_show_attachment_action': '_onClickShowAttachment',
    },
    get_html: function() {
        var self = this;
        var args = [
            this.given_context.active_id,
            this.given_context.searchQty || false,
            this.given_context.searchVariant,
        ];
        return this._rpc({
                model: 'report.report_cost_scenario_structure',
                method: 'get_html',
                args: args,
                context: this.given_context,
            })
            .then(function (result) {
                self.data = result;
            });
    },
    set_html: function() {
        var self = this;
        return this._super().then(function () {
            self.$('.o_content').html(self.data.lines);
            self.renderSearch();
            self.update_cp();
        });
    },
    render_html: function(event, $el, result){
        if (result.indexOf('mrp.document') > 0) {
            if (this.$('.o_mrp_has_attachments').length === 0) {
                var column = $('<th/>', {
                    class: 'o_mrp_has_attachments',
                    title: 'Files attached to the product Attachments',
                    text: 'Attachments',
                });
                this.$('table thead th:last-child').after(column);
            }
        }
        $el.after(result);
        $(event.currentTarget).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
        this._reload_report_type();
    },
    get_bom: function(event) {
      var self = this;
      var $parent = $(event.currentTarget).closest('tr');
      var activeID = $parent.data('id');
      var productID = $parent.data('product_id');
      var lineID = $parent.data('line');
      var qty = $parent.data('qty');
      var level = $parent.data('level') || 0;
      return this._rpc({
              model: 'report.report_cost_scenario_structure',
              method: 'get_bom',
              args: [
                  activeID,
                  productID,
                  parseFloat(qty),
                  lineID,
                  level + 1,
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },
    get_operations: function(event) {
      var self = this;
      var $parent = $(event.currentTarget).closest('tr');
      var activeID = $parent.data('bom-id');
      var qty = $parent.data('qty');
      var level = $parent.data('level') || 0;
      return this._rpc({
              model: 'report.report_cost_scenario_structure',
              method: 'get_operations',
              args: [
                  activeID,
                  parseFloat(qty),
                  level + 1
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },
    update_cp: function () {
        var status = {
            cp_content: {
                $buttons: this.$buttonPrint,
                $searchview_buttons: this.$searchView
            },
        };
        return this.updateControlPanel(status);
    },
    renderSearch: function () {
        this.$buttonPrint = $(QWeb.render('flsp_cost_scenario_structure.flsp_button'));
        this.$buttonPrint.find('.o_cost_scenario_unfold').on('click', this._onClickUnfoldAll.bind(this));
        this.$buttonPrint.find('.o_cost_scenario_fold').on('click', this._onClickFoldAll.bind(this));
        this.$searchView = $(QWeb.render('flsp_cost_scenario_structure.report_flsp_search', _.omit(this.data, 'lines')));
        this.$searchView.find('.o_flsp_cost_strc_report_qty').on('change', this._onChangeQty.bind(this));
        this.$searchView.find('.o_flsp_cost_strc_report_variants').on('change', this._onChangeVariants.bind(this));
        this.$searchView.find('.o_flsp_cost_scenario_structure_type').on('change', this._onChangeType.bind(this));
    },

    _onClickPrint: function (ev) {
        var childBomIDs = _.map(this.$el.find('.o_mrp_bom_foldable').closest('tr'), function (el) {
            return $(el).data('id');
        });
        framework.blockUI();
        var reportname = 'flsp_cost_scenario_structure.report_cost_scenario_structure?docids=' + this.given_context.active_id +
                         '&report_type=' + this.given_context.report_type +
                         '&quantity=' + (this.given_context.searchQty || 1);
        if (! $(ev.currentTarget).hasClass('o_mrp_bom_print_unfolded')) {
            reportname += '&childs=' + JSON.stringify(childBomIDs);
        }
        if (this.given_context.searchVariant) {
            reportname += '&variant=' + this.given_context.searchVariant;
        }
        var action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': reportname,
            'report_file': 'flsp_cost_scenario_structure.report_cost_scenario_structure',
        };
        return this.do_action(action).then(function (){
            framework.unblockUI();
        });
    },
    _onChangeQty: function (ev) {
        var qty = $(ev.currentTarget).val().trim();
        if (qty) {
            this.given_context.searchQty = parseFloat(qty);
            this._reload();
        }
    },
    _onChangeType: function (ev) {
        var report_type = $("option:selected", $(ev.currentTarget)).data('type');
        this.given_context.report_type = report_type;
        this._reload_report_type();
    },
    _onChangeVariants: function (ev) {
        this.given_context.searchVariant = $(ev.currentTarget).val();
        this._reload();
    },

    _onClickUnfoldAll: function(ev){
        var x = document.getElementsByClassName("o_mrp_bom_unfoldable");
        for (let i = 0; i < x.length; i++) {
            $(x[i]).click();
            $(x[i]).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
        }
    },
    _onClickUnfold: function (ev) {
        var redirect_function = $(ev.currentTarget).data('function');
        this[redirect_function](ev);
    },
    _onClickFoldAll: function(ev){
        var x = document.getElementsByClassName("o_mrp_bom_foldable");
        for (let i = 0; i < x.length; i++) {
            $(x[i]).click();
            $(x[i]).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
        }
    },
    _onClickFold: function (ev) {
        this._removeLines($(ev.currentTarget).closest('tr'));
        $(ev.currentTarget).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
    },
    _onClickAction: function (ev) {
        ev.preventDefault();
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            res_id: $(ev.currentTarget).data('res-id'),
            context: {
                'active_id': $(ev.currentTarget).data('res-id')
            },
            views: [[false, 'form']],
            target: 'current'
        });
    },
    _onClickShowAttachment: function (ev) {
        ev.preventDefault();
        var ids = $(ev.currentTarget).data('res-id');
        return this.do_action({
            name: _t('Attachments'),
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            domain: [['id', 'in', ids]],
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            view_mode: 'kanban,list,form',
            target: 'current',
        });
    },
    _reload: function () {
        var self = this;

        return this.get_html().then(function () {
            self.$('.o_content').html(self.data.lines);
            self._reload_report_type();
        });
    },
    _reload_report_type: function () {
        this.$('.o_mrp_bom_cost.o_hidden, .o_mrp_prod_cost.o_hidden').toggleClass('o_hidden');
        this.$('.o_flsp_cost_scenario_cad, .o_flsp_cost_scenario_usd').toggleClass('o_hidden', true);
        if (this.given_context.report_type === 'USD') {
            this.$('.o_flsp_cost_scenario_usd').toggleClass('o_hidden', false);
        }else{
            this.$('.o_flsp_cost_scenario_cad').toggleClass('o_hidden', false);
        }

        if (this.given_context.report_type === 'bom_structure') {
           this.$('.o_mrp_bom_cost, .o_mrp_prod_cost').toggleClass('o_hidden');
        }
    },
    _removeLines: function ($el) {
        var self = this;
        var activeID = $el.data('id');
        _.each(this.$('tr[parent_id='+ activeID +']'), function (parent) {
            var $parent = self.$(parent);
            var $el = self.$('tr[parent_id='+ $parent.data('id') +']');
            if ($el.length) {
                self._removeLines($parent);
            }
            $parent.remove();
        });
    },
});

core.action_registry.add('flsp_cost_strc_report', FlspBomReport);
return FlspBomReport;

});
