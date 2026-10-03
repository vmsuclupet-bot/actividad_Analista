"""
Sistema Experto de orientación rápida – Enfermedades respiratorias agudas (Neumología)
Metodología: guía para construir un Sistema Experto
  (variables -> diagrama de dependencias -> reglas IF-THEN -> interfaz)
Motor: encadenamiento hacia adelante (forward chaining) con explicación de reglas disparadas.

Ejecutar:  streamlit run app.py
"""
import streamlit as st

# =====================================================================
#  1. VARIABLES DE ENTRADA (hechos que se le preguntan al usuario)
#     clave -> (pregunta, {valor: etiqueta})
# =====================================================================
SN = {"no": "No", "si": "Sí"}
PREGUNTAS = {
    "signos_alarma": ("¿Hay labios o cara azulados, confusión, desmayo o somnolencia extrema?", SN),
    "disnea": ("¿Tiene dificultad para respirar?",
               {"no": "No", "esfuerzo": "Solo al hacer esfuerzo", "reposo": "Incluso en reposo"}),
    "dolor_toracico": ("¿Tiene dolor en el pecho al respirar o toser?", SN),
    "fiebre": ("Fiebre",
               {"ninguna": "Sin fiebre", "leve": "Leve (< 38 °C)", "alta": "Alta (≥ 38 °C)"}),
    "tos": ("Tos", {"no": "No tiene", "seca": "Seca", "flema": "Con flema"}),
    "dolor_garganta": ("¿Dolor de garganta?", SN),
    "congestion": ("¿Congestión nasal o estornudos?", SN),
    "dolor_cuerpo": ("¿Dolor muscular intenso, escalofríos o malestar general marcado?", SN),
    "sibilancias": ("¿Silbidos o 'pitos' en el pecho al respirar?", SN),
    "asma": ("¿Tiene antecedente de asma o EPOC?", SN),
    "anosmia": ("¿Perdió el olfato o el gusto?", SN),
    "riesgo": ("¿Es mayor de 65 años, embarazada, inmunodeprimido o tiene enfermedad crónica?", SN),
    "duracion": ("¿Cuánto tiempo lleva con los síntomas?",
                 {"corta": "4 días o menos", "media": "5 a 14 días", "larga": "Más de 14 días"}),
}


# =====================================================================
#  2. BASE DE CONOCIMIENTO (reglas SI-ENTONCES)
#     "si": {variable: {valores permitidos}}   (todas deben cumplirse = AND)
#     "entonces": (variable, valor)
#     Reglas intermedias: alarma, atencion.  Regla final: dx (diagnósticos).
#     Para variables intermedias, la PRIMERA regla que concluye gana
#     (las reglas están ordenadas de mayor a menor prioridad).
# =====================================================================
def R(id_, si, entonces):
    return {"id": id_, "si": si, "entonces": entonces}

REGLAS = [
    # ---- Etapa 1: nivel de alarma respiratoria (intermedia) ----------
    R("A1", {"signos_alarma": {"si"}}, ("alarma", "alta")),
    R("A2", {"disnea": {"reposo"}}, ("alarma", "alta")),
    R("A3", {"dolor_toracico": {"si"}, "disnea": {"esfuerzo"}}, ("alarma", "alta")),
    R("A4", {"disnea": {"esfuerzo"}}, ("alarma", "moderada")),
    R("A5", {"dolor_toracico": {"si"}}, ("alarma", "moderada")),
    R("A6", {"sibilancias": {"si"}}, ("alarma", "moderada")),
    R("A7", {"fiebre": {"alta"}, "tos": {"flema"}}, ("alarma", "moderada")),
    R("A8", {}, ("alarma", "baja")),  # por defecto

    # ---- Etapa 2: diagnósticos presuntivos ---------------------------
    R("D1", {"fiebre": {"alta"}, "tos": {"flema"}, "disnea": {"esfuerzo", "reposo"}},
      ("dx", "neumonia")),
    R("D2", {"fiebre": {"alta"}, "dolor_toracico": {"si"}, "tos": {"seca", "flema"}},
      ("dx", "neumonia")),
    R("D3", {"sibilancias": {"si"}, "asma": {"si"}}, ("dx", "asma")),
    R("D4", {"sibilancias": {"si"}, "disnea": {"esfuerzo", "reposo"}}, ("dx", "asma")),
    R("D5", {"fiebre": {"alta"}, "dolor_cuerpo": {"si"}, "tos": {"seca", "flema"},
             "duracion": {"corta"}}, ("dx", "influenza")),
    R("D6", {"anosmia": {"si"}, "fiebre": {"leve", "alta"}}, ("dx", "covid")),
    R("D7", {"anosmia": {"si"}, "tos": {"seca", "flema"}}, ("dx", "covid")),
    R("D8", {"fiebre": {"ninguna", "leve"}, "congestion": {"si"}, "dolor_cuerpo": {"no"},
             "disnea": {"no"}, "alarma": {"baja"}}, ("dx", "resfriado")),
    R("D9", {"dolor_garganta": {"si"}, "tos": {"no"}, "congestion": {"no"},
             "fiebre": {"leve", "alta"}}, ("dx", "faringitis")),
    R("D10", {"tos": {"flema"}, "duracion": {"media", "larga"},
              "fiebre": {"ninguna", "leve"}, "disnea": {"no"}}, ("dx", "bronquitis")),
    R("D11", {"tos": {"seca", "flema"}, "duracion": {"larga"}}, ("dx", "tos_prolongada")),

    # ---- Etapa 3: nivel de atención recomendado (intermedia/final) ---
    R("T1", {"alarma": {"alta"}}, ("atencion", "urgencias")),
    R("T2", {"alarma": {"moderada"}}, ("atencion", "pronta")),
    R("T3", {"alarma": {"baja"}, "riesgo": {"si"}}, ("atencion", "pronta")),
    R("T4", {"alarma": {"baja"}, "duracion": {"larga"}}, ("atencion", "programada")),
    R("T5", {"alarma": {"baja"}}, ("atencion", "autocuidado")),
]

