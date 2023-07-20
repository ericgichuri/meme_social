$(document).ready(function(){
	$(".button_next").click(function(){
		var next_block=$(this).attr('data_next')
		if(next_block=="1"){
			$(".block").removeClass('block_active')
			$(".block.block1").addClass('block_active')
		}else if(next_block=="2"){
			$(".block").removeClass('block_active')
			$(".block.block2").addClass('block_active')
		}
	})
	$(".button_prev").click(function(){
		var prev_block=$(this).attr('data_prev')
		if(prev_block=="0"){
			$(".block").removeClass('block_active')
			$(".block.block0").addClass('block_active')
		}else if(prev_block=="1"){
			$(".block").removeClass('block_active')
			$(".block.block1").addClass('block_active')
		}
	})
	$(".btn_signin").click(function(){
		window.location.href="/login"
	})
	$(".button_upload").change(function(e){
		var file=URL.createObjectURL(e.target.files[0])
		$(".image_preview").attr("src",file)
	})
	$(".button_cancel_image").click(function(){
		$(".image_preview").attr("src","")
		$(".button_upload").val("")
	})
	$(".form_register").on("submit",function(e){
		e.preventDefault()
		var formdata=new FormData(this)
		$.ajax({
			url:"/register/process_register",
			method:"post",
			data:formdata,
			processData:false,
			contentType:false,
			success:function(response){
				if(response.message=="1"){
					$(".info_text").text("You have been register successfully. \nPlease Wait")
					$(".info_text").css("color","green")
					window.setTimeout(waiting_redirect,3000)
					$(".form_register")[0].reset()
				}else{
					$(".info_text").text(response.message)
					$(".info_text").css("color","#FF0066")
				}
			}
		})
	})
	function waiting_redirect(){
		window.location.href="/login"
	}
})