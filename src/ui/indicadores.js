function formatCobertura(pct) {
    if (pct === null || pct === undefined) return "—";
    return `${pct}%`;
}

function escapeAttr(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

async function loadIndicadores() {
    const res = await fetch("/indicadores_referencia");
    const data = await res.json();

    const tbody = document.getElementById("indicadores-ref-tbody");
    tbody.innerHTML = "";

    data.indicadores.forEach(ind => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${ind.nombre_indicador}</td>
            <td>${ind.categoria_indicador}</td>
            <td><input type="text" id="desc-${ind.indicador_id}" value="${escapeAttr(ind.descripcion)}"
                onblur="guardarEdicion(${ind.indicador_id})"></td>
            <td><input type="checkbox" ${ind.aplica_municipal ? "checked" : ""}
                onchange="toggleIndicador(${ind.indicador_id}, 'municipal', this.checked)"></td>
            <td>${formatCobertura(ind.cobertura_municipal_pct)}</td>
            <td><input type="checkbox" ${ind.aplica_distrital ? "checked" : ""}
                onchange="toggleIndicador(${ind.indicador_id}, 'distrital', this.checked)"></td>
            <td>${formatCobertura(ind.cobertura_distrital_pct)}</td>
            <td><input type="checkbox" ${ind.usar_en_ml ? "checked" : ""}
                onchange="toggleIndicador(${ind.indicador_id}, 'ml', this.checked)"></td>
            <td><textarea id="notas-${ind.indicador_id}"
                onblur="guardarEdicion(${ind.indicador_id})">${escapeAttr(ind.notas_adaptacion)}</textarea></td>
        `;
        tbody.appendChild(tr);
    });
}

async function toggleIndicador(indicadorId, nivel, activo) {
    // "ml" no cambia qué datos entran a fact_indicadores_anuales/Power BI,
    // solo qué ve el próximo entrenamiento del modelo — no amerita confirm().
    if (nivel !== "ml") {
        const accion = activo ? "activar" : "desactivar";
        if (!confirm(`¿Seguro que quieres ${accion} este indicador a nivel ${nivel}?`)) {
            loadIndicadores();
            return;
        }
    }

    const res = await fetch(`/indicadores_referencia/${indicadorId}/toggle`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nivel, activo }),
    });

    if (!res.ok) {
        alert("Error al actualizar el indicador.");
        loadIndicadores();
    }
}

async function guardarEdicion(indicadorId) {
    const descripcion = document.getElementById(`desc-${indicadorId}`).value;
    const notas_adaptacion = document.getElementById(`notas-${indicadorId}`).value;

    const res = await fetch(`/indicadores_referencia/${indicadorId}/editar`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ descripcion, notas_adaptacion }),
    });

    if (!res.ok) {
        alert("Error al guardar los cambios.");
        loadIndicadores();
    }
}

async function aplicarCambios() {
    const res = await fetch("/indicadores_referencia/aplicar_cambios", { method: "POST" });
    const data = await res.json();
    alert(data.message);
}
