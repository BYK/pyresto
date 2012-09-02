# Pyresto Bugzilla API

```py
from pyresto.apis.bugzilla import mozilla

mozilla.auth(username='<USERNAME>', password='<PASSWORD>')
bug = mozilla.Bug.get('774141')
print bug.id, bug.status, bug.summary
# 774141 NEW Add generic Bugzilla Python client API
```
