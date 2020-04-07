var SidebarMenu = new Class({
    Implements: [Events, Options],
    options: {
        subMenuItems: '.item',
        subMenu: 'section'
    },

    initialize: function(nav, options) {
        this.setOptions(options);
        this.element = nav;
        this.subMenuItems = this.element.getElements(this.options.subMenuItems);
        this.children = nav.getElements(this.options.subMenuItems);
        this.current = false;
        var self = this;
        this.children.addEvent('click', function(ev){
            self.clicked(ev, this);
        });
        $(window).addEvent('click', function(ev){
            var is_nav = $(ev.target).getParents().contains(self.element);
            if(!is_nav) self.hide();
        });

        this.sspy = new ScrollSpy();
        this.sspy.addEvent('tick', function(){
            console.log('tick', arguments);
        });
    },

    clicked: function(ev, item) {
        var siblings = item.getSiblings(this.options.subMenu);
        var self = this;
        if(siblings.length > 0) {
            ev.stop();
            var section = siblings[0];
            self.show(item, section);
        } else {
            this.hide();
        }
    },

    show: function(item, section) {
        var parentContainer = section.getParents('li');
        if(this.current) {
            this.current.hide();
            var selectedItem = this.current.getParents('li');
            selectedItem.removeClass('open');
        }
        parentContainer.addClass('open');
        section.show();
        this.current = section;
    },

    hide: function() {
        if (this.current){
            this.current.hide();
            var selectedItem = this.current.getParents('li');
            selectedItem.removeClass('open');
            this.current = false;
        }
    }
});


//The base UI Controller; specific pages can override this.
var UIController = new Class({
    Implements: [Events, Options],

    options: {},

    initialize: function(options){
        this.setOptions(options);
        window.addEvent('domready', this.ready.bind(this));
        window.addEvent('load', this.loaded.bind(this));
    },

    ready: function(){
        this.nav = new SidebarMenu($$('nav section.nav')[0]);
    },

    loaded: function() {// sideMenuBar hovering
        console.log('loaded');
    },

});


var FormController = new Class({
    Extends: UIController,
    options: {
        content_css: false,
        fields: [], //configurations for each field in the form
    },

    initialize: function(options) {
        this.parent(options);
    },

    ready: function(){
        this.parent();

        tinymce.init({
            //https://www.tinymce.com/docs/configure/integration-and-setup/
            selector: '.richtext',
            height: 500,
            theme: 'modern',
            plugins: [
                'advlist autolink lists link image charmap print preview hr anchor pagebreak',
                'searchreplace wordcount visualblocks visualchars fullscreen',
                'insertdatetime media nonbreaking save table contextmenu directionality',
                'emoticons template paste textcolor colorpicker textpattern imagetools'
            ],
            toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | print preview media fullscreen | forecolor backcolor emoticons',
            image_advtab: true,
            removed_menuitems: 'newdocument',
            templates: [
                { title: 'Test template 1', content: '<h3>Test 1</h3>' },
                { title: 'Test template 2', content: 'Test 2' }
            ],

            content_css : this.options.content_css
        });
    }
})

