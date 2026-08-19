import json
from sortedcontainers import SortedDict
import poly_maker.poly_data.global_state as global_state
import poly_maker.poly_data.CONSTANTS as CONSTANTS

from trading import perform_trade
import time 
import asyncio
from poly_maker.poly_data.data_utils import set_position, set_order, update_positions

def process_book_data(asset, json_data):
    global_state.all_data[asset] = {
        'bids': SortedDict(),
        'asks': SortedDict()
    }

    global_state.all_data[asset]['bids'].update({float(entry['price']): float(entry['size']) for entry in json_data['bids']})
    global_state.all_data[asset]['asks'].update({float(entry['price']): float(entry['size']) for entry in json_data['asks']})

def process_price_change(asset, side, price_level, new_size):
    if side == 'bids':
        book = global_state.all_data[asset]['bids']
    else:
        book = global_state.all_data[asset]['asks']

    if new_size == 0:
        if price_level in book:
            del book[price_level]
    else:
        book[price_level] = new_size
"""""
def process_data(json_datas, trade=True):

    for json_data in json_datas:
        event_type = json_data['event_type']
        asset = json_data['market']

        if event_type == 'book':
            process_book_data(asset, json_data)

            if trade:
                asyncio.create_task(perform_trade(asset))
                
        elif event_type == 'price_change':
            for data in json_data['changes']:
                side = 'bids' if data['side'] == 'BUY' else 'asks'
                price_level = float(data['price'])
                new_size = float(data['size'])
                process_price_change(asset, side, price_level, new_size)

                if trade:
                    asyncio.create_task(perform_trade(asset))
        

        # pretty_print(f'Received book update for {asset}:', global_state.all_data[asset])
"""

def process_data(json_datas, trade=True):
    # Einzelobjekt in Liste wandeln
    if isinstance(json_datas, dict):
        json_datas = [json_datas]

    for json_data in json_datas:
        event_type = json_data.get('event_type')
        asset = str(json_data.get('market'))  # condition_id / market key
        if not asset:
            continue

        if event_type == 'book':
            process_book_data(asset, json_data)
            if trade:
                asyncio.create_task(perform_trade(asset))

        elif event_type == 'price_change':
            # Guard: Buch initialisieren falls nötig
            if asset not in global_state.all_data:
                global_state.all_data[asset] = {'bids': SortedDict(), 'asks': SortedDict()}

            # Neues Schema bevorzugen, altes als Fallback
            changes = json_data.get('price_changes')
            if changes is None:
                changes = json_data.get('changes', [])

            for data in changes:
                side = 'bids' if data.get('side') == 'BUY' else 'asks'
                price_level = float(data['price'])
                new_size = float(data['size'])
                process_price_change(asset, side, price_level, new_size)

                if trade:
                    asyncio.create_task(perform_trade(asset))


def add_to_performing(col, id):
    if col not in global_state.performing:
        global_state.performing[col] = set()
    
    if col not in global_state.performing_timestamps:
        global_state.performing_timestamps[col] = {}

    # Add the trade ID and track its timestamp
    global_state.performing[col].add(id)
    global_state.performing_timestamps[col][id] = time.time()

def remove_from_performing(col, id):
    if col in global_state.performing:
        global_state.performing[col].discard(id)

    if col in global_state.performing_timestamps:
        global_state.performing_timestamps[col].pop(id, None)
