Description
===========

Module adds functionality necessary for working with **spare parts**


.. note:: Because of the known bug, for correct functionality this model requires
    the core to be patched

https://github.com/odoo/odoo/issues/5248

In */web/static/src/js/view_tree.js*
change the following line in the function **activate**

Line: 237:

    //var c = new instance.web.CompoundContext(local_context).set_eval_context(ctx);

    var c = new instance.web.CompoundContext(ctx);

Now the context is propagated to the next view.
