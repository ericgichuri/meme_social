$(document).ready(function(){
	$(".button_upload").change(function(e){
		var file=URL.createObjectURL(e.target.files[0])
		$(".image_preview").attr("src",file)
	})
	$(".button_reset").click(function(){
		$(".image_preview").attr("src","")
	})
	$(".form_post_meme").on("submit",function(e){
		e.preventDefault()
		var formdata=new FormData(this)
		$.ajax({
			url:"/post/add_post",
			method:"post",
			data:formdata,
			contentType:false,
			processData:false,
			success:function(response){
				if(response.message=="1"){
					$(".info_text").text("Posted successful")
					$(".info_text").css("color","green")
					$(".form_post_meme")[0].reset()
					$(".image_preview").attr("src","")
				}else{
					$(".info_text").text(response.message)
					$(".info_text").css("color","#FF0066")
				}
			}
		})
	})
})