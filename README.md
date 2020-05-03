
For the Python only implementation (which is used by this library) see https://github.com/Amsterdam/python-audit-log


# DataPunt Flask Audit Log

DataPunt Audit Log is a simple Flask app that will log all incoming requests
and their corresponding responses to a configurable endpoint.

During the process request phase, the logger is attached to the Flask global `g`
object. Before returning a response the app can easily provide extra context.
In the teardown request phase the audit_log middleware will send the log.


## Links
- [Quick Start](#quick-start)
- [Settings](#settings)
- [Default Context Info](#default-context-info)
- [Custom Optional Context Info](#custom-optional-context-info)


## Quick start

1. Install using pip

    ```bash
    pip install datapunt_flask_audit_log
    ```
   
2. Add "flask_audit_log" middleware to your Flask app

    ```python
    from flask_audit_log.middleware import AuditLogMiddleware
    ...
    
    app = Flask('DemoApp')

    # Attach our middleware
    middleware = AuditLogMiddleware(app)
    ```

3. Set the AUDIT_LOG_EXEMPT_URLS setting to make sure certain urls will not be logged
(e.g. health check urls).

    ```python
    # If a URL path matches a regular expression in this list, the request will not be redirected to HTTPS.
    # The AuditLogMiddleware strips leading slashes from URL paths, so patterns shouldn’t include them, e.g.
    # [r'foo/bar$']

    # Use configuration from `app`
    app.config['AUDIT_LOG'] = {
      'EXEMPT_URLS': [],
      ...
    }
    ```

    At this point all requests/responses will be logged. For providing extra context
    (which you are strongly urged to do so), see next chapters.


## Settings

Settings for the Flask Audit Logger can be set using Flask's app.config under a 'AUDIT_LOG' as shown in the example
above. The following settings can be set to change the default behavior of the Audit Log library.

*EXEMPT_URLS*
A list of regex patterns to make sure certain urls will not be logged (e.g. health check urls).

*LOGGER_NAME*
Internal logger name used by the audit log. Leave None to use python-audit-log default ('audit_log')

*LOG_HANDLER_CALLABLE_PATH*
Log handler that determines what to do with the logs. Leave None to use python-audit-log default (write to stdout)

*LOG_FORMATTER_CALLABLE_PATH*
Log formatter that determines log formatting. Leave None to use python-audit-log default (AuditLogFormatter)

*USER_FROM_REQUEST_CALLABLE_PATH*
A function that gets the user from the request. Leave None to use the default which will only get the user's IP.


## Default context info

By default the audit log sends the following json structure per request:

```json
{
  "http_request": {
    "method": "get|post|head|options|etc..",
    "url": "https://datapunt.amsterdam.nl?including=querystring",
    "user_agent": "full browser user agent"
  },
  "http_response": {
    "status_code": "http status code",
    "reason": "http status reason",
    "headers": {
      "key": "value"
    }
  },
  "user": {
    "authenticated": "True/False",
    "provider": "auth backend the user authenticated with",
    "realm": "optional realm when using keycloak or another provider",
    "email": "email of logged in user",
    "roles": "roles attached to the logged in user",
    "ip": "ip address"
  }
}
```
    
Each json entry is set by its corresponding method. In this case,
the middleware sets them automatically by calling
`set_http_request()` and `set_user_fom_request()`
in the before_request method. In the after_request method the
last data is set by invoking `set_http_response()`.

After the response has been processed the middleware creates the
log item by calling `send_log()` in teardown_request.
    
## Custom optional context info

Per request it is possible to add optional context info. For a complete
audit log, you are strongly urged to add more info inside your view.

Adding extra context is quite simple. The audit_log object has been added
to the request by the middleware. Therefore every view can simply access
it via the request object.

### Filter
`q.audit_log.set_filter(self, object_name, fields, terms)` allows to provide
info on the requested type of object and the filters that have been used
(a user searches for 'terms', which are matched on specific 'fields' of the
'object').

This method will add the following details to the log:

```json
"filter": {
      "object": "Object name that is requested",
      "fields": "Fields that are being filtered on, if applicable",
      "terms": "Search terms, if applicable"
  }
```

### Results
`g.audit_log.set_results(self, results)` allows to pass a json dict
detailing exactly what results have been returned to the user.

It is up to the developer to decide whether the amount of
data that would be added here will become a burden instead
of a blessing.

This method will add the following details to the log:

```json
"results": {
    ...
  }
```

### Message and loglevel
At last, a log message and loglevel can be provided to indicate
what the request is actually doing. This is done by calling
one of the following methods:

```python
g.audit_log.debug(self, msg)
g.audit_log.info(self, msg)
g.audit_log.warning(self, msg)
g.audit_log.error(self, msg)
g.audit_log.critical(self, msg)
```
    
These methods will add the following details to the log:

```json
"type": "DEBUG|INFO|WARNING|ERROR|etc",
"message": "log message"
```
