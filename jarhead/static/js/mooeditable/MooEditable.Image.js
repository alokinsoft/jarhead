/*
---

name: MooEditable.Image

description: Extends MooEditable to insert image with manipulation options.

license: MIT-style license

authors:
- Radovan Lozej

requires:
# - MooEditable
# - MooEditable.UI
# - MooEditable.Actions

provides: [MooEditable.UI.ImageDialog, MooEditable.Actions.image]

usage: |
  Add the following tags in your html
  <link rel="stylesheet" href="MooEditable.css">
  <link rel="stylesheet" href="MooEditable.Image.css">
  <script src="mootools.js"></script>
  <script src="MooEditable.js"></script>
  <script src="MooEditable.Image.js"></script>

  <script>
  window.addEvent('domready', function(){
    var mooeditable = $('textarea-1').mooEditable({
      actions: 'bold italic underline strikethrough | image | toggleview'
    });
  });
  </script>

...
*/

MooEditable.Locale.define({
    imageAlt: 'alt',
    imageClass: 'class',
    imageAlign: 'align',
    imageAlignNone: 'none',
    imageAlignLeft: 'left',
    imageAlignCenter: 'center',
    imageAlignRight: 'right',
    addEditImage: 'Add/Edit Image'
});

MooEditable.UI.ImageDialog = function(editor){
    var clear = '<div class="clear"></div>';
    var help =  '<div class="help">' +
                    '<span class="spinner"></span>' +
                    '<span class="help_text"></span>' +
                '</div>';
    var title = '<div class="titlebar">' +
                    '<span class="title">Insert Image</span>' +
                    '<span class="button_upload"></span>' +
                '</div>'+ clear;

    var title2 = '<div class="titlebar">' +
                    '<span class="title">Upload Image</span>' +
                '</div>';

    var view2 = '<div id="image_browse" class="view2 hidden">' + title2 +
                '<form id="img_upload_form" name="device_data_form" method="POST" action="" class="device_form" enctype="multipart/form-data">'+
                    '<input type="hidden" value="db9039ef37e53d78a86e2d9b8cf7d228" name="csrfmiddlewaretoken">'+
                    '<input  type="file" class="browse" name="image" value="" />'+
                '</form>'+
                '<a href="#" class="button save"></a>'+ help +
                '<button class="dialog-button upload-cancel-button"></button>' +
            '</div>';

    var view1 = '<div id="image_uploader_plugin" class="view1">'+ title +
                '<div id="image_container" class="select_content"></div>' + clear +
                '<input type="hidden" id="img_upload" class="dialog-url" value="" size="15"> ' +
                '<button class="dialog-button dialog-ok-button">' + MooEditable.Locale.get('ok') + '</button> ' +
                '<button class="dialog-button dialog-cancel-button">' + MooEditable.Locale.get('cancel') + '</button>' +
            '</div>'+clear;

    var html = view1 + view2 ;

    return new MooEditable.UI.Dialog(html, {
        'class': 'mooeditable-image-dialog',
        onOpen: function(){
            var input = this.el.getElement('.dialog-url');
            var node = editor.selection.getNode();
            new ImageUpload(this.el,{});
            if (node.get('tag') == 'img'){
                this.el.getElement('.dialog-url').set('value', node.get('src'));
                // this.el.getElement('.dialog-alt').set('value', node.get('alt'));
                // this.el.getElement('.dialog-class').set('value', node.className);
                // this.el.getElement('.dialog-align').set('align', node.get('align'));
            }
            (function(){
                input.focus();
                input.select();
            }).delay(10);
        },
        onClick: function(e){
            if (e.target.tagName.toLowerCase() == 'button') e.preventDefault();
            var button = document.id(e.target);
            if (button.hasClass('dialog-cancel-button')){
                this.close();
            } else if (button.hasClass('dialog-ok-button')){
                this.close();
                var dialogAlignSelect = this.el.getElement('.dialog-align');
                var node = editor.selection.getNode();
                if (node.get('tag') == 'img'){
                    node.set('src', this.el.getElement('.dialog-url').get('value').trim());
                    // node.set('alt', this.el.getElement('.dialog-alt').get('value').trim());
                    // node.className = this.el.getElement('.dialog-class').get('value').trim();
                    // node.set('align', $(dialogAlignSelect.options[dialogAlignSelect.selectedIndex]).get('value'));
                } else {
                    var div = new Element('div');
                    var width = this.el.getElement('.dialog-url').get('w').toInt();
                    var height = this.el.getElement('.dialog-url').get('h').toInt();
                    if (width && height) {
                        new Element('img', {
                            src: this.el.getElement('.dialog-url').get('value').trim(),
                            width: width,
                            height: height,
                        }).inject(div);
                    } else {
                        new Element('img', {
                            src: this.el.getElement('.dialog-url').get('value').trim(),
                            // alt: this.el.getElement('.dialog-alt').get('value').trim(),
                            // 'class': this.el.getElement('.dialog-class').get('value').trim(),
                            // align: $(dialogAlignSelect.options[dialogAlignSelect.selectedIndex]).get('value'),
                        }).inject(div);
                    }
                    editor.selection.insertContent(div.get('html'));
                }
            }
        }
    });
};

MooEditable.Actions.image = {
    title: MooEditable.Locale.get('addEditImage'),
    options: {
        shortcut: 'm'
    },
    dialogs: {
        prompt: function(editor){
            return MooEditable.UI.ImageDialog(editor);
        }
    },
    command: function(){
        this.dialogs.image.prompt.open();
    }
};









// ' <input type="hidden" class="dialog-alt" value="" size="8"> ' +
// ' <input type="hidden" class="dialog-class" value="" size="8"> ' +
// ' <select style="display: none" class="dialog-align">' +
//     '<option>' + MooEditable.Locale.get('imageAlignNone') + '</option>' +
//     '<option>' + MooEditable.Locale.get('imageAlignLeft') + '</option>' +
//     '<option>' + MooEditable.Locale.get('imageAlignCenter') + '</option>' +
//     '<option>' + MooEditable.Locale.get('imageAlignRight') + '</option>' +
// '</select> '+