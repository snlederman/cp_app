import datetime
import timeit

import pandas as pd
from numpy import zeros
from scipy.linalg import expm
from scipy.stats import norm, t

COUNTRIES = ['Argentina', 'Bolivia', 'Brasil', 'Chile', 'Colombia', 'Costa Rica', 'Ecuador', 'El Salvador',
             'Guatemala', 'Honduras', 'Mexico', 'Panama', 'Paraguay', 'Peru', 'Republica Dominicana', 'Uruguay',
             'Venezuela']

from multiprocessing import Pool
from multiprocessing.dummy import Pool as PoolTh


def n_date(date):
    """
    :param date: Un str con una fecha correspondiente.
    :return: Tipo datetime con los dias, meses y anos correspondiente.
    """
    date = date.split('/')
    return datetime.date(day=int(date[1]), month=int(date[0]), year=int(date[2]))


def n_calif(C):
    """
    :param C: Un str con el tipo de calificacion.
    :return: Retorna un int con la clase de calificacion correspondiente
    """
    if C == 'AAA':
        return 1
    elif C in ['AA+', 'AA-', 'AA']:
        return 2
    elif C in ['A+', 'A-', 'A']:
        return 3
    elif C in ['BBB+', 'BBB-', 'BBB']:
        return 4
    elif C in ['BB+', 'BB-', 'BB']:
        return 5
    elif C in ['B+', 'B-', 'B']:
        return 6
    elif C in ['CCC+', 'CCC-', 'CCC', 'CC', 'C']:
        return 7
    elif C == 'SD':
        return 8


def country_id(cid):
    """
    :param id: id de tipo str y corresponde a un pais.
    :return: Un str con el nombre del pais correspondiente.
    """

    return COUNTRIES[int(cid) - 1]


def _count_int_y(data, t):
    return data[(data.to < t) & (data.tf >= t)].count().country


def int_y(to, data):
    """
    :param to: tiempo inicial.
    :param data: Un dataframe de prestarios en el tiempo de la clase i.
    :return: La integral de los prestarios en la clase i en el tiempo s.
        - Se inicializa y.
        - Se itera en el tiempo en un rango de to a tf.
        - Se filtra la data que esta en el rango definido, y luego se obtiene la cantidad de prestatarios en dicho rango.
        - Finalmente se devuelve la sumataria de y.
        - Se divide entre 365 para pasar de dias a agnos.
    """

    _count_pool = PoolTh()

    y = _count_pool.starmap(_count_int_y, [(data, t) for t in range(to, max(data['tf']) + 1)])
    return sum(map(lambda x: x / 365, y))


def _int_y_wrapper(i, df_data):
    to = min(df_data[df_data['rating_id'] == i]['to'])
    return int_y(to, df_data[df_data['rating_id'] == i])


