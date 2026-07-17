async function uploadFile() {
    const file = document.getElementById("file-input").files[0];
    if (!file) return alert("Selecciona un archivo");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/datasets_upload/upload", {
        method: "POST",
        body: formData
    });

    if (res.ok) {
        alert("Archivo subido correctamente");
        loadList();
    } else {
        alert("Error al subir archivo");
    }
}
