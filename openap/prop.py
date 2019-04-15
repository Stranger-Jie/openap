"""Retrive properties of aircraft and engines."""

import os
import glob
import yaml
import numpy as np
import pandas as pd
from openap import aero

curr_path = os.path.dirname(os.path.realpath(__file__))
dir_aircraft = curr_path + "/data/aircraft/"
db_engine = curr_path + "/data/engine/engines.txt"


def available_aircraft():
    """Get avaiable aircraft types in OpenAP model.

    Returns:
        list of string: aircraft types.

    """
    files = sorted(glob.glob(dir_aircraft + '*.yml'))
    acs = [f[-8:-4].upper() for f in files]
    return acs


def aircraft(ac):
    """Get details of an aircraft type.

    Args:
        ac (string): ICAO aircraft type (for example: A320).

    Returns:
        dict: Peformance parameters related to the aircraft.

    """
    ac = ac.lower()

    files = glob.glob(dir_aircraft + ac + '.yml')

    if len(files) == 0:
        raise RuntimeError('Aircraft data not found.')

    f = files[0]
    acdict = yaml.safe_load(open(f))

    return acdict


def aircraft_engine_options(ac):
    """Get engine options of an aircraft type.

    Args:
        ac (string): ICAO aircraft type (for example: A320).

    Returns:
        list of string: Engine options.

    """
    acdict = aircraft(ac)

    if type(acdict['engine']['options']) == dict:
        eng_options = list(acdict['engine']['options'].values())
    elif type(acdict['engine']['options']) == list:
        eng_options = list(acdict['engine']['options'])

    return eng_options


def search_engine(eng):
    """Search engine by the starting characters.

    Args:
        eng (string): Engine type (for example: CFM56-5).

    Returns:
        list or None: Matching engine types.

    """
    ENG = eng.strip().upper()
    engines = pd.read_fwf(db_engine)

    selengs = engines[engines['name'].str.upper().str.startswith(ENG)]

    if selengs.shape[0] == 0:
        print('Engine not found.')
        result = None
    else:
        print('Engines found:')
        result = selengs.name.tolist()
        print(result)

    return result


def engine(eng):
    """Get engine parameters.

    Args:
        eng (string): Engine type (for example: CFM56-5B6).

    Returns:
        dict: Engine parameters.

    """
    ENG = eng.strip().upper()
    engines = pd.read_fwf(db_engine)

    # try to look for the unique engine
    selengs = engines[engines['name'].str.upper() == ENG]
    if selengs.shape[0] == 1:
        selengs.index = selengs.name
        result = selengs.to_dict(orient='records')[0]

        # compute fuel flow correction factor kg/s/N per meter
        if np.isfinite(result['cruise_sfc']):
            sfc_cr = result['cruise_sfc']
            sfc_to = (result['fuel_c3'] + result['fuel_c2'] + result['fuel_c1']) / (result['max_thrust']/1000)
            fuel_ch = np.round((sfc_cr - sfc_to) / (result['cruise_alt'] * aero.ft), 8)
        else:
            fuel_ch = 6.7e-7

        result['fuel_ch'] = fuel_ch
    else:
        raise RuntimeError('Engine data not found.')

    return result
