(function($){
$(document).ready(function(){
$(".preview").on('click', function (event) {
				var c_document= $(this).data('id');
				console.log("preview");
                console.log($(this).attr('id'));
                $("#myModal").css("display","block");
                $('.modal .modal-body').html(c_document);
            	if($(this).attr('id')=="")
            	{
            		alert("Agreement has been terminated");
                    $("#sendbutton").hide();
            	}
            	else
            	{
            		$("#sendbutton").attr("href", "email/verify/"+$(this).attr('id'));
                    $("#sendbutton").show();
            	}
});
});
})(django.jQuery);
			      				