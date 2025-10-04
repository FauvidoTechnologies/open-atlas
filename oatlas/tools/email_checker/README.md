# Email verifier

If any emails are found during searches, this tool helps in verifying if that email address actually exists.

Implementation borrowed from: https://email-checker.net/check

1. Check if email address is of valid format (regexes)
2. Check if the domain name is valid (email addresses can be disposable, but the domain should exist somewhere!)
3. Extract MX records from the domain records and connects to that email server (over SMTP and simulates sending a message) to make sure the mailbox really exists.

This is achieved using a random leaked email list from the internet which servers as a "from" address. The domain is picked from that same email address. This makes the requests more believable.