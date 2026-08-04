let consultaCargada = false;

function switchView(viewId) {
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));

    document.getElementById(viewId).classList.add("active");
    document.querySelector(`.nav-btn[data-view="${viewId}"]`).classList.add("active");

    if (viewId === "view-consulta" && !consultaCargada) {
        consultaCargada = true;
        initConsulta();
    }
}

function switchSubtab(subtabId) {
    document.querySelectorAll(".subtab").forEach(s => s.classList.remove("active"));
    document.querySelectorAll(".subtab-btn").forEach(b => b.classList.remove("active"));

    document.getElementById(subtabId).classList.add("active");
    document.querySelector(`.subtab-btn[data-subtab="${subtabId}"]`).classList.add("active");
}
