var PublishControl = new Class({
    Implements: [Options],
    options: {
        container: '.publishing_controls',
        actual_publish_selector: 'id_status',
        actual_is_active: 'id_is_active',
        actual_publish_date: 'id_published_date_0',
        actual_publish_time: 'id_published_date_1',
        date_time_container: '.pub_date_time'
    },

    initialize: function(options) {
        this.setOptions(options);
        if ($$(this.options.container).length) {
            this.container = $$(this.options.container)[0];
            this.publish_selector = this.container.getElement('select');
            this.is_active = this.container.getElementById('pub_active');
            this.publish_date = this.container.getElementById('pub_date_0');
            this.publish_time = this.container.getElementById('pub_date_1');
            this.date_time_container = this.container.getElement(this.options.date_time_container);
            this.actual_publish_selector = $(this.options.actual_publish_selector);
            this.actual_is_active = $(this.options.actual_is_active);
            this.actual_publish_date = $(this.options.actual_publish_date);
            this.actual_publish_time = $(this.options.actual_publish_time);
            this.setData();
            this.stylefix();
            this.publish_selector.addEvent('change', this.publishSelectorChange.bind(this));
            this.is_active.addEvent('click', this.isActiveChange.bind(this));
            this.publish_date.addEvent('focus', this.publisDateChange.bind(this));
            this.publish_date.addEvent('change', this.publisDateChange.bind(this));
            this.publish_time.addEvent('focus', this.publisTimeChange.bind(this));
            this.publish_time.addEvent('change', this.publisTimeChange.bind(this));
        }
    },

    setData: function() {
        if (this.actual_is_active.checked) this.is_active.checked = true;
        var value = this.actual_publish_selector.get('value');
        this.publish_selector.set('value', value);
        if (value == 'P')
            this.date_time_container.addClass('show');
        else
            this.date_time_container.removeClass('show');
        this.publish_date.set('value', this.actual_publish_date.get('value'));
        this.publish_time.set('value', this.actual_publish_time.get('value'));
    },

    stylefix: function() {
        var pub = $$('.publishing_controls')[0];
        var control = $$('.object-tools')[0];
        if (pub && control) {
            control.setStyle('right', 210);
        }
    },

    publishSelectorChange: function(ev) {
        var publish_selector_value = this.publish_selector.get('value');
        this.actual_publish_selector.set('value', publish_selector_value);
        if (publish_selector_value == 'P')
            this.date_time_container.addClass('show');
        else
            this.date_time_container.removeClass('show');
    },

    isActiveChange: function(ev) {
        this.actual_is_active.checked = this.is_active.checked;
    },

    publisDateChange: function(ev) {
        this.actual_publish_date.set('value', this.publish_date.get('value'));
    },

    publisTimeChange: function(ev) {
        this.actual_publish_time.set('value', this.publish_time.get('value'));
    }

});

window.addEvent('domready', function(){
    if ($$('.publishing_controls').length > 0)
        new PublishControl();

    if ($$('textarea').length) {
        var overlay = new Element('div',{'id': "select_window_overlay"});
        var wrapper = new Element('div',{'class': "select_wrapper"});
        overlay.inject($(document.body));
        wrapper.inject($(document.body));
    }

    $$('textarea').each(function(el) {
        el.mooEditable({
            'dimensions': { 
                x: '800px',
                y: '450px'
            }
        });
    })
});

