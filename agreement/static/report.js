$(document).ready(function(){
  console.log("function");
    $('a').click(function(e){
      e.preventDefault();
        console.log("report");
          var agreement_type= $('#myinput').val();
          var status = $('#status').val();
          var sdate = $('#sdate').val();
          var edate = $('#edate').val();
          console.log(agreement_type+status+sdate+edate);
            $.ajax({
              url:"/mis_status_report",
              data:{
                      'sdate':sdate,
                      'edate':edate,
                      'agreement_type':agreement_type,
                      'status':status,

                    },
              success:function(data){
                console.log("Success");
                obj=JSON.parse(data)
                for(var item in obj['context'])
                {
                  if(item=="agreement_type")
                  {
                    console.log(obj['context'][item]);
                    $("#agreement_type").val(obj['context'][item]);
                  }
                  if(item=="sdate")
                  {
                    $("#sdate").val(obj['context'][item]);
                  }
                  if(item=="edate")
                  {
                    $("#edate").val(obj['context'][item]);
                  }
              }
                location.href = "http://127.0.0.1:8000/status/";

                // $("#status").val(data.a_status);

              }
            });
        });
  });