"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const navigationLinks = document.querySelectorAll(".navbar a");

    navigationLinks.forEach((link) => {
        link.addEventListener("click", () => {
            navigationLinks.forEach((item) => {
                item.classList.remove("active");
            });

            link.classList.add("active");
        });
    });
});