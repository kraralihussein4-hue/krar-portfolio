import sqlite3
from pathlib import Path


# =========================================================
# مكان قاعدة البيانات
# =========================================================

DATABASE_PATH = Path(__file__).parent / "portfolio.db"


# =========================================================
# الاتصال بقاعدة البيانات
# =========================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# إنشاء وتحديث قاعدة البيانات
# =========================================================

def create_database():

    connection = get_connection()

    try:

        # =====================================================
        # إنشاء الجدول الأساسي إذا لم يكن موجودًا
        # =====================================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS project_requests (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                full_name TEXT NOT NULL,

                company_name TEXT DEFAULT '',

                phone TEXT NOT NULL,

                email TEXT DEFAULT '',

                service TEXT NOT NULL,

                budget TEXT DEFAULT '',

                deadline TEXT DEFAULT '',

                project_details TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'new',

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP

            )
        """)

        # =====================================================
        # قراءة الأعمدة الموجودة حاليًا
        # =====================================================

        columns = connection.execute(
            "PRAGMA table_info(project_requests)"
        ).fetchall()

        column_names = [
            column["name"]
            for column in columns
        ]

        # =====================================================
        # إضافة company_name إذا كانت قاعدة البيانات قديمة
        # =====================================================

        if "company_name" not in column_names:

            connection.execute("""
                ALTER TABLE project_requests
                ADD COLUMN company_name TEXT DEFAULT ''
            """)

        # =====================================================
        # إضافة email
        # =====================================================

        if "email" not in column_names:

            connection.execute("""
                ALTER TABLE project_requests
                ADD COLUMN email TEXT DEFAULT ''
            """)

        # =====================================================
        # إضافة budget
        # =====================================================

        if "budget" not in column_names:

            connection.execute("""
                ALTER TABLE project_requests
                ADD COLUMN budget TEXT DEFAULT ''
            """)

        # =====================================================
        # إضافة deadline
        # =====================================================

        if "deadline" not in column_names:

            connection.execute("""
                ALTER TABLE project_requests
                ADD COLUMN deadline TEXT DEFAULT ''
            """)

        # =====================================================
        # إضافة status إذا لم يكن موجودًا
        # =====================================================

        if "status" not in column_names:

            connection.execute("""
                ALTER TABLE project_requests
                ADD COLUMN status TEXT NOT NULL
                DEFAULT 'new'
            """)

        # =====================================================
        # التأكد من وجود قيمة للحالة في الطلبات القديمة
        # =====================================================

        connection.execute("""
            UPDATE project_requests
            SET status = 'new'
            WHERE status IS NULL OR status = ''
        """)

        # =====================================================
        # حفظ التغييرات
        # =====================================================

        connection.commit()

    finally:

        connection.close()


# =========================================================
# تشغيل إنشاء قاعدة البيانات
# =========================================================

create_database()