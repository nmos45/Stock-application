function showInfo(show) {
  const dialog = document.getElementById("info");
  if (show) {
    dialog.showModal();
  } else {
    dialog.close();
  }
}
document.addEventListener("DOMContentLoaded", function () {

  const dialog = document.getElementById("info");
  const infoWrapper = document.getElementById("info-wrapper");

  dialog.addEventListener("click", (e) => {
    if (!infoWrapper.contains(e.target)) {
      dialog.close();
    }
  })



});

