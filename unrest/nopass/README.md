# Django no pass

Another passwordless login for Django. Currently part of django unrest, but will eventually be it's own repo.

# Installation
========

Add the urls to your main url file:

```
urlpatterns = [
   ...
   url("api/nopass/",include("nopass.urls")),
]

# Endpoints
=========

* `create/` - Creates a new user and logs in the current session as this user. At this point the user is anonymous and has no recovery method.

* `change_email/` - Posting an email address to this url will set the current users email.

* `send/` - Posting an email address to this url will send a login link to that address.

* `<uidb64>/<token>/` - Link sent to email address. If valid and not expired, this will log the user in.

* `bad_token/` - redirect url for bad or expire tokens.

