const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#primary-navigation");

if (menuButton && navigation) {
  menuButton.addEventListener("click", () => {
    const expanded = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!expanded));
    menuButton.setAttribute(
      "aria-label",
      expanded ? "Open navigation" : "Close navigation",
    );
    navigation.classList.toggle("is-open", !expanded);
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      menuButton.setAttribute("aria-expanded", "false");
      menuButton.setAttribute("aria-label", "Open navigation");
      navigation.classList.remove("is-open");
    });
  });
}

const form = document.querySelector("#enquiry-form");
if (form) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;

    const data = new FormData(form);
    const message = [
      `Hi Bekezela, my name is ${data.get("name")}.`,
      `I'm asking about: ${data.get("topic")}.`,
      String(data.get("message")).trim(),
    ].join("\n");
    const link = `https://wa.me/263712345678?text=${encodeURIComponent(message)}`;
    window.open(link, "_blank", "noopener,noreferrer");
  });
}

document
  .querySelector("#year")
  ?.replaceChildren(String(new Date().getFullYear()));
