from web3 import Web3
from datetime import datetime
import os

# Конфигурация
RPC_URLS = ["https://soneium.drpc.org"]
CONTRACT_ADDRESS = "0x64eA937352996dCa9B32D7A6a883FAa6C651Ccfc"  # Адрес NFT контракта
WALLET_FILE = "wallet.txt"  # Файл с адресами кошельков
PRIVATES_FILE = "privates.txt"  # Файл с приватными ключами
OUTPUT_FILE = "wallet_info.txt"  # Файл для вывода информации
MIN_ETH_BALANCE = 0.0000031  # Минимальный баланс ETH для вывода в пункте 5

# ABI для DropERC721 (balanceOf)
DROP_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

def load_file(filename):
    """Чтение данных из файла"""
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            raise Exception(f"Файл {filename} пуст")
        print(f"Загружено {len(lines)} записей из {filename}")
        return lines
    except FileNotFoundError:
        raise Exception(f"Файл {filename} не найден")

def get_web3_instance():
    """Создание подключения к RPC"""
    rpc_url = RPC_URLS[0]  # Используем первый RPC
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        raise Exception(f"Не удалось подключиться к {rpc_url}")
    return w3

def check_nft_balance(w3, wallet_address):
    """Проверка баланса NFT на кошельке"""
    drop_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=DROP_ABI)
    balance = drop_contract.functions.balanceOf(wallet_address).call()
    return balance

def get_wallet_info(wallet_address, private_key, wallet_number):
    """Получение информации о кошельке с проверкой соответствия и нумерацией"""
    w3 = get_web3_instance()
    try:
        # Проверка соответствия приватного ключа и адреса
        account = w3.eth.account.from_key(private_key)
        derived_address = account.address.lower()
        if derived_address != wallet_address.lower():
            raise Exception(f"Приватный ключ не соответствует адресу {wallet_address}. Ожидался адрес: {derived_address}")

        # Баланс в ETH (нативный токен Soneium)
        eth_balance_wei = w3.eth.get_balance(wallet_address)
        eth_balance = w3.from_wei(eth_balance_wei, 'ether')

        # Баланс NFT
        nft_balance = check_nft_balance(w3, wallet_address)

        # Формируем строку с информацией и номером кошелька
        info = (
            f"Кошелек #{wallet_number}:\n"
            f"Адрес: {wallet_address}\n"
            f"Приватный ключ: {private_key}\n"
            f"Баланс ETH: {eth_balance} ETH\n"
            f"Количество NFT: {nft_balance}\n"
            f"{'-'*50}\n"
        )
        print(info)
        return info, eth_balance, nft_balance

    except Exception as e:
        error_msg = f"Кошелек #{wallet_number}: Ошибка для адреса {wallet_address}: {str(e)}\n{'-'*50}\n"
        print(error_msg)
        return error_msg, 0, 0  # Возвращаем 0 для балансов в случае ошибки

def save_to_file(data, filename):
    """Сохранение данных в файл"""
    with open(filename, 'a') as f:
        f.write(data)

def get_total_eth_balance(wallet_addresses, private_keys):
    """Подсчет общего баланса ETH"""
    total_eth = 0
    w3 = get_web3_instance()
    
    for wallet_address, private_key in zip(wallet_addresses, private_keys):
        try:
            # Проверка соответствия приватного ключа и адреса
            account = w3.eth.account.from_key(private_key)
            derived_address = account.address.lower()
            if derived_address != wallet_address.lower():
                raise Exception(f"Приватный ключ не соответствует адресу {wallet_address}. Ожидался адрес: {derived_address}")

            eth_balance_wei = w3.eth.get_balance(wallet_address)
            eth_balance = w3.from_wei(eth_balance_wei, 'ether')
            total_eth += eth_balance
            print(f"Кошелек {wallet_address}: {eth_balance} ETH")
        except Exception as e:
            print(f"Ошибка для кошелька {wallet_address}: {str(e)}")
    
    return total_eth

