(function($){
$(document).ready(function(){
    console.log("ready");
$('.field-is_Status .status').click(function(){

    console.log("Triggered");
    console.log($(this).val());
    if ( $(this).val() == 1 ) {
        status=$(this).val();
        $(this).toggleClass('green',false);
        $(this).val(0);
        $(this).toggleClass('red',true);
    }else if($(this).val() == 0){
        status=$(this).val();
        $(this).toggleClass('red',false);
        $(this).val(1);
        $(this).toggleClass('green',true);
    }
    
    var id =$(this).closest('tr').find(".action-select").val();
    console.log(id);
        $.ajax({
        url: "toggle_status",
        data : {  'id': id,
        'status': status },
        success : function(data) {
            console.log("toggled");
       
       }     
    });
    });
});
})(django.jQuery);