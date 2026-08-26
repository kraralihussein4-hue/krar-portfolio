"use strict";

document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // Navigation
    // ==========================================

    const navigationLinks =
        document.querySelectorAll(".navbar a");

    navigationLinks.forEach((link) => {

        link.addEventListener("click", () => {

            navigationLinks.forEach((item) => {
                item.classList.remove("active");
            });

            link.classList.add("active");
        });

    });


    // ==========================================
    // Project Form
    // ==========================================

    const form =
        document.getElementById("projectForm");

    const formMessage =
        document.getElementById("formMessage");


    if (!form) {
        return;
    }


    // ==========================================
    // إرسال الطلب
    // ==========================================

    form.addEventListener("submit", async (event) => {

        event.preventDefault();


        // ======================================
        // رسالة مؤقتة
        // ======================================

        if (formMessage) {

            formMessage.textContent =
                "جاري إرسال طلبك...";

            formMessage.style.color =
                "#2563eb";
        }


        // ======================================
        // قراءة بيانات النموذج
        // ======================================

        const data = {

            full_name:
                document
                    .getElementById("fullName")
                    ?.value
                    .trim() || "",

            company_name:
                document
                    .getElementById("companyName")
                    ?.value
                    .trim() || "",

            phone:
                document
                    .getElementById("phone")
                    ?.value
                    .trim() || "",

            email:
                document
                    .getElementById("email")
                    ?.value
                    .trim() || "",

            service:
                document
                    .getElementById("service")
                    ?.value || "",

            budget:
                document
                    .getElementById("budget")
                    ?.value || "",

            deadline:
                document
                    .getElementById("deadline")
                    ?.value || "",

            project_details:
                document
                    .getElementById("projectDetails")
                    ?.value
                    .trim() || ""
        };


        // ======================================
        // إرسال إلى FastAPI
        // ======================================

        try {

            const response = await fetch(
                "/project-requests",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(data)
                }
            );


            // ==================================
            // قراءة النتيجة
            // ==================================

            const result =
                await response.json();


            // ==================================
            // نجاح
            // ==================================

            if (
                response.ok &&
                result.success
            ) {

                if (formMessage) {

                    formMessage.textContent =
                        "تم إرسال طلبك بنجاح ✅ سنتواصل معك قريبًا.";

                    formMessage.style.color =
                        "#16a34a";
                }


                // تفريغ النموذج
                form.reset();


                console.log(
                    "تم إرسال الطلب:",
                    result
                );


            } else {

                console.error(
                    "Server response:",
                    result
                );


                if (formMessage) {

                    formMessage.textContent =
                        result.detail ||
                        "حدث خطأ أثناء إرسال الطلب. حاول مرة أخرى.";

                    formMessage.style.color =
                        "#dc2626";
                }

            }


        } catch (error) {

            console.error(
                "Connection error:",
                error
            );


            if (formMessage) {

                formMessage.textContent =
                    "تعذر الاتصال بالخادم. تأكد أن FastAPI يعمل.";

                formMessage.style.color =
                    "#dc2626";
            }

        }

    });

});