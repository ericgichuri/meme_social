$(document).ready(function(){
	$(".button_send_comment").click(function(){
		var post_id=$(this).attr("post_id");
		var comment=$("#comment_input").val()
		var author_id=$(this).attr("id")
		if(comment===""){
			alert("Comment is empty")
		}else{
			$.ajax({
				url:"/viewpost/comment",
				method:"post",
				data:{post_id:post_id,comment:comment,author_id:author_id},
				success:function(response){
					if(response==1){
						window.location.reload();
					}else{
						alert(response)
					}
				}
			})
		}
	})
})