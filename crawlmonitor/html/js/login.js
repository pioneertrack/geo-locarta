$(document).ready(function(){
    $("#btn-login").click(function(){
        var name = $("#name").val();
        var password = $("#key").val();
    // Checking for blank fields.
        if( name =='' || password ==''){
            alert("Please fill all fields.");
        }else {
            $.post("api/login",{ name: name, password:password},
            function(data) {
                if(data["token"])
                {
                    Cookies.set('token', data["token"], { expires: 7 });
                    window.location.href = "./index.html";
                }
                
            }) .fail(function(error) { alert("login failed") });
        }
    });
});