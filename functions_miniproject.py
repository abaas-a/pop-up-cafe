import csv
import pandas
import sys
import pymysql
import os
from dotenv import load_dotenv


def import_cache(table_name,file_name):
    load_dotenv()
    host = 'localhost'
    user = 'root' 
    password = 'password'
    database = 'abaas_mini_project' 

    connection = pymysql.connect(host,user,password,database)

    cursor = connection.cursor()

    headers_from_sql = cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'{}' ORDER BY ORDINAL_POSITION".format(table_name))
    headers_from_sql = cursor.fetchall()
    field_names=[]
    for header in headers_from_sql:
        field_names.append(header[0])

    with open('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\{}.csv'.format(file_name),'w') as file:
        csv_writer = csv.DictWriter(file,fieldnames=field_names)
        csv_writer.writeheader()
    
    data = cursor.execute('SELECT * FROM {}'.format(table_name))
    data = cursor.fetchall()

    panda_csv_file = read_a_csv(file_name)

    for data_tuple in data:
        data_list = list(data_tuple)
        panda_csv_file.loc[len(panda_csv_file.index)] = data_list
        panda_csv_file.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\{}.csv'.format(file_name), index = False)
    
    connection.commit() 
    cursor.close()
    connection.close()

def export_cache(table_name,file_name):
    load_dotenv()
    host = 'localhost'
    user = 'root' 
    password = 'password'
    database = 'abaas_mini_project' 
    connection = pymysql.connect(host,user,password,database)

    cursor = connection.cursor()

    headers_from_sql = cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'{}' ORDER BY ORDINAL_POSITION".format(table_name))
    headers_from_sql = cursor.fetchall()
    column_names=[]
    for header in headers_from_sql:
        column_names.append(header[0])

    cache_table = read_a_csv(file_name)
    id_list = list(cache_table[cache_table.columns[0]].to_string(index = False))
    csv_id_list= []
    for i in id_list:
        if i != '\n':
            csv_id_list.append(int(i))
    
    cache_table.set_index(column_names[0])
    
    cursor.execute(
        "SELECT {} FROM {}".format(column_names[0],table_name))
    raw_data = list(cursor.fetchall())
    sql_id_list = []
    for a in raw_data:
        sql_id_list.append(a[0])

    ########## UPDATING EXISTING ROWS IN THE SQL SERVER ######################
    for row_id in csv_id_list:
        row_data = list(cache_table.loc[row_id])

        row_dict = {}
        for i in range(len(column_names)):
            row_dict[column_names[i]] = row_data[i]

            for key, value in row_dict.items():
                cursor.execute("UPDATE {} SET {} = '{}' WHERE {} = {}".format(table_name,key,value,column_names[0],row_dict[column_names[0]]))


    ########## INSERTING NEW ENTRIES INTO THE SQL SERVER #####################    
    for element in csv_id_list:
        match_id = element in sql_id_list
        if match_id == False:
            if table_name == 'products':
                cursor.execute("INSERT INTO {} (Product, Price) VALUES ('{}',{})".format(table_name,cache_table.loc[element,column_names[1]],cache_table.loc[element,column_names[2]]))

            if table_name == 'couriers':
                cursor.execute("INSERT INTO {} (Courier_Name, Courier_Phone) VALUES ('{}',{})".format(table_name,cache_table.loc[element,column_names[1]],cache_table.loc[element,column_names[2]]))

            if table_name == 'orders':
                cursor.execute(
                    "INSERT INTO {} (Customer_Name, Address, Phone, courier_id, Order_Status,Items) VALUES ('{}','{}',{},{},'{}','{}')".format(
                    table_name,cache_table.loc[element,column_names[1]],
                    cache_table.loc[element,column_names[2]],
                    cache_table.loc[element,column_names[3]],
                    cache_table.loc[element,column_names[4]],
                    cache_table.loc[element,column_names[5]],
                    cache_table.loc[element,column_names[6]]))

    ############## DELETING ENTRIES FROM THE SQL SERVER ######################
    for element in sql_id_list:
        match_id = element in csv_id_list
        if match_id == False:
            cursor.execute("DELETE FROM {} WHERE {} = {}".format(table_name,column_names[0],element))


    connection.commit() 
    cursor.close()
    connection.close()

