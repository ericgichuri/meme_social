from flask import Flask,redirect,url_for,render_template,session,abort,jsonify,request
import os,time,bcrypt,re
import mysql.connector

app=Flask(__name__)
app.config['SECRET_KEY']="memesocial"

# database configurations
dbhost="localhost"
dbuser="root"
dbpass=""
dbname="memesocial"
# connection
conn=mysql.connector.connect(host=dbhost,user=dbuser,password=dbpass)
# create database
try:
	cursor=conn.cursor()
	sql="CREATE DATABASE IF NOT EXISTS %s"%(dbname)
	cursor.execute(sql)
	conn.commit()
except Exception as e:
	abort(400)

# new connection
conn=mysql.connector.connect(host=dbhost,user=dbuser,password=dbpass,database=dbname)

# create table users
try:
	cursor=conn.cursor()
	sql="""CREATE TABLE IF NOT EXISTS users(
		userid int NOT NULL AUTO_INCREMENT PRIMARY KEY,
		firstname varchar(20) NOT NULL,
		lastname varchar(20) NOT NULL,
		date_of_birth date NOT NULL,
		phoneno varchar(20) NOT NULL UNIQUE KEY,
		email varchar(50) NOT NULL UNIQUE KEY,
		username varchar(30) NOT NULL UNIQUE KEY,
		password varchar(100) NOT NULL,
		profile varchar(30) NOT NULL,
		approval varchar(10) NOT NULL,
		date_joined date NOT NULL
	)"""
	cursor.execute(sql)
	conn.commit()
except Exception as e:
	abort(400)

# create table posts
try:
	cursor=conn.cursor()
	sql="""CREATE TABLE IF NOT EXISTS posts(
		postid int NOT NULL AUTO_INCREMENT PRIMARY KEY,
		post_photo varchar(40) NOT NULL,
		post_caption varchar(1000) NOT NULL,
		hash_tag varchar(50) NOT NULL,
		author_id int NOT NULL,
		date_posted date NOT NULL
	)"""
	cursor.execute(sql)
	conn.commit()
except Exception as e:
	abort(400)

# create table comment
try:
	cursor=conn.cursor()
	sql="""CREATE TABLE IF NOT EXISTS comments(
		commentid int NOT NULL AUTO_INCREMENT PRIMARY KEY,
		cooment varchar(200) NOT NULL,
		postid int NOT NULL,
		commentor_id int NOT NULL,
		author_id int NOT NULL,
		comment_status varchar(10) NOT NULL,
		date_commented date NOT NULL
	)"""
	cursor.execute(sql)
	conn.commit()
except Exception as e:
	abort(400)

# create table like
try:
	cursor=conn.cursor()
	sql="""CREATE TABLE IF NOT EXISTS likes(
		likeid int NOT NULL AUTO_INCREMENT PRIMARY KEY,
		postid int NOT NULL,
		liker_id int NOT NULL,
		like_status int NOT NULL,
		date_liked date NOT NULL
	)"""
	cursor.execute(sql)
	conn.commit()
except Exception as e:
	abort(400)

# create table follows
try:
	cursor=conn.cursor()
	sql="""CREATE TABLE IF NOT EXISTS follows(
		follow_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
		following_id int NOT NULL,
		follower_id int NOT NULL,
		confirmed int NOT NULL,
		date_followed datetime NOT NULL,
		date_confirmed date NOT NULL
	)"""
	cursor.execute(sql)
	conn.commit()
except Exception as e:
	abort(400)

# today
today=time.strftime("%Y-%m-%d")

# check if profile folder exists
cur_folder=os.getcwd()
profiles_folder=f'{cur_folder}\\static\\profile_images\\'
if not os.path.exists(profiles_folder):
	os.makedirs(profiles_folder)

meme_folder=f'{cur_folder}\\static\\meme_images\\'
if not os.path.exists(meme_folder):
	os.makedirs(meme_folder)

ALLOWED_EXTENSIONS={'png','jpg','gif','jpeg'}
# check file if is an image
def check_file(file):
	return "." in file and file.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

