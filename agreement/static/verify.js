$(document).ready(function(){

    $('#getcode').click(function(){
        console.log("getcode");
          var c_id= $('#c_id').val();
          var sign = $('#sign').val();
          var mobile_no = $('#mobileno').val();
            $.ajax({
              url:"/generateotp",
              data:{
                      'mobile_no':mobile_no,
                      'c_id':c_id,
                      'sign':sign,

                    },
              success:function(data){
                gen_otp=mobile_no;
                console.log("Success");
                $("#generateotp").html(data);
              }
            });
        });
    
    $('#agreementdownload').click(function(){
        var c_id= $('#c_id').val();
          console.log(c_id);
          console.log("Yes");
            $.ajax({
              url:"/send_sign_email",
              data:{
                      'c_id':c_id,
                  },
              success:function(data){
                console.log("Success");
               $("#mainbox").html(data);
               $('#agreementdownload').css('visibility','hidden');
                $('#addsign').css('visibility','hidden');  
                
              }
            });
        });
    $('#resend').click(function(){
        console.log("resend");
          var c_id= $('#c_id').val();
          var sign = $('#sign').val();
          var mobile_no=$('#resend').val();
            $.ajax({
              url:"/generateotp",
              data:{
                      'mobile_no':mobile_no,
                      'c_id':c_id,
                      'sign':sign,

                    },
              success:function(data){
                console.log("Success");
                $("#generateotp").html(data);
              }
            });
        });

        

        $('#confirm').click(function(){
          var user_otp = $('#otp').val();
          var gen_otp=$('#confirm').val();
          console.log(gen_otp);
          console.log("Success fr");
          
          if(user_otp==gen_otp)
          {
            console.log("Verified");
            alert('OTP verification Success!!! ')
            if ($('#generateotp').css('visibility') == 'visible')
          {
                 $('#generateotp').css('visibility','hidden'); 
                 $('#verifyotp').css('visibility','hidden');
                  $('#agreementdownload').css('visibility','visible'); 
          }
           
            
          }
          else{
             console.log("Not Verified");
            alert('OTP verification failed, Try Again!!!')

          }
        });
      });
