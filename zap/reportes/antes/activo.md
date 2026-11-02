# ZAP Scanning Report

ZAP by [Checkmarx](https://checkmarx.com/).


## Summary of Alerts

| Risk Level | Number of Alerts |
| --- | --- |
| High | 0 |
| Medium | 0 |
| Low | 2 |
| Informational | 3 |




## Insights

| Level | Reason | Site | Description | Statistic |
| --- | --- | --- | --- | --- |
| Medium | Exceeded High | http://backend:8000 | Percentage of responses with status code 4xx | 79 % |
| Info | Informational | http://backend:8000 | Percentage of responses with status code 2xx | 20 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with content type application/json | 100 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method DELETE | 7 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method GET | 63 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method PATCH | 15 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method POST | 7 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method PUT | 7 % |
| Info | Informational | http://backend:8000 | Count of total endpoints | 57    |







## Alerts

| Name | Risk Level | Number of Instances |
| --- | --- | --- |
| Cross-Origin-Resource-Policy Header Missing or Invalid | Low | 5 |
| X-Content-Type-Options Header Missing | Low | 5 |
| A Client Error response code was returned by the server | Informational | 55 |
| Non-Storable Content | Informational | Systemic |
| Storable and Cacheable Content | Informational | 3 |




## Alert Detail



### [ Cross-Origin-Resource-Policy Header Missing or Invalid ](https://www.zaproxy.org/docs/alerts/90004/)



##### Low (Medium)

### Description

Cross-Origin-Resource-Policy header is an opt-in header designed to counter side-channels attacks like Spectre. Resource should be specifically set as shareable amongst different origins.

* URL: http://backend:8000/medicos
  * Node Name: `http://backend:8000/medicos`
  * Method: `GET`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: http://backend:8000/openapi.json
  * Node Name: `http://backend:8000/openapi.json`
  * Method: `GET`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes`
  * Method: `GET`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: http://backend:8000/medicos
  * Node Name: `http://backend:8000/medicos ()({nombre,especialidad})`
  * Method: `POST`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes ()({nombre,fecha_nacimiento,contacto})`
  * Method: `POST`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``


Instances: 5

### Solution

Ensure that the application/web server sets the Cross-Origin-Resource-Policy header appropriately, and that it sets the Cross-Origin-Resource-Policy header to 'same-origin' for all web pages.
'same-site' is considered as less secured and should be avoided.
If resources must be shared, set the header to 'cross-origin'.
If possible, ensure that the end user uses a standards-compliant and modern web browser that supports the Cross-Origin-Resource-Policy header (https://caniuse.com/mdn-http_headers_cross-origin-resource-policy).

### Reference


* [ https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy)


#### CWE Id: [ 693 ](https://cwe.mitre.org/data/definitions/693.html)


#### WASC Id: 14

#### Source ID: 3

### [ X-Content-Type-Options Header Missing ](https://www.zaproxy.org/docs/alerts/10021/)



##### Low (Medium)

### Description

The Anti-MIME-Sniffing header X-Content-Type-Options was not set to 'nosniff'. This allows older versions of Internet Explorer and Chrome to perform MIME-sniffing on the response body, potentially causing the response body to be interpreted and displayed as a content type other than the declared content type. Current (early 2014) and legacy versions of Firefox will use the declared content type (if one is set), rather than performing MIME-sniffing.

* URL: http://backend:8000/medicos
  * Node Name: `http://backend:8000/medicos`
  * Method: `GET`
  * Parameter: `x-content-type-options`
  * Attack: ``
  * Evidence: ``
  * Other Info: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://backend:8000/openapi.json
  * Node Name: `http://backend:8000/openapi.json`
  * Method: `GET`
  * Parameter: `x-content-type-options`
  * Attack: ``
  * Evidence: ``
  * Other Info: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes`
  * Method: `GET`
  * Parameter: `x-content-type-options`
  * Attack: ``
  * Evidence: ``
  * Other Info: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://backend:8000/medicos
  * Node Name: `http://backend:8000/medicos ()({nombre,especialidad})`
  * Method: `POST`
  * Parameter: `x-content-type-options`
  * Attack: ``
  * Evidence: ``
  * Other Info: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes ()({nombre,fecha_nacimiento,contacto})`
  * Method: `POST`
  * Parameter: `x-content-type-options`
  * Attack: ``
  * Evidence: ``
  * Other Info: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`


Instances: 5

### Solution

Ensure that the application/web server sets the Content-Type header appropriately, and that it sets the X-Content-Type-Options header to 'nosniff' for all web pages.
If possible, ensure that the end user uses a standards-compliant and modern web browser that does not perform MIME-sniffing at all, or that can be directed by the web application/web server to not perform MIME-sniffing.

### Reference


* [ https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/gg622941(v=vs.85) ](https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/gg622941(v=vs.85))
* [ https://owasp.org/www-community/Security_Headers ](https://owasp.org/www-community/Security_Headers)


#### CWE Id: [ 693 ](https://cwe.mitre.org/data/definitions/693.html)


#### WASC Id: 15

#### Source ID: 3

### [ A Client Error response code was returned by the server ](https://www.zaproxy.org/docs/alerts/100000/)



##### Informational (High)

### Description

A response code of 422 was returned by the server.
This may indicate that the application is failing to handle unexpected input correctly.
Raised by the 'Alert on HTTP Response Code Error' script

* URL: http://backend:8000/medicos/medico_id
  * Node Name: `http://backend:8000/medicos/medico_id`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/
  * Node Name: `http://backend:8000/medicos/medico_id/`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id/
  * Node Name: `http://backend:8000/pacientes/paciente_id/`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000
  * Node Name: `http://backend:8000`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/
  * Node Name: `http://backend:8000/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/37680859118167753
  * Node Name: `http://backend:8000/37680859118167753`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/citas
  * Node Name: `http://backend:8000/citas`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: http://backend:8000/citas/
  * Node Name: `http://backend:8000/citas/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: http://backend:8000/citas/5661220659366465130
  * Node Name: `http://backend:8000/citas/5661220659366465130`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/citas/cita_id
  * Node Name: `http://backend:8000/citas/cita_id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/citas/cita_id/
  * Node Name: `http://backend:8000/citas/cita_id/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/citas/cita_id/7900053790793068638
  * Node Name: `http://backend:8000/citas/cita_id/7900053790793068638`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/citas/cita_id/actuator/health
  * Node Name: `http://backend:8000/citas/cita_id/actuator/health`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/medicos/8811748288361743519
  * Node Name: `http://backend:8000/medicos/8811748288361743519`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id
  * Node Name: `http://backend:8000/medicos/medico_id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/
  * Node Name: `http://backend:8000/medicos/medico_id/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/906113063238406676
  * Node Name: `http://backend:8000/medicos/medico_id/906113063238406676`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/citas
  * Node Name: `http://backend:8000/medicos/medico_id/citas`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/citas%3Ffecha=
  * Node Name: `http://backend:8000/medicos/medico_id/citas (fecha)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/citas/
  * Node Name: `http://backend:8000/medicos/medico_id/citas/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/citas/2485333715499775852
  * Node Name: `http://backend:8000/medicos/medico_id/citas/2485333715499775852`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/citas/rango
  * Node Name: `http://backend:8000/medicos/medico_id/citas/rango`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/citas/rango%3Fdesde=desde&hasta=hasta
  * Node Name: `http://backend:8000/medicos/medico_id/citas/rango (desde,hasta)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/citas/rango/
  * Node Name: `http://backend:8000/medicos/medico_id/citas/rango/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/disponibilidad
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/disponibilidad%3Ffecha=fecha
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad (fecha)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/disponibilidad/
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/disponibilidad/3732595979725775139
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad/3732595979725775139`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/disponibilidad/rango
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad/rango`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/disponibilidad/rango%3Fdesde=desde&hasta=hasta
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad/rango (desde,hasta)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/disponibilidad/rango/
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad/rango/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/1863510292457018142
  * Node Name: `http://backend:8000/pacientes/1863510292457018142`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id/
  * Node Name: `http://backend:8000/pacientes/paciente_id/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id/1701536422633091311
  * Node Name: `http://backend:8000/pacientes/paciente_id/1701536422633091311`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id/citas
  * Node Name: `http://backend:8000/pacientes/paciente_id/citas`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id/citas/
  * Node Name: `http://backend:8000/pacientes/paciente_id/citas/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/citas/cita_id/cancelacion
  * Node Name: `http://backend:8000/citas/cita_id/cancelacion`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/citas/cita_id/cancelacion/
  * Node Name: `http://backend:8000/citas/cita_id/cancelacion/`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/computeMetadata/v1/
  * Node Name: `http://backend:8000/computeMetadata/v1/`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/latest/meta-data/
  * Node Name: `http://backend:8000/latest/meta-data/`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/metadata/instance
  * Node Name: `http://backend:8000/metadata/instance`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/metadata/v1
  * Node Name: `http://backend:8000/metadata/v1`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/opc/v1/instance/
  * Node Name: `http://backend:8000/opc/v1/instance/`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/opc/v2/instance/
  * Node Name: `http://backend:8000/opc/v2/instance/`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/openstack/latest/meta_data.json
  * Node Name: `http://backend:8000/openstack/latest/meta_data.json`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: http://backend:8000/citas
  * Node Name: `http://backend:8000/citas ()({paciente_id,medico_id,fecha_hora})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/citas/
  * Node Name: `http://backend:8000/citas/ ()({paciente_id,medico_id,fecha_hora})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos
  * Node Name: `http://backend:8000/medicos ()({nombre,especialidad})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes ()({nombre,fecha_nacimiento,contacto})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id
  * Node Name: `http://backend:8000/medicos/medico_id ()({nombre,especialidad})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id/
  * Node Name: `http://backend:8000/medicos/medico_id/ ()({nombre,especialidad})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id ()({nombre,fecha_nacimiento,contacto})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id/
  * Node Name: `http://backend:8000/pacientes/paciente_id/ ()({nombre,fecha_nacimiento,contacto})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``


Instances: 55

### Solution



### Reference



#### CWE Id: [ 388 ](https://cwe.mitre.org/data/definitions/388.html)


#### WASC Id: 20

#### Source ID: 4

### [ Non-Storable Content ](https://www.zaproxy.org/docs/alerts/10049/)



##### Informational (Medium)

### Description

The response contents are not storable by caching components such as proxy servers. If the response does not contain sensitive, personal or user-specific information, it may benefit from being stored and cached, to improve performance.

* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `DELETE `
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id
  * Node Name: `http://backend:8000/medicos/medico_id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/medicos/medico_id
  * Node Name: `http://backend:8000/medicos/medico_id ()({nombre,especialidad})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `PUT `
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id ()({nombre,fecha_nacimiento,contacto})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `PUT `
  * Other Info: ``

Instances: Systemic


### Solution

The content may be marked as storable by ensuring that the following conditions are satisfied:
The request method must be understood by the cache and defined as being cacheable ("GET", "HEAD", and "POST" are currently defined as cacheable)
The response status code must be understood by the cache (one of the 1XX, 2XX, 3XX, 4XX, or 5XX response classes are generally understood)
The "no-store" cache directive must not appear in the request or response header fields
For caching by "shared" caches such as "proxy" caches, the "private" response directive must not appear in the response
For caching by "shared" caches such as "proxy" caches, the "Authorization" header field must not appear in the request, unless the response explicitly allows it (using one of the "must-revalidate", "public", or "s-maxage" Cache-Control response directives)
In addition to the conditions above, at least one of the following conditions must also be satisfied by the response:
It must contain an "Expires" header field
It must contain a "max-age" response directive
For "shared" caches such as "proxy" caches, it must contain a "s-maxage" response directive
It must contain a "Cache Control Extension" that allows it to be cached
It must have a status code that is defined as cacheable by default (200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501).

### Reference


* [ https://datatracker.ietf.org/doc/html/rfc7234 ](https://datatracker.ietf.org/doc/html/rfc7234)
* [ https://datatracker.ietf.org/doc/html/rfc7231 ](https://datatracker.ietf.org/doc/html/rfc7231)
* [ https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html ](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html)


#### CWE Id: [ 524 ](https://cwe.mitre.org/data/definitions/524.html)


#### WASC Id: 13

#### Source ID: 3

### [ Storable and Cacheable Content ](https://www.zaproxy.org/docs/alerts/10049/)



##### Informational (Medium)

### Description

The response contents are storable by caching components such as proxy servers, and may be retrieved directly from the cache, rather than from the origin server by the caching servers, in response to similar requests from other users. If the response data is sensitive, personal or user-specific, this may result in sensitive information being leaked. In some cases, this may even result in a user gaining complete control of the session of another user, depending on the configuration of the caching components in use in their environment. This is primarily an issue where "shared" caching servers such as "proxy" caches are configured on the local network. This configuration is typically found in corporate or educational environments, for instance.

* URL: http://backend:8000/medicos
  * Node Name: `http://backend:8000/medicos`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: ``
  * Other Info: `In the absence of an explicitly specified caching lifetime directive in the response, a liberal lifetime heuristic of 1 year was assumed. This is permitted by rfc7234.`
* URL: http://backend:8000/openapi.json
  * Node Name: `http://backend:8000/openapi.json`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: ``
  * Other Info: `In the absence of an explicitly specified caching lifetime directive in the response, a liberal lifetime heuristic of 1 year was assumed. This is permitted by rfc7234.`
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: ``
  * Other Info: `In the absence of an explicitly specified caching lifetime directive in the response, a liberal lifetime heuristic of 1 year was assumed. This is permitted by rfc7234.`


Instances: 3

### Solution

Validate that the response does not contain sensitive, personal or user-specific information. If it does, consider the use of the following HTTP response headers, to limit, or prevent the content being stored and retrieved from the cache by another user:
Cache-Control: no-cache, no-store, must-revalidate, private
Pragma: no-cache
Expires: 0
This configuration directs both HTTP 1.0 and HTTP 1.1 compliant caching servers to not store the response, and to not retrieve the response (without validation) from the cache, in response to a similar request.

### Reference


* [ https://datatracker.ietf.org/doc/html/rfc7234 ](https://datatracker.ietf.org/doc/html/rfc7234)
* [ https://datatracker.ietf.org/doc/html/rfc7231 ](https://datatracker.ietf.org/doc/html/rfc7231)
* [ https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html ](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html)


#### CWE Id: [ 524 ](https://cwe.mitre.org/data/definitions/524.html)


#### WASC Id: 13

#### Source ID: 3


