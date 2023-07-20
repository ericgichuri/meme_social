$(document).ready(function(){
	$(".btn_signup").click(function(){
		window.location.href="/register"
	})
	$(".form_login").on("submit",function(e){
		e.preventDefault()
		var formdata=new FormData(this)
		$.ajax({
			url:"/login/process_login",
			method:"post",
			data:formdata,
			processData:false,
			contentType:false,
			success:function(response){
				if(response.message=="1"){
					$(".info_text").text("Login Successful. \nplease wait")
					$(".info_text").css("color","green")
					$(".form_login")[0].reset()
					window.setTimeout(waiting_redirect,3000)
				}else{
					$(".info_text").text(response.message)
					$(".info_text").css("color","#FF0066")
				}
				
			}
		})
	})
	function waiting_redirect(){
		window.location.href="/home"
	}
})