async function loadList() {
    const res = await fetch("/datasets_upload");
    const data = await res.json();

    console.log("Respuesta API:", data);

    const table = document.getElementById("datasets-table");
    table.innerHTML = `
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Formato</th>
            <th>Tamaño</th>
            <th>Estado</th>
            <th>Preview</th>
        </tr>
    `;

    
    data.datasets.forEach(d => {
        table.innerHTML += `
            <tr>
                <td>${d.id}</td>
                <td>${d.dataset_name}</td>
                <td>${d.file_format}</td>
                <td>${(d.size_bytes/1024).toFixed(1)} KB</td>
                <td><span class="status status-${d.status}">${d.status}</span></td>
                <td><button onclick="showPreview(${d.id})">Ver</button></td>
            </tr>
        `;
    });
}


async function showPreview(id) {
    const res = await fetch(`/datasets_upload/${id}/preview`);
    const data = await res.json();
    alert(JSON.stringify(data, null, 2));
}
