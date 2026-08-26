from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import secrets
import os

from dotenv import load_dotenv

from database import get_connection, create_database
from backup import create_backup, list_backups


# =========================================================
# المسارات الأساسية
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


# =========================================================
# تحميل ملف .env
# =========================================================

load_dotenv(
    PROJECT_DIR / ".env"
)


# =========================================================
# إعداد التطبيق
# =========================================================

app = FastAPI(
    title="Krar Ali Portfolio API",
    version="2.1.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# إنشاء قاعدة البيانات
# =========================================================

create_database()


# =========================================================
# إعداد الإدارة
# =========================================================

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "كرار1991"
)

admin_sessions = {}

SESSION_DURATION_HOURS = 24


# =========================================================
# نماذج البيانات
# =========================================================

class AdminLogin(BaseModel):
    password: str


class StatusUpdate(BaseModel):
    status: str


class ProjectRequest(BaseModel):

    full_name: str

    company_name: Optional[str] = ""

    phone: str

    email: Optional[str] = ""

    service: str

    budget: Optional[str] = ""

    deadline: Optional[str] = ""

    project_details: str


# =========================================================
# التحقق من جلسة الإدارة
# =========================================================

def verify_admin_token(
    authorization: Optional[str]
):

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="غير مصرح"
        )

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=401,
            detail="رمز الدخول غير صحيح"
        )

    token = authorization.replace(
        "Bearer ",
        "",
        1
    ).strip()

    session = admin_sessions.get(
        token
    )

    if not session:

        raise HTTPException(
            status_code=401,
            detail="جلسة الدخول غير صالحة"
        )

    if datetime.now() > session[
        "expires_at"
    ]:

        del admin_sessions[token]

        raise HTTPException(
            status_code=401,
            detail="انتهت جلسة الدخول"
        )

    return True


# =========================================================
# الصفحة الرئيسية
# =========================================================

@app.get("/")
def root():

    index_file = (
        PROJECT_DIR /
        "index.html"
    )

    if not index_file.exists():

        raise HTTPException(
            status_code=404,
            detail="index.html غير موجود"
        )

    return FileResponse(
        index_file
    )


# =========================================================
# اختبار السيرفر
# =========================================================

@app.get("/test")
def test():

    return {
        "success": True,
        "status": "Online",
        "message":
            "Krar Ali Portfolio API يعمل بنجاح"
    }


# =========================================================
# تسجيل دخول الإدارة
# =========================================================

@app.post("/admin/login")
def admin_login(
    data: AdminLogin
):

    if data.password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="كلمة المرور غير صحيحة"
        )

    token = secrets.token_urlsafe(
        32
    )

    admin_sessions[token] = {

        "created_at":
            datetime.now(),

        "expires_at":
            datetime.now()
            + timedelta(
                hours=
                SESSION_DURATION_HOURS
            )
    }

    return {

        "success": True,

        "message":
            "تم تسجيل الدخول بنجاح",

        "token":
            token
    }


# =========================================================
# تسجيل خروج الإدارة
# =========================================================

@app.post("/admin/logout")
def admin_logout(
    authorization: Optional[str] =
        Header(default=None)
):

    if (
        authorization
        and authorization.startswith(
            "Bearer "
        )
    ):

        token = authorization.replace(
            "Bearer ",
            "",
            1
        ).strip()

        admin_sessions.pop(
            token,
            None
        )

    return {

        "success": True,

        "message":
            "تم تسجيل الخروج"
    }


# =========================================================
# حالة الإدارة
# =========================================================

@app.get("/admin/status")
def admin_status(
    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    return {

        "success": True,

        "status":
            "online",

        "message":
            "الموقع يعمل"
    }


# =========================================================
# إنشاء طلب مشروع
# =========================================================

@app.post("/project-requests")
def create_project_request(
    request: ProjectRequest
):

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            INSERT INTO project_requests
            (
                full_name,
                company_name,
                phone,
                email,
                service,
                budget,
                deadline,
                project_details,
                status
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.full_name.strip(),

                (
                    request.company_name.strip()
                    if request.company_name
                    else ""
                ),

                request.phone.strip(),

                (
                    request.email.strip()
                    if request.email
                    else ""
                ),

                request.service.strip(),

                (
                    request.budget.strip()
                    if request.budget
                    else ""
                ),

                (
                    request.deadline.strip()
                    if request.deadline
                    else ""
                ),

                request.project_details.strip(),

                "new"
            )
        )

        connection.commit()

        request_id = (
            cursor.lastrowid
        )

        return {

            "success": True,

            "message":
                "تم إرسال الطلب بنجاح",

            "request_id":
                request_id
        }

    finally:

        connection.close()


# =========================================================
# جلب جميع الطلبات
# =========================================================

