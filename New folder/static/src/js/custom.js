odoo.define('spx_vesco.FormView', function (require) {
"use strict";

var core = require('web.core');
var FormRenderingEngine = require('web.FormRenderingEngine');
var utils = require('web.utils');
var FormView = require('web.FormView');

var FormViewExt = FormView.include({
    init: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.fields = {};
        this.fields_order = [];
        this.datarecord = {};
        this.onchanges_mutex = new utils.Mutex();
        this.default_focus_field = null;
        this.default_focus_button = null;
        this.fields_registry = core.form_widget_registry;
        this.tags_registry = core.form_tag_registry;
        this.widgets_registry = core.form_custom_registry;
        this.has_been_loaded = $.Deferred();
        this.translatable_fields = [];
        this.is_initialized = $.Deferred();
        this.record_loaded = $.Deferred();
        this.mutating_mutex = new utils.Mutex();
        this.save_list = [];
        this.render_value_defs = [];
        this.reload_mutex = new utils.Mutex();
        this.__clicked_inside = false;
        this.__blur_timeout = null;
        this.rendering_engine = new FormRenderingEngine(this);
        try {
            if ('force_form_edit' in this.options.action.context) {
                this.options.initial_mode = "edit";
            };
        } catch(err) {

        }
        this.set({actual_mode: this.options.initial_mode});
        this.has_been_loaded.done(function() {
            self.on("change:actual_mode", self, self.toggle_buttons);
            self.on("change:actual_mode", self, self.toggle_sidebar);
        });
        self.on("load_record", self, self.load_record);
        core.bus.on('clear_uncommitted_changes', this, function(chain_callbacks) {
            var self = this;
            chain_callbacks(function() {
                return self.can_be_discarded();
            });
        });
    },
});

return FormViewExt;

});