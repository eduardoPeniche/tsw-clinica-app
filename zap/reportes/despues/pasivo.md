# ZAP Scanning Report

ZAP by [Checkmarx](https://checkmarx.com/).


## Summary of Alerts

| Risk Level | Number of Alerts |
| --- | --- |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Informational | 2 |




## Insights

| Level | Reason | Site | Description | Statistic |
| --- | --- | --- | --- | --- |
| Info | Informational | http://backend:8000 | Percentage of responses with status code 2xx | 27 % |
| Info | Informational | http://backend:8000 | Percentage of responses with status code 4xx | 72 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with content type application/json | 100 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method DELETE | 11 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method GET | 55 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method PATCH | 5 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method POST | 16 % |
| Info | Informational | http://backend:8000 | Percentage of endpoints with method PUT | 11 % |
| Info | Informational | http://backend:8000 | Count of total endpoints | 18    |







## Alerts

| Name | Risk Level | Number of Instances |
| --- | --- | --- |
| A Client Error response code was returned by the server | Informational | 13 |
| Non-Storable Content | Informational | Systemic |




## Alert Detail



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
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id`
  * Method: `DELETE`
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
* URL: http://backend:8000/medicos/medico_id/citas%3Ffecha=
  * Node Name: `http://backend:8000/medicos/medico_id/citas (fecha)`
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
* URL: http://backend:8000/medicos/medico_id/disponibilidad%3Ffecha=fecha
  * Node Name: `http://backend:8000/medicos/medico_id/disponibilidad (fecha)`
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
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id/citas
  * Node Name: `http://backend:8000/pacientes/paciente_id/citas`
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
* URL: http://backend:8000/citas
  * Node Name: `http://backend:8000/citas ()({paciente_id,medico_id,fecha_hora})`
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
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id ()({nombre,fecha_nacimiento,contacto})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``


Instances: 13

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
* URL: http://backend:8000/medicos
  * Node Name: `http://backend:8000/medicos`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: http://backend:8000/pacientes/paciente_id
  * Node Name: `http://backend:8000/pacientes/paciente_id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: http://backend:8000/pacientes
  * Node Name: `http://backend:8000/pacientes ()({nombre,fecha_nacimiento,contacto})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
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


