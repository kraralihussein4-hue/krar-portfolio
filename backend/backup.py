import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


# =========================================================
# المسارات
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "portfolio.db"

PROJECT_DIR = BASE_DIR.parent

BACKUP_DIR = PROJECT_DIR / "backups"


# =========================================================
# إنشاء مجلد النسخ الاحتياطية
# =========================================================

def ensure_backup_directory():

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# =========================================================
# إنشاء نسخة احتياطية
# =========================================================

def create_backup():

    ensure_backup_directory()

    if not DATABASE_PATH.exists():

        raise FileNotFoundError(
            "قاعدة البيانات portfolio.db غير موجودة"
        )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    backup_filename = (
        f"portfolio_backup_{timestamp}.db"
    )

    backup_path = (
        BACKUP_DIR / backup_filename
    )

    # -----------------------------------------------------
    # استخدام SQLite Backup API
    # -----------------------------------------------------

    source = sqlite3.connect(
        DATABASE_PATH
    )

    destination = sqlite3.connect(
        backup_path
    )

    try:

        source.backup(
            destination
        )

    finally:

        destination.close()
        source.close()

    return backup_path


# =========================================================
# عرض النسخ الاحتياطية
# =========================================================

def list_backups():

    ensure_backup_directory()

    backups = sorted(
        BACKUP_DIR.glob(
            "portfolio_backup_*.db"
        ),
        key=lambda file:
            file.stat().st_mtime,
        reverse=True
    )

    return backups


# =========================================================
# الحصول على نسخة احتياطية محددة
# =========================================================

def get_backup(
    filename: str
):

    ensure_backup_directory()

    # -----------------------------------------------------
    # منع استخدام مسار خارج مجلد backups
    # -----------------------------------------------------

    safe_name = Path(
        filename
    ).name

    # التأكد من أن الاسم هو اسم نسخة احتياطية
    if not safe_name.startswith(
        "portfolio_backup_"
    ):

        raise FileNotFoundError(
            "اسم النسخة الاحتياطية غير صالح"
        )

    if not safe_name.endswith(
        ".db"
    ):

        raise FileNotFoundError(
            "ملف النسخة الاحتياطية غير صالح"
        )

    backup_path = (
        BACKUP_DIR / safe_name
    )

    if not backup_path.exists():

        raise FileNotFoundError(
            "النسخة الاحتياطية غير موجودة"
        )

    if not backup_path.is_file():

        raise FileNotFoundError(
            "النسخة الاحتياطية غير صالحة"
        )

    return backup_path


# =========================================================
# حذف نسخة احتياطية
# =========================================================

def delete_backup(
    filename: str
):

    backup_path = get_backup(
        filename
    )

    backup_path.unlink()

    return True


# =========================================================
# اختبار النظام
# =========================================================

if __name__ == "__main__":

    backup = create_backup()

    print(
        "تم إنشاء النسخة الاحتياطية:"
    )

    print(
        backup
    )