db.createUser({
	user: "admin",
	pwd: "admin",
	role:[
		{role:"readWrite", db="admin"}
	]

});