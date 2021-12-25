# SOME CODE IS TAKEN FROM [TRUCKERSMP-CLI](https://github.com/truckersmp-cli/truckersmp-cli)

# Python TruckersMP Launcher

This was a side project of mine during free time since I usually play TruckersMP on Euro Truck Simulator 2

## Requirements
- Windows 64bit installation (preferably 8 or 10)
- Python 3 (tested only on 3.10 but will likely work on older versions aswell)
- `aiohttp` and `aiofiles` for async operations

###  Reasons why I made this in the first place:
- Wanted to learn more about the windows api and how DLL injection works in Python
- Speed, mostly download speed since the official launcher is *really* slow when it comes to updates **(atleast for me, ~35 seconds for updating all files)**

# How to use

Download this repository using git `git clone https://github.com/michei69/Python-TruckersMP-Launcher`

Install the requirements `pip install -r requirements.txt`

Run `launch.py`

Keep in mind, this will take longer on first run due to python being slow, but it will speed up after python caches the code.

###### also dont scream at me for my ugly code ty