# home section
@app.route("/")
@app.route("/home")
def func_home():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	userid=session['userid']
	try:
		cursor=conn.cursor()
		sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			user_details=results
		else:
			user_details=""
	except Exception as e:
		user_details=""
		return redirect(url_for('func_login'))

	# get posts
	try:
		cursor=conn.cursor()
		#sql="SELECT posts.*,users.username,users.userid,users.profile FROM posts INNER JOIN users ON posts.author_id=users.userid"
		sql="""SELECT p.postid, p.post_photo, p.post_caption, p.hash_tag,p.author_id,p.date_posted, u.username,u.userid,u.profile, u.firstname, u.lastname, COUNT(l.likeid), l.liker_id AS like_count
			FROM posts p
			JOIN users u ON p.author_id = u.userid
			LEFT JOIN likes l ON p.postid = l.postid
			GROUP BY p.postid, p.post_photo, p.post_caption, p.hash_tag, u.username,u.userid,u.profile, u.firstname, u.lastname ORDER BY p.postid DESC"""
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			all_posts=results
		else:
			all_posts=""
	except Exception as e:
		all_posts=""
	return render_template("index.html",user_details=user_details,all_posts=all_posts)

# login section
@app.route("/login")
def func_login():
	return render_template("login.html")

# process login user
@app.route("/login/process_login",methods=["POST"])
def func_process_login():
	if request.method=="POST":
		email=request.form['email']
		password=request.form['password']
		if email=="":
			msg="Email is empty"
		elif password=="":
			msg="Password is empty"
		else:
			try:
				cursor=conn.cursor()
				sql="SELECT userid,username,password FROM users WHERE email='%s'"%(email)
				cursor.execute(sql)
				results=cursor.fetchall()
				if results:
					db_pass=results[0][2].encode('utf-8')
					input_password=password.encode('utf-8')
					if bcrypt.checkpw(input_password,db_pass)==True:
						msg="1"
						session['userid']=results[0][0]
					else:
						msg="Invalid username or password"
				else:
					msg="User does not exists"
			except Exception as e:
				msg=str(e)

		return jsonify({"message":msg})

# register
@app.route("/register")
def func_register():
	return render_template("register.html")

# process register user
@app.route("/register/process_register",methods=["POST"])
def func_process_register():
	if request.method=="POST":
		fname=request.form['firstname']
		lname=request.form['lastname']
		date_of_birth=request.form['date_of_birth']
		phoneno=request.form['phoneno']
		email=request.form['email']
		username=request.form['username']
		password=request.form['password']
		confirm_password=request.form['confirm_password']
		if fname=="" or lname=="" or date_of_birth=="" or phoneno=="" or email=="" or username=="" or password=="" or confirm_password=="":
			msg="Please fill every field !"
		else:
			# check phone no
			pattern='[+]\d{12}'
			phone_matches=re.findall(pattern,phoneno)
			if phone_matches:
				pattern2='[a-z0-9A-Z]*@[a-z0-9A-Z]*\.[a-zA-Z]*'
				email_match=re.findall(pattern2,email)
				if email_match:
					if password!=confirm_password:
						msg="Password does not match"
					else:
						profile_pic=request.files['profile_pic']
						filename=profile_pic.filename
						if filename=="":
							msg="Select Profile Photo"
						elif check_file(filename)==False:
							msg="Invalid Image (Allowed PNG,JPG,GIF,JPEG)"
						else:
							# profile rename
							profilerename=f"propic{str(fname)[0]}{str(lname)[0]}_{time.strftime('%H%M%S')}.png"
							# hash password
							password_encoded=password.encode('utf-8')
							hashed_password=bcrypt.hashpw(password_encoded,bcrypt.gensalt())
							# check if username exists
							try:
								cursor=conn.cursor()
								sql="SELECT * FROM users WHERE username='%s'"%(username)
								cursor.execute(sql)
								results=cursor.fetchall()
								if results:
									msg="Select Another username"
								else:
									cursor=conn.cursor()
									sql="INSERT INTO users(firstname,lastname,date_of_birth,phoneno,email,username,password,profile,approval,date_joined) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
									values=(fname,lname,date_of_birth,phoneno,email,username,hashed_password.decode('utf-8'),profilerename,'False',today)
									cursor.execute(sql%values)
									conn.commit()
									profile_pic.save(profiles_folder+"//"+profilerename)
									msg="1"
							except Exception as e:
								msg=str(e)
							
				else:
					msg="Email is invalid"
			else:
				msg="phoneno is invalid"
		return jsonify({"message":msg})

