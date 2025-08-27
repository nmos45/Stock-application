// function showInfo(show) {
//   const dialog = document.querySelector(".info");
//   if (show) {
//     dialog.showModal();
//   } else {
//     dialog.close();
//   }
// }

function showHeaderInfo(show) {
  const dialog = document.querySelector("#header-dialog");
  if (show) {
    dialog.showModal();
    // dialog.querySelector("#info-wrapper").focus();
  } else {
    dialog.close();
  }
}

function dialogLogic() {

  const dialogs = document.querySelectorAll(".info");

  dialogs.forEach((dialog) => {
    dialog.addEventListener("click", (e) => {
      const infoWrapper = dialog.querySelector(".info-wrapper");
      if (!infoWrapper.contains(e.target)) {
        dialog.close();
      }
    })
  });

  const detailDialogContainer = document.querySelectorAll(".dialog-container");

  detailDialogContainer.forEach((container) => {
    const dialog = container.querySelector(".dialog");
    const openDialog = container.querySelector(".open-dialog");
    const closeDialog = container.querySelector(".close-dialog");


    if (openDialog && dialog) {
      openDialog.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!dialog.open) {
          dialog.show();
        }
      });
    }

    if (closeDialog && dialog) {
      closeDialog.addEventListener("click", (e) => {

        e.preventDefault();
        e.stopPropagation();
        if (dialog.open) {
          dialog.close();
        }
      });
    }

    if (dialog) {
      dialog.addEventListener("click", (e) => {
        const infoWrapper = dialog.querySelector(".dialog-wrapper");
        if (infoWrapper && !infoWrapper.contains(e.target)) {
          dialog.close();
        }
      });
    }
  })

  const dialogHeader = document.querySelector("#header-dialog");
  if (dialogHeader) {
    dialogHeader.addEventListener("click", (e) => {
      const infoWrapper = dialogHeader.querySelector("#info-wrapper");
      if (infoWrapper && !infoWrapper.contains(e.target)) {
        dialogHeader.close();
      }
    });
  }
}



document.addEventListener("scroll", () => {
  const toTop = document.querySelector("#scroll-top");
  if (window.pageYOffset > 100 || window.scrollY > 100) {
    toTop.classList.add("active");
  } else {
    toTop.classList.remove("active");
  }
});

document.addEventListener("DOMContentLoaded", () => {

  // Disable autocomplete on all form inputs except tom-select
  const formInputs = document.querySelectorAll('.content form input:not(.ts-input)');
  formInputs.forEach(input => {
    input.setAttribute('autocomplete', 'off');
  });

  const formSelects = document.querySelectorAll(".form-select");
  formSelects.forEach(select => {
    const ts = new TomSelect(select, {
      create: false,
      sortField: {
        field: "text",
        direction: "asc"
      }
    });
  });

  const recipeInventorySelect = document.querySelector("#recipe_inventory");
  const recipeIngredientsSelect = document.querySelector("#recipe_ingredients");


  if (recipeInventorySelect && recipeIngredientsSelect) {

    const invetoryTS = new TomSelect(recipeInventorySelect, {
      create: false,
      options: recipeContext.inventories,
      valueField: "id",
      labelField: "name",
      searchField: "name",
      sortField: {
        field: "text",
        direction: "asc"
      }
    });
    // tomselect generation expects key value object
    const ingredientTS = new TomSelect(recipeIngredientsSelect, {
      create: false,
      options: recipeContext.foods.map(f => ({ value: f, text: f })),
      valueField: "value",
      labelField: "text",
    });


    function filterIngredients(inventoryId) {
      const filteredInventory = recipeContext.inventories.filter(inventory => {
        return inventory.id === parseInt(inventoryId);
      });
      ingredientTS.clearOptions();
      ingredientTS.addOptions(filteredInventory[0].foods.map(f => ({ value: f, text: f })));
      ingredientTS.refreshOptions(false);
    }

    recipeInventorySelect.addEventListener("change", (e) => {
      filterIngredients(e.target.value);
    });
  }


  const embeddedLists = document.querySelectorAll(".embedded");
  embeddedLists.forEach(list => {
    list.addEventListener("click", () => {
      const innerList = list.querySelector(".nested-ul");
      if (getComputedStyle(innerList).opacity === "1") {
        innerList.style.opacity = "0";
        innerList.style.pointerEvents = "none";
      } else {
        innerList.style.opacity = "1";
        innerList.style.pointerEvents = "auto";
      }
    })
  });

  dialogLogic();

  const toTop = document.querySelector("#scroll-top");
  if (!toTop) return;
  toTop.classList.toggle("active", window.pageYOffset > 100);

  document.addEventListener("htmx:afterSwap", dialogLogic);
  document.addEventListener("htmx:afterSwap", () => {
    const toTop = document.querySelector("#scroll-top");
    if (!toTop) return;
    toTop.classList.toggle("active", window.pageYOffset > 100);
  });

  document.addEventListener("htmx:afterSwap", (e) => {
    const swappedEl = e.detail.target;
    // Attach logic to new dialogs only
    if (swappedEl.matches(".info, #header-dialog, .dialog-container") || swappedEl.querySelector(".info, #header-dialog, .dialog-container")) {
      dialogLogic();
    }

    // Update scroll-to-top button
    const toTop = document.querySelector("#scroll-top");
    if (toTop) {
      toTop.classList.toggle("active", window.pageYOffset > 100);
    }

  });



  const openFilter = document.querySelector("#open-filters");
  const innerList = document.querySelector("#inner-list");

  if (openFilter && innerList) {
    openFilter.addEventListener("click", (e) => {
      innerList.classList.toggle("visible");
    });
  }


});


// ["DOMContentLoaded", "htmx:afterSwap"].forEach(eventType => {
//   document.addEventListener(eventType, dialogLogic);
//
//   document.addEventListener(eventType, () => {
//     const toTop = document.querySelector("#scroll-top");
//     if (!toTop) return;
//     toTop.classList.toggle("active", window.pageYOffset > 100);
//   });
// });