# =====================================================================
#  3. MOTOR DE INFERENCIA (encadenamiento hacia adelante)
# =====================================================================
def cumple(cond, hechos):
    return all(v in hechos and hechos[v] in permitidos for v, permitidos in cond.items())


def inferir(hechos_iniciales):
    hechos, dx, traza, disparadas = dict(hechos_iniciales), [], [], set()
    cambio = True
    while cambio:
        cambio = False
        for r in REGLAS:
            if r["id"] in disparadas or not cumple(r["si"], hechos):
                continue
            var, val = r["entonces"]
            if var == "dx":
                if val not in dx:
                    dx.append(val)
            elif var in hechos:        # ya la fijó una regla de mayor prioridad
                continue
            else:
                hechos[var] = val
            disparadas.add(r["id"])
            traza.append(r)
            cambio = True
    return hechos, dx, traza


def texto_regla(r):
    if r["si"]:
        cond = " Y ".join(f"{v} = {' o '.join(sorted(vals))}" for v, vals in r["si"].items())
    else:
        cond = "(ninguna otra regla aplicó)"
    var, val = r["entonces"]
    return f"SI {cond} ENTONCES {var} = {val}"


# =====================================================================
#  4. TEXTOS DE SALIDA
# =====================================================================
DIAGNOSTICOS = {
    "neumonia": ("Posible neumonía",
                 "Fiebre alta con tos y/o dolor torácico y dificultad respiratoria."),
    "asma": ("Posible crisis de asma / broncoespasmo",
             "Silbidos en el pecho, con antecedente de asma o dificultad para respirar."),
    "influenza": ("Posible influenza (gripe)",
                  "Fiebre alta, dolor muscular y tos de inicio reciente."),
    "covid": ("Sospecha de COVID-19",
              "Pérdida de olfato/gusto junto con fiebre o tos. Conviene hacer una prueba."),
    "resfriado": ("Posible resfriado común",
                  "Congestión con tos o dolor de garganta, sin fiebre alta ni dificultad para respirar."),
    "faringitis": ("Posible faringitis (viral o bacteriana)",
                   "Dolor de garganta con fiebre, sin tos ni congestión. Una prueba rápida puede aclarar la causa."),
    "bronquitis": ("Posible bronquitis aguda",
                   "Tos con flema de varios días, sin fiebre alta ni dificultad para respirar."),
    "tos_prolongada": ("Tos prolongada (más de 14 días)",
                       "Requiere estudio médico para descartar otras causas."),
}

ATENCION = {
    "urgencias": ("error", "🚨 Acuda a URGENCIAS ahora",
                  "Hay señales de alarma respiratoria. No espere: vaya a un servicio de urgencias "
                  "o llame al número de emergencias de su localidad."),
    "pronta": ("warning", "⚠️ Consulta médica pronta (hoy o en 24 horas)",
               "Sus síntomas o factores de riesgo requieren valoración médica en breve. "
               "Si empeora la respiración, acuda a urgencias."),
    "programada": ("info", "📅 Consulta médica programada",
                   "Los síntomas llevan demasiado tiempo. Pida una cita para estudiarlos."),
    "autocuidado": ("success", "✅ Autocuidado en casa y vigilancia",
                    "Reposo, buena hidratación y ventilar los ambientes. "
                    "Consulte si aparece fiebre alta, dificultad para respirar o si no mejora en unos días."),
}


# =====================================================================
#  5. INTERFAZ (Streamlit)
# =====================================================================
def main():
    st.set_page_config(page_title="SE Respiratorio", page_icon="🫁", layout="centered")
    st.title("🫁 Sistema Experto: orientación rápida en enfermedades respiratorias")
    st.caption("Prototipo educativo delimitado a **neumología (infecciones respiratorias agudas)**. "
               "Orienta, no diagnostica: **no sustituye la valoración de un profesional de la salud.**")

    with st.form("consulta"):
        respuestas = {}
        c1, c2 = st.columns(2)
        for i, (clave, (pregunta, opciones)) in enumerate(PREGUNTAS.items()):
            with (c1 if i % 2 == 0 else c2):
                respuestas[clave] = st.selectbox(
                    pregunta, list(opciones.keys()),
                    format_func=lambda k, o=opciones: o[k], key=clave)
        enviar = st.form_submit_button("Evaluar síntomas", type="primary")

    if not enviar:
        st.info("Responda las preguntas y pulse **Evaluar síntomas**.")
        return

    hechos, dx, traza = inferir(respuestas)

    tipo, titulo, detalle = ATENCION[hechos["atencion"]]
    getattr(st, tipo)(f"**{titulo}**\n\n{detalle}")

    st.subheader("Diagnóstico presuntivo")
    if dx:
        for d in dx:
            nombre, motivo = DIAGNOSTICOS[d]
            st.markdown(f"- **{nombre}**: {motivo}")
    else:
        st.write("No se identificó un patrón claro con los datos ingresados. "
                 "Si los síntomas persisten o empeoran, consulte a un médico.")

    st.metric("Nivel de alarma respiratoria", hechos["alarma"].upper())

    with st.expander("¿Por qué? Reglas disparadas (explicación del sistema)"):
        for r in traza:
            st.code(f"{r['id']}: {texto_regla(r)}", language=None)

    with st.expander("Ver la base de conocimiento completa"):
        for r in REGLAS:
            st.code(f"{r['id']}: {texto_regla(r)}", language=None)


if __name__ == "__main__":
    main()