# logout
@app.route("/logout")
def func_logout():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	else:
		session.pop('userid',None)
		return redirect(url_for('func_login'))

# posts
@app.route("/post")
def func_post():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	userid=session['userid']
	try:
		cursor=conn.cursor()
		sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			user_details=results
		else:
			user_details=""
	except Exception as e:
		user_details=""
		return redirect(url_for('func_login'))
	return render_template("post.html",user_details=user_details)

# follow
@app.route("/follow")
def func_follow():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	userid=session['userid']
	try:
		cursor=conn.cursor()
		sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			user_details=results
		else:
			user_details=""
	except Exception as e:
		user_details=""
		return redirect(url_for('func_login'))

	# get people to connect
	try:
		cursor=conn.cursor()
		sql="SELECT users.userid,users.username,users.profile FROM users"
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			connect_people=results
		else:
			connect_people=""
	except Exception as e:
		connect_people=""

	# get my followers
	try:
		cursor=conn.cursor()
		sql="SELECT users.userid,users.username,users.profile,follows.follower_id FROM users INNER JOIN follows ON users.userid=follows.follower_id WHERE follows.following_id='%s'"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			my_followers=results
		else:
			my_followers=""
	except Exception as e:
		my_followers=""

	# get my following
	try:
		cursor=conn.cursor()
		sql="SELECT users.userid,users.username,users.profile,follows.follower_id FROM users INNER JOIN follows ON users.userid=follows.following_id WHERE follows.follower_id='%s'"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			my_followings=results
		else:
			my_followings=""
	except Exception as e:
		my_followings=""
	return render_template("follow.html",user_details=user_details,connect_people=connect_people,my_followers=my_followers,my_followings=my_followings)

# send follow
@app.route("/follow/following",methods=['POST'])
def func_follow_user():
	if request.method=="POST":
		userid=session['userid']
		following_id=request.form['following_id']
		if following_id=="":
			msg="Unable to follow"
		else:
			print("here")
			try:
				cursor=conn.cursor()
				# check is he is my follower or following
				sql="SELECT * FROM follows WHERE following_id='%s' AND follower_id='%s'"%(following_id,userid)
				cursor.execute(sql)
				results=cursor.fetchall()
				if results:
					msg="You have already followed"
				else:
					print("here1")
					cursor=conn.cursor()
					sql1="INSERT INTO follows(following_id,follower_id,confirmed,date_followed) VALUES('%s','%s','%s','%s')"
					values=(following_id,userid,1,today)
					cursor.execute(sql1%values)
					conn.commit()
					msg="1"
			except Exception as e:
				msg=str(e)

		return jsonify({"message":msg})

# profile
@app.route("/profile")
def func_profile():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	userid=session['userid']
	try:
		cursor=conn.cursor()
		sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			user_details=results
		else:
			user_details=""
	except Exception as e:
		user_details=""
		return redirect(url_for('func_login'))
	# get profile data
	try:
		cursor=conn.cursor()
		sql="SELECT userid,firstname,lastname,date_of_birth,phoneno,email,username,profile,date_joined FROM users WHERE userid='%s'"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			profile_id=results[0][0]
			profile_data=results
		else:
			profile_data=""
			return redirect(url_for('func_login'))
	except Exception as e:
		profile_data=""
		return redirect(url_for('func_login'))

	# select followers
	try:
		cursor=conn.cursor()
		sql="SELECT COUNT(follow_id) FROM follows WHERE follower_id='%s'"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			profile_followers=results[0][0]
		else:
			profile_followers=0
	except Exception as e:
		profile_followers=0

	# select following
	try:
		cursor=conn.cursor()
		sql="SELECT COUNT(follow_id) FROM follows WHERE following_id='%s'"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			profile_following=results[0][0]
		else:
			profile_following=0
	except Exception as e:
		profile_following=0

	# select posts
	try:
		cursor=conn.cursor()
		sql="SELECT * FROM posts WHERE author_id='%s'"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			my_posts=results
		else:
			my_posts=""
	except Exception as e:
		my_posts=""
	return render_template("profile.html",user_details=user_details,profile_data=profile_data,profile_followers=profile_followers,profile_following=profile_following,my_posts=my_posts)