def get_wallets_with_nft(wallet_addresses, private_keys):
    """Отображение кошельков с NFT и подсчет общей суммы NFT"""
    wallets_with_nft = []
    total_nft = 0
    w3 = get_web3_instance()
    
    for wallet_address, private_key in zip(wallet_addresses, private_keys):
        try:
            # Проверка соответствия приватного ключа и адреса
            account = w3.eth.account.from_key(private_key)
            derived_address = account.address.lower()
            if derived_address != wallet_address.lower():
                raise Exception(f"Приватный ключ не соответствует адресу {wallet_address}. Ожидался адрес: {derived_address}")

            # Проверка баланса NFT
            nft_balance = check_nft_balance(w3, wallet_address)
            total_nft += nft_balance
            if nft_balance > 0:
                eth_balance_wei = w3.eth.get_balance(wallet_address)
                eth_balance = w3.from_wei(eth_balance_wei, 'ether')
                info = (
                    f"Адрес: {wallet_address}\n"
                    f"Приватный ключ: {private_key}\n"
                    f"Баланс ETH: {eth_balance} ETH\n"
                    f"Количество NFT: {nft_balance}\n"
                    f"{'-'*50}\n"
                )
                wallets_with_nft.append(info)
                print(info)
        except Exception as e:
            print(f"Ошибка для кошелька {wallet_address}: {str(e)}")
    
    return wallets_with_nft, total_nft

def get_private_keys_with_nft(wallet_addresses, private_keys):
    """Получение только приватных ключей кошельков с NFT"""
    private_keys_with_nft = []
    w3 = get_web3_instance()
    
    for wallet_address, private_key in zip(wallet_addresses, private_keys):
        try:
            # Проверка соответствия приватного ключа и адреса
            account = w3.eth.account.from_key(private_key)
            derived_address = account.address.lower()
            if derived_address != wallet_address.lower():
                raise Exception(f"Приватный ключ не соответствует адресу {wallet_address}. Ожидался адрес: {derived_address}")

            # Проверка баланса NFT
            nft_balance = check_nft_balance(w3, wallet_address)
            if nft_balance > 0:
                private_keys_with_nft.append(private_key)
                print(private_key)
        except Exception as e:
            print(f"Ошибка для кошелька {wallet_address}: {str(e)}")
    
    return private_keys_with_nft

def get_private_keys_without_nft(wallet_addresses, private_keys):
    """Получение только приватных ключей кошельков без NFT с балансом > 0.0000031 ETH"""
    private_keys_without_nft = []
    w3 = get_web3_instance()
    
    for wallet_address, private_key in zip(wallet_addresses, private_keys):
        try:
            # Проверка соответствия приватного ключа и адреса
            account = w3.eth.account.from_key(private_key)
            derived_address = account.address.lower()
            if derived_address != wallet_address.lower():
                raise Exception(f"Приватный ключ не соответствует адресу {wallet_address}. Ожидался адрес: {derived_address}")

            # Проверка баланса NFT
            nft_balance = check_nft_balance(w3, wallet_address)
            # Проверка баланса ETH
            eth_balance_wei = w3.eth.get_balance(wallet_address)
            eth_balance = w3.from_wei(eth_balance_wei, 'ether')
            
            if nft_balance == 0 and eth_balance > MIN_ETH_BALANCE:
                private_keys_without_nft.append(private_key)
                print(private_key)
        except Exception as e:
            print(f"Ошибка для кошелька {wallet_address}: {str(e)}")
    
    return private_keys_without_nft

