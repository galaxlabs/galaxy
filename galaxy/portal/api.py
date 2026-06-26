from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

from galaxy.portal.auth import (
    portal_create_session,
    portal_delete_session,
    portal_get_session,
    portal_require_session,
    portal_signup,
    portal_verify_password,
)


async def handle_portal_login(request):
    data = await request.json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return JSONResponse({"success": False, "error": "Email and password required"}, status_code=400)
    user = portal_verify_password(email, password)
    if user is None:
        return JSONResponse({"success": False, "error": "Invalid email or password"}, status_code=401)
    token = portal_create_session(email)
    response = JSONResponse({"success": True, "user": user, "token": token})
    response.set_cookie(key="portal_session", value=token, max_age=86400, httponly=True, path="/")
    return response


async def handle_portal_signup(request):
    data = await request.json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    display_name = data.get("display_name", "")
    if not email or not password:
        return JSONResponse({"success": False, "error": "Email and password required"}, status_code=400)
    if len(password) < 6:
        return JSONResponse({"success": False, "error": "Password must be at least 6 characters"}, status_code=400)
    user = portal_signup(email, password, display_name or None)
    if user is None:
        return JSONResponse({"success": False, "error": "Email already registered"}, status_code=409)
    return JSONResponse({"success": True, "user": user})


async def handle_portal_logout(request):
    session = portal_require_session(request)
    if session:
        cookie = request.cookies.get("portal_session")
        if cookie:
            portal_delete_session(cookie)
    response = JSONResponse({"success": True})
    response.delete_cookie("portal_session", path="/")
    return response


async def handle_portal_me(request):
    session = portal_require_session(request)
    if session is None:
        return JSONResponse({"success": False, "error": "Not authenticated"}, status_code=401)
    return JSONResponse({"success": True, "user": session})


async def handle_portal_home(request):
    return HTMLResponse("<h1>Portal</h1><p>Welcome to Galaxy Portal</p>")


async def handle_portal_login_page(request):
    return HTMLResponse("<h1>Portal Login</h1><form><input type='email' placeholder='Email'/><input type='password' placeholder='Password'/><button>Login</button></form>")


async def handle_portal_signup_page(request):
    return HTMLResponse("<h1>Portal Signup</h1><form><input type='email' placeholder='Email'/><input type='password' placeholder='Password'/><button>Sign Up</button></form>")


async def handle_portal_profile(request):
    session = portal_require_session(request)
    if session is None:
        return JSONResponse({"success": False, "error": "Not authenticated"}, status_code=401)
    from sqlalchemy import text
    from galaxy.config import load_site_config
    from galaxy.db.connection import get_engine
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT name, email, display_name, username, portal_role, language,
                       timezone, account_status, email_verified, last_login
                FROM "tabPortalUser" WHERE email = :email
            """),
            {"email": session["email"]},
        ).mappings().one_or_none()
    if row is None:
        return JSONResponse({"success": False, "error": "User not found"}, status_code=404)
    return JSONResponse({"success": True, "profile": dict(row)})
