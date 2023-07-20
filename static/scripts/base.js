$(document).ready(function(){
	$(".toggle_menu").click(function(){
		$(".maincontainer").toggleClass("showmenu")
		$(".toggle_menu span").toggleClass('fa-bars fa-close')
	})
	$(".button_home").click(function(){
		window.location.href="/home"
	})
	$(".button_search").click(function(){
		window.location.href="/search"
	})
	$(".button_follows").click(function(){
		window.location.href="/follow"
	})
	$(".button_post").click(function(){
		window.location.href="/post"
	})
	$(".button_notifys").click(function(){
		window.location.href="/notifications"
	})
	$(".button_profile").click(function(){
		window.location.href="/profile"
	})
	$(".button_settings").click(function(){
		window.location.href="/settings"
	})
	$(".button_logout").click(function(){
		confirm_msg=confirm("Do you want to logout?")
		if(confirm_msg==true){
			window.location.href="/logout"	
		}
		
	})
})