def main_menu():
    """Главное меню для выбора действия"""
    while True:
        print("\nВыберите действие:")
        print("1. Загрузить данные о кошельках (адрес, приватный ключ, баланс ETH, количество NFT)")
        print("2. Подсчитать общий баланс ETH со всех кошельков")
        print("3. Отобразить кошельки с NFT и общую сумму NFT")
        print("4. Вывести приватные ключи кошельков с NFT")
        print("5. Вывести приватные ключи кошельков без NFT (баланс > 0.0000031 ETH)")
        print("6. Выйти")
        
        choice = input("Введите номер действия (1-6): ").strip()
        
        if choice == "1":
            # Загрузка данных о кошельках с нумерацией
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
            
            wallet_addresses = load_file(WALLET_FILE)
            private_keys = load_file(PRIVATES_FILE)
            
            if len(wallet_addresses) != len(private_keys):
                print("Ошибка: Количество адресов в wallet.txt не соответствует количеству ключей в privates.txt")
                continue
            
            for i, (wallet_address, private_key) in enumerate(zip(wallet_addresses, private_keys), start=1):
                wallet_info, _, _ = get_wallet_info(wallet_address, private_key, i)
                save_to_file(wallet_info, OUTPUT_FILE)
            
            print(f"Информация о кошельках сохранена в {OUTPUT_FILE}")
        
        elif choice == "2":
            # Подсчет общего баланса ETH
            wallet_addresses = load_file(WALLET_FILE)
            private_keys = load_file(PRIVATES_FILE)
            
            if len(wallet_addresses) != len(private_keys):
                print("Ошибка: Количество адресов в wallet.txt не соответствует количеству ключей в privates.txt")
                continue
            
            total_eth = get_total_eth_balance(wallet_addresses, private_keys)
            print(f"\nОбщий баланс ETH со всех кошельков: {total_eth} ETH")
            save_to_file(f"Общий баланс ETH: {total_eth} ETH\n", OUTPUT_FILE)
        
        elif choice == "3":
            # Отображение кошельков с NFT и общей суммы NFT
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
            
            wallet_addresses = load_file(WALLET_FILE)
            private_keys = load_file(PRIVATES_FILE)
            
            if len(wallet_addresses) != len(private_keys):
                print("Ошибка: Количество адресов в wallet.txt не соответствует количеству ключей в privates.txt")
                continue
            
            wallets_with_nft, total_nft = get_wallets_with_nft(wallet_addresses, private_keys)
            if wallets_with_nft:
                for info in wallets_with_nft:
                    save_to_file(info, OUTPUT_FILE)
                total_nft_message = f"Общее количество NFT со всех кошельков: {total_nft}\n"
                print(total_nft_message)
                save_to_file(total_nft_message, OUTPUT_FILE)
                print(f"Информация о кошельках с NFT сохранена в {OUTPUT_FILE}")
            else:
                print("Кошельков с NFT не найдено.")
                total_nft_message = f"Общее количество NFT со всех кошельков: {total_nft}\n"
                print(total_nft_message)
                save_to_file("Кошельков с NFT не найдено.\n" + total_nft_message, OUTPUT_FILE)
        
        elif choice == "4":
            # Вывод только приватных ключей кошельков с NFT
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
            
            wallet_addresses = load_file(WALLET_FILE)
            private_keys = load_file(PRIVATES_FILE)
            
            if len(wallet_addresses) != len(private_keys):
                print("Ошибка: Количество адресов в wallet.txt не соответствует количеству ключей в privates.txt")
                continue
            
            private_keys_with_nft = get_private_keys_with_nft(wallet_addresses, private_keys)
            if private_keys_with_nft:
                save_to_file("\n".join(private_keys_with_nft) + "\n", OUTPUT_FILE)
                print(f"Приватные ключи кошельков с NFT сохранены в {OUTPUT_FILE}")
            else:
                print("Кошельков с NFT не найдено.")
                save_to_file("Кошельков с NFT не найдено.\n", OUTPUT_FILE)
        
        elif choice == "5":
            # Вывод только приватных ключей кошельков без NFT и с балансом > 0.0000031 ETH
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
            
            wallet_addresses = load_file(WALLET_FILE)
            private_keys = load_file(PRIVATES_FILE)
            
            if len(wallet_addresses) != len(private_keys):
                print("Ошибка: Количество адресов в wallet.txt не соответствует количеству ключей в privates.txt")
                continue
            
            private_keys_without_nft = get_private_keys_without_nft(wallet_addresses, private_keys)
            if private_keys_without_nft:
                save_to_file("\n".join(private_keys_without_nft) + "\n", OUTPUT_FILE)
                print(f"Приватные ключи кошельков без NFT (баланс > {MIN_ETH_BALANCE} ETH) сохранены в {OUTPUT_FILE}")
            else:
                print(f"Кошельков без NFT и с балансом > {MIN_ETH_BALANCE} ETH не найдено.")
                save_to_file(f"Кошельков без NFT и с балансом > {MIN_ETH_BALANCE} ETH не найдено.\n", OUTPUT_FILE)
        
        elif choice == "6":
            print("Выход из программы.")
            break
        
        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2, 3, 4, 5 или 6.")

if __name__ == "__main__":
    main_menu()
    