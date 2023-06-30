# RDP

Remote Desktop Protocol

> **Note**<br>
 If your internet speed is slow or [Telegram](https://telegram.org) is filtered in your country, you may face issues.

### Tested on:
+ Kali Linux
+ Parrot OS
+ Ubuntu
+ Windows 10
+ Windows 7
+ add more..

## Installation

First, need to uninstall other versions and then install the latest version.
```bash
pip uninstall rdp
pip install git+https://github.com/hctilg/rdp
```

## Run

Run it like this:
```bash
python3 -m rdp
```

## Authentication

if you have run RDP correctly, 
it will prompt you to enter a Telegram Bot token which you can get from _[@BotFather](https://t.me/BotFather)_.
Once you have a valid token, it will generate a key that you need to send to the bot.
if you enter the correct **key**, your Telegram account will be registered as an admin of the bot.
```
⁪⁬⁪⁬
┌─[#root]─[~/Desktop]
└──╼ $ python3 -m rdp

  [+] Token: 5832941996:AAH1MLCagmSJndYFSsB-e12tfBd6QOMbrEg
  [*] Key: p3cLwR5N7gac6nx6

  [#] Activated

```

<br>