def read_a_csv(csv_file_name):
    panda_csv_file = pandas.read_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\{}.csv'.format(csv_file_name))
    panda_csv_file.index += 1
    # left_aligned = panda_csv_file.style.set_properties(**{'text-align': 'left'})
    return (panda_csv_file)

def display_table(table_type,file_name,index):
    print('\n ---{}---\n'.format(table_type).upper())
    panda_csv_display = read_a_csv(file_name)
    panda_csv_display = panda_csv_display.set_index(index)
    print(panda_csv_display)
    return panda_csv_display

def delete_a_row_csv(category,file_name,make_index):
    category_table_csv = display_table(category, file_name,make_index)
    while True:
        try:
            row_id_to_delete = int(input('\nEnter the \'{}\' of the product you wish to delete (or enter \'0\' to cancel): '.format(make_index)))
            if row_id_to_delete == 0:
                break
            else:
                category_table_csv.loc[row_id_to_delete]
                category_table_csv.drop(index = row_id_to_delete, inplace = True)
                category_table_csv.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\{}.csv'.format(file_name), index = True)
                print('\n...Successfully deleted entry.')
                break
        except:
            print('\n !Invalid Entry!\n')
            continue

def sort_orders_by(coloumn_title):
    panda_csv_file = read_a_csv('Orders')
    sorted_table = panda_csv_file.sort_values(coloumn_title)
    print (sorted_table)

#####################
# PRODUCTS
#####################

def create_product(file_name,id_column_name,new_item,new_price):
    panda_csv_append = read_a_csv(file_name)
    new_id = (int(panda_csv_append.loc[len(panda_csv_append.index),id_column_name])+ 1 )

    with open('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\{}.csv'.format(file_name), 'a', newline='') as csv_file:
        csv_add = csv.writer(csv_file)
        csv_add.writerow([new_id,new_item,new_price])
    
    print('\n...Successfully added the product to the list.')

def update_product():
    panda_products_csv = read_a_csv('Products_cache')
    panda_products_csv = panda_products_csv.set_index('product_id')
    print('\n ---Update a Product---\n')
    print(panda_products_csv)

    while True:
        try:
            product_id_to_update = int(input('\nEnter product_id of the product you wish to update (or enter 0 to cancel): '))
            if product_id_to_update == 0:
                products_menu()
                break
            else:
                print('\nYou have selected the following product:\n')
                print(panda_products_csv.loc[product_id_to_update].to_string())
                updated_product_name = input('\nType in the updated product name (or press enter to skip): ').title()
            break        
        except:
            print('\n !Invalid Entry!\n')
            continue
    
    
    if updated_product_name != '':
        panda_products_csv.loc[product_id_to_update,'Product'] = updated_product_name
        panda_products_csv.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Products_cache.csv', index = True)

    try:
        updated_product_price = float(input('\nType in the updated product price (or press enter to skip): '))
    except ValueError:
        updated_product_price = ''
    
    if updated_product_price != '':
        panda_products_csv.loc[product_id_to_update,'Price'] = updated_product_price
        panda_products_csv.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Products_cache.csv', index = True)
        print('\n...The products list has been updated with '+ 
             panda_products_csv.loc[product_id_to_update,'Product'] +
             ' at a price of £' + str(panda_products_csv.loc[product_id_to_update,'Price']) + '.')

#####################
# COURIERS
#####################

def create_courier(id_column_name,name,phone):
    panda_csv_append = read_a_csv('Couriers_cache')
    new_id = (int(panda_csv_append.loc[len(panda_csv_append.index),id_column_name])+ 1 )

    with open('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Couriers_cache.csv', 'a', newline='') as csv_file:
        csv_add = csv.writer(csv_file)
        csv_add.writerow([new_id,name,phone])
    
    print('\n Successfuly added a new courier to the list')

