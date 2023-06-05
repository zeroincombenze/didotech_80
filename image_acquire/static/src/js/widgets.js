openerp.image_acquire = function(instance, m)
{
	var _t = instance.web._t,
		_lt = instance.web._lt;
    QWeb = instance.web.qweb;
	
	instance.web.form.widgets = instance.web.form.widgets.extend(
	{
		'one2many_selectable' : 'instance.web.form.One2ManySelectable'
	});
	
	instance.web.form.One2ManySelectable = instance.web.form.FieldOne2Many.extend(
	{
		multi_selection: true,
	    start: function() 
	    {
	    	this._super.apply(this, arguments);
	    	var self=this;
	    	self.on("change:effective_readonly", this, function(){
	    		if (this.get("effective_readonly"))
	    			self.$(".ep_button_confirm").attr("disabled", "");
	    		else
	    			self.$(".ep_button_confirm").removeAttr("disabled", "");
	    	});
			// self.$(".ep_button_confirm").removeAttr("disabled", "");
	    	this.$el.prepend(QWeb.render("One2ManySelectable", {widget: this}));
	        this.$el.find(".ep_button_confirm").click(function(){
	        	self.action_selected_lines();
	        });
	   },

	   action_selected_lines: function()
	   {
		   var self=this;
		   selected_ids=self.get_selected_ids_one2many();
		   if (selected_ids.length===0)
		   {
			   new instance.web.Dialog(this, {
                   title: _t("Warning"),
                   size: 'medium',
               }, $("<div />").text(_t("You must choose at least one record."))).open();
               return false;
		   }
		   for(i=0; i<selected_ids.length; i++)
		   {
			   if(isNaN(selected_ids[i]))
			   {
				   new instance.web.Dialog(this, {
	                   title: _t("Warning"),
	                   size: 'medium',
	               }, $("<div />").text(_t("Some selected items have not been saved! " +
	               		"Please save the record first before proceeding."))).open();
	               return false;
			   }
		   }
/*		   Uncomment the following lines and put your model name and function name to call your python function */
		   var model_obj=new instance.web.Model("wizard.select.image");

		   model_obj.call('action_move_images', [ selected_ids ], {
				context : self.dataset.context
		   }).then(function(result) {
			    self.view.reload();
		   });
	   },
	   get_selected_ids_one2many: function ()
	   {
	       var ids =[];
	       this.$el.find('th.oe_list_record_selector input:checked')
	               .closest('tr').each(function () {
	               	ids.push(parseInt($(this).context.dataset.id));
	       });
	       return ids;
	   }
	});
}