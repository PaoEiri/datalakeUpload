function formatearNumeroES(n) {
    return Number(n).toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

async function initConsulta() {
    await loadGeografias();
    await loadAniosPrecios();
    await loadAniosIndicadores();
    await loadCategorias();
    buscarPrecios();
    buscarIndicadores();
}

async function loadGeografias() {
    const res = await fetch("/consulta/geografias");
    const data = await res.json();
    const opts = data.geografias
        .map(g => `<option value="${g.id_geografia}">${g.nombre} (${g.nivel})</option>`)
        .join("");

    document.getElementById("precios-geografia").innerHTML = `<option value="">Todas</option>${opts}`;
    document.getElementById("ind-geografia").innerHTML = `<option value="">Todas</option>${opts}`;
}

async function loadAniosPrecios() {
    const res = await fetch("/consulta/anios?grano=trimestral");
    const data = await res.json();
    document.getElementById("precios-anio").innerHTML =
        `<option value="">Todos</option>` + data.anios.map(a => `<option value="${a}">${a}</option>`).join("");
}

async function loadAniosIndicadores() {
    const res = await fetch("/consulta/anios?grano=anual");
    const data = await res.json();
    document.getElementById("ind-anio").innerHTML =
        `<option value="">Todos</option>` + data.anios.map(a => `<option value="${a}">${a}</option>`).join("");
}

async function loadCategorias() {
    const res = await fetch("/consulta/categorias_indicador");
    const data = await res.json();
    document.getElementById("ind-categoria").innerHTML =
        `<option value="">Todas</option>` + data.categorias.map(c => `<option value="${c}">${c}</option>`).join("");
}

async function onCategoriaChange() {
    const categoria = document.getElementById("ind-categoria").value;
    const url = categoria ? `/consulta/indicadores?categoria=${encodeURIComponent(categoria)}` : "/consulta/indicadores";
    const res = await fetch(url);
    const data = await res.json();
    document.getElementById("ind-indicador").innerHTML =
        `<option value="">Todos</option>` + data.indicadores.map(i => `<option value="${i.id_indicador}">${i.nombre_indicador}</option>`).join("");
    buscarIndicadores();
}

async function buscarPrecios() {
    const geografia = document.getElementById("precios-geografia").value;
    const anio = document.getElementById("precios-anio").value;

    const params = new URLSearchParams();
    if (geografia) params.set("id_geografia", geografia);
    if (anio) params.set("anio", anio);

    const res = await fetch(`/consulta/precios?${params}`);
    const data = await res.json();

    const filas = data.precios.map(p => `
        <tr>
            <td>${p.nombre_geografia}</td>
            <td>${p.nivel_geografia}</td>
            <td>${p.anio} T${p.trimestre}</td>
            <td>${formatearNumeroES(p.precio_m2)} €</td>
        </tr>
    `).join("");

    document.getElementById("precios-tbody").innerHTML =
        filas || `<tr><td colspan="4" class="empty">Sin resultados</td></tr>`;
}

async function buscarIndicadores() {
    const geografia = document.getElementById("ind-geografia").value;
    const anio = document.getElementById("ind-anio").value;
    const indicador = document.getElementById("ind-indicador").value;

    const params = new URLSearchParams();
    if (geografia) params.set("id_geografia", geografia);
    if (anio) params.set("anio", anio);
    if (indicador) params.set("id_indicador", indicador);

    const res = await fetch(`/consulta/indicadores_valores?${params}`);
    const data = await res.json();

    const filas = data.valores.map(v => `
        <tr>
            <td>${v.nombre_geografia}</td>
            <td>${v.nivel_geografia}</td>
            <td>${v.anio}</td>
            <td>${v.nombre_indicador}</td>
            <td>${formatearNumeroES(v.valor)} ${v.unidad}</td>
        </tr>
    `).join("");

    document.getElementById("indicadores-tbody").innerHTML =
        filas || `<tr><td colspan="5" class="empty">Sin resultados</td></tr>`;
}
