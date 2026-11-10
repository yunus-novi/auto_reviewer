import os
import sys
from functies import *
import json

# In het begin doen we alles op json file. Dan als het op latere moment nodig is kunnen we vanuit json file lezen ipv niewe request te doen.

def main():
    while True:
        main_menu_choice = main_menu()
        match main_menu_choice:
            case "1":
                kenteken = input("Kenteken van de auto: ").upper()

                if not exist_auto(kenteken):
                    # Haal de auto informatie op van de RDW API
                    # try:
                        auto_info = get_auto_info(kenteken)
                        if auto_info == []:
                            input("Druk op Enter om door te gaan..1")
                            continue

                        fuel_info = get_fuel_info(kenteken)
                        if fuel_info == []:
                            input("Druk op Enter om door te gaan..2")
                            continue

                        for i in range(len(fuel_info)):
                            del fuel_info[i]["kenteken"]
                        # Voeg de auto informatie en brandstofinformatie toe aan een dictionary en sla deze op in een JSON-bestand
                        auto = {}
                        auto_info[0]["brandstoffen"] = fuel_info
                        auto["auto_info"] = auto_info[0]
                        auto = energy_consumption_flag_electric(auto)
                        auto = get_horsepower(auto)
                        add_to_json(auto)
                    # except Exception as e:
                    #     print(f"Fout bij het ophalen van informatie voor kenteken {kenteken}: {e}")
                    #     input("Druk op Enter om door te gaan..3")
                    #     continue

                while True:
                    auto_menu_choice = auto_menu(kenteken)
                    match auto_menu_choice:
                        case "1":
                            show_info(kenteken)
                        case "2":
                            purchasing_power_analysis(kenteken)
                        case "3":
                            estimated_monthly_costs(kenteken)
                        case "4":
                            if exist_in_garage(kenteken):
                                del_from_garage(kenteken)
                                break
                            else:
                                add_to_garage(kenteken)
                        case "0":
                            break
                        case _:
                            print("Ongeldige optie. Probeer opnieuw.")
                            input("Druk op Enter om door te gaan...")
                            continue
            case "2":
                if not os.path.exists("my_garage.txt"):
                    print("Geen auto's in de garage. Voeg eerst een auto toe.")
                    input("Druk op Enter om door te gaan...")
                    continue
                else:
                    kenteken = choose_from_garage()
                    while True:
                        auto_menu_choice = auto_menu(kenteken)
                        match auto_menu_choice:
                            case "1":
                                show_info(kenteken)
                            case "2":
                                purchasing_power_analysis(kenteken)
                            case "3":
                                estimated_monthly_costs(kenteken)
                            case "4":
                                del_from_garage(kenteken)
                            case "0":
                                break
                            case _:
                                print("Ongeldige optie. Probeer opnieuw.")
                                input("Druk op Enter om door te gaan...")
                                continue

            case "0":
                print("Bedankt voor het gebruiken van de applicatie!")
                exit()
            case _:
                print("Ongeldige optie. Probeer opnieuw.")
                input("Druk op Enter om door te gaan...")
main()