def select_courier():
    panda_csv_file = read_a_csv('Couriers_cache')
    panda_csv_file = panda_csv_file.set_index('courier_id')
    while True:
        try:
            print('\n---Select From Couriers---\n')
            print(panda_csv_file)
            select_courier = int(input('\nEnter the courier_id of courier you wish to assign: '))
            break
        except:
            print('\n !Invalid Entry!\n')
            continue
    return select_courier

def update_courier():
    panda_couriers_csv = display_table('Couriers', 'Couriers_cache','courier_id')

    while True:
        try:
            select_courier_to_update = int(input('\nSelect from one of the option above: '))
            if select_courier_to_update == 0:
                couriers_menu()
                break
            else:
                panda_couriers_csv.loc[select_courier_to_update]
                updated_courier_name = input('\nType in the updated courier name (or press enter to skip): ')
                if updated_courier_name != '' or updated_courier_name != 0:
                    panda_couriers_csv.loc[select_courier_to_update,'Courier_Name'] = updated_courier_name
                    panda_couriers_csv.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Couriers_cache.csv', index = True)
                
                updated_courier_phone = input('\nType in the updated courier phone (or press enter to skip): ')
                if updated_courier_phone != '' or updated_courier_phone != 0:
                    panda_couriers_csv.loc[select_courier_to_update,'Courier_Phone'] = updated_courier_phone
                    panda_couriers_csv.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Couriers_cache.csv', index = True)
                
                print('\n...The products list has been updated with '+ 
                    str(panda_couriers_csv.loc[select_courier_to_update,'Courier_Name']) +
                    ' with the contact number ' + str(panda_couriers_csv.loc[select_courier_to_update,'Courier_Phone']) + '.'
                    )
            break
        except:
            print('\n !Invalid Entry!\n')
            continue

#####################
# ORDERS
#####################

def items_add_to_order():
    panda_products_csv = read_a_csv('Products_cache')
    panda_products_csv = panda_products_csv.set_index('product_id')
    items_selected = []
    while True:
        try:
            print('\n---Select From Menu---\n')
            print(panda_products_csv)
            choose_foods = int(input('\nEnter products\' corresponding number  (or \'0\' to end product selection):  '))
            choose_foods <= len(panda_products_csv.index)
        except:
            print('\n !!!! Invalid Entry! Choose from the options above:  \n')
            continue
        
        if choose_foods > 0 and choose_foods <= len(panda_products_csv.index):
            items_selected.append(choose_foods)
            print(items_selected)
            continue
        elif choose_foods == 0:
            break
        else:
            print('\n !Invalid Entry!\n')
            continue
    return items_selected

def create_order():
    new_order_items = items_add_to_order()
    new_order_name = input('\nNew customer name: ').title()
    new_order_address = input('\nNew Customer Address: ').title()
    new_order_phone = input('\nNew cusotmer contact number: ')
    new_order_status = 1
    order_list = []
    panda_csv_append = read_a_csv('orders_cache')
    new_id = (int(panda_csv_append.loc[len(panda_csv_append.index),'order_id'])+ 1 )

    order_list.extend([new_id,new_order_name, new_order_address, new_order_phone, select_courier(), new_order_status,new_order_items])

    with open('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Orders_cache.csv', 'a', newline='') as csv_file:
        csv_add = csv.writer(csv_file)
        csv_add.writerow(order_list)
    print('\n ...Successfully created a new order.')

def select_order_status():
    list_status = ['Preparing', 'Out for Delivery', 'Delivered', 'Cancelled']
    print('\n')
    for i, status in enumerate(list_status):
        print (str(i+1) + ' ' + status)
    select_status = int(input('\nSelect from one of the statuses above: '))

    while select_status <1 or select_status > len(list_status):
            select_status = int(input('\n INVALID NUMBER! Select from one of the avaialbe options: '))
    else: 
        chosen_delivery_status = list_status[select_status - 1]
        print('\n...successfully updated the order\'s status\n')
    return chosen_delivery_status

