# Reverse insta lookups

This is a nice and legal way of scraping public and private profiles. I am techincally not violating any TOS enforced by Meta at all. The way this is being done is as follows:

1. Search for a profile using `https://instagram.com/<username>`
2. If the username exists, we'll get to see a HTML page. Instagram renders the HTML page and then tells you to sign in to view that. This means we can directly catch the HTML page if we hit this URL with a GET request.

From the HTML the following information can be extracted:

- [x] The number of followers and following for public and private accounts
- [x] The number of posts for public and private accounts
- [x] The profile picture for public and private accounts
- [ ] Posts and comments (upto last 10) for public accounts (not sure how that will work)

The only problem is that insta will block my IP if I make continued requests. So need to figure out a way to bypass that.

Okay Instagram will not block my IP like that. The only thing I need to take care of is the user-agent. If I make it too much like a real browser's request then we're fucked because then it will give me a popup for login thinking that I am a real human interacting with it.