""""
def process_user_data(rows):

    for row in rows:
        market = row['market']

        side = row['side'].lower()
        token = row['asset_id']
            
        if token in global_state.REVERSE_TOKENS:     
            col = token + "_" + side

            if row['event_type'] == 'trade':
                size = 0
                price = 0
                maker_outcome = ""
                taker_outcome = row['outcome']

                is_user_maker = False
                for maker_order in row['maker_orders']:
                    if maker_order['maker_address'].lower() == global_state.client.browser_wallet.lower():
                        print("User is maker")
                        size = float(maker_order['matched_amount'])
                        price = float(maker_order['price'])
                        
                        is_user_maker = True
                        maker_outcome = maker_order['outcome'] #this is curious

                        if maker_outcome == taker_outcome:
                            side = 'buy' if side == 'sell' else 'sell' #need to reverse as we reverse token too
                        else:
                            token = global_state.REVERSE_TOKENS[token]
                
                if not is_user_maker:
                    size = float(row['size'])
                    price = float(row['price'])
                    print("User is taker")

                print("TRADE EVENT FOR: ", row['market'], "ID: ", row['id'], "STATUS: ", row['status'], " SIDE: ", row['side'], "  MAKER OUTCOME: ", maker_outcome, " TAKER OUTCOME: ", taker_outcome, " PROCESSED SIDE: ", side, " SIZE: ", size) 


                if row['status'] == 'CONFIRMED' or row['status'] == 'FAILED' :
                    if row['status'] == 'FAILED':
                        print(f"Trade failed for {token}, decreasing")
                        asyncio.create_task(asyncio.sleep(2))
                        update_positions()
                    else:
                        remove_from_performing(col, row['id'])
                        print("Confirmed. Performing is ", len(global_state.performing[col]))
                        print("Last trade update is ", global_state.last_trade_update)
                        print("Performing is ", global_state.performing)
                        print("Performing timestamps is ", global_state.performing_timestamps)
                        
                        asyncio.create_task(perform_trade(market))

                elif row['status'] == 'MATCHED':
                    add_to_performing(col, row['id'])

                    print("Matched. Performing is ", len(global_state.performing[col]))
                    set_position(token, side, size, price)
                    print("Position after matching is ", global_state.positions[str(token)])
                    print("Last trade update is ", global_state.last_trade_update)
                    print("Performing is ", global_state.performing)
                    print("Performing timestamps is ", global_state.performing_timestamps)
                    asyncio.create_task(perform_trade(market))
                elif row['status'] == 'MINED':
                    remove_from_performing(col, row['id'])

            elif row['event_type'] == 'order':
                print("ORDER EVENT FOR: ", row['market'], " STATUS: ",  row['status'], " TYPE: ", row['type'], " SIDE: ", side, "  ORIGINAL SIZE: ", row['original_size'], " SIZE MATCHED: ", row['size_matched'])
                
                set_order(token, side, float(row['original_size']) - float(row['size_matched']), row['price'])
                asyncio.create_task(perform_trade(market))

    else:
        print(f"User date received for {market} but its not in")
"""

def process_user_data(rows):
    # Einzelobjekt in Liste wandeln
    if isinstance(rows, dict):
        rows = [rows]

    # Unser Identifikator
    my_api_key = str(getattr(global_state.client, "creds", None).api_key) if getattr(global_state.client, "creds", None) else ""
    my_wallet  = str(getattr(global_state.client, "owner_address", "")).lower()  # nur falls du es irgendwo loggen willst

    for row in rows:
        market = row.get('market')
        side = row.get('side', '').lower()
        token = row.get('asset_id')

        if token not in global_state.REVERSE_TOKENS:
            # Token ist uns (noch) egal / nicht konfiguriert
            continue

        col = f"{token}_{side}"

        if row.get('event_type') == 'trade':
            size = 0.0
            price = 0.0
            maker_outcome = ""
            taker_outcome = row.get('outcome', '')

            is_user_maker = False
            for maker_order in row.get('maker_orders', []):
                # Bevorzugt über API-Key identifizieren
                if str(maker_order.get('owner', '')) == my_api_key:
                    is_user_maker = True
                    size = float(maker_order.get('matched_amount', 0))
                    price = float(maker_order.get('price', 0))
                    maker_outcome = maker_order.get('outcome', '')

                    # Outcome-Logik wie gehabt
                    if maker_outcome == taker_outcome:
                        side = 'buy' if side == 'sell' else 'sell'
                    else:
                        token = global_state.REVERSE_TOKENS[token]

            if not is_user_maker:
                size = float(row.get('size', 0))
                price = float(row.get('price', 0))
                # print("User is taker")  # optional

            print("TRADE EVENT FOR:", row.get('market'),
                  "ID:", row.get('id'),
                  "STATUS:", row.get('status'),
                  "SIDE:", row.get('side'),
                  "MAKER OUTCOME:", maker_outcome,
                  "TAKER OUTCOME:", taker_outcome,
                  "PROCESSED SIDE:", side,
                  "SIZE:", size)

            status = row.get('status')
            if status in ('CONFIRMED', 'FAILED'):
                if status == 'FAILED':
                    print(f"Trade failed for {token}, forcing positions refresh")
                    asyncio.create_task(asyncio.sleep(2))
                    update_positions()
                else:
                    remove_from_performing(col, row.get('id'))
                    asyncio.create_task(perform_trade(market))

            elif status == 'MATCHED':
                add_to_performing(col, row.get('id'))
                set_position(token, side, size, price)
                asyncio.create_task(perform_trade(market))

            elif status == 'MINED':
                remove_from_performing(col, row.get('id'))

        elif row.get('event_type') == 'order':
            print("ORDER EVENT FOR:", row.get('market'),
                  "STATUS:", row.get('status'),
                  "TYPE:", row.get('type'),
                  "SIDE:", side,
                  "ORIGINAL SIZE:", row.get('original_size'),
                  "SIZE MATCHED:", row.get('size_matched'))

            open_size = float(row.get('original_size', 0)) - float(row.get('size_matched', 0))
            set_order(token, side, open_size, row.get('price', 0))
            asyncio.create_task(perform_trade(market))