@app.get("/project-requests")
def get_project_requests(
    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                id,
                full_name,
                company_name,
                phone,
                email,
                service,
                budget,
                deadline,
                project_details,
                status,
                created_at
            FROM project_requests
            ORDER BY id DESC
            """
        ).fetchall()

        requests = [
            dict(row)
            for row in rows
        ]

        return {

            "success": True,

            "count":
                len(requests),

            "requests":
                requests
        }

    finally:

        connection.close()


# =========================================================
# جلب طلب واحد
# =========================================================

@app.get(
    "/project-requests/{request_id}"
)
def get_project_request(
    request_id: int,

    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT
                id,
                full_name,
                company_name,
                phone,
                email,
                service,
                budget,
                deadline,
                project_details,
                status,
                created_at
            FROM project_requests
            WHERE id = ?
            """,
            (
                request_id,
            )
        ).fetchone()

        if not row:

            raise HTTPException(
                status_code=404,
                detail="الطلب غير موجود"
            )

        return {

            "success": True,

            "request":
                dict(row)
        }

    finally:

        connection.close()


# =========================================================
# تحديث حالة الطلب
# =========================================================

@app.put(
    "/project-requests/{request_id}/status"
)
def update_project_status(
    request_id: int,

    data: StatusUpdate,

    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    allowed_statuses = {

        "new",

        "contacted",

        "in_progress",

        "completed",

        "cancelled"
    }

    if data.status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="حالة الطلب غير صحيحة"
        )

    connection = get_connection()

    try:

        existing = connection.execute(
            """
            SELECT id
            FROM project_requests
            WHERE id = ?
            """,
            (
                request_id,
            )
        ).fetchone()

        if not existing:

            raise HTTPException(
                status_code=404,
                detail="الطلب غير موجود"
            )

        connection.execute(
            """
            UPDATE project_requests
            SET status = ?
            WHERE id = ?
            """,
            (
                data.status,
                request_id
            )
        )

        connection.commit()

        return {

            "success": True,

            "message":
                "تم تحديث حالة الطلب",

            "request_id":
                request_id,

            "status":
                data.status
        }

    finally:

        connection.close()


# =========================================================
# حذف طلب
# =========================================================

@app.delete(
    "/project-requests/{request_id}"
)
def delete_project_request(
    request_id: int,

    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    connection = get_connection()

    try:

        existing = connection.execute(
            """
            SELECT id
            FROM project_requests
            WHERE id = ?
            """,
            (
                request_id,
            )
        ).fetchone()

        if not existing:

            raise HTTPException(
                status_code=404,
                detail="الطلب غير موجود"
            )

        connection.execute(
            """
            DELETE FROM project_requests
            WHERE id = ?
            """,
            (
                request_id,
            )
        )

        connection.commit()

        return {

            "success": True,

            "message":
                "تم حذف الطلب بنجاح",

            "request_id":
                request_id
        }

    finally:

        connection.close()


# =========================================================
# إحصائيات لوحة التحكم
# =========================================================

@app.get("/admin/statistics")
def admin_statistics(
    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    connection = get_connection()

    try:

        total = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM project_requests
            """
        ).fetchone()["count"]

        today = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM project_requests
            WHERE date(created_at)
                  = date('now')
            """
        ).fetchone()["count"]

        latest = connection.execute(
            """
            SELECT
                id,
                created_at
            FROM project_requests
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        return {

            "success": True,

            "total":
                total,

            "today":
                today,

            "latest":
                (
                    dict(latest)
                    if latest
                    else None
                )
        }

    finally:

        connection.close()


# =========================================================
# اختصار الإحصائيات
# =========================================================

@app.get("/admin/stats")
def admin_stats(
    authorization: Optional[str] =
        Header(default=None)
):

    return admin_statistics(
        authorization
    )


# =========================================================
# إنشاء نسخة احتياطية
# =========================================================

@app.post("/admin/backup")
def admin_backup(
    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    try:

        backup_path = create_backup()

        return {

            "success": True,

            "message":
                "تم إنشاء النسخة الاحتياطية بنجاح",

            "filename":
                backup_path.name
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=
                f"فشل إنشاء النسخة الاحتياطية: {error}"
        )


# =========================================================
# عرض النسخ الاحتياطية
# =========================================================

@app.get("/admin/backups")
def get_backups(
    authorization: Optional[str] =
        Header(default=None)
):

    verify_admin_token(
        authorization
    )

    try:

        backups = list_backups()

        return {

            "success": True,

            "count":
                len(backups),

            "backups": [

                {
                    "filename":
                        backup.name,

                    "size":
                        backup.stat().st_size,

                    "created_at":
                        datetime.fromtimestamp(
                            backup.stat().st_mtime
                        ).isoformat()
                }

                for backup in backups
            ]
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=
                f"فشل قراءة النسخ الاحتياطية: {error}"
        )


# =========================================================
# لوحة التحكم
# =========================================================

@app.get("/admin")
def admin_page():

    admin_file = (
        PROJECT_DIR /
        "admin.html"
    )

    if not admin_file.exists():

        raise HTTPException(
            status_code=404,
            detail="admin.html غير موجود"
        )

    return FileResponse(
        admin_file
    )


# =========================================================
# الملفات الثابتة
# =========================================================

app.mount(
    "/",
    StaticFiles(
        directory=PROJECT_DIR,
        html=True
    ),
    name="site"
)


# =========================================================
# تشغيل السيرفر
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )