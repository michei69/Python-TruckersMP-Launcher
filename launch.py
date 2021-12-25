###########################################
#####Main file for Starting TruckersMP#####
###########################################
import json
import sys
import os
import hashlib
import time
import aiohttp
import asyncio
import aiofiles
import ctypes
import ctypes.wintypes
from extra import *

StartingTime = time.time()

UPDATELINK = "https://update.ets2mp.com/files.json"
#dir = os.path.dirname(os.path.realpath(__file__))+"\\files" #what
DOWNLOADURL = "download.ets2mp.com"

def check_hash(path, digest, hashobj):
    """
    Compare given digest and calculated one.
    This returns True if the two digests match.
    Otherwise this returns False.
    path: Path to the input file
    digest: Expected hex digest string
    hashobj: hashlib object (e.g. hashlib.md5())
    """
    with open(path, "rb") as f_in:
        while True:
            buf = f_in.read(hashobj.block_size * 4096)
            if not buf:
                break
            hashobj.update(buf)
    return hashobj.hexdigest() == digest

def game_starter(gamedir: str, gameexe: str, dllpath: str): # prototype of a game starter
    kernel32 = ctypes.WinDLL('Kernel32', use_last_error=True)
    dllpath = os.path.abspath(dllpath)

    startupinfo = STARTUPINFO()
    procinfo = PROCESS_INFORMATION()
    secAtr1 = SECURITY_ATTRIBUTES()
    secAtr2 = SECURITY_ATTRIBUTES()

    os.environ["SteamGameId"] = "227300" # 227300 is ETS2 game id
    os.environ["SteamAppId"] = "227300" # must set the app id aswell

    proc = kernel32.CreateProcessW(gamedir + gameexe, None, byref(secAtr1), byref(secAtr2), BOOL(False), 0x4, 0, gamedir, byref(startupinfo), byref(procinfo))
    if not proc:
        raise FileNotFoundError("Could not start Euro Truck Simulator 2") # could make this better ngl 
    
    proc = procinfo.hProcess
    intPtr = kernel32.VirtualAllocEx(proc, 0, (len(dllpath) + 1) * sizeof(WCHAR), 0x1000, 0x40)
    if intPtr == 0:
        sys.exit("Could not allocate memory") # TODO: again, same thing
    
    flag = kernel32.WriteProcessMemory(proc, intPtr, dllpath, (len(dllpath) + 1) * sizeof(WCHAR), None)
    if not flag:
        sys.exit("Could not write memory") # TODO: at this point i think i just need to make an error handler rlly
    
    hKernel = kernel32._handle

    anotherIntPtr = kernel32.CreateRemoteThread(proc, 0, 0x0, kernel32.LoadLibraryW, intPtr, 0x0, None)
    if not anotherIntPtr:
        sys.exit("Could not create remote thread") # TODO: :weary:
    
    kernel32.WaitForSingleObject(anotherIntPtr, -1) #wait 10 sec
    num = DWORD(0)
    kernel32.GetExitCodeThread(anotherIntPtr, byref(num))
    # print(num) # exitcode
    if num == 0x0:
        sys.exit("Initialization of client has failed") # TODO: current state: crying
    
    kernel32.CloseHandle(anotherIntPtr)
    kernel32.FreeLibrary(HANDLE(hKernel))
    kernel32.ResumeThread(procinfo.hThread)

    print("Successfully started game")

async def download_file(url: str, dest: str, filename: str):
    # print("a") # testing this function 
    startTime = time.time()
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as res:
            data = await res.read()
            async with aiofiles.open(dest, "wb") as f:
                await f.write(data)
    return f"[{round(time.time() - startTime, 2)}sec] Finished downloading {filename}"