# notifications
@app.route("/notifications")
def func_notifications():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	userid=session['userid']
	try:
		cursor=conn.cursor()
		sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			user_details=results
		else:
			user_details=""
	except Exception as e:
		user_details=""
		return redirect(url_for('func_login'))
	return render_template("notifications.html",user_details=user_details)

# search
@app.route("/search")
def func_search():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	userid=session['userid']
	try:
		cursor=conn.cursor()
		sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			user_details=results
		else:
			user_details=""
	except Exception as e:
		user_details=""
		return redirect(url_for('func_login'))
	return render_template("search.html",user_details=user_details)


# settings
@app.route("/settings")
def func_settings():
	if not 'userid' in session:
		return redirect(url_for('func_login'))
	userid=session['userid']
	try:
		cursor=conn.cursor()
		sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
		cursor.execute(sql)
		results=cursor.fetchall()
		if results:
			user_details=results
		else:
			user_details=""
	except Exception as e:
		user_details=""
		return redirect(url_for('func_login'))
	return render_template("settings.html",user_details=user_details)

@app.route("/user/<string:username>")
def func_get_user_profile(username):
	if username:
		if not 'userid' in session:
			return redirect(url_for('func_login'))
		userid=session['userid']
		try:
			cursor=conn.cursor()
			sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				user_details=results
			else:
				user_details=""
		except Exception as e:
			user_details=""
			return redirect(url_for('func_login'))

		# get profile data
		try:
			cursor=conn.cursor()
			sql="SELECT userid,firstname,lastname,date_of_birth,phoneno,email,username,profile,date_joined FROM users WHERE username='%s'"%(username)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				profile_id=results[0][0]
				profile_data=results
			else:
				profile_data=""
				return redirect(url_for('func_follow'))
		except Exception as e:
			profile_data=""
			return redirect(url_for('func_follow'))

		# select followers
		try:
			cursor=conn.cursor()
			sql="SELECT COUNT(follow_id) FROM follows WHERE follower_id='%s'"%(profile_id)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				profile_followers=results[0][0]
			else:
				profile_followers=0
		except Exception as e:
			profile_followers=0

		# select following
		try:
			cursor=conn.cursor()
			sql="SELECT COUNT(follow_id) FROM follows WHERE following_id='%s'"%(profile_id)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				profile_following=results[0][0]
			else:
				profile_following=0
		except Exception as e:
			profile_following=0

		# get user posts
		try:
			cursor=conn.cursor()
			sql="SELECT * FROM posts WHERE author_id='%s'"%(profile_id)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				user_posts=results
			else:
				user_posts=""
		except Exception as e:
			user_posts=""

		return render_template("users.html",user_details=user_details,profile_data=profile_data,profile_followers=profile_followers,profile_following=profile_following,user_posts=user_posts)
	else:
		return redirect(url_for('func_follow'))

@app.route("/post/add_post",methods=['POST'])
def func_add_post():
	userid=session['userid']
	if request.method=="POST":
		photo=request.files['meme_photo']
		caption=request.form['meme_caption']
		hashtag=request.form['meme_hashtag']
		if caption=="" or hashtag=="":
			msg="Every field must be filled !"
		else:
			filename=photo.filename
			if filename=="":
				msg="Select Meme image"
			elif check_file(filename)==False:
				msg="Invalid Image (Allowed PNG,JPG,JPEG,GIF)"
			else:
				# rename photo
				meme_photo_name=f'meme_{userid}_{time.strftime("%H%M%S")}.png'
				try:
					cursor=conn.cursor()
					sql="INSERT INTO posts(post_photo,post_caption,hash_tag,author_id,date_posted) VALUES('%s','%s','%s','%s','%s')"
					values=(meme_photo_name,caption,hashtag,userid,today)
					cursor.execute(sql%values)
					conn.commit()
					photo.save(meme_folder+"//"+meme_photo_name)
					msg="1"
				except Exception as e:
					conn.rollback()
					msg=str(e)
				
		return jsonify({"message":msg})

