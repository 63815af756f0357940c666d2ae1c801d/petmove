import re


def get_uuid_by_username(server, playername):
    uuidmostrawstr = server.rcon_query('data get entity ' + playername + ' UUIDMost')
    uuidleastrawstr = server.rcon_query('data get entity ' + playername + ' UUIDLeast')
    if (re.fullmatch(playername + r' has the following entity data: [+-]?\d*L', uuidmostrawstr)) and (
            re.fullmatch(playername + r' has the following entity data: [+-]?\d*L', uuidleastrawstr)):
        uuidmoststr = uuidmostrawstr.split(' ')[6][:-1]
        uuidleaststr = uuidleastrawstr.split(' ')[6][:-1]
        uuidmostint = int(uuidmoststr)
        uuidleastint = int(uuidleaststr)
        uuidmostint += (1 << 64)
        uuidleastint += (1 << 64)
        uuidmostint &= (1 << 64) - 1
        uuidleastint &= (1 << 64) - 1
        rawuuid = hex(uuidmostint)[2:] + hex(uuidleastint)[2:]
        uuid = rawuuid[0:8] + '-' + rawuuid[8:12] + '-' + rawuuid[12:16] + '-' + rawuuid[16:20] + '-' + rawuuid[20:32]
        return uuid
    else:
        print('Error: Invalid result: ' + uuidmostrawstr + ' ' + uuidleastrawstr)
        return


def checkowner(server, playername, owneruuid):
    res = server.rcon_query(
        'execute as ' + playername + ' at ' + playername + ' run data get entity @e[type=!minecraft:player,sort=nearest,limit=1] OwnerUUID')
    if (re.match(r'.* has the following entity data: .*', res)):
        uidval = res.rsplit(':')[-1]
        uidval = uidval.strip()
        uidval = uidval.strip('"')
        if (uidval.lower() == owneruuid.lower()):
            return True
    print(res,'Failed')
    return False


def on_info(server, info):
    if info.is_player:
        if info.content.startswith("!!petmove "):
            args = info.content.split(" ")
            if (len(args) != 2):
                server.tell(info.player, '!!petmove <username>')
                return
            olduuid = get_uuid_by_username(server, playername=info.player)
            # checkowner
            if (checkowner(server, info.player, olduuid)):
                newuuid = get_uuid_by_username(server, playername=args[1])
                server.execute(
                    'execute as ' + info.player + ' at ' + info.player + ' run data modify entity @e[type=!minecraft:player,sort=nearest,limit=1] OwnerUUID set value "' + newuuid + '"')
                server.tell(info.player, 'Success')
                server.tell(args[1], info.player + ' give you a pet')
                server.execute(
                    'execute as ' + info.player + ' at ' + info.player + ' run effect give @e[type=!minecraft:player,sort=nearest,limit=1] glowing')
            else:
                server.tell(info.player,'Fail to recognize ownership.')
    else:
        if info.content.startswith("!!petmove "):
            print('This command must be executed as a player.')


def on_load(server, old):
    server.add_help_message('!!petmove <username>', 'give your nearest pet to someone else online')
