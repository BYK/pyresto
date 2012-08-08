# Pyresto Bugzilla API

```py
import pyresto.apis.bugzilla as bugzilla

bugzilla.auth(username='<USERNAME>', password='<PASSWORD>')
bug = bugzilla.Bug.get('774141')
print bug.id, bug.status, bug.summary
# 774141 NEW Add generic Bugzilla Python client API
```
