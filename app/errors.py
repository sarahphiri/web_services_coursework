#from __future__ import annotations

#from fastapi import FastAPI, Request
#from fastapi.exceptions import RequestValidationError
#from fastapi.responses import JSONResponse
#from starlette.exceptions import HTTPException as StarletteHTTPException


#def _http_code_to_label(status_code: int) -> str:
 #   if status_code == 400:
 #       return "BAD_REQUEST"
 #   if status_code == 401:
 #       return "UNAUTHORIZED"
  #  if status_code == 403:
  #      return "FORBIDDEN"
  #  if status_code == 404:
  #      return "NOT_FOUND"
  #  if status_code == 409:
  #      return "CONFLICT"
  #  if status_code == 422:
  #      return "VALIDATION_ERROR"
  #  if status_code >= 500:
  #      return "SERVER_ERROR"
  #  return "ERROR"


#def install_error_handlers(app: FastAPI) -> None:
  #  @app.exception_handler(StarletteHTTPException)
  #  async def http_exception_handler(request: Request, exc: StarletteHTTPException):
   #     return JSONResponse(
   #         status_code=exc.status_code,
   #         content={
   #             "error": {
   #                 "code": _http_code_to_label(exc.status_code),
  #                  "message": exc.detail if isinstance(exc.detail, str) else "Request failed",
   #                 "details": exc.detail if not isinstance(exc.detail, str) else None,
   #                 "path": str(request.url.path),
   #             }
   #         },
   #     )

  #  @app.exception_handler(RequestValidationError)
  #  async def validation_exception_handler(request: Request, exc: RequestValidationError):
  #      return JSONResponse(
  #          status_code=422,
  #          content={
    #            "error": {
    #                "code": "VALIDATION_ERROR",
    #                "message": "Invalid request data",
    #               "details": exc.errors(),
   #                 "path": str(request.url.path),
    #            }
   #         },
   #     )

  #  @app.exception_handler(Exception)
  #  async def unhandled_exception_handler(request: Request, exc: Exception):
        # Don't leak stack traces to clients
   #     return JSONResponse(
  #          status_code=500,
  #          content={
    #            "error": {
    #                "code": "SERVER_ERROR",
    #                "message": "An unexpected error occurred",
    #                "details": None,
    #                "path": str(request.url.path),
     #           }
     #       },
   #     )