So that is a 6000+ line codebase that I need to clean and merge. The only reason I am doing this is because the API library that is available for Nettacker is so fucking outdated. There is not one line of code that I have written which exists there so its that old.

let's start from the basics

1. Add dependencies

	a. Couldn't add `impacket` as a dependency, not sure what can fuck up, let's see
	b. Next step is to expose the APIs and remove CLI support

2. Remove unncessary files

	a. no tests, pyproject or poetry. Its all there in the root anyways and I don't care about tests yet.
	b. don't need the Nettacker entrypoint cause we aren't running it through that. Fuck this is gonna be hard man.
	c. removed version.py
	d. removed the web directory because we aren't doing any web thing with nettacker
	e. removed the main.py entrypoint cause again, we need modular functions and not entrypoints
	f. removed `logo.txt`

	We technically don't need the databases as well, I will just implement a nettacker schema locally so I don't have to use that.
	We'll need a database becaues the core architecture is based on that. Trust me bro.

	- We'll probably just need `TempEvents` and `HostLogs` with us. The reportdb is not needed. These I will copy over to my own `models.py` file
	- From the database functions, we'll just need the following functions (rest are either implemented or not needed)


	# This is still left
	Note that we'll have to make major changes to the config files. Remove all unncessary stuff and migrate the paths... including names of the database!

	- Working on the logger file now, implement the other loggers inside out logger file
	- Removed the `api` directory as well because that is completely flask and web stuff, not needed

	Now the goal is to remove arg_parser and make everything like a function argument thing inside app.py

	- removed `graph` and `compare_report` because we aren't doing that shit
	- removed all the mysql, sqlite, and postgres code inside database cause again that's redundant, oh and all `models.py`.
	- we don't need to `get_logs_by_scanid` because we're not using `graph.py` cause we don't want to get that sorta outputs. We do want a nice json output that's all 
	- After these changes, removed `database` directory
	- removed `die.py`, `fuzzer.py`, `graph.py`, 

	Time to change config -> The idea is to push this to the main config and call everything relevant from there
	- Replicated the config and removed it now. make sure to use the Nettacker class for its specific settings (the paths are inside `Config.path` only)


	NOW WE'RE AT app.py aahhhh, firstly imports