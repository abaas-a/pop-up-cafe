import csv
import sys
import functions_miniproject as functions
    

def main_menu():
    print('\n 0 Exit\n 1 Product Menu\n 2 Courier Menu\n 3 Orders Menu')
    choice_m = int(input("\nEnter the number of the menu you'd like to access, or '0' to exit: "))
    while choice_m < 0 or choice_m > 3:
        print('!!!!Invalid Number')
        choice_m = int(input("Choose from the options above or input '0' to exit: "))
    else:
        if choice_m == 1: #PRODUCTS
            functions.products_menu()
            main_menu()
        elif choice_m == 2: #COURIERS
            functions.couriers_menu()
            main_menu()
        elif choice_m == 3: #ORDERS
            functions.orders_menu()
            main_menu()
        else: 
            functions.export_cache('products','Products_cache')
            functions.export_cache('couriers','Couriers_cache')    
            functions.export_cache('orders','Orders_cache')        
            sys.exit('\n Exited')

functions.import_cache('products','Products_cache')
functions.import_cache('couriers','Couriers_cache')
functions.import_cache('orders','Orders_cache')

main_menu()
