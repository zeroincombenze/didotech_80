$(document).ready(function () {
    $('.oe_website_sale #add_to_cart, .oe_website_sale #products_grid .a-submit')
        .off('click')
        .removeClass('a-submit')
        .click(function (event) {
			
        var $link = $(event.currentTarget);
        var $input = $link.parent().find("input[name='add_qty']");
        var $input_product = $link.parent().find("input[name='product_id']");
        var $product_id = parseInt($input_product.val(),10);
        if(!$product_id) {
            $product_id = parseInt($input.data('product-id'),10);
        }        
        var value = parseInt($input.val(), 10);
        var line_id = parseInt($input.data('line-id'),10);
        if (isNaN(value)) value = 0;
        openerp.jsonRpc("/shop/cart/update_json", 'call', {
            'line_id': line_id,
            'product_id': $product_id,
            'set_qty': value})
            .then(function (data) {
                if (!data.quantity) {
                    location.reload();
                    return;
                }
                var $q = $(".my_cart_quantity");
                //$q.parent().parent().removeClass("hidden", !data.quantity);
                $q.html(data.cart_quantity).hide().fadeIn(600);

                $input.val(data.quantity);
                
                $('.css_quantity[data-product-id='+parseInt($input.data('product-id'),10)+']').removeClass("hidden", !data.quantity)
                
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                $("#cart_total").replaceWith(data['website_sale.total']);
            });
        
        //$(this).closest('form').submit();
    });

    $(".oe_website_sale .oe_product input.js_quantity").change( function () {
//        alert("website_sale_qty : hello qty changed to input box ");
        var $input = $(this);
        var value = parseInt($input.val(), 10);
        var line_id = parseInt($input.data('line-id'),10);
        if (isNaN(value)) value = 0;
        openerp.jsonRpc("/shop/cart/update_json", 'call', {
            'line_id': line_id,
            'product_id': parseInt($input.data('product-id'),10),
            'set_qty': value})
            .then(function (data) {
                if (!data.quantity) {
                    location.reload();
                    return;
                }
                var $q = $(".my_cart_quantity");
                $q.parent().parent().removeClass("hidden", !data.quantity);
                $q.html(data.cart_quantity).hide().fadeIn(600);

                $input.val(data.quantity);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                $("#cart_total").replaceWith(data['website_sale.total']);
            });
    });
});


// replace hack
//function createjscssfile(filename, filetype){
//    if (filetype=="js"){ //if filename is a external JavaScript file
//        var fileref=document.createElement('script')
//        fileref.setAttribute("type","text/javascript")
//        fileref.setAttribute("src", filename)
//    }
//
//return fileref
//}
//
//function replacejscssfile(oldfilename, newfilename, filetype){
// var targetelement=(filetype=="js")? "script" : (filetype=="css")? "link" : "none" //determine element type to create nodelist using
// var targetattr=(filetype=="js")? "src" : (filetype=="css")? "href" : "none" //determine corresponding attribute to test for
// var allsuspects=document.getElementsByTagName(targetelement)
// for (var i=allsuspects.length; i>=0; i--){ //search backwards within nodelist for matching elements to remove
//  if (allsuspects[i] && allsuspects[i].getAttribute(targetattr)!=null && allsuspects[i].getAttribute(targetattr).indexOf(oldfilename)!=-1){
//   var newelement=createjscssfile(newfilename, filetype)
//   allsuspects[i].parentNode.replaceChild(newelement, allsuspects[i])
//   filesadded[oldfilename] = 0;
//   filesadded[newfilename] = 1;
//  }
// }
//}
//
//replacejscssfile("website_sale.js", "website_sale_mod.js", "js") //Replace all occurences of "oldscript.js" with "newscript.js"