def mt(data, DEBUG=False):
    start = timeit.default_timer()

    data['country'] = list(map(country_id, data['id']))  # Crea una llave con nos nombres de los paises segun su id.
    data['rating_id'] = list(map(n_calif, data['rating']))  # Crea una llave con las clases de calificaciones.
    data['date'] = list(map(n_date, data['date']))  # Se modifica la llave date de tipo str a datetime.

    df_data = pd.DataFrame(data=data).sort_values(
        'date')  # Creo un dataframe con la data original y lo ordeno por date.

    st = min(df_data['date'])  # Tomo el start time, o tiempo de inicio de la muestra.
    ft = max(df_data['date'])  # Tomo el finish time, o tiempo final de la muestra.
    """
        Tomo los date y los resto con el start time para tener un to (tiempo inicio) 
        con respecto al primer tiempo en nuestra muestra.
    """
    df_data['to'] = list(map(lambda x: (x - st).days, df_data['date']))

    """
        Cantidad de clases para transiciones.
    """
    N_id = len(df_data.drop_duplicates(['rating_id'])['rating_id'].values)
    N = zeros((N_id, N_id))  # Inicio mi matrix N como una matrix de ceros tamano N_id, N_id.

    """
        Creacion de la matrix de transiciones de prestarios de la clase i a la clase j; donde i y j puede tomar N_id clases.
        - Itero entre los prestatarios.
        - Luego filtro la data de dicho prestario, y tomo un array con sus distintas clases.
        - Itero entre las clases - 1, ya que el ultimo no tiene transcicion.
        -  Luego se incrementa la posicion de N, donde se hayo una transicion de clase i a j.
    """
    for country in df_data.drop_duplicates(['country'])['country'].values:
        rate = df_data[df_data.country == country]['rating_id'].values
        for i in range(len(rate) - 1):
            N[rate[i] - 1][rate[i + 1] - 1] += 1

    """
        Cantidad de prestatarios.
    """
    N_country = len(df_data.drop_duplicates(['country'])['country'].values)
    """
        Se registra la duracion de los prestarios en cada clase.
            - Se itera entre los distintos prestatarios.
            - Luego de cada prestario se itera en sus tiempos de inicio en cada clase.
            - Se crea una condicion donde hay un booleano new que nos dice si estamos 
            en un prestario nuevo.
            - Si el prestario es nuevo, se toma el punto to como aux.
            - Si no se toma el punto to y se resta el aux, que es el punto anterior,
            dandonos la duracion.
            - Se toma el to del siguiente y se le asigna al tf del anterior.
            - Se toma el to como aux para la proxima iteracion.
            - Para la ultima iteracion se toma el to y se resta con respecto a la 
            diferencia que hay entre el tiempo final y el tiempo inicial.
            - Y para el tiempo final se toma el ultimo el ultimo tiempo.

    """
    df_data.sort_values(['id', 'date'])
    dt = []  # Duracion.
    tf = []  # Tiempo final.
    for i in range(1, N_country + 1):
        new = True
        for data in df_data[df_data['id'] == i]['to']:
            if new:
                aux = data
                new = False
            else:
                dt.append(data - aux)
                tf.append(data)
                aux = data
        dt.append((ft - st).days - aux)
        tf.append((ft - st).days)

    df_data['dt'] = pd.Series(data=dt)  # Se agrega una columna dt (duracion) al dataframe.
    df_data['tf'] = pd.Series(data=tf)  # Se agrega una columna tf (tiempo final) al dataframe

    """
        Creacion de la cantidad de prestatarios en la clase i.
            - Se itera entre las distintas clase.
            - Se toma el menor tiempo inicial.
            - Se ejecuta la funcion int_y para tener la integracion por cada clase.
    """
    Y = []  # Inicializo el array de Y
    # Tomo los valores de las clases, ordenadas crecientemente.
    rate = df_data.drop_duplicates(['rating_id']).sort_values('rating_id')['rating_id'].values

    _loop_rate = Pool()

    Y = _loop_rate.starmap(_int_y_wrapper, [(i, df_data) for i in rate])

    """
        Se calcula la matrix generadora.
            - Se itera entre el numero de clase.
            - Cada fila se divide entre Yi, llamado tasa de transicion.
            - La digonal corresponde a la sumatoria negativa de cada fila.
            - Se hace el elemento [i,i], igual a cero para que no afecte en la sumatoria.
            - La ultima fila es igual a cero, debido a que es un estado absorbente.
    """

    for i in range(N_id - 1):
        N[i] = N[i] / Y[i]
        N[i][i] = 0
        N[i][i] = -sum(N[i])
    else:
        N[N_id - 1] = N[N_id - 1] * 0

    """
        Calculo de la matrix de transicion.
            - Se aplica la funcion exponecial a la matrix N y se multiplica por 100 para obtenerlo en probabilidad.
    """
    Mt = expm(N) * 100

    """
        Para verificar todas las filas tienen que dar 100.
        Solo se ejecuta cuando se es de modo DEBUG.
    """

    stop = timeit.default_timer()
    execution_time = stop - start
    if DEBUG:
        """
        print(Mt)
        for country in df_data.drop_duplicates(['country'])['country'].values:
            print(df_data[df_data.country == country].values[-1])
        for i in range(N_id):
            print(sum(Mt[i]))
        """
        print("mat_trans Program Executed in {} seconds".format(execution_time))

    # TODO: Comentar esta parte del codigo.
    sol = {'country': [], 'rate_id': [], 'Pd': [], 'd': []}
    for country in df_data.drop_duplicates(['country'])['country'].values:
        rate = df_data[df_data.country == country]['rating_id'].values[-1]
        sol['country'].append(country)
        sol['rate_id'].append(rate)
        Pd = Mt[rate - 1][- 1]
        if Pd == 100:
            Pd = 99.9999999
        sol['Pd'].append(Pd)
        # sol['d'].append(norm.ppf(Pd / 100))
        alfa = 3
        sol['d'].append(t.ppf(Pd / 100, alfa))
    df_sol = pd.DataFrame(data=sol).sort_values('country')
    return df_sol.loc[:,['country', 'Pd']]
