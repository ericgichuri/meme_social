$(document).ready(function(){
	$(".user_info_holder").click(function(){
		var username=$(this).attr("post_author")
		window.location.href="/user/"+username
	})
	$(".btn_like").click(function(){
		var post_id=$(this).attr("post_id")
		$.ajax({
			url:"/post/liking",
			method:"post",
			data:{post_id:post_id},
			success:function(response){
				if(response=="1"){
					current_likes=$("#btn_like"+post_id+" .likevalue").text()
					next_likes=parseInt(current_likes)+1
					$("#btn_like"+post_id+" .likevalue").text(next_likes)
					$("#btn_like"+post_id).css("color","#FF0066")
				}else if(response=="0"){
					
				}else{
					$(".alert-holder .alert").text(response)
					$(".alert-holder .alert").css("display","flex")
					$("#btn_like"+post_id).css("color","#000088")
					$(".alert-holder .alert").append('<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>')
				}
			}
		})
	})
	// view post
	$(".btn_comment").click(function(){
		var username=$(this).attr("author")
		var post_id=$(this).attr("post_id")
		window.location.href="/viewpost/"+username+"."+post_id
	})
})