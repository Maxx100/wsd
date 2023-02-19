import os
import subprocess
import argparse
from PIL import Image


# Путь к нашему исполняемому файлу
path = os.path.dirname(os.path.abspath(__file__))


# Красивый вывод с цветами
def pprint(text, color="WHITE"):
    colors = {"WHITE": '\033[37m', "PURPLE": '\033[95m', "OKBLUE": '\033[94m',
    "OKCYAN": '\033[96m', "OKGREEN": '\033[92m', "WARNING": '\033[93m', "FAIL": '\033[91m'}
    print(colors[color], end="")
    print(text, end="")
    print(colors["WHITE"])



# Парсер аргументов
parser = argparse.ArgumentParser(description='Screen extractor')

# Путь к нашему дампу
parser.add_argument('-f', '--file', type=str,
                    help='Path to dump')
# Со сколькимим PID работать
parser.add_argument('--max_pids', type=int, default=100,
                    help='Max pid\'s count')
# Принудительное использование профиля
parser.add_argument('-p', '--profile', type=str, default="all",
                    help='Using profile: all (default); Win10; Win8; Win7; WinXP')

"""parser.add_argument('--skip_pids', type=bool,
                    const=True, default=False,
                    help='skip pids and dumo extracting')"""

"""
# Проверка наличия и корректность всех необходимых аргументов
args = parser.parse_args()
if not args.file:
    pprint("Missing arg --file", "FAIL")
    exit(-1)
elif not os.path.exists(f"{path}/{args.file}"):
    pprint(f"File not found: {path}/{args.file}", "FAIL")
    exit(-1)
if args.max_pids < 1:
    pprint(f"PIDS count cannot be < 1", "FAIL")
    exit(-1)


pprint("Searching explorer.exe...", "OKCYAN")
output = os.popen(f"{path}/vol.py -f {path}/{args.file} windows.pstree | grep 'explorer.exe'").read().split("\n")
pids = []
for i in output:
    if "explorer.exe" not in i:
        continue
    if "ress" in i:
        pids.append(int(i.split("ress")[0]))
    else:
        if "*" in i.split()[0]:
            pids.append(int(i.split()[1]))
        else:
            pids.append(int(i.split()[0]))
print()
pprint("Found PIDs: " + ", ".join(map(str, pids)), "OKCYAN")
if len(pids) > args.max_pids:
    pids = pids[:args.max_pids]
pprint("Executing pid's dump...", "OKCYAN")
for i in range(len(pids)):
    os.system(f"{path}/vol.py -f {args.file} windows.memmap --dump --pid {pids[i]} > /dev/null")
    print()
    pprint(f"Dump extracted: pid.{pids[i]}.dmp", "OKCYAN")
for i in pids:
    os.rename(f'pid.{i}.dmp', f'pid.{i}.dmp.data')

pprint("Extracting sreen size...", "OKCYAN")

if args.profile == "Win10":
    output = os.popen(f"{path}/vol.py -f {path}/{args.file} windows.registry.printkey --key \
        'ControlSet001\\Control\\UnitedVideo' --recurse | grep 'Resolution\\|BitsPerPel'").read().split("\n")
elif args.profile == "WinXP":
    output = os.popen(f"{path}/vol.py -f {path}/{args.file} windows.registry.printkey --key \
        'ControlSet001\\Services' --recurse | grep 'Resolution\\|BitsPerPel'").read().split("\n")
else:
    output = os.popen(f"{path}/vol.py -f {path}/{args.file} windows.registry.printkey --key \
        'ControlSet001\\Control\\UnitedVideo' --recurse | grep 'Resolution\\|BitsPerPel'").read().split("\n")
    output += os.popen(f"{path}/vol.py -f {path}/{args.file} windows.registry.printkey --key \
        'ControlSet001\\Services' --recurse | grep 'Resolution\\|BitsPerPel'").read().split("\n")

screen_size = {}
for i in output:
    if "BitsPerPel" in i or "XResolution" in i or "YResolution" in i:
        temp = list(map(int, i.replace("\t", " ").split()[1].split("-") + i.replace("\t", " ").split()[2].split(".")[0].split(":")))
        time = (((((temp[0] * 365) + temp[1] * 30) + temp[2]) * 24) + temp[3] * 60) + temp[4]
        if time not in screen_size:
            screen_size[time] = [-1, -1, -1]  # BitPerPel; X; Y
        # pprint(i.split("\t"), "WARNING")
        if "BitsPerPel" in i:
            screen_size[time][0] = int(i.split("\t")[-2])
        elif "XResolution" in i:
            screen_size[time][1] = int(i.split("\t")[-2])
        elif "YResolution" in i:
            screen_size[time][2] = int(i.split("\t")[-2])

pprint("Possible sizes:", "OKCYAN")
for i in sorted(screen_size, reverse=True):
    pprint(f"{screen_size[i][0]}bits {screen_size[i][1]}x{screen_size[i][2]}", "WARNING")"""

pids = [1632]
screen_size = {0: (32, 640, 480)}
pprint("Loading...", "OKCYAN")
for name in pids:
    file = open(f"pid.{name}.dmp.data", "rb").read()
    temp = [[]]
    flag = 0
    for i in file[85295108:85295108 + 640 * 480 * 4 + 1]:
        if len(temp[-1]) == 4:
            temp.append([])
        temp[-1].append(i)

    image = Image.new("RGB", (screen_size[max(screen_size)][1], screen_size[max(screen_size)][2]))

    pixels = image.load()
    for i in range(screen_size[max(screen_size)][1]):
        for j in range(screen_size[max(screen_size)][2]):
            pixels[i, j] = (temp[i + j * 640][2], temp[i + j * 640][1], temp[i + j * 640][0])

    image.save(f"{name}.png", "PNG")