def update_order_status():
    panda_orders_csv = pandas.read_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Orders_cache.csv')
    panda_orders_csv.index += 1
    print(panda_orders_csv)
    select_order_to_update = int(input('\nWhich order\'s status would you like to update?\n Or select 0 to Cancel: '))
    if select_order_to_update == 0:
        # orders_menu()
        pass
    else:
        list_status = ['Preparing', 'Out for Delivery', 'Delivered', 'Cancelled']
        print('\n')
        for i, status in enumerate(list_status):
            print (str(i+1) + ' ' + status)
        select_status = int(input('\nSelect from one of the statuses above: '))

        while select_status <1 or select_status > len(list_status):
            print('\n INVALID NUMBER! Select from one of the options above')
        else: 
            panda_orders_csv.loc[select_order_to_update,'Order_Status'] = list_status[select_status - 1]

        panda_orders_csv.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Orders_cache.csv', index = False)

def save_updated_order_csv(row_index,coloumn,new_value):
    if new_value != '':
        panda_orders_csv = read_a_csv('Orders_cache')
        panda_orders_csv.loc[row_index,coloumn] = new_value
        panda_orders_csv.to_csv('C:\\Users\\abaas\\Documents\\vsCode\\Generation\\Orders_cache.csv', index = False)

def update_entire_order():
    
    panda_orders_csv = read_a_csv('Orders_cache')
    panda_orders_csv = panda_orders_csv.set_index('order_id')
    print('\n ---Update an Order---\n')
    print(panda_orders_csv)
    
    while True:
        try:
            select_order_to_update = int(input('\nEnter order_id of the order you wish to update (or enter 0 to cancel): '))
            if select_order_to_update == 0:
                # orders_menu()
                break
            else:
                print('\nYou have selected the following order:\n')
                print(panda_orders_csv.loc[select_order_to_update].to_string())

                updated_name_order = input('\nEnter a new customer name (or leave blank to skip): ')
                updated_address_order = input('\nEnter a new customer address (or leave blank to skip): ')
                updated_phone_order = input('\nEnter a new customer phone number (or leave blank to skip): ')
                    
                ask_assign_courier = int(input('\nWould you like to assign a courier? 1 = yes. 2 = No : '))
                while ask_assign_courier != 1 and ask_assign_courier != 2:
                    print('\n !Invalid Entry!\n')
                    ask_assign_courier = int(input('\nWould you like to assign a courier? 1 = yes. 2 = No : '))

                else:
                    if ask_assign_courier == 1:
                        updated_courier_order = select_courier()
                    else:
                        updated_courier_order = ''
                    
                ask_assign_order_status = int(input('\nWould you like to update the Order Status? 1 = yes. 2 = No : '))
                while ask_assign_order_status != 1 and ask_assign_order_status != 2:
                    print('\n !Invalid Entry!\n')
                    ask_assign_order_status = int(input('\nWould you like to update the Order Status? 1 = yes, 2 = No : '))
                else:
                    if ask_assign_order_status == 1:
                        updated_order_status = select_order_status()
                    else:
                        updated_order_status = ''
                    
                ask_change_items = int(input('\nWould you like to update the items? 1 = yes, 2 = No : '))
                while ask_change_items != 1 and ask_change_items != 2:
                    print('\n !Invalid Entry!\n')
                    ask_change_items = int(input('\nINVALID ENTRY! Would you like to update the items? 1 = yes, 2 = No : '))
                else:
                    if ask_change_items == 1:
                        updated_items_order = str(items_add_to_order())
                    else:
                        updated_items_order = ''
                        
                save_updated_order_csv(select_order_to_update,'Customer_Name',updated_name_order)
                save_updated_order_csv(select_order_to_update,'Address',updated_address_order)
                save_updated_order_csv(select_order_to_update,'Phone',updated_phone_order)
                save_updated_order_csv(select_order_to_update,'courier_id',updated_courier_order)
                save_updated_order_csv(select_order_to_update,'Order_Status',updated_order_status)
                save_updated_order_csv(select_order_to_update,'Items',updated_items_order)
                print('\n...successfully updated the order\n ')
            break
        except:
            print('\n !Invalid Entry!\n')
            continue
     
#####################
# INDIVIDUAL MENUS
#####################