@app.route("/post/liking",methods=['POST'])
def func_like_post():
	if request.method=="POST":
		if not 'userid' in session:
			return redirect(url_for('func_login'))
		userid=session['userid']
		post_id=request.form['post_id']
		try:
			cursor=conn.cursor()
			# check if you have liked
			sql="SELECT  * FROM likes WHERE postid='%s' AND liker_id='%s' AND like_status='%s'"%(post_id,userid,1)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				msg="0"
			else:
				sql1="INSERT INTO likes(postid,liker_id,like_status,date_liked) VALUES('%s','%s','%s','%s')"
				values=(post_id,userid,1,today)
				cursor.execute(sql1%values)
				conn.commit()
				msg="1"
		except Exception as e:
			msg=str(e)
		return msg

@app.route("/viewpost/<string:username>.<int:post_id>")
def func_view_post(username,post_id):
	if username and post_id:
		if not 'userid' in session:
			return redirect(url_for('func_login'))
		userid=session['userid']
		try:
			cursor=conn.cursor()
			sql="SELECT userid,username,profile FROM users WHERE userid='%s' LIMIT 1"%(userid)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				user_details=results
			else:
				user_details=""
		except Exception as e:
			user_details=""
			return redirect(url_for('func_login'))
		
		# get post details
		try:
			cursor=conn.cursor()
			sql="SELECT * FROM posts WHERE postid='%s'"%(post_id)
			"""SELECT p.postid, p.post_photo, p.post_caption, p.hash_tag, u.userid, u.firstname, u.lastname, COUNT(l.likeid) AS like_count
				FROM posts p
				JOIN users u ON p.author_id = u.userid
				LEFT JOIN likes l ON p.postid = l.postid
				GROUP BY p.postid, p.post_photo, p.post_caption, p.hash_tag, u.userid, u.firstname, u.lastname WHERE p.postid='%s'"""%(post_id)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				posts=results
			else:
				posts=""
		except Exception as e:
			posts=""

		# get author details
		try:
			cursor=conn.cursor()
			sql="SELECT userid,username,profile,firstname,lastname FROM users WHERE username='%s'"%(username)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				author_details=results
			else:
				author_details=""
		except Exception as e:
			author_details=""

		# get no of likes posts has
		try:
			cursor=conn.cursor()
			sql="SELECT COUNT(likeid) FROM likes WHERE postid='%s'"%(post_id)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				total_likes=results
			else:
				total_likes=0
		except Exception as e:
			total_likes=0

		# get total comments 
		try:
			cursor=conn.cursor()
			sql="SELECT COUNT(commentid) FROM comments WHERE postid='%s'"%(post_id)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				total_comments=results
			else:
				total_comments=0
		except Exception as e:
			total_comments=0

		# get comments
		try:
			cursor=conn.cursor()
			sql="SELECT commentid,cooment,postid,commentor_id,author_id WHERE postid='%s'"%(post_id)
			cursor.execute(sql)
			results=cursor.fetchall()
			if results:
				post_comments_details=results
			else:
				post_comments_details=""
		except Exception as e:
			post_comments_details=""


		return render_template("viewposts.html",user_details=user_details,posts=posts,author_details=author_details,total_likes=total_likes,total_comments=total_comments,post_comments_details=post_comments_details)

"""SELECT p.postid, p.post_photo, p.post_caption, p.hash_tag, u.userid, u.firstname, u.lastname, COUNT(l.likeid) AS like_count
FROM posts p
JOIN users u ON p.author_id = u.userid
LEFT JOIN likes l ON p.postid = l.postid
GROUP BY p.postid, p.post_photo, p.post_caption, p.hash_tag, u.userid, u.firstname, u.lastname"""
@app.route("/viewpost/comment",methods=["POST"])
def func_comment_post():
	if not 'userid' in session:
		return redirect(url_for('func_login'))

	userid=session['userid']
	if request.method=="POST":
		post_id=request.form['post_id']
		comment=request.form['comment']
		author_id=request.form['author_id']

		try:
			cursor=conn.cursor()
			sql="INSERT INTO comments(cooment,postid,commentor_id,author_id,comment_status,date_commented) VALUES('%s','%s','%s','%s','%s','%s')"
			values=(comment,post_id,userid,author_id,'Not_Seen',today)
			cursor.execute(sql%values)
			conn.commit()
			msg="1"
		except Exception as e:
			msg=str(e)
		return msg

if __name__=="__main__":
	app.run(debug=True)