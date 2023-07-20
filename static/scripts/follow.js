$(document).ready(function(){
	$(".p_holder").click(function(){
		var username=$(this).attr("connect_username")
		window.location.href="/user/"+username
	})
	$(".button_connect").click(function(){
		var following_id=$(this).attr("following_id")
		$.ajax({
			url:"/follow/following",
			method:"post",
			data:{following_id:following_id},
			success:function(response){
				if(response.message=="1"){
					alert("Follow Successful")
					//$("#profile"+following_id).empty()
					window.location.href="/follow"
				}else{
					alert(response.message)
				}
			}
		})
	})
	$(".button_show_connect").click(function(){
		$(".inner_follow_holder").removeClass("active_follow_holder")
		$(".connect_holder").addClass("active_follow_holder")
		$(".follow_nav .inner_follow_nav button").removeClass("active_button")
		$(this).addClass('active_button')
	})
	$(".button_show_followers").click(function(){
		$(".inner_follow_holder").removeClass("active_follow_holder")
		$(".followers_holder").addClass("active_follow_holder")
		$(".follow_nav .inner_follow_nav button").removeClass("active_button")
		$(this).addClass('active_button')
	})
	$(".button_show_following").click(function(){
		$(".inner_follow_holder").removeClass("active_follow_holder")
		$(".following_holder").addClass("active_follow_holder")
		$(".follow_nav .inner_follow_nav button").removeClass("active_button")
		$(this).addClass('active_button')
	})
})