odoo.define('ks_binary_file_preview.ks_binary_preview', function(require) {

    var BasicFields = require('web.basic_fields');
    var DocumentViewer = require('mail.DocumentViewer');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var ks_file_data = undefined;

    BasicFields.FieldBinaryFile.include({

        events: _.extend({}, BasicFields.FieldBinaryFile.prototype.events, {
            'click .ks_binary_file_preview': "ks_onAttachmentView",
        }),

        _renderReadonly: function() {
            var self = this;
            self._super.apply(this, arguments);
            if (!self.res_id) {
                self.$el.css('cursor', 'not-allowed');
            } else {
                self.$el.css('cursor', 'pointer');
                self.$el.attr('title', 'Download');
            }
            self.$el.append(core.qweb.render("ks_preview_button"));
        },

        ks_onAttachmentView: function(ev) {
            var self = this;
            try {
                ev.preventDefault();
                ev.stopPropagation();
                var ks_mimetype = self.recordData.mimetype;

                function ks_docView(ks_file_data) {
                    if (ks_file_data) {
                        var match = ks_file_data.type.match("(image|video|application/pdf|text)");
                        if(match){
                            var ks_attachment = [{
                                filename: ks_file_data.name,
                                id: ks_file_data.id,
                                is_main: false,
                                mimetype: ks_file_data.type,
                                name: ks_file_data.name,
                                type: ks_file_data.type,
                                url: "/web/content/" + ks_file_data.id + "?download=true",
                            }]
                            var ks_activeAttachmentID = ks_file_data.id;
                            var ks_attachmentViewer = new DocumentViewer(self,ks_attachment,ks_activeAttachmentID);
                            ks_attachmentViewer.appendTo($('body'));
                        }
                        else{
                            alert('This file type can not be previewed.')
                        }
                    }
                }
                if (ks_mimetype) {
                    ks_file_data = {
                        'id': self.recordData.id,
                        'type': self.recordData.mimetype || 'application/octet-stream',
                        'name': self.recordData.name || self.recordData.display_name || "",
                    }
                    ks_docView(ks_file_data);
                } else {
                    var def = ajax.jsonRpc("/get/record/details", 'call', {
                        'res_id': self.res_id,
                        'model': self.model,
                        'size': self.value,
                        'res_field': self.name || self.field.string,
                    });
                    return $.when(def).then(function(vals) {
                        if (vals && vals.id) {
                            ks_docView(vals);
                        } else {
                            alert('The preview of the file can not be generated as it does not exist in the Odoo file system (Attachments).')
                        }
                    });
                }
            } catch (err) {
                alert(err);
            }
        },
    });
});
