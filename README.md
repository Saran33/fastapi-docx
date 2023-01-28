# fastapi-docx

<p align="center">
  <a href="https://github.com/Saran33/fastapi-docx"><img src="https://saran33.github.io/fastapi-docx/img/fastapi-docx-logo-teal.png" alt="FastAPI"></a>
</p>
<p align="center">
    <em>Add HTTPException responses to a FastAPI OpenAPI spec</em>
</p>
<p align="center">
<a href="https://github.com/saran33/fastapi-docx/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/saran33/fastapi-docx/workflows/Tests/badge.svg?event=push&branch=main" alt="Tests">
</a>
<a href="https://saran33.github.io/fastapi-docx/coverage_report/coverage.html" target="_blank">
    <img src="https://saran33.github.io/fastapi-docx/coverage_report/coverage-badge.svg" alt="Coverage">
</a>
<a href="https://pypi.org/project/fastapi-docx" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-docx?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastapi-docx" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fastapi-docx" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: <a href="https://saran33.github.io/fastapi-docx" target="_blank">https://saran33.github.io/fastapi-docx</a>

**Source Code**: <a href="https://github.com/Saran33/fastapi-docx" target="_blank">https://github.com/Saran33/fastapi-docx</a>

---

FastAPI-docx extends the FastAPI OpenAPI spec to include all possible `HTTPException` or custom Exception response schemas that may be raised within path operations.

The key features are:

* **Document Exception Responses**: Automatically find all possible respones within path operations, whether they originate from a `HTTPException` raised by the endpoint function directly, in a nested function, class method, or callable class instance, or by the fastAPI dependency-injection system.
* **Include Custom Exceptions**: Optionally find and document any custom Exception types if using custom Exception handlers in your FastAPI application.
* **Generate Exception schemas**: A default `HTTPExceptionSchema` will be added to the OpenAPI specification. The default can be modified to use any other [Pydantic](*https://github.com/pydantic/pydantic) model. An additional schema for app-specific custom Exceptions can also be included.

##### License
This project is licensed under the terms of the MIT license.