def products_menu():
    print('\n---PRODUCT MENU---\n0 Return to Main Menu\n1 Print Products\n2 Create new product\n3 Update product\n4 Delete Product')
    while True:
        try:
            product_menu_input = int(input('\nEnter the corresponding number from one of the options above: '))
            if product_menu_input >= 0 and product_menu_input <= 4:
                break
            else:
                print('\n !Invalid Entry!\n')
        except:
            print('\n !Invalid Entry!\n')
            continue

    if product_menu_input == 1: #print products
        display_table('products', 'Products_cache', 'product_id')
        input('\nPress Enter to go back to the Product Menu.')
        products_menu()
    elif product_menu_input == 2: #create new product
        create_product_name = input('\nEnter name of the new product: ').title()
        create_product_price = float(input('\nEnter price of the new product: '))
        create_product('Products_cache','product_id',create_product_name,create_product_price)
        input('\nPress Enter to go back to the Product Menu.')
        products_menu()
    elif product_menu_input == 3: #update prodcut
        update_product()
        input('\nPress Enter to go back to the Product Menu.')
        products_menu()
    elif product_menu_input == 4: #delete product
        delete_a_row_csv('products','Products_cache','product_id')
        input('\nPress Enter to go back to the Product Menu.')
        products_menu()
    elif product_menu_input == 0:
        pass

def couriers_menu():
    print('\n---COURIER MENU---\n0 Return to Main Menu\n1 Print Couriers\n2 Create new Courier\n3 Update Courier\n4 Delete Courier')
    while True:
        try:
            Courier_menu_input = int(input('\nEnter the corresponding number from one of the options above: '))
            if Courier_menu_input >= 0 and Courier_menu_input <= 4:
                break
            else:
                print('\n !Invalid Entry!\n')
        except:
            print('\n !Invalid Entry!\n')
            continue

    if Courier_menu_input == 1: #print Couriers
        display_table('couriers', 'Couriers_cache', 'courier_id')
        input('\nPress Enter to go back to the Courier Menu.')
        couriers_menu()
    elif Courier_menu_input == 2: #create new Courier
        new_corier_name = input('\nEnter name of the new courier: ').title()
        new_courer_phone = input('\nEnter contact number of the new courier: ')
        create_courier('courier_id',new_corier_name,new_courer_phone)
        input('\nPress Enter to go back to the Courier Menu.')
        couriers_menu()
    elif Courier_menu_input == 3: #update Courier
        update_courier()
        input('\nPress Enter to go back to the Courier Menu.')
        couriers_menu()
    elif Courier_menu_input == 4: #delete courier
        delete_a_row_csv('couriers','Couriers_cache','courier_id')
        couriers_menu()
    elif Courier_menu_input == 0:
        pass

def orders_menu():
    print('\n---ORDERS MENU---\n0 Return to Main Menu\n1 Print Orders\n2 Create new Order\n3 Update an Order Status\n4 Update an Entire Order\n5 Delete an Order')
    while True:
        try:
            order_menu_input = int(input('\nEnter the corresponding number from one of the options above: '))
            if order_menu_input >= 0 and order_menu_input <= 5:
                break
            else:
                print('\n !Invalid Entry!\n')
        except:
            print('\n !Invalid Entry!\n')
            continue
    
    if order_menu_input == 1: #print orders
        display_table('orders', 'Orders_cache', 'order_id')
        input('\nPress Enter to go back to the Order Menu.')
        orders_menu()
    elif order_menu_input == 2: #create order
        create_order()
        input('\nPress Enter to go back to the Order Menu.')
        orders_menu()
    elif order_menu_input == 3: #Update an order's Status
        update_order_status()
        input('\nPress Enter to go back to the Order Menu.')
        orders_menu()
    elif order_menu_input == 4: #Update an entire order
        update_entire_order()
        input('\nPress Enter to go back to the Order Menu.')
        orders_menu()
    elif order_menu_input == 5: #Delete an order
        delete_a_row_csv('orders','Orders_cache','order_id')
        input('\nPress Enter to go back to the Order Menu.')
        orders_menu()
    else:
        pass

# if __name__== '__main__':
#     update_entire_order()
#     export_cache('orders','Orders_cache')

