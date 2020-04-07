/*
---

name: Form.MultipleFileInput.extend
description: Extends Form.MultipleFileInput to disable provided file manager tool
license: MIT-style license.
authors: atelierZuppinger
requires: [Form.MultipleFileInput]
provides: Form.MultipleFileInput.extend

...
*/

Form.MultipleFileInput = new Class({
	
	Extends: Form.MultipleFileInput,
	
	add: function(file){
		this._files.push(file);
		var self = this;
		this.fireEvent('add', file);
		return this;
	},

	remove: function(file){
		var index = this._files.indexOf(file);
		if (index == -1) return this;
		this.fireEvent('remove', file);
		if (!this._files.length) this.fireEvent('empty');
		return this;
	}

});