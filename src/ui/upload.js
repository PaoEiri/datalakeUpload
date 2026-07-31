async function loadFuentes() {
    const res = await fetch("/fuentes_registradas/");
    const data = await res.json();

    const select = document.getElementById("fuente-select");
    select.innerHTML = `<option value="">-- Sin fuente (huérfano) --</option>`;

    data.fuentes.forEach(f => {
        const actual = f.dataset_actual ? f.dataset_actual.dataset_name : "ninguno";
        const option = document.createElement("option");
        option.value = f.id_fuente;
        option.textContent = `${f.codigo_fuente} — ${f.sistema_origen} (actual: ${actual})`;
        select.appendChild(option);
    });
}

async function uploadFile() {
    const file = document.getElementById("file-input").files[0];
    if (!file) return alert("Selecciona un archivo");

    const idFuente = document.getElementById("fuente-select").value;

    const formData = new FormData();
    formData.append("file", file);
    if (idFuente) {
        formData.append("id_fuente", idFuente);
    }

    const res = await fetch("/datasets_upload/upload", {
        method: "POST",
        body: formData
    });

    if (res.ok) {
        alert("Archivo subido correctamente");
        loadList();
        loadFuentes();
    } else {
        const data = await res.json().catch(() => null);
        alert(data && data.detail ? data.detail : "Error al subir archivo");
    }
}
