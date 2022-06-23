from decimal import Decimal
from collections import namedtuple

# Constantes
# r1 * r2 * c1 * c2 = 1/omega^2
OMEGA_SQUARE = 281.45e-9
# 1/(r1 * c2) + 1/(r1 * c1) = 2666
W_Q = 2666
# Limites de los elementos
min_cap = 1e-9
max_cap = 1e-6
min_res = 1e3
max_res = 1e6
# Series de los elementos
cap_set = [100,120,150,180,220,270,330,390,470,560,680,820]
res_set = [100,110,120,130,150,160,180,200,220,240,270,300,330,360,390,430,470,510,560,620,680,750,820,910]

Components = namedtuple('components', ('r1', 'r2', 'c1', 'c2', 'w2', 'err_w2', 'wq', 'err_w_q'))


def fexp(number):
    """
    Dado un numero, devuelve el exponente en base 10 del mismo
    """
    (sign, digits, exponent) = Decimal(number).as_tuple()
    return len(digits) + exponent - 1

# Validadores de valores
def check_res(r):
    """
    Verifica si una resistencia se encuentra entre los valores permitidos
    """
    return min_res <= r <= max_res


def check_cap(c):
    """
    Verifica si un capacitor se encuentra entre los valores permitidos
    """
    return min_cap <= c <= max_cap


def value_yielder(base, serie_value, exp, check_func):
    """
    Dada una valor deserie y un exponente inicial, se buscan todos los valores de multiplicadores
        (..., 0.01, 0.1, 1, 10, 100, ...)
    que estén dentro de los valores permitidos.
    Para ello se usa una base que se espera sea 1 o -1 para ver si se debe aumentar o disminuir
    el multiplicador
    Ejemplos:
        base = 1
        serie_value = 10
        exp = 10^-9

        Se prueba: 10^-9, 10^-8, 10^-7, ...

    En cambio si base = -1:
        10^-9, 10^-10, 10^-11, ...
    """
    n = 0
    while True:
        new_base = base * n
        multi = 10 ** new_base
        num = serie_value * exp * multi
        print(num)
        if check_func(num):
            yield num
            n += 1
        else:
            break


def get_valid_element(min_val, series, check_func):
    # Tomo como referencia el valor minimo permitido y tomo su exponente como base
    exp = 10**fexp(min_val)

    # Primero itero por los valores de las series
    for serie_value in series:
        # Empiezo con multiplicadores negativos
        for value in value_yielder(base=-1, serie_value=serie_value, exp=exp, check_func=check_func):
            yield value

        # Sigo con multiplicadores positivos
        for value in value_yielder(base=1, serie_value=serie_value, exp=exp, check_func=check_func):
            yield value


def brute_force(valid_caps, valid_res):
    for c1 in valid_caps:
        for c2 in valid_caps:
            for r1 in valid_res:
                for r2 in valid_res:
                    calc_omega = r1 * r2 * c1 * c2
                    omega_err = abs(calc_omega - OMEGA_SQUARE) / OMEGA_SQUARE
                    calc_q = (1/(r1*c1))+(1/(r1*c2))
                    q_err = abs(calc_q - W_Q) / W_Q
                    if omega_err <= 0.1 and q_err <= 0.1:
                        comp = Components(r1=r1, r2=r2,
                                          c1=c1, c2=c2,
                                          w2=calc_omega, err_w2=omega_err,
                                          wq=calc_q, err_w_q=q_err)
                        yield comp, max(omega_err, q_err)

def resolver():
    valid_caps = set(get_valid_element(min_cap, cap_set, check_cap))
    valid_res = set(get_valid_element(min_res, res_set, check_res))
    n_caps = len(valid_caps)
    n_res = len(valid_res)
    print(f"Tenemos {n_caps} valores posibles de capacitores")
    print(f"Tenemos {n_res} valores posibles de resistencias")
    print(f"Tenemos {n_res**2 * n_caps**2} valores posibles totales")

    print('Busco por fuerza bruta')
    valid_res = list(brute_force(valid_caps, valid_res))
    print(f"Tengo {len(valid_res)} posibilidades")
    mejor = min(valid_res, key=lambda x:x[1])
    print(mejor)

resolver()
