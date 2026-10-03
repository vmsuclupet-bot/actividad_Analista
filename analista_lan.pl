% =====================================================================
%  SISTEMA EXPERTO PARA LA ASIGNACION DE UN ANALISTA DE REDES LAN
%  Caso: Analista Red LAN  (Inteligencia Artificial 2)
%
%  Uso en SWISH (swish.swi-prolog.org):
%     ?- analista.
%  Responda cada pregunta con un numero terminado en punto. Ej:  50.
% =====================================================================

% ---------------------------------------------------------------------
%  PROGRAMA PRINCIPAL (interfaz de usuario)
% ---------------------------------------------------------------------
analista :-
    nl,
    write('=== SISTEMA EXPERTO PARA LA ASIGNACION DE UN ANALISTA DE REDES ==='), nl, nl,
    pregunta('1. Cuantas personas laboran en su organizacion', positivo, Personas),
    pregunta('2. Cual es el presupuesto estimado para este proyecto', positivo, PE),
    pregunta('3. Cuantas computadoras seran conectadas en red', no_negativo, NC),
    pregunta('4. Cuantas computadoras seran adicionadas en los proximos 2 anios', no_negativo, NA),
    pregunta('5. De cuantos pisos es su organizacion', no_negativo, Pisos),
    pregunta('6. Con cuantos edificios cuenta su organizacion', no_negativo, Edificios),
    evaluar(Personas, PE, NC, NA, Pisos, Edificios, R),
    mostrar_resultado(R).

pregunta(Texto, Tipo, Valor) :-
    format('~w? (numero terminado en punto): ', [Texto]),
    read(V),
    (   number(V), valido(Tipo, V)
    ->  Valor = V
    ;   V == end_of_file
    ->  fail
    ;   write('  Dato invalido, intente de nuevo.'), nl,
        pregunta(Texto, Tipo, Valor)
    ).

valido(positivo, V)    :- V > 0.
valido(no_negativo, V) :- V >= 0.

mostrar_resultado(r(Tam, NivP, Costo, FC, NivC, Tipo)) :-
    Costo = costo(Tarjetas, Cableado, Mant, Consul, CE),
    nl,
    write('--------------- RESULTADO ---------------'), nl,
    format('Tamano de la organizacion : ~w~n', [Tam]),
    format('Nivel de presupuesto      : ~w~n', [NivP]),
    format('Tarjetas de red           : $~2f~n', [Tarjetas]),
    format('Cableado                  : $~2f~n', [Cableado]),
    format('Mantenimiento (9%)        : $~2f~n', [Mant]),
    format('Consultoria               : $~2f~n', [Consul]),
    format('COSTO ESTIMADO            : $~2f~n', [CE]),
    format('Factor de costo           : ~3f~n', [FC]),
    format('Nivel de costo            : ~w~n', [NivC]),
    upcase_atom(Tipo, TipoMay),
    nl,
    write('SE LE RECOMIENDA EL ANALISTA: '), write(TipoMay), nl.

% ---------------------------------------------------------------------
%  EVALUACION (se puede consultar directamente, sin preguntas)
%  ?- evaluar(50, 30000, 40, 10, 2, 1, R).
% ---------------------------------------------------------------------
evaluar(Personas, PE, NC, NA, Pisos, Edificios, r(Tam, NivP, Costo, FC, NivC, Tipo)) :-
    tamano_organizacion(Personas, Tam),
    nivel_presupuesto(PE, NivP),
    costo_estimado(NC, NA, Pisos, Edificios, Costo),
    Costo = costo(_, _, _, _, CE),
    factor_costo(CE, PE, FC),
    nivel_costo(FC, NivC),
    tipo_analista(NivP, Tam, NivC, Tipo), !.

% ---------------------------------------------------------------------
%  TRIANGULOS DEL DIAGRAMA DE DEPENDENCIAS
% ---------------------------------------------------------------------

% Triangulo 3: Numero de personas -> Tamano de la organizacion
tamano_organizacion(NPer, pequena)    :- NPer >= 1,   NPer =< 20.
tamano_organizacion(NPer, mediana)    :- NPer > 20,   NPer < 100.
tamano_organizacion(NPer, grande)     :- NPer >= 100, NPer < 500.
tamano_organizacion(NPer, muy_grande) :- NPer >= 500.

% Triangulo 4: Presupuesto estimado -> Nivel de presupuesto
nivel_presupuesto(PE, bajo)  :- PE > 0,      PE < 10000.
nivel_presupuesto(PE, medio) :- PE >= 10000, PE < 50000.
nivel_presupuesto(PE, alto)  :- PE >= 50000.

% Triangulo 6: NC, NA, pisos, edificios -> Costo estimado
costo_estimado(NC, NA, Pisos, Edificios, costo(Tarjetas, Cableado, Mant, Consul, CE)) :-
    Tarjetas is 600 * (NC + NA),
    Cableado is 2000 * Pisos + 8000 * Edificios,
    Neto     is Tarjetas + Cableado,
    Mant     is 0.09 * Neto,
    Consul   is 2000 + 0.06 * Neto,
    CE       is Neto + Mant + Consul.

% Triangulo 5: Costo estimado y presupuesto -> Factor de costo
factor_costo(CE, PE, FC) :- FC is CE / PE.

% Triangulo 2: Factor de costo -> Nivel de costo
nivel_costo(FC, aceptable) :- FC =< 1.
nivel_costo(FC, en_rango)  :- FC > 1, FC =< 1.5.
nivel_costo(FC, alto)      :- FC > 1.5.

% ---------------------------------------------------------------------
%  TRIANGULO 1: REGLAS FINALES (conjunto de reglas del Paso 5)
%  tipo_analista(NivelPresupuesto, Tamano, NivelCosto, Tipo)
%  El nivel de costo es "_" cuando la regla acepta los tres valores.
% ---------------------------------------------------------------------

% RULE 1
tipo_analista(bajo, Tam, _, principiante) :-
    memberchk(Tam, [pequena, mediana]).
% RULE 2
tipo_analista(bajo, grande, _, entrenado).
% RULE 3
tipo_analista(bajo, muy_grande, _, experimentado).
% RULE 4
tipo_analista(medio, pequena, _, principiante).
% RULE 5
tipo_analista(medio, mediana, _, entrenado).
% RULE 6
tipo_analista(medio, grande, _, entrenado).
% RULE 7
tipo_analista(medio, muy_grande, _, experimentado).
% RULE 8
tipo_analista(alto, pequena, _, entrenado).
% RULE 9
tipo_analista(alto, mediana, _, entrenado).
% RULE 10
tipo_analista(alto, Tam, _, experimentado) :-
    memberchk(Tam, [grande, muy_grande]).