# @asyncio.coroutine
async def download_files(host: str, files_to_download: list[str]):
    # TODO: refactor this in asyncio -- doing this rn 24/12/2021 21:04 -- i think its done (21:51)

    file_count = 1
    try:
        tasks = []
        while len(files_to_download) > 0:
            path, dest, md5 = files_to_download[0]
            # md5hash = hashlib.md5() -- unused
            # bufsize = md5hash.block_size * 256 -- unused
            name = os.path.basename(dest)
            destdir = os.path.dirname(dest)
            url = f"https://{host}{path}"
            # name_getting = "[{}/{}] Get: {}".format(file_count, num_of_files, name) -- unused
            # print("Downloading file https://{}{} to {}".format(host, path, destdir)) # TODO: remove this print since its useless lol -- done as of 21:48
            os.makedirs(destdir, exist_ok=True)
            tasks.append(asyncio.ensure_future(download_file(url, dest, name)))
            del files_to_download[0] # lol del
            file_count += 1
            
        for file in asyncio.as_completed(tasks):
            tempres = await file
            print(tempres)
        # OLD IMPLEMENTATION -- using requests lib
        #     while len(files_to_download) > 0:
        #         path, dest, md5 = files_to_download[0]
        #         md5hash = hashlib.md5()
        #         bufsize = md5hash.block_size * 256
        #         name = os.path.basename(dest)
        #         destdir = os.path.dirname(dest)
        #         name_getting = "[{}/{}] Get: {}".format(file_count, num_of_files, name)
        #         print(
        #             "Downloading file https://{}{} to {}".format( host, path, destdir))

        #         # make file hierarchy
        #         os.makedirs(destdir, exist_ok=True)

        #         # download file
        #         c =s.get("https://"+host+path)
        #         with open(dest,"wb") as f:
        #             f.write(c.content)
                
        #         del files_to_download[0]

        #         file_count += 1
    except (OSError, aiohttp.client.HTTPException) as ex:
        print("Failed to download https://{}{}: {}}".format(host, path, ex))
        print("Trying again")
        check()

    return True

async def check(gamedir, gameexe, TMPdir):
    if not os.path.isdir(TMPdir):
        print(f"Creating TruckersMP dir: {TMPdir}")
        os.makedirs(TMPdir)

    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(UPDATELINK) as thing:
                files_json = await thing.read()
    except (OSError, aiohttp.client.HTTPException) as ex:
        sys.exit("Failed to download files.json: {}".format(ex))

    modfiles = []
    try:
        for item in json.JSONDecoder().decode(str(files_json, "ascii"))["Files"]:
            if item["Type"] != "ats":
                modfiles.append((item["Md5"], item["FilePath"]))
        if len(modfiles) == 0:
            raise ValueError("File list is empty")
    except ValueError as ex:
        sys.exit(f"Failed to parse files.json: {ex}")

    dlfiles = []
    for md5, jsonfilepath in modfiles:
        modfilepath = os.path.join(TMPdir, jsonfilepath[1:])
        if not os.path.isfile(modfilepath):
            dlfiles.append(("/files" + jsonfilepath, modfilepath, md5))
            continue
        try:
            if not check_hash(modfilepath, md5, hashlib.md5()):
                dlfiles.append(("/files" + jsonfilepath, modfilepath, md5))
        except OSError as ex:
            sys.exit(f"Failed to read {modfilepath}: {ex}")
    
    if len(dlfiles) > 0:
        message_dlfiles = "Files to download:\n"
        for path, _, _ in dlfiles:
            message_dlfiles += f"  {path}\n"
        print(message_dlfiles.rstrip())
    else:
        print("No files to download")
    
    await download_files(DOWNLOADURL, dlfiles)
    if not "--download-only" in sys.argv:
        game_starter(gamedir, gameexe, f"{TMPdir}\\core_ets2mp.dll")
    EndingTime = time.time()
    print("Time taken: "+str(round(EndingTime-StartingTime,3)))

if __name__ == "__main__": 
    GameDir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Euro Truck Simulator 2\\bin\\win_x64\\" # TODO: get this off of registry
    GameExec = "eurotrucks2.exe" # TODO: make this interchangable between ETS2 and ATS
    TMPDir = "C:\\ProgramData\\TruckersMP" # TODO: make TMP folder movable
    asyncio.run(check(GameDir, GameExec, TMPDir))