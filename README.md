# TWS - Equities Data Downloader
Owner: **K2Q Capital Limited**  
Author: **Mandeep Singh**  
Updated On: **04th January 2021**  
Latest Release: **1.0.0**  


## Table Of Contents:
1. **[About this project](#About-this-project:)**  
2. **[Prerequisites](#Prerequisites:)**  
3. **[How to use this project?](#How-to-use-this-project?)**  
4. **[Available commands & options](#Available-commands-&-options:)**  
5. **[Sample Commands](#Sample-Commands:)**  
5. **[How to contribute to this project?](#How-to-contribute-to-this-project?)**  
6. **[Contact information](#Contact-information:)**  
7. **[License](#License:)**  


### About this project:
TWS Equities Data Downloader is a Python project written around [Interactive Broker's API](https://interactivebrokers.github.io/tws-api/introduction.html) that provides access to stock data from different financial exchanges. It is designed to be flexible enough to accomodate various market parameters and provide data ready to be consumed in an organized fashion by means of JSON objects.
<br><font size="1">**NOTE:** Currently the program has only been tested on Japanese Market.</font>


### Prerequisites:
Before users try to interact with the code, they must ensure that following criteria are met:
- Install **Python 3.8** or later.
- Use **Linux** or **Mac OS** machine, Windows is not currently supported.
- Have some basic knowledge about using **Command Line Interfaces(CLIs)**.

Once the above requirements are, follow the below steps to setup the project on your local machine:

#### Cloning the project:
To be able to use this code to extract market data, user first needs have the code cloned to into their local machine. Run the following command to do that:  
<b>
```
    git clone https://github.com/sudoMode/TWS-Project.git
```
</b>

#### Virtual Environment
The project itself contains the **virtual environment(env_k2q)** needed to run the code, so that user doesn't have to spend time getting all the dependencies right. Though the user is expected to activate the vritual environment before trying to extract any data, here's how to do it:
1. Change directory to project directory:  
```
    cd TWS-Project
```
   
2. Activate the virtual environment:  
```
    source env_k2q/bin/activate
```

<font size="1">**NOTE:** "env_k2q/bin" contains multiple activation scripts, command given above works for Linux based system that use bash as their default shell. Use one according to your system envrionment.</font>  

#### Launch IB's Trader Work Station(TWS):
User must launch TWS prior to interacting with the code, this is necessary because IB API will be hosted on your local machine once you're logged into TWS. Code uses default values to connect with the API which can be tweaked from Global API Settings in TWS.  
<b>
```
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 7497
```
</b>

<font size="1">
**NOTE:**  
    
    - To allow connections from other hosts, add the requesting to host address to "Trusted IPs" under "Edit -> Global Configuration -> API -> Settings".  
    - Developers must only log into **TWS Paper Trading** account, credentials for which can be retreived from (To be added...).
</font>


### How to use this project?
Once all the above mentioned prerequisites are met, user can start interacting with the code via given Command Line Interface(CLI). The main file that serves as the starting point for the program is called **"controller.py"**, user can call this file and pass arguments in the following manner:  
<font size="2"><b>
```
  python controller.py --end-date 20210104 --end-time 09:01:00 -vb tickers -l 1301
```
</font></b>

User can expected output data to be in the following format:  
<font size="1"><b>
```
    {
      "1301": {
        "bar_data": [
          {
            "average": 2951.0,
            "close": 2951.0,
            "count": 1,
            "high": 2951.0,
            "low": 2951.0,
            "open": 2951.0,
            "session": 1,
            "time_stamp": "20210104  09:00:00",
            "volume": 300
          }
        ],
        "meta_data": {
          "_error_stack": [],
          "attempt": 1,
          "end": "20210104  09:01:00",
          "output_file": "~/TWS-Project/data_files/historical_data/20210104/success/1301.json",
          "start": "20210103  09:01:00",
          "status": true
        }
      }
    }
```
</b>  

**NOTE:** Default nature of the program is to create a data dump in the form of a JSON file for each ticker that is processed, the same JSON file is used to create a final CSV file and can be found at the location mentioned inside "out_file" field in the "meta_data" section. This feature can be turned off by use "--data-dump / -dd " toggle.
</font>


### Available commands & options:
The project provides a large catalog of CLI options that user can tweak according to his prefrences, here's a detailed description of them all:
#### Commands:
- **tickers:**  
> Tickers commands is to be used to pass ticker IDs as an inout to the program, there're 3 ways in which the user can do so:
> - **--list / -l:** This option will let you pass a custom list of ticker IDs as input.<br>
>> <font size="2">**Sample:**  
```
        python controller.py tickers -l 1301 1302 13013 1304 1305
```
</font>  

> - **--file / -f:** This option will let you pass a file path as the ticker input, file must be a CSV and should contain ticker IDs for which the data is to be exracted.  
>> <font size="2">**Sample:**  
```
        python controller.py tickers -f data_files/input/tickers.csv
```
</font>  

> - **--url / -u:** This option will let you pass a Google Sheet URL as ticker input.<br>
>> <font size="2">**Sample:**  
```
        python controller.py tickers -u https://sheets.google.com/?sheet_id=123
```
</font>  


>>> <font size="1">**NOTE:**  
>>>> - URL feature is still being developed and is not available for live usage.<br>
>>>> - As of now it is mandatory to first pass all the optional arguments and then use the **tickers** command at the end of the CLI call, this is because of how Python's Argparse accepts optional arguments. This feature will be improved in future releases.  
</font>

#### Options:  

- **--end-date / -ed:** This option can be used to pass as an argument a date value that will be used as the target date for which the data extraction is to be perfomed.<br>
Expected date format: "YYYYMMDD"  
Default value: "20210104"  

- **--end-time / -et:** This options can be used to pass as an argument a time value will be used as the target time for which the extraction is to be perfomed.<br>
  Expected time format(24 hour): "HH:MM:SS"<br>
  Default value: "15:01:00"<br>
- **--duration / -d:** This field will specify the amount of time to go back from the end date & time value. This field accepts very sepcific values, understand more in detail about this field by running the **--help** option against the CLI or by visiting [IB API help page](https://interactivebrokers.github.io/tws-api/historical_bars.html).<br>
  Default value: "1 D"<br>
- **--bar-size / -b:** This field specifies the granularity of the data to be extracted. User can choose from a variety of bar-sizes, [find them here](https://interactivebrokers.github.io/tws-api/historical_bars.html).<br>
  Default value: "1 min"<br>
- **--what-to-show / -w:** This field decides the type of the data that is to be retrieved.<br>
  Supported values: ["TRADES", "MIDPOINT", "BID", "ASK"]
  Default value: "TRADES"
- **-use-rth / -u:** Using this option user can extract data which is outside regular trading hours, this feature is yet to be tested properly and currently the CLI only supports the default option which is 1 or provides data within regular trading hours only.<br>
- **--data-dump / -dd:** This switch can be toggled to diabled data-dump feature, by default this stays on and creates a data-dump for every ticker in the form of a JSON file.
- **--verbose / -vb:** Toggle this switch to increase the verbosity of the program and start seeing log messages on the console.
- **--debug / -db:** Toggle this switch to get detailed info about the program execution.


### Sample Commands:

- **Basic Usage:**
    - Specifying tickers as a list.<br>
      <font size="2"><b>
    ```
        python controller.py tickers -l 1301 1302
    ```
  </b></font>
    - Specifying tickers in a file.<br>
      <font size="2"><b>
    ```
        python controller.py tickers -f data_files/input/tickers.csv
    ```
  </b></font>

- **Modifying optional parameters:**
    - Setting end-date.<br>
      <font size="2"><b>
    ```
        python controller.py -ed 20201231 tickers -l 1301 1302
    ```
  </b></font>
    - Setting end-time.<br>
      <font size="2"><b>
    ```
        python controller.py -ed 20201231 -et 09:01:00 tickers -l 1301 1302
    ```
  </b></font>
    - Disable data-dump creation.<br>
      <font size="2"><b>
    ```
        python controller.py -ed 20201231 -et 09:01:00 -dd tickers -l 1301 1302
    ```
  </b></font>
    - Enable debug messages.<br>
      <font size="2"><b>
    ```
        python controller.py -ed 20201231 -et 09:01:00 -dd -db tickers -l 1301 1302
    ```
  </b></font>

<br><font size="1">
**NOTE:** CLI provides support for many other options to be used an input, please refer to the [Available commands & options section](#Available-commands-&-options:) for more details on the all available options.
</font>


### How to contribute to this project?
This project follows a pretty straightforward branching strategy that allows new developers to contribute in a very intuitive manner. Branching strategy is as follows:<br>
<b>
```
    dev --> test --> master
```
</b>

- **Master** branch is the default one and used to create new release links.
- **Test** branch contains the new features for which developement has been completed and are being tested currently.
- **Dev** branch always has the latest code and all the experimental features that are under development.

Developer are recommended to follow the steps below to make contribution to the project:
#### 🐞 Raise a bug:
- Users can drop an email to ***(to be added...)*** with a detailed description of the problem.
- It is recommended that users attach screenshot of the problem and also provide input command &
  output received from the CLI.

#### 💻 Contribute to code:
- Developers are recommended to fork this Github repository and code new features in their in your repository.
- Create a new branch by the name of the feature you are developing.
- Once changes are done, commit them with proper messages.
- Push the original branch back to origin and create a pull request.
- Changes will be reviewed and merged after approval from the repository owner.

#### 📖 Contibuting to documentation:
- If you spot a problem with the project documentation and wish to report it, please follow the steps mentioned under **[Raise a bug section](#Raise-a-bug:)**.
- If you want to update the documentation yourself:
    - Fork the **dev** branch and make your changes.
    - Publish your changes(with proper commit messages) and create a pull request back into the **dev** branch.


### Contact information:
- Project Owner: **[Aman Oberoi](mailto:aman.oberoi@k2qcapital.com)**
- Developers:
    - **[Mandeep Singh](mailto:mandeep@amakaan.com)**
    - **[Kiran Kumar](mailto:kiran@amakaan.com)**


### License:
This project uses a `GNU GENERAL PUBLIC LICENSE Version 3(GPLv3)`.
