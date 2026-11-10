import requests
import json
import os
from assumptions import *

if not os.path.exists("minimum_wage.json"):
    with open("minimum_wage.json", "w") as file:
        minimum_wage = get_minimum_wage()
        data = {}
        data["value"] = minimum_wage["value"]
        data["time"] = minimum_wage["dimension"]["time"]["category"]["index"]
        json.dump(data, file, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_auto_info(kenteken):
    try:
        url = f"https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={kenteken}"
        response = requests.get(url)
        if response.json() == []:
            print(f"Geen informatie gevonden voor kenteken {kenteken}.")
            return []
        elif response.status_code != 200:
            print(f"Fout bij het ophalen van auto-informatie voor kenteken {kenteken}: {response.status_code}")
            return []
        else:
            return response.json()
    except Exception as e:
        print(f"Fout bij het ophalen van auto-informatie voor kenteken {kenteken}: {e}")
        return []

def get_horsepower(auto):

    fuel_info = auto['auto_info']['brandstoffen']
    horsepower = 0
    for fuel in fuel_info:
        if fuel['brandstof_omschrijving'] == 'Elektriciteit' :
           horsepower += int(fuel['nominaal_continu_maximumvermogen'].split('.')[0])*1.35962
        elif fuel['brandstof_omschrijving'] == 'Benzine' :
           horsepower += int(fuel['nettomaximumvermogen'].split('.')[0])*1.35962
        if fuel['brandstof_omschrijving'] == 'Diesel' :
           horsepower += int(fuel['nettomaximumvermogen'])*1.35962
    auto['auto_info']['totaal_continue_vermogen_pk'] = f"{horsepower:.2f}"
    return auto

def get_fuel_info(kenteken):
    try:
        url = f"https://opendata.rdw.nl/resource/8ys7-d773.json?kenteken={kenteken}"
        response = requests.get(url)
        if response.json() == []:
            print(f"Geen brandstofinformatie informatie gevonden voor kenteken {kenteken}.")
            return []
        elif response.status_code != 200:
            print(f"Fout bij het ophalen van brandstofinformatie voor kenteken {kenteken}: {response.status_code}")
            return []
        else:
            return response.json()
    except Exception as e:
        print(f"Fout bij het ophalen van brandstofinformatie voor kenteken {kenteken}: {e}")
        return []

def get_minimum_wage():
    try:
        url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/earn_mw_cur?geo=NL"
        response = requests.get(url)
        if response.json() == []:
            print("Geen minimumlooninformatie gevonden.")
            return []
        elif response.status_code != 200:
            print(f"Fout bij het ophalen van minimumlooninformatie: {response.status_code}")
            return []
        else:
            return response.json()
    except Exception as e:
        print(f"Fout bij het ophalen van minimumlooninformatie: {e}")
        return []

def exist_auto(kenteken):
    try:
        with open("auto.json", "r") as file:
            data = json.load(file)
            return kenteken in data
    except FileNotFoundError:
        return False

def energy_consumption_flag_electric(auto):
    # Controleer of de auto een elektrische auto is en bepaal het model op basis van het gewicht qua energieverbruik
    fuel_info = auto['auto_info']['brandstoffen']
    for fuel in fuel_info:
        if fuel['brandstof_omschrijving'] == 'Elektriciteit' and not (fuel.get('klasse_hybride_elektrisch_voertuig', None) == 'NOVC-HEV' or fuel.get('klasse_plug_in_hybrid_voertuig', None) == 'OVC-HEV'):
            if int(auto['auto_info']['massa_ledig_voertuig']) < 1500:
                model= "small"
            elif 1500 <= int(auto['auto_info']['massa_ledig_voertuig']) < 2000:
                model= "average"
            elif int(auto['auto_info']['massa_ledig_voertuig']) >= 2000:
                model= "large"
            auto['auto_info']['brandstoffen'][0]['energy_consumption_flag'] = model
    return auto

def add_to_json(auto):

    if not os.path.exists("auto.json"):
        with open("auto.json", "w") as file:
            data = {}
            data[auto['auto_info']["kenteken"]] = auto
            json.dump(data, file, indent=4)
    
    else:
        with open("auto.json", "r+") as file:
            data = json.load(file)
            data[auto['auto_info']["kenteken"]] = auto
            file.seek(0)
            json.dump(data, file, indent=4)

def read_json(kenteken):
    with open("auto.json", "r") as file:
        data = json.load(file)
        return data.get(kenteken, None)

def main_menu():
    clear_screen()
    print("----------Welkom bij de Auto Informatie Applicatie!----------")
    print("\033[91m1-\033[0m Kenteken opzoeken")
    print("\033[91m2-\033[0m Keuze uit garage")
    print("\033[91m0-\033[0m Exit")
    return input("\nKies een optie: ")

def auto_menu(kenteken):
    clear_screen()
    auto_info = read_json(kenteken)
    print("-----------------------Voertuig Menu-------------------------")
    print(f"Auto menu voor \033[92m{auto_info['auto_info']['handelsbenaming']}\033[0m")
    print(f"\033[91m1-\033[0m Toon Eigenschappen")
    print(f"\033[91m2-\033[0m Koopkracht en minimumloon analyse")
    print(f"\033[91m3-\033[0m Geschatte maandelijkse kosten")
    print(f"\033[91m4-\033[0m Garage beheer(Toevoegen/verwijderen)")
    print(f"\033[91m0-\033[0m Terug naar hoofdmenu")
    print("-----------------------Voertuig Menu-------------------------")
    return input("\nKies een optie: ")    

def show_info(kenteken):
    clear_screen()
    auto_info = read_json(kenteken)
    print("-----------------------Voertuig Informatie-------------------------")
    print(f"Merk: {auto_info['auto_info']['merk']}")
    print(f"Model: {auto_info['auto_info']['handelsbenaming']}")
    print(f"Bouwjaar: {auto_info['auto_info']['datum_eerste_toelating'][:4]}")
    print(f"Brandstoffen: {', '.join([fuel['brandstof_omschrijving'] for fuel in auto_info['auto_info']['brandstoffen']])}")
    print(f"Catalogusprijs: {auto_info['auto_info']['catalogusprijs']} Euro")
    print(f"Gewicht: {auto_info['auto_info']['massa_ledig_voertuig']} kg")
    print(f"Vermogen: {auto_info['auto_info']['totaal_continue_vermogen_pk']} pk")
    print(f"Eerste kleur: {auto_info['auto_info']['eerste_kleur']}")
    print(f"Wa verzekerd: {auto_info['auto_info']['wam_verzekerd']}")
    print(f"Openstaande terugroepactie: {auto_info['auto_info']['openstaande_terugroepactie_indicator']}")
    print(f"Taxi geweest: {auto_info['auto_info']['taxi_indicator']}")
    print(f"Tenaamstellen mogelijk: {auto_info['auto_info']['tenaamstellen_mogelijk']}")
    print(f"Vervaldatum APK: {auto_info['auto_info']['vervaldatum_apk_dt'][:10]}")
    print("-----------------------Voertuig Informatie-------------------------")

    input("Druk op Enter om door te gaan...")

def read_minimum_wage(year):
    with open("minimum_wage.json", "r") as file:
        data = json.load(file)
        data = data["value"][str(data["time"][f"{year}-S1"])]
        return data

def calculate_koopkracht(auto_info):
    minimum_wage = read_minimum_wage(auto_info['auto_info']['datum_eerste_toelating'][:4])
    return int(auto_info['auto_info']['catalogusprijs']) / minimum_wage

def purchasing_power_analysis(kenteken):
    clear_screen()
    print("-----------------------Koopkracht Analyse-------------------------")
    auto_info = read_json(kenteken)
    purchasing_power = calculate_koopkracht(auto_info)
    print(f"Oorspronkelijk waarde van de auto was {auto_info['auto_info']['catalogusprijs']} Euro \nToen was het {purchasing_power:.2f} keer minimumloon waard.")
    print("-----------------------Koopkracht Analyse-------------------------")
    input("\nDruk op Enter om door te gaan...")

def estimated_monthly_costs(kenteken):
    clear_screen()
    print("-----------------------Geschatte Maandelijkse Kosten-------------------------")
    auto_info = read_json(kenteken)
    fuel_info = auto_info['auto_info']['brandstoffen']
    total_monthly_costs = 0
    hybrid_electric = False
    plug_in_hybrid = False
    for fuel in fuel_info:
        try:
            if fuel['klasse_hybride_elektrisch_voertuig']=='NOVC-HEV':
                hybrid_electric = True
            if fuel['klasse_plug_in_hybrid_voertuig']=='OVC-HEV':
                plug_in_hybrid = True
        except KeyError:
            pass
        
        if fuel['brandstof_omschrijving'] == 'Benzine':
            total_monthly_costs += PRICE_PER_LITER_BEN * KM_PER_MONTH / 100 * float(fuel['brandstofverbruik_gecombineerd'])
        elif fuel['brandstof_omschrijving'] == 'Diesel':
            total_monthly_costs += PRICE_PER_LITER_DIE * KM_PER_MONTH / 100 * float(fuel['brandstofverbruik_gecombineerd'])
        elif fuel['brandstof_omschrijving'] == 'Elektriciteit' and not (hybrid_electric or plug_in_hybrid):
            if fuel['energy_consumption_flag'] == 'small':
                total_monthly_costs += PRICE_PER_KWH * KM_PER_MONTH / 100 * SMALL_ELECTRIC_VEHICLE_CONSUMPTION
            elif fuel['energy_consumption_flag'] == 'average':
                total_monthly_costs += PRICE_PER_KWH * KM_PER_MONTH / 100 * AVERAGE_ELECTRIC_VEHICLE_CONSUMPTION
            elif fuel['energy_consumption_flag'] == 'large':
                total_monthly_costs += PRICE_PER_KWH * KM_PER_MONTH / 100 * LARGE_ELECTRIC_VEHICLE_CONSUMPTION
        
    print(f"Totaal geschatte maandelijkse kosten: {total_monthly_costs:.2f} Euro")
    print("-----------------------Geschatte Maandelijkse Kosten-------------------------")
    input("\nDruk op Enter om door te gaan...")

def add_to_garage(kenteken):
    with open(os.path.join("my_garage.txt"), mode='a') as file:
        file.write(f"{kenteken}\n")
    print(f"{kenteken} is toegevoegd aan garage")
    input("Druk enter om door te gaan...")

def del_from_garage(kenteken):
    with open(os.path.join("my_garage.txt"), mode='w') as file:
        data = file.readlines()
        for line in enumerate(data, start=1):
            if line != kenteken:
                file.write(line)
    print(f"{kenteken} is verwijderd uit garage")
    input("Druk enter om door te gaan...")

def show_garage():
    with open(os.path.join("my_garage.txt"), mode='r') as file:
        data = file.readlines()
        print("------------Mijn Garage------------")
        for line in enumerate(data, start=1):
            print(f"{line[0]} - {line[1].strip()}")
    return None

def create_garage():
    if not os.path.exists(os.path.join("my_garage.txt")):
        with open(os.path.join("my_garage.txt"), mode='w') as file:
            file.write("")

def choose_from_garage():
    clear_screen()
    create_garage()
    show_garage()
    kenteken = None
    while True:
        choice = int(input("Enter de nummer van de auto: "))
        with open(os.path.join("my_garage.txt"), mode='r') as file:
            data = file.readlines()
            for n,line in enumerate(data, start=1):
                print(f"line = {line}, choice = {choice},  n= {n}")
                if n == choice:
                    print("binnen")
                    kenteken = line
                    break
            if kenteken is None:
                print("Aljeblieft kies een line nummer van de gegeven lijst!")
            else:
                break
    print(f"Gekozen kenteken is : {kenteken}")
    input("Druk enter om door te gaan...")
    return kenteken

def exist_in_garage(kenteken):
    create_garage()
    exist = False
    with open(os.path.join("my_garage.txt"), mode='r') as file:
        data = file.readlines()
        for line in enumerate(data, start=1):
            if line == kenteken:
                exist = True

    return exist
