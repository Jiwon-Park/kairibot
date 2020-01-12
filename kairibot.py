import discord
import keep_alive
from database import discord_token
def read_kma_db(path):
    '''
    read kma db and return splited result.
    return: name list, description list
    '''
    res: str
    with open(path, "r", encoding='UTF8') as file:
        res = file.read()

    res = res.split('ㅡ')
    _names = res[0:][::2]
    _names = list(map(str.strip, _names))
    _arthur_types = [x[0:2] if x[0] != '스' else x[0:3] for x in _names]
    _arthur_types = list(map(str.strip, _arthur_types))
    _names = [x[3:] if x[0] != '스' else x[4:] for x in _names]
    _descriptions = res[1:][::2]
    _descriptions = list(map(str.strip, _descriptions))
    return _names, _arthur_types, _descriptions

def write_kma_db(path, text):
    '''
    write kma db
    '''
    with open(path, "w", encoding='UTF8') as file:
        try:
            file.write(text)
        except IOError as e:
            print(e.strerror)
        except:
            print('unexpected error')
            


names, arthur_types, descriptions = read_kma_db('./database/KMA_DB.txt')
find_arr = []
working_user = None
working_name = ''
working_param = ''
working_index = -1

client = discord.Client()

@client.event
async def on_ready():
    print('logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.bot:
        return
    
    global find_arr
    global working_user
    global working_name
    global working_param
    global working_index

    if message.content.startswith('>'):
        print(message.content)
        text = message.content[1:]
        if text.startswith('help'):
            await message.channel.send('''```
>검색 검색어1, 검색어2, ... [용병|부호|도적|가희|스피어|전승|연금]
>(숫자)
>추가 [용병|부호|도적|가희|스피어|전승|연금] 카드이름
>편집 [카드 타입]카드이름
>설명 카드설명
```''')
            return
        elif text.startswith('검색'):
            sendres = ''
            text = text[2:].strip()
            find_num = 0
            find_arr = []
            
            arthur_param = False
            if '[' in text and ']' in text:
                arthur_param = text[text.find('[')+1 : text.find(']')]
                text = text.replace('[' + arthur_param + ']', '')
            if not text.strip():
                params = []
            else:
                params = text.split(',')
                params = list(map(str.strip, params))
            for index, (description, arthur_type) in enumerate(zip(descriptions, arthur_types)):
                flag = False
                if not params:
                    flag = True
                if not params and not arthur_param:
                    flag = False
                if all(x in description for x in params):
                    flag = True
                if flag and arthur_param:
                    if arthur_type != arthur_param:
                        flag = False
                if flag:
                    find_num = find_num + 1
                    find_arr.append(index)


            if find_num == 1:
                sendres = descriptions[find_arr[0]].strip()
            else:
                msg = ''
                for idx in find_arr:
                    msg = msg + '[' + arthur_types[idx] + ']' + names[idx] + '\n'
                sendres = msg.strip()
            if not sendres:
                await message.channel.send('결과가 없습니다.')
            else:
                await message.channel.send(sendres)
        elif text.isdigit() and int(text.strip()) > 0:
            await message.channel.send(descriptions[find_arr[int(text.strip())-1]])
        elif text.startswith('추가'):
            if working_user:
                await message.channel.send(working_user.name +' 님이 카드를 추가 중입니다. 기다려 주세요.')
                return
            working_user = message.author
            text = text[2:].strip()
            arthur_param = text[text.find('[')+1 : text.find(']')]
            text = text.replace('[' + arthur_param + ']', '')
            text = text.strip()
            working_name = text
            working_param = arthur_param
            await message.channel.send('>설명 뒤에 설명을 붙여서 설명을 추가해 주세요')
        elif text.startswith('편집'):
            if working_user:
                await message.channel.send(working_user.name +' 님이 카드를 추가 중입니다. 기다려 주세요.')
                return
            working_user = message.author
            text = text[2:].strip()
            arthur_param = text[text.find('[')+1 : text.find(']')]
            text = text.replace('[' + arthur_param + ']', '')
            text = text.strip()
            working_index = 0
            working_param = arthur_param
            for index, (name, arthur_type) in enumerate(zip(names, arthur_types)):
                if name == text and arthur_type == arthur_param:
                    working_index = index
                    break
            if working_index == 0:
              await message.channel.send('카드 직업군과 이름을 정확히 입력해 주세요.\n>검색 키워드를 사용해서 나온 결과대로 입력해 주세요.')
              return
            await message.channel.send('[' + arthur_types[working_index] + ']' + names[working_index] +
                                       '를 편집합니다.\n>설명 뒤에 설명을 붙여서 설명을 갱신해 주세요')
        elif text.startswith('설명'):
            if not working_user:
                await message.channel.send('추가 혹은 편집 명령어를 먼저 입력해 주세요')
                return
            if working_user != message.author:
                await message.channel.send(working_user.name +' 님이 설명을 입력해야 합니다. 기다려 주세요.')
                return
            text = text[2:].strip()
            working_description = text
            if working_index == -1:
                names.append(working_name)
                arthur_types.append(working_param)
                descriptions.append(working_description)
                data = []
                for name, param, description in zip(names, arthur_types, descriptions):
                    data.append(param)
                    data.append('@')
                    data.append(name)
                    data.append('\nㅡ\n')
                    data.append(description)
                    data.append('\nㅡ\n')
                working_user = None
                data[-1] = '\n'
                write_kma_db('./database/KMA_DB.txt', ''.join(data))
                await message.channel.send(working_param + '@' + working_name + '\n\n' + working_description +
                                           '\n으로 추가되었습니다.')
            else:
                descriptions[working_index] = text
                data = []
                for name, param, description in zip(names, arthur_types, descriptions):
                    data.append(param)
                    data.append('@')
                    data.append(name)
                    data.append('\nㅡ\n')
                    data.append(description)
                    data.append('\nㅡ\n')
                working_user = None
                data[-1] = '\n'
                write_kma_db('./database/KMA_DB.txt', ''.join(data))
                await message.channel.send(arthur_types[working_index] + '@' + names[working_index] + '\n\n' +
                                           text + '\n으로 갱신되었습니다.')
                working_index = -1
        elif text.startswith('취소'):
            if not working_user:
                await message.channel.send('현재 추가 중인 유저가 없습니다.')
                return
            if working_user != message.author:
                await message.channel.send(working_user.name +' 님만이 현재 취소할수 있습니다.')
                return
            working_user = None
            working_index = -1
            working_name = ''
            working_param = ''
            await message.channel.send('취소되었습니다.')
    return

keep_alive.keep_alive()
client.run(discord_token.token)
