
var ImageUpload = new Class({
    Binds: [],
    options: {
        url: '/image_upload/',
        get_image_url: '/image_display/'
    },
    initialize: function(element,options) {
        this.element = element;
        var win = $$('.select_wrapper')[0];
        win.empty();
        this.view1 = this.element.getElement('.view1');
        this.view2 = this.element.getElement('.view2');
        this.spinner = this.element.getElement('.spinner');
        this.helpText = this.element.getElement('.help_text');
        this.element.inject(win);
        this.dispWindow = new SelectModalWindow();
        var saveButton = this.element.getElement('.button.save');
        var uploadButton = this.element.getElement('.button_upload');
        var uploadCancel = this.element.getElement('.upload-cancel-button');
        uploadButton.addEvent('click',this.toggleView2.bind(this));
        uploadCancel.addEvent('click',this.toggleView1.bind(this));
        saveButton.addEvent('click', this.save.bind(this));
        this.request = new Request.JSON({
            url: this.options.get_image_url,
            onSuccess: this.loadData.bind(this),
        });
        this.toggleView1();
        this.dispWindow.startWindow();
    },

    toggleView2: function() {
        this.view1.addClass('hidden');
        this.view2.removeClass('hidden');
        this.helpText.set('html','');
        this.spinner.removeClass('active');
    },

    toggleView1: function() {
        this.getImages();
        this.view2.addClass('hidden');
        this.view1.removeClass('hidden');
    },

    loadData: function(d) {
        var container = this.element.getElementById('image_container');
        container.empty();
        var path = d.thumbnail_path;
        var files = d.files;
        files.each(function(el) {
            var p = path+'/thumbnail_'+el.name;
            var image = new Element('span', {
                'path': d['path']+'/'+el.name,
                'class': 'thumbnail',
                w: el.width,
                h: el.height,
                styles: {
                    background: 'url('+p+')',
                },
            });
            image.inject(container);
        });
        // this.dispWindow.reposition();
        this.setEvents();
    },

    setEvents: function() {
        var self = this;
        var thumbnails = this.element.getElements('.thumbnail');
        var ok_button = this.element.getElement('.dialog-ok-button');
        var path = '';
        var height = '';
        var width = '';
        thumbnails.each(function(el) {
            el.addEvent('click', function(){
                thumbnails.removeClass('selected');
                el.addClass('selected');
                path = el.get('path');
                height = el.get('h');
                width = el.get('w');
            });
        });

        ok_button.addEvent('click', function() {
            var x = self.element.getElement('#img_upload');
            x.set('value',path);
            x.set('h',height);
            x.set('w',width);
            self.dispWindow.closeWindow();
        });
    },

    getImages: function(ev) {
        this.request.get();
    },

    save: function(ev) {
        ev.stop();
        var self = this;

        form = this.element.getElement('#img_upload_form');
        var val = form.getElement('.browse');
        if (val.value) {
            this.spinner.addClass('active');
            this.helpText.set('html',"Image uploading..");
        } else {
            this.helpText.set('html',"Please select an image to upload");
        }
        var fd = new FormData(form);
        var req = new XMLHttpRequest();
        req.onload = function() {
            if (this.response == "ok") {
                self.helpText.set('html',"Image uploaded successfully");
                self.spinner.removeClass('active');
            }
        };
        req.open("POST",this.options.url,true);
        req.send(fd);
    }
});



var SelectModalWindow = new Class({
    Implements: [Options],

    options: {
        winSelector: '.select_wrapper',
        triggers: '.image-item',
        closeButton: '.dialog-cancel-button'
    },

    initialize: function(options) {
        var self = this;
        this.element = null;
        this.setOptions(options);
        this.win = $$(this.options.winSelector);
        this.triggers = $$(this.options.triggers);
        this.closeButton = this.win.getElement(this.options.closeButton);
        this.overlay = $('select_window_overlay');
        this.triggers.each(function (t) {
            t.addEvent('click', this.startWindow.bind(this));
        }.bind(this));
        this.closeButton.addEvent('click', this.closeWindow.bind(this));
    },

    startWindow: function(ev) {
        if(ev) ev.stop();
        this.overlay.setStyle('display', 'block');
        this.win.setStyle('display', 'block');
        this.reposition();
    },

    reposition: function() {
        var x = window.getSize().x;
        var y = window.getSize().y;
        var dy = this.win[0].getSize().y;
        var dx = this.win[0].getSize().x;
        var  left= (x-dx)/2;
        var top = (y-dy)/2;
        this.win[0].setStyles({
            'display': 'block',
            'top': top,
            'left': left,
        });
    },

    closeWindow: function(ev) {
        this.overlay.setStyle('display', 'none');
        this.win.setStyle('display', 'none');
    },

});